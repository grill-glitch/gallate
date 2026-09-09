# 09. 诊断

> 状态:**规范性**。定义两条非协议通道(stderr)和协议通道中使用的结构化错误模型。

## 通道

```text
stdout  → 机器协议       (Response / Events)
stderr  → 人类诊断        (日志 / 警告 / 给用户的进度)
exit    → 最终结果        (整数)
```

边界严格:

- `stdout` 只发协议。CLI **不得**在 stdout 打自由文本或装饰性进度条。
- `stderr` 给人看。CLI 可用 ANSI 颜色、进度条、verbose dump。Wrapper **不得**解析 stderr。

Wrapper **不得**通过解析 stderr 判定操作状态。见 [02-核心协议.md § 通道](./02-core-protocol.md)。

## stderr 内容示例

```text
Scanning archive...
Extracting text from scene_037.bin...
warning: foo.dat uses unsupported format, skipping

✓ 317 files processed
✓ 8421 strings extracted
```

这些行面向操作员的终端与 wrapper 的日志文件。格式引擎自定,可随时变。

## 结构化错误

Wrapper 必须分类的错误走协议(`event: error`),带稳定 `code`:

```yaml
type: event
event: error
code: INVALID_INPUT
message: Input archive is corrupted
path: ./game.pfs
```

### 必填字段

| 字段 | 备注 |
| --- | --- |
| `code` | 稳定、机器分类。UPPER_SNAKE_CASE。 |
| `message` | 人类可读,可跨版本变。 |

### 可选字段

| 字段 | 备注 |
| --- | --- |
| `path` | 错误所指资源路径 |
| `file` | 源文件(与 `path` 不同时) |
| `line` | 行号 |
| `offset` | 字符偏移 |
| `length` | 区域长度 |
| `resource` | 逻辑资源 id(引擎定) |
| `details` | 自由格式额外上下文(object) |

### Wrapper 规则

```text
错误:
    if "corrupted" in message:
        show_repair_dialog

正确:
    if code == "INVALID_INPUT":
        show_repair_dialog
```

Wrapper 必须以 `code` 为键,**绝不**以 `message` 为键。

## 稳定错误码

CLI 必须给可分类错误选稳定 code:

```text
INVALID_INPUT
INVALID_CONFIG
UNSUPPORTED_OPERATION
UNSUPPORTED_FORMAT
UNSUPPORTED_ENCODING
FILE_NOT_FOUND
PERMISSION_DENIED
ARCHIVE_CORRUPTED
CHECKSUM_MISMATCH
OUT_OF_MEMORY
TIMEOUT
INTERNAL_ERROR
PROTOCOL_ERROR
```

Minor 版本可加新 code;code **不得**复用。

见 [12-兼容性.md § 稳定标识符](./12-compatibility.md)。

## 警告 vs 错误

`warning` 事件**不得**引起非零退出码,除非 CLI 显式提升。`error` 事件**应**导致非零退出码(通常 `1` 或更具体 code),但 CLI 也可继续运行(用于弹性批处理)。

推荐映射:

```text
warning event       → exit code 不变
error event         → exit code 1
protocol violation  → exit code 7
internal crash      → exit code 8
```

CLI 可自行决定具体映射,标准 code 见 [02-核心协议.md § 退出码](./02-core-protocol.md)。

## 调试 / Verbose

CLI 可支持 `--verbose` / `--debug`。影响的是 stderr 详细度,不影响协议流:

```text
--verbose   → 更多 stderr 行
--debug     → verbose + 引擎内部 (仍在 stderr)
```

启用 verbose 时 CLI **不得**改协议流。

## 取消的诊断

取消时 CLI 可给操作员最后一行 stderr:

```text
warning: operation cancelled, cleaning up temp files
```

但协议必须显示 `cancelled` event 与 exit code `6`。