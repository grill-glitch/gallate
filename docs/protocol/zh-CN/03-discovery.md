# 03. 能力发现

> 状态:**规范性**。CLI 必须暴露 `manifest` 和 `features` 以供 Wrapper 发现。

## 为什么需要能力发现

```text
错误(反模式):

        if cli == "artemis":
            show_image
        elif cli == "renpy":
            show_image
        elif …

正确(按 feature):

        if features.resources.image:
            show_image
```

Wrapper 必须**全部**由 `features` 文档驱动 UI 与路由决策。CLI id / name / engine id 都是稳定标识符 —— 但 Wrapper **不得**据此推测行为。

## Manifest

Manifest 是 CLI 的身份文档。

接口:

```bash
cli manifest --yaml
```

Schema:[`schema/manifest.schema.yaml`](../../schema/manifest.schema.yaml)。

示例:

```yaml
type: manifest
protocol:
  name: gcwp
  version: 1.0
id: artemis
name: Artemis CLI
version: 1.2.0
engine:
  id: artemis
  versions:
    - 2.x
```

### 字段

| 字段 | 必填 | 备注 |
| --- | --- | --- |
| `id` | ✓ | 稳定 CLI 标识符。见 [12-兼容性.md § 稳定标识符](./12-compatibility.md)。 |
| `name` | ✓ | 人类可读名,可随版本变化 |
| `version` | ✓ | CLI 版本 |
| `protocol` | ✓ | 含 `name`、`version` 的对象 |
| `engine` | 可选 | 引擎识别;引擎专有 CLI 应填 |

`id` 在兼容版本之间**不得**变更。改 `id` 等于该 CLI 已成为不同的兼容实现(Wrapper 可能需要重新协商)。

## Features

features 文档描述 CLI 能做什么。

接口:

```bash
cli features --yaml
```

Schema:[`schema/features.schema.yaml`](../../schema/features.schema.yaml)。

示例:

```yaml
type: features

operations:
  extract: true
  inject: true
  build: true
  unpack: true
  repack: true

resources:
  text: true
  image: true
  audio: false
  video: false

validation:
  syntax: true
  regex: true
  placeholder: true
  constraint: true

runtime:
  events: true
  status: true
  statistics: true
  cancellation: true
```

### 四个独立维度

```text
                CLI
                 │
       ┌─────────┼──────────┐
       │         │          │
  Operations  Resources  Runtime
       │         │          │
  extract     text      status
  inject      image     events
  build       audio     statistics
  unpack      video     cancellation
  repack
                 │
            Validation
                 │
          ┌──────┼──────┐
          │      │      │
        regex  placeholder  constraint
```

这四个维度相互独立,可任意子集实现。

### 字段

| 分组 | 字段 | 类型 | 含义 |
| --- | --- | --- | --- |
| operations | `extract` | bool | 资源提取 |
| operations | `inject` | bool | 翻译注入 |
| operations | `build` | bool | 引擎构建 |
| operations | `unpack` | bool | 引擎归档解包 |
| operations | `repack` | bool | 引擎归档打包 |
| resources | `text` | bool | 文本媒体 |
| resources | `image` | bool | 图片媒体 |
| resources | `audio` | bool | 音频媒体 |
| resources | `video` | bool | 视频媒体 |
| validation | `syntax` | bool | 通用语法检查(引擎定义) |
| validation | `regex` | bool | 正则规则 |
| validation | `placeholder` | bool | 占位符保留 |
| validation | `constraint` | bool | 约束规则 |
| runtime | `events` | bool | 事件流 |
| runtime | `status` | bool | 状态查询 |
| runtime | `statistics` | bool | 统计输出 |
| runtime | `cancellation` | bool | 取消支持 |

### 否定式真理

不支持的能力必须显式标 `false`,**不得**省略:

```yaml
runtime:
  status: false
  statistics: false

validation:
  syntax: false
```

Wrapper **不得**因某字段在 `features` 中缺失就假定它存在。

## 发现顺序

```text
1. 启动 CLI
2. 通告 / 检查协议版本
3. 取 manifest
4. 取 features
5. 取 validation 规则
6. 构造操作请求
7. 执行
8. 消费事件
9. 取 statistics
10. 检查 exit code
```

完整生命周期见 [11-进程.md](./11-process.md)。

## 一致性等级映射

CLI 暴露的能力决定其一致性等级:

```text
Basic    = manifest + features + 一个操作 + exit codes
Standard = Basic + events + statistics + validation
Full     = Standard + cancellation + status 流式 + diagnostics
```

见 [13-一致性.md](./13-conformance.md)。