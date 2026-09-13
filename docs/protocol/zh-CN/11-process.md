# 11. 进程

> 状态:**规范性**。从 Wrapper 视角定义 CLI 进程的 spawn、运行、取消、终止。

## 生命周期

```text
discover
   ↓
start
   ↓
initialize     (协议握手, manifest, features)
   ↓
running        (一次或多次操作)
   ↓
complete
   ↓
exit
```

一个 CLI 进程可串行跑**一或多次**操作。Wrapper 可让 CLI 长存活以摊薄启动成本。见 [12-兼容性.md](./12-compatibility.md) 关于长进程。

## 启动

Wrapper spawn CLI:

| 通道 | 设置 |
| --- | --- |
| stdin | 管道(Wrapper 发 request / command) |
| stdout | 管道(Wrapper 读 response / events) |
| stderr | 管道或继承(Wrapper 可记录但**不得**解释) |
| env | Wrapper 控制;CLI 不应依赖环境变量 |

工作目录默认 gallate.yaml Project Root。见 [10-配置.md § Project Root](./10-configuration.md)。

## 发现序列

```text
1. spawn CLI
2. 通告 / 检查协议版本
3. 读 manifest       (cli manifest)
4. 读 features       (cli features)
5. 读 validation     (cli validation)
6. 读操作列表         (扩展;可选)
7. 开始操作
```

Wrapper **不得**跳步。见 [03-能力发现.md](./03-discovery.md)。

## 操作选择(每个目标)

Wrapper 拿到所有候选 CLI 的发现结果后,**必须**在调用任何操作之前
为每个候选游戏 / 文件挑出合适的 CLI。两步过程:

```text
1. 读每个候选 CLI 的 manifest.targets
2. 选与目标路径匹配的候选;若多个匹配,对每个分别调 cli identify <path>
3. 选最高置信度的 identify 结果
```

第 2 步的 `cli identify` 是 per-CLI、per-path 的。Wrapper 对每个
通过 manifest.targets 过滤的候选各跑一次。

没有候选匹配时,Wrapper 向用户报告"无引擎识别"。Wrapper **不得**
静默选一个 CLI。

响应形状与置信度等级见 [03-能力发现.md § Identify](./03-discovery.md#identify)。

---

## 跑一次操作

```text
Wrapper                          CLI
   │                              │
   │  ── request ──────────────▶  │
   │                              │
   │  ◀── response ────────────  │   (确认 + id)
   │  ◀── event started ───────  │
   │  ◀── event progress ──────  │
   │  ◀── event file ──────────  │
   │  ◀── event completed ─────  │
   │                              │
   │  exit code                  │
```

`response` 之后,CLI 发 `event` 流。流以恰好一个终止事件(`completed`、`cancelled`,或隐式失败通过 exit code)结束。

## 取消

Wrapper 发 `command` 消息:

```jsonl
{"type":"command","command":"cancel"}
```

Schema:[`schema/cancel-command.schema.yaml`](../../schema/cancel-command.schema.yaml)。

CLI 行为:

1. 尽快停止当前操作。
2. 发 `cancelled` event。
3. 退出码 `6`。

CLI 应在退出前清理临时文件。

## 信号

信号实现相关,**不应**作为主要取消机制。若 CLI 处理信号:

| 信号 | 推荐行为 |
| --- | --- |
| `SIGTERM` | 优雅关闭。同 `cancel`。 |
| `SIGINT` | 同 `SIGTERM`。 |
| `SIGKILL` | OS 级;CLI 无法清理。Wrapper 应避免。 |

Wrapper 应先发 `cancel` 命令,等 `cancelled` event,超时后才升级到信号。

## Timeout

Wrapper 可强制操作超时。触发时:

1. 发 `cancel`。
2. 等最多 N 秒(建议 30s)。
3. 发 `SIGTERM`。
4. 等最多 M 秒(建议 5s)。
5. 发 `SIGKILL`。

具体秒数由 Wrapper 选。CLI **不应**假设特定超时。

## 临时文件

CLI 创建临时文件时必须:

1. 使用系统临时目录或 Project Root 下 `.gallate-tmp/`。
2. 正常退出时清理。
3. 取消时清理。
4. `SIGTERM` 时尽力清理;`SIGKILL` 不可能清理。

Wrapper 可在启动时扫描 `.gallate-tmp/`,清理上次崩溃残留。

## 并发操作

单个 CLI 进程**最多**跑一个操作。并发操作需要多个 CLI 实例。

Wrapper 可并行 spawn 多个实例;每个有独立 stdin/stdout,**必须**用不同 operation ID。

## 优雅关闭

Wrapper 想关闭长存活 CLI 时应:

1. 等当前操作完成。
2. 关 stdin。
3. 读 stdout 剩余内容。
4. 收 exit code。

突然终止(操作中关 stdin)允许,但 CLI 可视为协议错误。