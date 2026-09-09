# 13. 项目元数据(`.meta.json`)

> 状态:**规范性**。定义 gallate CLI 写入并维护的项目级状态文件 `.meta.json`。

## 13.1 设计目标

`.meta.json` 是 gallate 项目的**派生项目元数据**(Derived Project Metadata),
记录 gallate 项目文件(在 Project Root 下)与原始游戏资源之间的**实际**映射。

规则:

- `.meta.json` 由 **CLI 自动维护**。用户**不得**被要求直接创建或编辑它。
- `.meta.json` **不是**用户配置文件,属于 CLI 的内部簿记。
- `.meta.json` 位于 **Project Root**,与 `gallate.yaml` 同级。
- `.meta.json` **必须**让后续 `extract` / `inject` / `update` /
  `validate` 操作能在不重新扫描的情况下,找到每个项目文件对应的源游戏文件。
- Wrapper **可以**读 `.meta.json`,但**不得**自行推断、重建或维护其中的映射。

核心原则:

> `gallate.yaml` 描述"项目应当如何被处理"。
>
> `.meta.json` 描述"项目实际建立了什么关系"。

`.meta.json` **不是** `gallate.yaml` 的复制或镜像。

## 13.2 文件位置

```text
project/
├── gallate.yaml
├── .meta.json
└── ...
```

标准位置:Project Root,与 `gallate.yaml` 同级。

当 `gallate.yaml` 尚不存在、但直接 CLI 操作产生了可持久化的映射时,CLI
**可以**创建 `.meta.json`。若之后 `gallate.yaml` 被创建或读取,CLI
将二者视为同一项目中的不同信息层,**不得**互相覆盖。

## 13.3 生成与修改规则

`.meta.json` **必须**由 gallate CLI 基于**实际执行结果**写入并修改。

两条触发路径:

### 13.3.1 直接 CLI 操作

```bash
gallate extract ./game ./project
```

CLI 处理给定的输入/输出,观察**实际结果**,据此创建或更新
`.meta.json`。

### 13.3.2 `gallate.yaml` 驱动的操作

```bash
gallate extract
```

CLI 读取 `gallate.yaml`、执行操作、并**从观察到的结果**写入 `.meta.json`
——**不是**把 `gallate.yaml` 重新序列化成 JSON:

```text
gallate.yaml
     │
     │ 意图 / 配置
     ▼
 CLI 执行
     │
     │ 观察到的结果
     ▼
 .meta.json
```

`gallate.yaml` 是输入(意图),`.meta.json` 是输出(状态)。

## 13.4 映射模型

`.meta.json` **必须**能表达 gallate 项目文件与原始游戏资源之间的稳定映射。

Schema: [`schema/meta.schema.yaml`](../../schema/meta.schema.yaml)。

最小示例:

```json
{
  "schema_version": 1,
  "generated_by": {
    "id": "artemis",
    "version": "1.2.0"
  },
  "generated_at": "2026-09-09T12:34:56Z",
  "project": {
    "root": "."
  },
  "files": [
    {
      "project": "text/units/scenes_intro.xlf",
      "source": "scenes/intro.bin",
      "type": "text",
      "cli": {"id": "artemis", "version": "1.2.0"},
      "engine": {"id": "artemis", "version": "2.1"},
      "sub_media": "dialog"
    }
  ]
}
```

### 13.4.1 标准字段

