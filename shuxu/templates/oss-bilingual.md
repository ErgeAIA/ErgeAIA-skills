# 开源双语模板指南

生成两个文件：**README.md（中文主文件）** + **README.en.md（英文版）**。
两文件章节一一对应，标题下方互放语言切换链接。以下为章节骨架，按项目复杂度删减；占位符按实际内容替换。

## README.md 结构（中文主文件）

```markdown
# {项目名}

[English](README.en.md) | [中文](README.md)

> {一句话定位：解决什么问题、与同类方案的差异}

{徽章区：仅真实来源（CI 状态 / License / 版本）；动态数字徽章（stars/downloads）标注动态值}

## 核心功能
- {每条必须可追溯到具体代码}

## 下载 / 安装
{平台矩阵 + 精确版本链接；前置要求：运行时 + 最低版本（以清单文件 engines 为准）}
```bash
{精确命令，来源：清单文件}
```

## 快速上手
{最小可用示例 + 预期输出；未运行验证的示例标注「未经运行验证」}

## 用法
{示例先于解释；配置项用表格}
| 配置项 | 类型 | 默认值 | 说明 |
| ------ | ---- | ------ | ---- |
| {name} | {type} | {default} | {说明} |

## 测试
```bash
{精确测试命令}
```

## 常见问题 / 已知限制
- {如实列出，不回避}

## 贡献
See [CONTRIBUTING.md](CONTRIBUTING.md)。{行为准则 + PR 流程}

## 许可
{License 名称} — see [LICENSE](LICENSE)。
```

## README.en.md 结构（英文版，平行对照）

```markdown
# {Project Name}

[中文](README.md) | [English](README.en.md)

> {One-line value proposition}

## Core Features
## Download / Install
## Quick Start
## Usage
## Testing
## FAQ / Known Limitations
## Contributing
## License
```

术语对照规则：专有名词（CLI、API、运行时名）保持英文；正文术语中英版本一致，首次出现可附括号注释。
