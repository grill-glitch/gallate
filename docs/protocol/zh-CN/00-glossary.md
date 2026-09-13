# 00. 术语表

> 状态:**规范性**。CLI 与 Wrapper 在实现与文档中必须按统一含义使用这些术语。

## A

### 架构

三层结构:

```text
OmegaT → Wrapper → CLI → 游戏引擎
```

### 参数(Argument)

传给操作的 key/value 或 flag。区别于 **Options**(操作级结构化配置)和 **Input / Output**(文件系统路径)。

## C

### 取消(Cancellation)

Wrapper 通过 stdin 的 `cancel` 命令中止正在进行的操作。见 [11-进程.md](./11-process.md)。

### CLI

一个独立可执行文件,面向**一个**具体游戏引擎、引擎家族或资源格式。说 GCWP 协议。例如:`artemis-cli`、`renpy-cli`。

### 命令(Command)

Wrapper 经 stdin 发给 CLI 的**非操作请求**短消息。当前只有 `cancel` 一个标准命令。

### 一致性等级

CLI 声称覆盖 GCWP 的层级:Basic / Standard / Full。见 [13-一致性.md](./13-conformance.md)。

### 核心协议

线缆格式层:协议版本、Line Protocol、stdin/stdout 通道、退出码。见 [02-核心协议.md](./02-core-protocol.md)。

## D

### 诊断(Diagnostics)

CLI 写到 **stderr** 的人类可读信息。**不**属于机器协议。见 [09-诊断.md](./09-diagnostics.md)。

### 能力发现(Discovery)

学习 CLI 身份(`manifest`)和能力(`features`)的过程。见 [03-能力发现.md](./03-discovery.md)。

## E

### 引擎(Engine)

CLI 包装的目标游戏引擎、文件格式或运行时。

### 事件(Event)

CLI 在操作过程中写到 stdout 的结构化消息。见 [05-事件流.md](./05-events.md)。

### 退出码

CLI 进程结束时返回的整数。标准定义见 [02-核心协议.md § 退出码](./02-core-protocol.md)。

## F

### 特性(Features)

`cli features --yaml` 返回的静态能力描述。见 [03-能力发现.md](./03-discovery.md)。

### Full 一致性

最高等级,含取消、状态流式、完整诊断等。见 [13-一致性.md](./13-conformance.md)。

## G

### GCWP

**Gamelate CLI–Wrapper Protocol**。本规范定义的协议。尽管 umbrella 项目改名为 `gallate`,协议短名 `GCWP` 保留作为历史锚点。

### gallate.yaml