| 字段 | 必填 | 含义 |
| --- | --- | --- |
| `schema_version` | 是 | 文件格式版本。CLI 拒绝加载 `schema_version` 高于自身已知版本的 `.meta.json`。 |
| `generated_by` | 是 | 哪个 CLI 写了此文件。捕获 `manifest.id` 与 `manifest.version`。 |
| `generated_at` | 是 | 上次成功重写的 ISO-8601 时间戳。 |
| `project.root` | 可选 | Project Root 路径。 |
| `files[]` | 是 | 映射条目,每个 CLI 管理的项目文件一条。 |
| `files[].project` | 是 | 项目文件路径,**相对 Project Root**。 |
| `files[].source` | 是 | 原始游戏资源路径。 |
| `files[].type` | 是 | 资源类型。标准媒体用标准标识符;引擎扩展媒体用引擎命名空间。 |
| `files[].hash` | 可选 | 项目文件内容哈希(算法命名空间,如 `sha256:abc123…`)。 |
| `files[].size` | 可选 | 上次写入时项目文件大小(字节)。 |
| `files[].cli` | 可选 | 上次写本条目的 CLI。 |
| `files[].engine` | 可选 | 本条目针对的引擎 id + 版本。 |
| `files[].resource_id` | 可选 | 引擎内部逻辑 id(如资源表中的条目名)。 |
| `files[].timestamp` | 可选 | 本条目上次写入的 ISO-8601 时间戳。 |
| `files[].encoding` | 可选 | 项目文件文本编码。 |
| `files[].sub_media` | 可选 | Sub-Media 标识符(`dialog`、`portrait_diff` 等)。 |
| `files[].extensions` | 可选 | 命名空间扩展字段,每个 CLI 一个键。 |

### 13.4.2 扩展字段

CLI 可以在 `files[].extensions.<cli-id>` 下添加自定义字段。扩展字段
**不得**取代或改变任何标准字段的语义。两个 CLI **不得**写入同一个
扩展命名空间。

## 13.5 映射的稳定性

`project` / `source` 关系**必须**是显式的。

CLI:

- **不得**仅根据文件名推测映射。
- **不得**根据目录名猜测源文件。
- **不得**要求 Wrapper 自行重新建立映射。
- 在已有 `.meta.json` 映射时,应**优先**使用之。

例如,已知:

```text
text/units/scenes_intro.xlf
```

CLI **不得**将其视为 `scenes/intro.bin` 的可靠提示。源路径来自
`.meta.json`,或来自当前 CLI 操作明确建立的映射。

## 13.6 生命周期

```text
CLI command
  │
  ├── 读取 gallate.yaml(若存在)
  ├── 解析 input / output
  ├── 执行操作
  ├── 确定创建/修改了哪些项目文件
  └── 创建或更新 .meta.json
```

成功 `extract` 之后:

```text
project/
├── gallate.yaml
├── .meta.json
└── text/
    └── main.xliff
```

下一次 `inject` 读取 `.meta.json`,配对:

```text
text/main.xliff
        │
        ▼
game/data/script.pfs
```

无需重新扫描游戏归档以定位源。

## 13.7 更新规则

当 CLI 对已有 `.meta.json` 条目的项目文件进行创建、修改、移动或删除
时,**必须**同步更新 `.meta.json`。

### 创建

新项目文件获得新条目。

### 修改

就地编辑但保持文件身份时,保留 `project` / `source` 映射。CLI 更新
`hash` 与 `timestamp`(若存在)。

### 移动

项目文件移动时,更新条目中的 `project` 字段:

```json
{
  "project": "new/path/main.xliff",
  "source": "game/data/script.pfs"
}
```

`source` 字段**不**丢失。CLI 可将旧条目保留一个世代在
`_previous_project` 字段(引擎定义)以支持撤销。

### 删除

CLI 删除它管理的项目文件时,移除对应 `.meta.json` 条目。

## 13.8 一致性

CLI **必须**保持 `.meta.json` 与实际项目状态之间的可验证一致性。当
CLI 检测到漂移:

```text
.meta.json ≠ 实际项目状态
```

**不得**静默产生错误映射。CLI 可报告错误、报告 warning、要求重新生成
metadata,或根据操作语义安全地修复。具体恢复行为由操作规范定义;
规则是**永不静默破坏**。

CLI **不得**静默忽略:

- 条目指向的项目文件不存在。
- 条目指向的 `source` 资源不存在(引擎资源缺失)。
- `project` / `source` 映射歧义(一个项目文件映射到多个源,反之亦然)。
- `schema_version` 无法识别。
- 外部程序破坏了 `.meta.json`。

## 13.9 原子性

