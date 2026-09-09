# 02. 核心协议

> 状态:**规范性**。定义 GCWP 的最低层:版本字符串、线缆格式、通道、退出码。

本章与具体操作(`extract`、`inject` …)刻意无关。操作见 [04-操作.md](./04-operations.md)。

## 通信模型

CLI 是独立进程。Wrapper 启动后通过标准 I/O 与之通信:

```text
stdin   ← Request / Command       (Wrapper 发出)
stdout  → Response / Event 流     (Wrapper 读取)
stderr  → 人类可读诊断             (给用户 / 日志)
exit    → 最终结果                 (Wrapper 读取)
```

机器可读通道(stdin / stdout)使用 **YAML Line Protocol**:每行一个 YAML 文档。普通文本或自由日志**不得**出现在 stdout —— 必须走 stderr。

## YAML Line Protocol

stdin / stdout 上每条携带协议内容的行必须是一个独立 YAML 文档。推荐 flow-mapping 单行形式以保持紧凑:

```yaml
{type: event, event: started, operation: extract}
{type: event, event: progress, current: 10, total: 100}
{type: event, event: progress, current: 50, total: 100}
{type: event, event: completed}
```

接收方必须把每行视为独立文档。

允许多行 block YAML,但接收方仍必须把每行作为独立 YAML 文档处理,**不得**要求跨行解析。

JSON Lines(NDJSON / JSONL)**不属于** GCWP。实现可以出于遗留原因同时支持两者,但新字段必须以 YAML 规定。

## 通道

| 通道 | 方向 | 内容 |
| --- | --- | --- |
| stdin | Wrapper → CLI | 一条或多条协议消息:通常一次操作请求,可选 `cancel` 命令 |
| stdout | CLI → Wrapper | 初始 `response`,随后是事件流 |
| stderr | CLI → 用户 | 人类可读诊断,**不是**协议 |
| exit | CLI → OS | 整数退出码 |

## 协议版本

每条 GCWP 消息必须声明协议版本。版本字符串 `MAJOR.MINOR`(如 `1.0`、`1.1`、`2.0`)。

```yaml
type: protocol
name: gcwp
version: 1.0
```

### MAJOR

不兼容变更时递增。

```text
1.x → 2.x   Wrapper 可拒绝不支持的 MAJOR
```

### MINOR

向后兼容新增时递增。

```text
1.0 → 1.1   老 Wrapper 忽略未知字段
```

完整规则见 [12-兼容性.md](./12-compatibility.md)。

## 消息类型

| `type` | 方向 | 用途 |
| --- | --- | --- |
| `protocol` | 双方 | 通告 / 检查协议版本 |
| `request` | Wrapper → CLI | 操作请求 |
| `command` | Wrapper → CLI | 带外指令(当前只有 `cancel`) |
| `response` | CLI → Wrapper | 确认请求并通告操作 ID |
| `event` | CLI → Wrapper | 事件流的一项 |
| `validation` | CLI → Wrapper | 操作中或操作后的验证发现 |

所有消息类型由 [`schema/`](../../schema/) 下的 JSON Schema 定义。

## 操作流(骨架)

```text
Wrapper                          CLI
   │                              │
   │  ── request ──────────────▶  │   (一次操作)
   │                              │
   │  ◀── response ────────────  │   (确认)
   │                              │
   │  ◀── event started ───────  │
   │  ◀── event progress ──────  │
   │  ◀── event file ──────────  │
   │  ◀── event warning ───────  │
   │  ◀── event completed ─────  │
   │                              │
   │  exit code                  │
```

若 Wrapper 想中止:

```text
Wrapper                          CLI
   │                              │
   │  ── command cancel ───────▶  │
   │                              │
   │  ◀── event cancelled ─────  │
   │  exit code 6                 │
```

## 退出码

标准退出码 —— 语义不得改变:

| Code | 含义 |
| --- | --- |
| `0` | 成功 |
| `1` | 操作失败 |
| `2` | 参数错误 |
| `3` | 配置错误 |
| `4` | 不支持的操作 |
| `5` | 验证失败 |
| `6` | 已取消 |
| `7` | 协议错误 |
| `8` | 内部错误 |

CLI 可定义额外退出码;标准码语义必须保留。

## 退出码 vs 事件的关系

```text
Event     → 过程信息(操作中)
Exit code → 最终结果(操作后)
```

Wrapper 必须同时考虑两者,**不得**仅由最后一个 event 推断结果。

例子:

```text
started
progress
error               (事件:流级失败)
exit 1               (进程级失败)
```

```text
started
progress
cancelled
exit 6
```