# 12. 兼容性

> 状态:**规范性**。定义 CLI 与 Wrapper 如何协商协议版本、容忍对方新增。

## 协议版本

```text
MAJOR.MINOR
```

CLI / Wrapper 通过 `manifest.protocol.version` 通告自己说的协议版本。见 [02-核心协议.md § 协议版本](./02-core-protocol.md)。

## Bumping 规则

### MAJOR

不兼容变更时递增:

- 重命名 / 删除字段
- 改字段语义
- 改线缆格式(如换 Line Protocol)
- 复用稳定标识符(CLI id、error code 等)

Wrapper  MAY 拒绝不支持 MAJOR 的 CLI。

### MINOR

向后兼容新增时递增:

- 加可选字段
- 加枚举值(老值仍能用)
- 加新 event 类型
- 加新操作

老 Wrapper 必须容忍新字段;老 Wrapper MAY 忽略不识别的事件。

## 未知字段

接收方必须忽略未知字段。例:

```yaml
# CLI 发(新版本,加了 speed)
{type: event, event: progress, current: 50, total: 100, speed: 123.4}

# 老 Wrapper 读这条消息
# 不认 `speed` → 必须忽略并继续
```

模式:**未知字段必须忽略。**

例外:某些值是稳定标识符,未知时**可**拒绝:

```text
protocol major version   → 可拒绝
event type               → 除非 type=command 否则忽略
operation type           → 拒绝(unsupported operation, exit 4)
validation rule type     → 不识别类型时忽略
```

## 未知事件

```text
错误:
    if event == "unknown_event_type":
        raise ProtocolError

正确:
    skip silently
```

Wrapper **必须**忽略未知 event 类型。这让 CLI 可以演化事件词汇而不破坏老 Wrapper。

## Feature negotiation

`features` 报 `false` 的能力,Wrapper **不得**调用。省略的能力 Wrapper 视为 `false`([03-能力发现.md § 否定式真理](./03-discovery.md))。

Wrapper 可在操作之间重新查 `features`,因为 CLI 能力可能变。

## 前向 / 后向兼容矩阵

| 变更 | 后向兼容? | 操作 |
| --- | --- | --- |
| 加可选字段 | 是 | MINOR bump |
| 加新 event 类型 | 是 | MINOR bump |
| 加新 operation | 是 | MINOR bump |
| 加新 error code | 是 | MINOR bump |
| 重命名字段 | **否** | MAJOR bump |
| 改字段语义 | **否** | MAJOR bump |
| 复用 error code | **否** | MAJOR bump |
| 删可选字段 | **否** | MAJOR bump |
| 改 Line Protocol | **否** | MAJOR bump |

## 稳定标识符

兼容 CLI 更新时这些字段必须稳定:

```text
CLI id              (manifest.id)
Engine id           (manifest.engine.id)
Operation 名        (request.operation 值)
Feature 名          (features.* 键)
Validation rule id  (rules[].id)
Error code          (event.code 值)
```

Wrapper 必须以这些值为键,**不**靠人类可读字符串。见 [09-诊断.md § Wrapper 规则](./09-diagnostics.md)。

## 可变标识符

```text
CLI 人类可读名          (manifest.name)
CLI 版本字符串          (manifest.version)
Event message 文本      (event.message)
Validation rule message (rules[].message)
Progress 值
Statistics 数字
```

Wrapper **不得**依赖这些字段的字节内容。

## CLI 版本 vs 协议版本

CLI 自身版本(`manifest.version`)与协议版本(`manifest.protocol.version`)相互独立:

```text
manifest.version          CLI 发布 (e.g. 1.2.0)
manifest.protocol.version 协议层级 (e.g. 1.0)
```

CLI 一次发布可绑定任何兼容的协议版本。

## CLI 与协议何时 bump

| CLI 变更 | Bump |
| --- | --- |
| 修 bug,内部重构 | CLI 版本(PATCH) |
| 加 feature flag(默认关) | CLI 版本(MINOR) |
| 加新 event type | CLI 版本(MINOR) + Protocol MINOR |
| 线缆格式变更 | Protocol MAJOR(并 CLI MAJOR) |

## 终极规则

> 增加第 100 个 CLI 不需要 Wrapper 改。
> 增加第 100 个 Wrapper 特性不需要 CLI 改。
> 增加新 GCWP 特性是 MINOR bump —— 老侧忽略。