`.meta.json` 的写入**应**是原子的。

推荐模式:

```text
生成临时 metadata
  ↓
校验
  ↓
原子替换
  ↓
.meta.json
```

若实际操作失败,CLI **不得**提交一个描述未完成状态的 `.meta.json`。

## 13.10 CLI 所有权

`.meta.json` 是项目级公共格式,但每条 `files[]` 条目由写入它的 CLI 拥有。

两个 CLI 共享项目:

```text
CLI A ──┐
        ├── .meta.json
CLI B ──┘
```

**不得**静默互相覆盖。条目上的 `generated_by` 字段记录所有权。CLI
**只**编辑 `cli.id` 等于自身 id 的条目,除非用户明确指示。

跨 CLI 共享项目时,使用 `files[].extensions.<cli-id>` 命名空间避免冲突。

## 13.11 Wrapper 职责

Wrapper **可以**读 `.meta.json` 用于:

- 展示项目资源;
- 构建资源管理 UI;
- 显示 `project` / `source` 映射;
- 为用户筛选资源;
- 协调 CLI 操作。

Wrapper **不得**:

- 把 `.meta.json` 当作自己的数据库;
- 自行重新推导映射;
- 修改 CLI 管理的条目;
- 复制 CLI 内部资源发现逻辑。

Wrapper 是**消费者与协调者**,不是 CLI 的再实现。

```text
                 Gallate CLI
                     │
       ┌─────────────┴─────────────┐
       │                           │
       ▼                           ▼
 gallate.yaml                  实际操作
       │                           │
       └─────────────┬─────────────┘
                     ▼
                .meta.json
                     │
                     ▼
                  Wrapper
```

## 13.12 与 `gallate.yaml` 的关系

| 文件           | 性质          | 主要来源   | 作用                              |
| ------------ | ----------- | ------ | ------------------------------- |
| `gallate.yaml` | 意图 / 配置    | 用户或 CLI | 声明输入、输出、ignore、处理流程。     |
| `.meta.json`   | 派生项目状态    | CLI   | 记录实际项目文件与游戏资源之间的关系。 |

```yaml
# gallate.yaml —— 意图
input: ./game
output: ./translation
ignore: ["*.tmp"]
```

```json
// .meta.json —— 状态
{
  "files": [
    {"project": "translation/main.xliff", "source": "game/data/script.pfs", "type": "text"}
  ]
}
```

两个文件互补,不可互换。

## 13.13 用户可见性

`.meta.json` 位于项目目录,但**不是**用户配置文件。

- CLI **不得**要求用户创建它。
- CLI **不得**要求用户通过 flag 维护它。
- 文档**不得**告诉普通用户编辑它。
- 用户删除 `.meta.json` 后,CLI **可以**从下次操作的**实际结果**重建。
- 用户修改 `.meta.json` 后,CLI **可以**将其视为外部修改并执行一致性检查。

`.meta.json` 的存在**应**对正常工作流透明。

## 13.14 规范定位

`.meta.json` 属于 **Gallate Project Specification**,不是任何单个 CLI
的私有格式。

- 所有兼容 gallate 的 CLI **必须**遵循 `.meta.json` 的标准语义;
- 引擎 CLI **可以**在 `files[].extensions.<cli-id>` 下扩展;
- Wrapper **可以**消费标准字段而无需了解具体引擎实现;
- 核心语义**必须**与 CLI 内部实现解耦。

```text
                Gallate Project
                      │
          ┌───────────┴───────────┐
          │                       │
   gallate.yaml              .meta.json
          │                       │
     用户意图                 实际状态
          │                       │
          └───────────┬───────────┘
                      │
                 Gallate CLI
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Engine A    Engine B    Engine C
          │           │           │
          └───────────┼───────────┘
                      ▼
                   Wrapper
```

这一设计保持 Unix 哲学:**CLI 负责执行并产生明确的文件状态,
配置描述意图,metadata 描述实际关系,Wrapper 负责组合、展示和协调,
而不复制 CLI 内部业务逻辑。**