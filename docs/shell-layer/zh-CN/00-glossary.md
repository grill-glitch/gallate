# 00. 术语表

> 状态:**规范性**。Shell 层规范使用的术语。交叉引用
> [协议层术语表](../../protocol/00-glossary.md)。

## A

### Argument

CLI 命令行上单个 flag(如 `--output`)或 key/value(如 `--ignore "*.tmp"`)。区别于 **Option**(`gallate.yaml` 中的结构化键)。

## C

### CLI(gallate CLI)

面向**一个**具体游戏引擎、引擎家族或资源格式的可执行文件。同时实现 Shell 层(本规范)与[协议层(GCWP)](../../protocol/00-glossary.md#c)。

### CLI Override

CLI 参数,临时改变 `gallate.yaml` 字段的值,但不持久化修改。

### Config File

`gallate.yaml` —— 项目级 YAML 文件,位于 Project Root。见 [05-config-file.md](./05-config-file.md)。

### Conformance

CLI 是否符合本规范。见 [11-conformance.md](./11-conformance.md)。

### Configuration Priority

CLI / YAML / 引擎默认值合并的顺序。见 [01-overview.md § Configuration Priority](./01-overview.md)。

## D

### Default Media

`-e` / `-i` 不带 media flag 时使用的媒体列表。来源:`gallate.yaml` 的 `media:`,缺省时使用引擎默认值。

### Dry Run

`--dry-run` —— 跑操作逻辑但不动资源,然后报告会发生什么。见 [09-std-flags.md § Dry Run](./09-std-flags.md#dry-run)。

## E

### Engine Default

CLI 在 CLI 与 YAML 都未提供时使用的回退值。引擎特定,非标准化。

### Engine Extension

CLI 在标准 Shell 层之上增加的任何特性。必须使用 `--engine.*` 命名空间。见 [08-engine-extensions.md](./08-engine-extensions.md)。

### Extract

`-e` —— 读引擎资源,产出翻译资产。见 [03-operations.md § Extract](./03-operations.md#extract)。

## F

### Force

`--force` —— 绕过安全检查(目前用于:允许 `init` 覆盖现有项目)。见 [07-init.md § Force](./07-init.md#force)。

## G

### gallate.yaml

唯一的项目级配置文件。标准 Project Target。Schema 见 [05-config-file.md](./05-config-file.md)。

## I

### Ignore

从任何操作中排除资源的 glob 模式。见 [09-std-flags.md § Ignore](./09-std-flags.md#ignore)。

### In-Place

操作结果替换输入。标准 CLI **不得**静默地将操作转为 in-place;引擎声明是否支持。见 [10-stdout-stderr.md § In-Place](./10-stdout-stderr.md#in-place)。

### Inject

`-i` —— 读已翻译资产,产出引擎输出。见 [03-operations.md § Inject](./03-operations.md#inject)。

### Init

`init` ——项目初始化子命令。见 [07-init.md](./07-init.md)。

## M

### Media

操作目标的资源类型:`text` / `image`(**标准**)或引擎扩展媒体。见 [04-media.md](./04-media.md)。

### Media Sub-Option

同一 Media 下的子分类,由引擎声明。例如 `text.hardcoded`、`image.portrait_diff`。见 [04-media.md § Sub-Media](./04-media.md#sub-media)。

## O

### Operation

`-e`(extract)或 `-i`(inject)。CLI 调用的动词部分。见 [03-operations.md](./03-operations.md)。

### Option

`gallate.yaml` 中的一个键。两种作用域:
- **Standard options**:`input`、`output`、`media`、`ignore`、`scripts`、`engine`。
- **Engine options**:`engine:` 下的键,对标准 CLI 不透明。

### Output

操作结果的目的地。见 [09-std-flags.md § Output](./09-std-flags.md#output)。

## P

### Path Resolution

相对路径相对 Project Root(`gallate.yaml` 所在目录)解析,而不是相对 Shell 当前工作目录。

### Pre / Post Script

操作前后执行的用户脚本。配置见 [05-config-file.md § scripts](./05-config-file.md#scripts)。

### Project Root

包含 `gallate.yaml` 的目录。所有相对路径的锚点。

## Q

### Quick Reference

Shell 层语法一行:`tool [op][media] project [options]`。见 [02-cli-grammar.md](./02-cli-grammar.md)。

## R

### Request ID(协议层)

与本层不同。见 [协议层术语表 § Operation ID](../../protocol/00-glossary.md#i)。

## S

### Script

pre/post 钩子调用的可执行文件。用户所有,通过 `scripts.pre` / `scripts.post` 在 `gallate.yaml` 中引用。

### Standard Output(stdout)

操作结果。Wrapper 可用作机器可读输出。**不**用于人类进度。

### Standard Error(stderr)

进度、警告、诊断。自由格式,**不得**被 Wrapper 解析。

### Sub-Media

引擎定义的 Media 子分类。见 [04-media.md § Sub-Media](./04-media.md#sub-media)。

## T

### Tool

gallate CLI 可执行文件。本规范中使用的通用名称。

## U

### Unknown Media

引擎不支持的媒体标识符。CLI **必须**报告并以退出码 6(`Unsupported Media`)失败,**不得**静默跳过。

### Unknown Sub-Media

引擎未在 `gallate.yaml` 中声明的 sub-media 标识符。CLI **必须**报告。

## V

### Verbose

`-v` / `-vv`。增加 stderr 上的诊断详细度。

### Quiet

`-q`。抑制非必要输出,用于脚本环境。

## W

### Wrapper

通过 GCWP 驱动 CLI 的 OmegaT 集成层。见 [协议层术语表 § Wrapper](../../protocol/00-glossary.md#w)。不是 Shell 层术语,但提及以提供上下文。