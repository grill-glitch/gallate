# GCWP 协议文档(中文版)

本目录是 [`../`](../) 全部章节的简体中文翻译。

英文版是规范权威来源(specification of record);中文版用于阅读便利,**规范冲突时以英文版为准**。

---

## 章节目录

| # | 文档 | 范围 |
| --- | --- | --- |
| 00 | [术语表](./00-glossary.md) | 统一术语 |
| 01 | [架构](./01-architecture.md) | OmegaT / Wrapper / CLI 职责边界 |
| 02 | [核心协议](./02-core-protocol.md) | 线缆格式、版本、Line Protocol |
| 03 | [能力发现](./03-discovery.md) | manifest + features |
| 04 | [操作](./04-operations.md) | extract / inject / build / unpack / repack |
| 05 | [事件流](./05-events.md) | 实时事件流 |
| 06 | [状态](./06-status.md) | 按需状态快照 |
| 07 | [统计](./07-statistics.md) | 结果指标 |
| 08 | [验证](./08-validation.md) | 引擎专有验证规则 |
| 09 | [诊断](./09-diagnostics.md) | stderr / error.code 语义 |
| 10 | [配置](./10-configuration.md) | `gallate.yaml` ↔ GCWP 请求转换 |
| 11 | [进程](./11-process.md) | 进程生命周期与取消 |
| 12 | [兼容性](./12-compatibility.md) | 版本、未知字段 |
| 13 | [一致性](./13-conformance.md) | Basic / Standard / Full 等级 |

---

## 阅读顺序

初读请按此顺序:

```text
00-术语 → 01-架构 → 02-核心协议
    ↓
03-能力发现 → 04-操作 → 05-事件
    ↓
06-状态 → 07-统计
    ↓
08-验证 → 09-诊断 → 10-配置
    ↓
11-进程 → 12-兼容性 → 13-一致性
```

CLI 作者可只看:

```text
03-能力发现 → 04-操作 → 05-事件 → 08-验证 → 13-一致性
```

Wrapper 作者必须通读,重点关注:

```text
03-能力发现 → 05-事件 → 06-状态 → 07-统计
→ 08-验证 → 11-进程 → 12-兼容性
```

---

## 版本

```text
name      : gcwp
version   : 1.0
status    : Draft
license   : CC BY-SA 4.0
```