# 05. 事件流

> 状态:**规范性**。定义 CLI 在操作过程中写到 stdout 的实时事件流。

事件是 Wrapper 的主要实时信号。必须是 YAML Line Protocol 格式。

## 标准事件

| 事件 | 必选等级 | 含义 |
| --- | --- | --- |
| `started` | Basic | 操作开始 |
| `phase` | Standard | 子阶段切换 |
| `progress` | Standard | 进度更新 |
| `file` | Standard | 文件级动作 |
| `resource` | Standard | 资源级动作(引擎粒度) |
| `warning` | Standard | 非致命警告 |
| `error` | Standard | 可恢复错误 |
| `validation` | Standard | 验证发现 |
| `statistics` | Standard | 统计快照(通常在完成时) |
| `completed` | Basic | 操作成功结束 |
| `cancelled` | Full | 操作被取消 |

Schema:[`schema/event.schema.yaml`](../../schema/event.schema.yaml)。

## started

```yaml
type: event
event: started
id: 01HXYZ
operation: extract
```

## phase

```yaml
type: event
event: phase
name: scanning
```

推荐阶段名:

```text
preparing
scanning
extracting
processing
writing
finalizing
```

阶段名可引擎扩展,以上只是建议。

## progress

```yaml
type: event
event: progress
current: 37
total: 100
```

不确定进度:

```yaml
type: event
event: progress
current: 37
total: null
```

Wrapper 必须支持不确定进度。

## file

```yaml
type: event
event: file
action: extract
path: script/scene_037.bin
```

标准 action:

```text
scan
read
write
create
modify
skip
extract
inject
delete
```

## resource

与 `file` 同形,但引擎资源粒度:

```yaml
type: event
event: resource
action: extract
path: scenes/day1/scene_037/string_0042
```

## warning

```yaml
type: event
event: warning
code: UNSUPPORTED_FORMAT
message: Unsupported resource format
path: foo.dat
```

`warning` **不得**引起非零退出码,除非 CLI 显式提升。见 [09-诊断.md](./09-diagnostics.md)。

## error

```yaml
type: event
event: error
code: INVALID_INPUT
message: Input archive is corrupted
path: ./game.pfs
```

`error.code` 是 Wrapper 分类错误的稳定键。`message` 可随版本变化。

## validation

```yaml
type: event
event: validation
rule: placeholder
severity: error

source: Hello {player}
target: 你好

message: Required placeholder is missing: {player}

file: script/scene_037.bin
line: 42
offset: 12
length: 8
```

见 [08-验证.md](./08-validation.md)。

## statistics

```yaml
type: event
event: statistics

statistics:
  files:
    processed: 317
  text:
    extracted: 8421
```

通常承载最终快照。见 [07-统计.md](./07-statistics.md)。

## completed

```yaml
type: event
event: completed

statistics:
  files:
    processed: 317
```

`completed` 表示操作成功结束。CLI 必须在 exit 0 前发出,然后进程退出。

## cancelled

```yaml
type: event
event: cancelled
```

CLI 必须在收到 `cancel` 命令后(见 [11-进程.md § 取消](./11-process.md))且在退出码 `6` 之前发出 `cancelled`。

## 事件顺序

```text
1. started                    必须
2. 零或多个:                   可选
   phase, progress, file, resource,
   warning, error, validation,
   statistics
3. 以下恰好一个:                必须
   completed, cancelled
```

两个终止事件为协议错误。