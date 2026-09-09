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
text:
image:
audio:
video:
engine:
```

| 字段      | 类型   | 用途                                    |
| -------- | ------ | ---------------------------------------- |
| `input`  | path   | 游戏输入                                 |
| `output` | path   | 默认输出目的地               |
| `media`  | list   | 默认 media 列表                       |
| `ignore` | list   | 默认 ignore 模式                  |
| `scripts`| object | Pre / Post 脚本                       |
| `text`   | object | 文本媒体输出配置                  |
| `image`  | object | 图片媒体输出配置                 |
| `audio`  | object | 音频媒体输出配置                 |
| `video`  | object | 视频媒体输出配置                 |
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

# 文本媒体输出配置。
# standard CLI 默认把每条翻译单元写到 text/units/*.xlf,并附带
# original-file / source-context 等元数据。
text:
  format: xliff
  layout: flat
  metadata:
    original_file: true
    source_context: true
    location: true
    engine_path: true
  hardcoded:
    context_lines: 3
    max_bytes: 4096
    engine_extensions:
      - .py
      - .lua
      - .rpy
      - .ks
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

## 5.8 按媒体的输出配置

每个标准媒体都有独立顶层配置块,控制 `text/`、`image/`、`audio/`、`video/` 中文件的结构与元数据。引擎可按相同模式添加引擎扩展媒体的配置块。

### `text`

```yaml
text:
  format: xliff            # xliff | po | json | engine-extension
  layout: flat             # flat | mirror | single (见 12-file-structure.md)
  sub_media_dirs: false    # 对 text 无意义(text 的 sub-media 在文件内)

  # 每个翻译单元必须携带的元数据字段。
  metadata:
    original_file: true        # 源路径(游戏归档内)
    source_context: true       # 源代码上下文(对 hardcoded 字符串)
    location: true             # line / offset / length(若引擎知道)
    engine_path: true          # 引擎内部逻辑路径

  # hardcoded 字符串的源代码上下文捕获。
  hardcoded:
    context_lines: 3           # 捕获源代码周边行数
    max_bytes: 4096            # 每单元上下文 payload 上限
    engine_extensions:         # 引擎视作代码的文件扩展名
      - .py
      - .lua
      - .js
      - .rpy
      - .ks
```

#### 字段

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `format` | enum | 输出格式。标准:`xliff` / `po` / `json`。 |
| `layout` | enum | 文件布局。标准:`flat` / `mirror` / `single`。见 [12-file-structure.md](./12-file-structure.md)。 |
| `metadata.original_file` | bool | 若为 true,每个 `<trans-unit>` 携带 `original-file` 属性,标明游戏归档内的源资源路径。默认 `true`。 |
| `metadata.source_context` | bool | 若为 true,每个 `text.hardcoded` 单元携带 `source-context` 字段,含周边源代码(见下)。默认 `true`。 |
| `metadata.location` | bool | 若为 true,单元携带 `line` / `offset` / `length`(引擎知道时)。默认 `true`。 |
| `metadata.engine_path` | bool | 若为 true,单元携带引擎内部逻辑路径(引擎定义)。默认 `true`。 |
| `hardcoded.context_lines` | int | `text.hardcoded` 单元捕获周边代码行数。默认 `3`。 |
| `hardcoded.max_bytes` | int | 每单元捕获的 payload 上限。默认 `4096`。 |
| `hardcoded.engine_extensions` | list | 引擎视作代码的文件扩展名。空列表 = 引擎自决。 |

#### `original-file`

`original-file` 字段让译者知道翻译单元来自游戏归档的哪个文件。没有它,QA 无法把丢失的翻译溯源到原始位置。

XLIFF 单元示例:

```xml
<trans-unit id="tu-0042" original-file="scenes/day1/scene_001.bin">
  <source>Hello {player}</source>
  <target>你好 {player}</target>
</trans-unit>
```

CLI **必须**在能拿到值时发出 `original-file`。当 `metadata.original_file` 为 `false` 时,CLI 可以省略,但 Wrapper / OmegaT 应把缺席视为"未知来源"。

#### `source-context`(对 hardcoded sub-media)

CLI 提取 `text.hardcoded` 字符串(嵌入脚本或二进制资源的字符串)时,**必须**同时捕获源代码上下文:周边代码行,以便译者看到实际用法。

示例:

```text
# Hardcoded 字符串在 scenes/day1/scene_001.rpy:42

 41 │     if player.gender == "male":
 42 │         narrator("Hello {player}.")
 43 │     else:
 44 │         narrator("Hello {playeress}.")
```

字符串 `"Hello {player}."` 被提取,其 source-context 捕获 41–43 行(按配置 3 行)。捕获块进入翻译单元,作为注释或上下文字段。

XLIFF 表示:

```xml
<trans-unit id="tu-0042" original-file="scenes/day1/scene_001.rpy">
  <source>Hello {player}.</source>
  <target>你好 {player}。</target>
  <context-group name="source-context" purpose="information">
    <context context-type="sourcefile">scenes/day1/scene_001.rpy</context>
    <context context-type="linenumber">42</context>
    <context context-type="snippet">
41 │     if player.gender == "male":
42 │         narrator("Hello {player}.")
43 │     else:</context>
  </context-group>
</trans-unit>
```

PO 表示:

```po
#: scenes/day1/scene_001.rpy:41
#: scenes/day1/scene_001.rpy:42
msgid "Hello {player}."
msgstr "你好 {player}。"
```

JSON 表示(引擎定义):

```json
{
  "id": "tu-0042",
  "source": "Hello {player}.",
  "target": "你好 {player}。",
  "context": {
    "original_file": "scenes/day1/scene_001.rpy",
    "line": 42,
    "snippet": "41 │     if player.gender == \"male\":\n42 │         narrator(\"Hello {player}.\")\n43 │     else:"
  }
}
```

#### `location`

CLI 已知的位置信息(XLIFF 写为 `<context context-type="linenumber">`;PO 写为 `file:line`)。未知时省略。

#### `engine_path`

引擎内部逻辑路径。引擎定义;CLI 原样传递。省略则 OmegaT 回退 `original-file`。

### `image` / `audio` / `video`

```yaml
image:
  layout: sub_media_dirs    # sub_media_dirs | flat
  sidecar: yaml            # 引擎定义的 sidecar 格式(可选)

audio:
  layout: sub_media_dirs
  manifest: ./audio/manifest.yaml

video:
  layout: sub_media_dirs
  reencode: false          # 若为 true,CLI 在 extract 时可以重编码
```

这里的字段是惯例提示。引擎可忽略任意一项。完整语义见
[12-file-structure.md](./12-file-structure.md)。

### 引擎扩展媒体

每个引擎扩展媒体标识符都遵循同一种块形:

```yaml
font:
  layout: sub_media_dirs
  manifest: ./font/manifest.yaml
```

当引擎把 `font` 作为已有媒体的 sub-media 暴露时,配置走那个父媒体
(见 [04-media.md § Sub-Media](./04-media.md#sub-media))。

## 5.9 `engine`

```yaml
engine:
  text_encoding: utf-8
  rebuild_index: true
```

引擎特定配置。标准 CLI **不**解释 `engine:` 内的任何键 —— 它们原样传递给引擎 wrapper。

引擎应使用命名空间键(如 `text_encoding`)避免冲突。CLI 接受任何键。

引擎扩展 media / sub-media 也配置在 `engine:` 下,见 [04-media.md § Sub-Media](./04-media.md#sub-media) 与 [08-engine-extensions.md](./08-engine-extensions.md)。

## 5.10 保留顶层键

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

## 5.11 路径解析

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