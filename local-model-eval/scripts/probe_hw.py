#!/usr/bin/env python3
"""硬件探测：只记录实测/规格/缺失，不推算不伪造。

输出 hardware.json，每个字段带 source 标注。任何命令失败一律写「缺失」+ 原因，
不猜、不沿用上次结果、不把规格当实测。
"""

from __future__ import annotations

import ctypes
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time

GIB = 1024 ** 3
MIB = 1024 ** 2


def field(value, source: str, note: str = "") -> dict:
    return {"value": value, "source": source, "note": note}


def missing(reason: str) -> dict:
    return field(None, "缺失", reason)


def run(cmd: list[str], timeout: float = 12.0) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"命令不存在：{cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"命令超时：{' '.join(cmd)}"
    except Exception as exc:  # noqa: BLE001
        return 1, "", f"{type(exc).__name__}: {exc}"


def probe_gpu_nvidia() -> dict:
    out = {"available": False, "vendor": "NVIDIA"}
    if not shutil.which("nvidia-smi"):
        out["error"] = "nvidia-smi 不在 PATH"
        return out
    query = ("name,memory.total,memory.free,memory.used,utilization.gpu,"
             "temperature.gpu,power.draw,clocks.sm,clocks.mem,"
             "pcie.link.gen.current,pcie.link.width.current")
    code, stdout, stderr = run(["nvidia-smi", f"--query-gpu={query}",
                                "--format=csv,noheader,nounits"])
    if code != 0 or not stdout:
        out["error"] = stderr or f"nvidia-smi 退出码 {code}"
        return out
    line = stdout.splitlines()[0]
    parts = [p.strip() for p in line.split(",")]
    keys = ["name", "vram_total_mib", "vram_free_mib", "vram_used_mib",
            "util_pct", "temp_c", "power_w", "clock_sm_mhz", "clock_mem_mhz",
            "pcie_gen", "pcie_width"]
    if len(parts) < len(keys):
        out["error"] = f"nvidia-smi 字段数不足：{len(parts)}/{len(keys)}"
        return out
    for k, v in zip(keys, parts):
        out[k] = field(v, "实测")
    for k in ["vram_total_mib", "vram_free_mib", "vram_used_mib", "util_pct",
              "temp_c", "power_w", "clock_sm_mhz", "clock_mem_mhz",
              "pcie_gen", "pcie_width"]:
        try:
            out[k]["value"] = float(out[k]["value"])
        except (TypeError, ValueError):
            out[k] = missing(f"无法解析原始值 {out[k]['value']!r}")
    out["available"] = isinstance(out.get("vram_total_mib", {}).get("value"), float)
    out["stability"] = field("单次采样，非负载稳定区间", "缺失",
                             "本探测未执行持续负载，采样值不得当作稳定读数")
    return out


def probe_memory() -> dict:
    out = {}
    if sys.platform == "win32":
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        st = MEMORYSTATUSEX()
        st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ok = bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)))
        if ok:
            out["total_gib"] = field(round(st.ullTotalPhys / GIB, 2), "实测")
            out["available_gib"] = field(round(st.ullAvailPhys / GIB, 2), "实测")
            out["load_pct"] = field(st.dwMemoryLoad, "实测")
            out["pagefile_total_gib"] = field(round(st.ullTotalPageFile / GIB, 2), "实测",
                                              "分页文件不等于物理内存，不参与容量预算")
        else:
            out["error"] = "GlobalMemoryStatusEx 调用失败"
    else:
        try:
            info = {}
            with open("/proc/meminfo", encoding="utf-8") as fh:
                for line in fh:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        info[k] = v.strip()
            total = re.search(r"(\d+)", info.get("MemTotal", ""))
            avail = re.search(r"(\d+)", info.get("MemAvailable", ""))
            if total:
                out["total_gib"] = field(round(int(total.group(1)) * 1024 / GIB, 2), "实测")
            if avail:
                out["available_gib"] = field(round(int(avail.group(1)) * 1024 / GIB, 2), "实测")
            if not total or not avail:
                out["error"] = "/proc/meminfo 字段缺失"
        except Exception as exc:  # noqa: BLE001
            out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def probe_cpu() -> dict:
    name = platform.processor()
    out = {
        "name": field(name or None, "实测" if name else "缺失",
                      "" if name else "platform.processor() 返回空"),
        "logical_cores": field(os.cpu_count(), "实测"),
    }
    code, stdout, _ = run(["wmic", "cpu", "get", "Name,NumberOfCores,NumberOfLogicalProcessors",
                           "/format:list"], timeout=8)
    if code == 0 and stdout:
        vals = {}
        for line in stdout.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip()
        if vals.get("Name"):
            out["name"] = field(vals["Name"], "实测")
        if vals.get("NumberOfCores"):
            out["physical_cores"] = field(int(vals["NumberOfCores"]), "实测")
    else:
        out["topology_note"] = field(None, "缺失", "无法读取物理核心布局（wmic 不可用）")
    out["sustained_freq"] = missing("本探测未执行持续负载，无稳定频率读数")
    return out


def probe_gpu_details() -> dict:
    """架构与显存类型属于规格，不在本次实测里——留给外部 JSON 输入。"""
    return {
        "architecture": field(None, "缺失", "nvidia-smi 不返回架构代号，需用户提供或查规格"),
        "vram_type": field(None, "缺失", "nvidia-smi 不返回显存类型，需用户提供或查规格"),
        "bus_width": field(None, "缺失", "需规格数据"),
        "memory_bandwidth_gbs": field(None, "缺失", "未运行 bandwidthTest，理论带宽不等于有效带宽"),
        "stream_triad_gbs": field(None, "缺失", "未运行 STREAM Triad"),
    }


def probe() -> dict:
    gpu = probe_gpu_nvidia()
    data = {
        "schema": "hardware-fit/1",
        "probed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "platform": field(platform.platform(), "实测"),
        "python": field(platform.python_version(), "实测"),
        "gpu": gpu,
        "cpu": probe_cpu(),
        "ram": probe_memory(),
        "gpu_specs": probe_gpu_details(),
        "method_note": "单次采样。稳定区间、持续负载、带宽测试均未执行，对应字段标缺失。",
    }
    return data


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="探测本机硬件，逐项标注来源")
    ap.add_argument("--out", default="hardware.json", help="输出 JSON 路径")
    ap.add_argument("--stdout", action="store_true", help="同时打印到 stdout")
    args = ap.parse_args()
    data = probe()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    if args.stdout:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        gpu = data["gpu"]
        if gpu.get("available"):
            print(f"GPU: {gpu['name']['value']}  显存 {gpu['vram_free_mib']['value']:.0f}/"
                  f"{gpu['vram_total_mib']['value']:.0f} MiB 空闲（实测）")
        else:
            print(f"GPU: 未取得实测数据（{gpu.get('error', '未知')}）", file=sys.stderr)
        ram = data["ram"]
        print(f"RAM: {ram.get('total_gib', {}).get('value', '—')} GiB 总量 / "
              f"{ram.get('available_gib', {}).get('value', '—')} GiB 可用（实测）")
        print(f"已写入 {os.path.abspath(args.out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
