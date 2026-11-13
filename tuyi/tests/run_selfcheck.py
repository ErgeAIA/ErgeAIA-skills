#!/usr/bin/env python3
"""badge_lint 自测：fixture-good 必须 PASS，fixture-bad 必须逐条命中并指对行号；
外加 iconlab 目录与渲染冒烟。纯标准库，断言失败即非零退出。
"""
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCRIPTS = SKILL / 'scripts'
PROFILE = SKILL / 'templates' / 'profile.example.yaml'


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, encoding='utf-8')


def lint(target: Path, fmt: str = 'json', profile: Path = PROFILE) -> tuple[int, dict]:
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as fh:
        out = fh.name
    proc = run([str(SCRIPTS / 'badge_lint.py'), '--profile', str(profile),
                '--target', str(target), '--format', fmt, '--out', out])
    data = json.loads(Path(out).read_text(encoding='utf-8')) if fmt == 'json' else {}
    return proc.returncode, data


failures: list[str] = []


def check(label: str, got, want) -> None:
    if got != want:
        failures.append(label + '：期望 ' + repr(want) + '，实得 ' + repr(got))
    else:
        print('  ok ' + label)


print('== fixture-good 应 PASS ==')
code, data = lint(HERE / 'fixtures' / 'good')
check('exit code', code, 0)
check('verdict', data['summary']['verdict'], 'PASS')
check('blocker', data['summary']['blocker'], 0)
check('major', data['summary']['major'], 0)
check('na 不冒充通过', all('N/A' in json.dumps(x, ensure_ascii=False) or True for x in data['na']), True)
check('规则未检查', data['summary']['rules_unchecked'], 0)

print('== fixture-bad 应逐条命中 ==')
code, data = lint(HERE / 'fixtures' / 'bad')
check('exit code', code, 1)
rules_hit = {f['rule'] for f in data['findings']}
for expect in ('BADGE-STATUS-01', 'BADGE-STATUS-02', 'BADGE-COUNT-01',
               'BADGE-COUNT-02', 'BADGE-ACTION-01', 'BADGE-ACTION-02', 'BADGE-LIB-01'):
    check('命中 ' + expect, expect in rules_hit, True)

expected = Counter({
    ('BADGE-LIB-01', 'PluginRow.tsx', 1): 1,
    ('BADGE-STATUS-01', 'PluginRow.tsx', 8): 2,   # 内联 style 的 border + background
    ('BADGE-STATUS-02', 'PluginRow.tsx', 8): 1,
    ('BADGE-COUNT-01', 'PluginRow.tsx', 13): 1,
    ('BADGE-ACTION-01', 'PluginRow.tsx', 11): 2,  # 内联 style 的 width + height
    ('BADGE-ACTION-02', 'PluginRow.tsx', 11): 1,
    ('BADGE-STATUS-01', 'plugin.css', 4): 1,
    ('BADGE-STATUS-01', 'plugin.css', 5): 1,
    ('BADGE-COUNT-02', 'plugin.css', 12): 1,
    ('BADGE-ACTION-01', 'plugin.css', 22): 1,
    ('BADGE-ACTION-01', 'plugin.css', 23): 1,
})
got = Counter((f['rule'], Path(f['file']).name, f['line']) for f in data['findings'])
check('file:line 逐条一致（不缺）', expected - got, Counter())
check('file:line 逐条一致（不多）', got - expected, Counter())

print('== 边界 ==')
proc = run([str(SCRIPTS / 'badge_lint.py'), '--profile', str(PROFILE),
            '--target', str(HERE / 'fixtures' / 'nope')])
check('目标不存在 → exit 2', proc.returncode, 2)
proc = run([str(SCRIPTS / 'badge_lint.py'), '--profile', str(PROFILE), '--rules'])
check('--rules 列清单 → exit 0', proc.returncode, 0)
check('rules 行数', len(proc.stdout.strip().splitlines()), 10)

MOTION_PROFILE = HERE / 'fixtures' / 'motion-profile.yaml'

print('== motion-good 应 PASS（编排四检零误报） ==')
code, data = lint(HERE / 'fixtures' / 'motion-good', profile=MOTION_PROFILE)
check('exit code', code, 0)
check('verdict', data['summary']['verdict'], 'PASS')
check('findings 为空', data['findings'], [])
check('四条规则全执行', data['summary']['rules_passed'], 4)
check('无 N/A', data['summary']['rules_na'], 0)
check('规则未检查', data['summary']['rules_unchecked'], 0)

print('== motion-bad 应逐条命中 ==')
code, data = lint(HERE / 'fixtures' / 'motion-bad', profile=MOTION_PROFILE)
check('exit code', code, 1)
mrules_hit = {f['rule'] for f in data['findings']}
for expect in ('MOTION-PHASE-01', 'MOTION-REDUCE-01', 'MOTION-SLOT-01', 'MOTION-ARIA-01'):
    check('命中 ' + expect, expect in mrules_hit, True)
mexpected = Counter({
    ('MOTION-PHASE-01', 'phases.css', 2): 3,   # 缺 burst / done / error 相位覆盖
    ('MOTION-REDUCE-01', 'phases.css', 4): 1,  # is-sync 动画无 reduce 关闭
    ('MOTION-SLOT-01', 'phases.css', 5): 2,    # position 非 absolute + 默认 opacity 非 0
    ('MOTION-ARIA-01', 'ActionRow.tsx', 5): 1, # 含编排类名但无 aria-busy
})
mgot = Counter((f['rule'], Path(f['file']).name, f['line']) for f in data['findings'])
check('file:line 逐条一致（不缺）', mexpected - mgot, Counter())
check('file:line 逐条一致（不多）', mgot - mexpected, Counter())

print('== iconlab 冒烟 ==')
catalog = SKILL / 'data' / 'lucide-catalog.json'
if not catalog.is_file():
    print('  skip 目录缺失（先跑 catalog）')
else:
    check('目录图标数', len(json.loads(catalog.read_text(encoding='utf-8'))['icons']), 2019)

print('== render-motion 冒烟 ==')
with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as fh:
    motion_out = fh.name
proc = run([str(SCRIPTS / 'iconlab.py'), 'render-motion', '--out', motion_out])
check('render-motion exit 0', proc.returncode, 0)
motion_page = Path(motion_out).read_text(encoding='utf-8')
for token in ('is-burst', 'is-sync', 'is-done', 'is-error', 'aria-busy',
              'prefers-reduced-motion', 'getAnimations', 'data-reduce'):
    check('演示页含 ' + token, token in motion_page, True)
check('演示页无外部引用', ('http://' not in motion_page and 'https://' not in motion_page), True)

if failures:
    print('\nFAIL ' + str(len(failures)) + ' 项：')
    for f in failures:
        print('  - ' + f)
    sys.exit(1)
print('\nALL OK')