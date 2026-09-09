# Shell 层规范(中文版)

本目录是 [`../`](../) 全部章节的简体中文翻译。

英文版是规范权威来源(specification of record);中文版用于阅读便利,**规范冲突时以英文版为准**。

---

## 章节目录

| # | 文档 | 范围 |
| --- | --- | --- |
| 00 | [术语表](./00-glossary.md) | Shell 层统一术语 |
| 01 | [概述](./01-overview.md) | 三大设计原则:Engine Specific / Project-Centric / Unix |
| 02 | [CLI 语法](./02-cli-grammar.md) | `tool [op][media] project [options]` |
| 03 | [操作](./03-operations.md) | `-e` / `-i` 与 media flag 的组合语义 |
| 04 | [媒体](./04-media.md) | 标准媒体 + 引擎扩展媒体 + Sub-Media |
| 05 | [配置文件](./05-config-file.md) | `gallate.yaml` 完整 schema |
| 06 | [项目结构](./06-project-structure.md) | 标准 init 结构 + 引擎扩展目录 |
| 07 | [Init](./07-init.md) | `init` 子命令 |
| 08 | [引擎扩展](./08-engine-extensions.md) | `--engine.*`、sub-media includes/excludes |
| 09 | [标准 flags](./09-std-flags.md) | `--output` / `--ignore` / `--dry-run` / `-v` / `-q` / `--force` |
| 10 | [stdout/stderr 与退出码](./10-stdout-stderr.md) | stdout vs stderr, 退出码表 |
| 11 | [一致性](./11-conformance.md) | "兼容 Shell 层" 的语义 |

---

## 阅读顺序

初读请按此顺序:

```text
00-术语 → 01-概述 → 02-CLI 语法
    ↓
03-操作 → 04-媒体 → 05-配置文件
    ↓
06-项目结构 → 07-Init → 08-引擎扩展
    ↓
09-flags → 10-stdout/stderr → 11-一致性
```

CLI 作者可只看:

```text
02-CLI 语法 → 04-媒体 → 05-配置文件 → 09-flags → 11-一致性
```