# 05. 配置文件

> 状态:**规范性**。定义 `gallate.yaml` 结构 —— 唯一的项目级配置文件。

## 5.1 顶层字段

标准 `gallate.yaml` 使用以下顶层键:

```yaml
input:
output:
media:
ignore:
scripts:
engine:
```

| 字段      | 类型   | 用途                                    |
| -------- | ------ | ---------------------------------------- |
| `input`  | path   | 游戏输入                                 |
| `output` | path   | 默认输出目的地               |
| `media`  | list   | 默认 media 列表                       |
| `ignore` | list   | 默认 ignore 模式                  |
| `scripts`| object | Pre / Post 脚本                       |
| `engine` | object | 引擎特定选项                       |

所有键都是可选的。引擎**可**识别 `engine:` 下的额外键;**不得**添加规范保留作标准用途的新顶层键。

## 5.2 完整示例

```yaml
# gallate.yaml — 标准配置
input: ./game.pfs

media:
  - text
  - image

ignore:
  - "*.tmp"
  - "cache/"
  - "debug.log"

output: ./game-zh.pfs

scripts:
  pre:
    - ./scripts/unpack.py
    - ./scripts/normalize.py
  post:
    - ./scripts/repack.py
    - ./scripts/cleanup.py

engine:
  text_encoding: utf-8
  rebuild_index: true
  # 如果此引擎暴露 audio/video 作为扩展媒体,
  # 它们也会出现在这里:
  # audio:
  #   includes: [voice]
  #   excludes: [bgm]
  # video:
  #   includes: [cutscene]
```

## 5.3 `input`

```yaml
input: ./game.pfs
```

原始游戏输入。可以是:

- 文件(如 `./game.pfs`)
- 目录(如 `./www/`)

路径相对 Project Root 解析,除非是绝对路径。某个引擎接受文件还是目录(或两者)是引擎特定的。

CLI **不**接受 input 作为 CLI 参数;路径来自 `gallate.yaml`。

## 5.4 `output`

```yaml
output: ./game-zh.pfs
```

默认输出目的地。可被 CLI 上的 `--output` 覆盖。见 [09-std-flags.md § Output](./09-std-flags.md#output)。

与 `input` 类似,值可以是文件或目录;引擎决定哪种有意义。

## 5.5 `media`

```yaml
media:
  - text
  - image
```

`-e` 或 `-i` 不带 media flag 时使用的默认媒体列表。见 [04-media.md § Default Media](./04-media.md#default-media)。

项目加载时,列表会被规范化(去重,无顺序含义)。列表元素是媒体标识符 —— 见 [04-media.md](./04-media.md)。

## 5.6 `ignore`

```yaml
ignore:
  - "*.tmp"
  - "cache/"
  - "debug.log"
```

从任何操作中排除资源的 glob 模式(`.gitignore` 风格)。匹配语义见 [09-std-flags.md § Ignore](./09-std-flags.md#ignore)。

## 5.7 `scripts`

```yaml
scripts:
  pre: ./scripts/unpack.py
  post: ./scripts/repack.py
```

或多脚本列表形式:

```yaml
scripts:
  pre:
    - ./scripts/unpack.py
    - ./scripts/normalize.py
  post:
    - ./scripts/repack.py
    - ./scripts/cleanup.py
```

执行顺序:

```text
Input
  ↓
Pre 脚本         (定义顺序,自上而下)
  ↓
Operation
  ↓
Output
  ↓
Post 脚本        (定义顺序,自上而下)
```

每个脚本的默认工作目录:Project Root。所以 `./scripts/pre.py` 总是 `<ProjectRoot>/scripts/pre.py`。

CLI 不能覆盖 `scripts:` —— pre/post 钩子只在 YAML 中配置。这是故意的:pre/post 钩子可能改变输入布局,每次执行静默改变会使用户感到意外。

## 5.8 `engine`

```yaml
engine:
  text_encoding: utf-8
  rebuild_index: true
```

引擎特定配置。标准 CLI **不**解释 `engine:` 内的任何键 —— 它们原样传递给引擎 wrapper。

引擎应使用命名空间键(如 `text_encoding`)避免冲突。CLI 接受任何键。

引擎扩展 media / sub-media 也配置在 `engine:` 下,见 [04-media.md § Sub-Media](./04-media.md#sub-media) 与 [08-engine-extensions.md](./08-engine-extensions.md)。

## 5.9 保留顶层键

以下键为未来规范保留,引擎**今天不应使用**:

```text
hooks       # reserved
watch       # reserved
profile     # reserved
```

保留命名空间:

```text
gallate.*   # 保留用于项目级配置(非引擎选项)
gcwp.*      # 保留用于协议级选项
```

## 5.10 路径解析

`gallate.yaml` 内的所有相对路径都相对 **Project Root**(`gallate.yaml` 所在目录)解析:

```yaml
# gallate.yaml 位于 /home/me/projects/gamelate.yaml
input: ./game.pfs
```

`./game.pfs` 解析为 `/home/me/projects/game.pfs`,而不是 `/home/me/game.pfs`(Shell 的 CWD)。

绝对路径原样使用。此规则适用于:

```text
input
output
ignore
scripts.pre / scripts.post
engine.* 路径
```