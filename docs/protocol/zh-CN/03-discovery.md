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

        if features.media.image:
            show_image
```

Wrapper 必须**全部**由 `features` 文档驱动 UI 与路由决策。CLI id / name / engine id 都是稳定标识符 —— 但 Wrapper **不得**据此推测行为。

## Manifest

Manifest 是 CLI 的身份文档。

接口:

```bash
cli manifest
```

CLI 在 stdout 输出一个 JSON 对象,然后以 0 退出。
Schema:[`schema/manifest.schema.yaml`](../../schema/manifest.schema.yaml)。

示例:

```json
{
  "type": "manifest",
  "protocol": {"name": "gcwp", "version": "1.0"},
  "id": "artemis",
  "name": "Artemis CLI",
  "version": "1.2.0",
  "engine": {"id": "artemis", "versions": ["2.x"]}
}
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
cli features
```

CLI 在 stdout 输出一个 JSON 对象,然后以 0 退出。
Schema:[`schema/features.schema.yaml`](../../schema/features.schema.yaml)。

示例:

```json
{
  "type": "features",

  "operations": {
    "extract": true,
    "inject":  true,
    "build":   true,
    "unpack":  true,
    "repack":  true
  },

  "media": {
    "text":  true,
    "image": true,
    "audio": false,
    "video": false
  },

  "validation": {
    "syntax":      true,
    "regex":       true,
    "placeholder": true,
    "constraint":  true
  },

  "runtime": {
    "events":       true,
    "status":       true,
    "statistics":   true,
    "cancellation": true
  }
}
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
| media | `text` | bool | **标准**文本媒体(baseline) |
| media | `image` | bool | **标准**图片媒体(baseline) |
| media | `audio` | bool | 引擎扩展媒体,仅在引擎支持时出现 |
| media | `video` | bool | 引擎扩展媒体,仅在引擎支持时出现 |
| validation | `syntax` | bool | 通用语法检查(引擎定义) |
| validation | `regex` | bool | 正则规则 |
| validation | `placeholder` | bool | 占位符保留 |
| validation | `constraint` | bool | 约束规则 |
| runtime | `events` | bool | 事件流 |
| runtime | `status` | bool | 状态查询 |
| runtime | `statistics` | bool | 统计输出 |
| runtime | `cancellation` | bool | 取消支持 |

> **标准 vs 扩展媒体**:Wrapper 可把 `text` 和 `image` 当作 baseline(每个
> gallate CLI 都声明,至少 `text: true`)。`audio` / `video` 与其他键
> (例如 `font`)都是引擎扩展,**不得**假设一定存在。Shell 层关于标准
> vs 扩展媒体的定义在 [docs/shell-layer/04-media.md](../../shell-layer/04-media.md)。

### 否定式真理

不支持的能力必须显式标 `false`,**不得**省略:

```json
{
  "runtime":    {"status": false, "statistics": false},
  "validation": {"syntax": false}
}
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
---

## Identify(引擎识别)

Wrapper 拿到一组候选 CLI 后,**必须**为每个候选游戏/文件挑出合适的 CLI,
才能调用 `extract` / `inject`。这是两步过程:

```text
1. 读每个候选 CLI 的 manifest.targets
2. targets 命中的 CLI 中,如有多于 1 个,分别调用 cli identify <path>
3. 选最高置信度的结果
```

### `targets` 块

`manifest.targets` 告诉 Wrapper 该 CLI 能识别哪些游戏与文件形态。
三部分:

- `targets.games` — 该 CLI 能识别的具体游戏(名称 + 引擎版本 + 可选稳定 id)。
  通用引擎可留空。
- `targets.formats` — 文件/目录形态: `extension` / `name_match` /
  `path_glob` / `directory` / `min_bytes` / `kind: file | directory | any`。
- `targets.magic_bytes` — 二进制内容签名: `offset` + `bytes`(默认十六进制)。
  用于扩展名撒谎的情况(改名文件、加密壳)。

Schema: [`schema/manifest.schema.yaml`](../../schema/manifest.schema.yaml)。

Artemis CLI 示例:

```json
{
  "type": "manifest",
  "protocol": {"name": "gcwp", "version": "1.0"},
  "id": "artemis",
  "name": "Artemis CLI",
  "version": "1.2.0",
  "engine": {"id": "artemis", "versions": ["2.x"]},
  "targets": {
    "games": [
      {"name": "Higurashi no Naku Koro ni", "engine_versions": ["2.0", "2.1"]},
      {"name": "Umineko no Naku Koro ni",  "engine_versions": ["2.1", "2.2"]}
    ],
    "formats": [
      {"extension": ".pfs", "kind": "file"},
      {"name_match": "system.ini", "kind": "file"}
    ],
    "magic_bytes": [
      {
        "offset": 0,
        "bytes": "50 46 53 20",
        "encoding": "hex",
        "description": "PFS archive magic header"
      }
    ]
  }
}
```

`targets` 是**声明性**的 —— CLI 是真值来源,规则列表是 CLI 作者决定的。
不同 CLI 的规则形态可以差异很大。Wrapper 把 `targets` 当作**提示**,不是合同。

### `cli identify`

CLI 还可以暴露一个按路径识别的操作:

```bash
cli identify <path>
```

`<path>` 是文件或目录。CLI 检查路径并返回命中的 `targets` 规则,
带置信度与证据。

Wrapper 用 `cli identify` 在粗筛之后做精确识别。Wrapper 也可以对同一
路径调用所有候选 CLI 的 `cli identify`,选最高置信度 —— 这是多引擎启动器
(如一个 CLI 对应一个引擎家族)对新游戏的分流方式。

Schema: [`schema/identify.schema.yaml`](../../schema/identify.schema.yaml)。

```json
{
  "type": "identify",
  "id": "01HIDENT",

  "target": {
    "path": "/storage/games/higurashi/game.pfs",
    "kind": "file",
    "size": 421876
  },

  "matched": [
    {
      "engine": "artemis",
      "confidence": "high",
      "rule": {"kind": "magic_bytes", "matched": "50 46 53 20"},
      "game": {"name": "Higurashi no Naku Koro ni", "engine_versions": ["2.0", "2.1"]}
    }
  ]
}
```

`matched` 为空表示 CLI 不处理该目标。多条记录代表歧义候选;Wrapper 应按
`confidence` 降序排序。

### 置信度

| 等级 | 含义 |
| --- | --- |
| `high`   | 多条规则同时命中(如 extension + magic_bytes + 已知游戏 id)。 |
| `medium` | 一条规则命中。 |
| `low`    | 启发式猜测。Wrapper **不得**把 `low` 当作确认,必须自己做合理性检查。 |

### 调用时机

Wrapper 在以下情况调用 `cli identify`:

- 新游戏的第一次 extract/inject(冷启动)
- 用户添加新游戏目录,让 Wrapper 挑选 CLI
- Wrapper 的 `manifest.targets` 过滤太粗,需要更精确的答案

Wrapper **不得**在 extract/inject 的热循环中调用 `cli identify` —— 它是
冷路径操作。