**项目级** YAML 配置文件。在 [`Documents/通用行为规范.txt`](https://github.com/grill-glitch/Documents) 详细定义。GCWP 只消费解析后的结果,不读原文件。

## H

### 帮助输出(Help Output)

不带参数或带 `--help` 调 CLI 时打印的自由格式人可读文本。
帮助输出**不是**线缆协议的一部分;Wrapper **不得**解析。

## I

### Identify

`cli identify <path>` 操作。返回 `manifest.targets` 中命中的识别规则列表,每条带置信度等级(`high` / `medium` / `low`)。Wrapper 用它为候选游戏路径挑选合适的 CLI。见 [03-能力发现.md § Identify](./03-discovery.md#identify)。

### 操作 ID

Wrapper 给每次操作请求分配的 ULID/UUID,用于关联事件、状态快照和最终退出。

### 忽略(Ignore)

从操作中过滤资源的 glob / path 列表。见 [04-操作.md § Ignore](./04-operations.md)。

### 不确定进度(Indeterminate Progress)

`total: null` 的进度报告。见 [05-事件流.md § progress](./05-events.md)。

## J

### JSON 单元文件

OmegaT 产生/消费的标准单元文件格式 —— 每个逻辑翻译域一个 JSON 文档,内含
扁平的 `units` 数组。GCWP 不直接接触单元文件;Wrapper 在 GCWP 操作与 Shell 层
([12-file-structure.md](../shell-layer/12-file-structure.md))描述的 JSON
单元文档之间做映射。

## L

### JSON Line Protocol

GCWP 线缆格式:每行一个 JSON 对象(标准 [JSON Lines][jsonl] / NDJSON 格式)。
YAML **不**属于 GCWP 线缆,YAML 留给 Shell 层(人类面对的 CLI 调用与
`gallate.yaml` 项目文件)。

[jsonl]: https://jsonlines.org/

## M

### Manifest

CLI 身份文档,由 `cli manifest` 返回。

## O

### 操作(Operation)

Wrapper 请求、CLI 执行的工作单元。标准操作:`extract`、`inject`、`build`、`unpack`、`repack`。

### 操作请求(Operation Request)

操作开始时 Wrapper 通过 stdin 发出的结构化消息。

### 选项(Options)

操作级结构化配置(如 `text_encoding`、`rebuild_index`),键名按引擎命名空间。

## P

### 阶段(Phase)

`running` 状态内的标签。区别于 **State**(整体生命周期阶段)。

### 占位符规则(Placeholder Rule)

要求目标中保留特定占位符(如 `{player}`)的验证规则。

### 协议版本(Protocol Version)

`MAJOR.MINOR` 字符串。Major 表示破坏性变更,Minor 表示向后兼容新增。

## R

### 正则规则(Regex Rule)

由正则表达式支撑的验证规则。

### 请求(Request)

**操作请求**的同义词。

### 响应(Response)

CLI 在操作开始时的回应(确认请求并通告选定的操作 ID)。

## S

### 模式(Schema)

`schema/` 下的 JSON Schema 文件(YAML 形式),定义消息的精确线缆形状。

### 作用域(Scope,验证)

验证规则作用于什么:`text`、`source`、`target`、`placeholder`、`metadata`、`resource`。

### 严重性(Severity)

规则执行严格度:`info`、`warning`、`error`。

### 稳定标识符

兼容版本之间**不得**变更的标识符:CLI id、Engine id、Operation id、Feature 名、Error code。

### 状态(State)

操作整体生命周期阶段:`idle`、`preparing`、`running`、`completed`、`failed`、`cancelled`。

### 统计(Statistics)

操作结束时的结果指标。区别于 **Status**(当前)与 **Event**(过程)。

### 状态(Status)

按需查询的 CLI 当前快照。

## U

### 未知字段

协议消息中接收方不识别的字段。接收方**必须**忽略未知字段(见 [12-兼容性.md](./12-compatibility.md))。例外:未知 MAJOR 协议版本、event type、operation type、validation type 可被拒绝。

### 未知操作

CLI 未实现的操作类型。CLI 必须以退出码 4(`unsupported operation`)拒绝。

### 未知事件

Wrapper 不识别的事件类型。Wrapper 必须忽略。

## V

### 验证规则(Validation Rule)

CLI 向 OmegaT 暴露的具名规则,用于对翻译文本做验证。

## W

### Wrapper

OmegaT 的唯一集成点。拥有 GCWP client、项目配置加载、事件/状态聚合、OmegaT glue。**不得**包含引擎逻辑。

## Y

### YAML vs JSON

GCWP 按角色只取一种格式:

| 角色 | 格式 | 原因 |
| --- | --- | --- |
| 项目配置(`gallate.yaml`) | YAML | 由人编辑;注释与多行字符串重要。 |
| 线缆协议(stdin / stdout) | 流式用 JSON Line Protocol,一次性发现用 JSON | 机器到机器;人从不读。 |
| 发现输出的参考快照(如 `examples/full-cli/manifest.json`) | JSON | 单个文档;schema 是真相之源。 |
| 项目状态(`.meta.json`) | JSON | 机器派生;schema 是真相之源。 |
| 翻译状态(`text/units/*.json`,格式 `gallate.translation`) | JSON | 人编辑的字段装在 JSON 容器内,数据形状仍可被机器校验。 |

YAML 只出现在 `gallate.yaml`(项目配置文件,人可编辑)中。**没有** `--yaml`
flag;CLI 发现命令(`cli manifest`、`cli features`、`cli validation`、
`cli identify <path>`、`cli status`)在 stdout 输出 JSON。