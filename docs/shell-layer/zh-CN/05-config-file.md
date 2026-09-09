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
  lifecycle:
    written_on: extract
    read_on:
      - post-extract
      - pre-inject
  meta:
    original_file:  trans-unit-attribute
    source_context: context-group
    location:       context.linenumber
    engine_path:    trans-unit-attribute
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

  # 是否在翻译单元上输出每个元数据字段。
  # 默认全为 true。数据形状本身由本规范固定;
  # 这些 flag 只控制是否输出。
  metadata:
    original_file: true        # 源路径(游戏归档内)
    source_context: true       # text.hardcoded 的四字段记录
    location: true             # line / offset / length(非 hardcoded 单元)
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

  # 各元数据字段的写入与读取时机。
  # 默认匹配标准工作流;两个字段都可选。
  # 整块 OPTIONAL —— 不写时,行为匹配下面的默认值。
  lifecycle:
    written_on: extract     # extract | never
                            #   extract (默认):CLI 在 extract 时写入元数据,
                            #     inject 时原样保留。源代码在 extract
                            #     与 inject 之间不会变,CLI 没有重捕的理由。
                            #   never:从不写元数据(覆盖所有 metadata.* flag)。
    read_on:                 # Wrapper / OmegaT 何时读
      - post-extract         #   extract 后立刻:给译者看
      - pre-inject           #   inject 前:QA 审
                             #   build 阶段 MUST NOT 读 source-context。
```

#### 字段

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `format` | enum | 输出格式。标准:`xliff` / `po` / `json`。 |
| `layout` | enum | 文件布局。标准:`flat` / `mirror` / `single`。见 [12-file-structure.md](./12-file-structure.md)。 |
| `metadata.original_file` | bool | 若为 true,每个 `<trans-unit>` 携带 `original-file` 属性,标明游戏归档内的源资源路径。默认 `true`。 |
| `metadata.source_context` | bool | 若为 true,每个 `text.hardcoded` 单元携带四字段源代码上下文记录(`file` / `line` / `end_line` / `snippet`),详见下文 `source-context` 一节。默认 `true`。 |
| `metadata.location` | bool | 若为 true,非 hardcoded 单元携带 `line` / `offset` / `length`,标识源字符串在文件内的位置。默认 `true`。`text.hardcoded` 单元的位置走 `source-context` 而非此处。 |
| `metadata.engine_path` | bool | 若为 true,单元携带引擎内部逻辑路径(引擎定义)。默认 `true`。 |
| `hardcoded.context_lines` | int | `text.hardcoded` 单元捕获周边代码行数。默认 `3`。 |
| `hardcoded.max_bytes` | int | 每单元捕获的 payload 上限。默认 `4096`。 |
| `hardcoded.engine_extensions` | list | 引擎视作代码的文件扩展名。空列表 = 引擎自决。 |
| `lifecycle.written_on` | enum | `extract`(默认)或 `never`。CLI 仅在 extract 时写入元数据,inject 时保留。build 阶段从不写元数据。 |
| `lifecycle.read_on` | list | Wrapper / OmegaT 应展示元数据的阶段。默认:`post-extract` 与 `pre-inject`。**build 阶段 MUST NOT 读 source-context**。 |

#### `meta:`(可选映射)

```yaml
text:
  meta:
    # 可选:声明每个元数据字段落到输出格式的哪个键。
    # 没有这个块时,使用规范的默认映射。
    # 这块**纯声明** —— 它不改变数据形状,只声明输出键。
    original_file:  trans-unit-attribute      # XLIFF <trans-unit> 属性
    source_context: context-group            # XLIFF <context-group> 名
    location:       context.linenumber        # 在 context-group 内
    engine_path:    trans-unit-attribute      # 或自定义命名空间
```

`meta:` 块**纯声明** —— 它告诉 CLI 规范规定的数据形状使用哪些输出键。
它**不得**增加、重命名、删除字段。数据形状(source-context 的
`file` / `line` / `end_line` / `snippet`)由本规范固定,不可协商。

引擎可为自己的扩展媒体定义 `meta:` 块。键名引擎定;约束同上
(不改变形状,只映射键)。

#### `original-file`

`original-file` 字段让译者知道翻译单元来自游戏归档的哪个文件。
没有它,QA 无法把丢失的翻译溯源到原始位置。

XLIFF 单元示例:

```xml
<trans-unit id="tu-0042" original-file="scenes/day1/scene_001.bin">
  <source>Hello {player}</source>
  <target>你好 {player}</target>
</trans-unit>
```

CLI **必须**在能拿到值时发出 `original-file`。当 `metadata.original_file` 为 `false` 时,CLI 可以省略,但 Wrapper / OmegaT 应把缺席视为"未知来源"。

`original-file` 在 **extract** 时写入(此时读源代码),在 inject 时
**原样保留**(源代码未变,CLI 不重读)。

#### `source-context`(对 hardcoded sub-media)

> ⚠ **规范性数据模型。** CLI **必须**把每个 `text.hardcoded` 单元的源代码
> 上下文捕获为一个固定数据模型。选择的输出格式(XLIFF / PO / JSON)只是
> 一种序列化 —— Wrapper / OmegaT 按同一组字段读取,与格式无关。

**source-context 何时写?**

源代码只在 **extract** 时读。CLI 在那里捕获四字段记录并嵌入翻译
单元。**inject** 时,CLI 读翻译文本;它**不重捕源代码**(源代码没变)。
捕获的 source-context **必须**在任意次 extract → inject 循环中原样保留。

**source-context 何时读?**

Wrapper / OmegaT 应在 extract 后(`post-extract`)向译者展示
source-context,并在 inject 前(`pre-inject`)向 QA 展示。**build** 阶段
**不得**读 source-context —— 引擎已经知道代码,捕获的 snippet 只
供人读。

这些阶段由 `lifecycle.read_on`(见上)控制。默认覆盖两个预期消费者;
build 阶段被故意排除。

**数据模型**

CLI 提取 `text.hardcoded` 字符串(嵌入脚本或二进制资源的字符串)时,
把源代码上下文捕获为一个**四字段记录**:

| 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `file` | path | 是 | 字符串所在文件的源路径。与单元的 `original-file` 相同。 |
| `line` | int | 是 | 字符串所在行(1-based)。 |
| `end_line` | int | 是 | 捕获片段最后一行(1-based)。单行字符串时与 `line` 相等。 |
| `snippet` | string | 是 | 捕获的源行,以 `\n` 连接。前导行号可选但建议。 |

`snippet` 长度受 `hardcoded.max_bytes`(默认 4096)限制。CLI 需要截断时
**必须**保留第一行(含字符串的那一行)完整。

##### 数据模型示例

字符串 `"Hello {player}."` 在 `scenes/day1/scene_001.rpy:42`,
配置 3 行上下文时产出此记录:

```yaml
context:
  file: scenes/day1/scene_001.rpy
  line: 42
  end_line: 44
  snippet: |
    41 │     if player.gender == "male":
    42 │         narrator("Hello {player}.")
    43 │     else:
```

##### 各格式的序列化

CLI **必须**把同一组四字段序列化到所选格式。Wrapper / OmegaT 转换器
**必须**能在两种格式之间无损往返。

**XLIFF**(`<trans-unit>`):

```xml
<trans-unit id="tu-0042" original-file="scenes/day1/scene_001.rpy">
  <source>Hello {player}.</source>
  <target>你好 {player}。</target>
  <context-group name="source-context" purpose="information">
    <context context-type="sourcefile">scenes/day1/scene_001.rpy</context>
    <context context-type="linenumber">42</context>
    <context context-type="endlinenumber">44</context>
    <context context-type="snippet">41 │     if player.gender == "male":
42 │         narrator("Hello {player}.")
43 │     else:</context>
  </context-group>
</trans-unit>
```

必需的 `context-type` 键:`sourcefile`、`linenumber`、`endlinenumber`、
`snippet`。CLI **可**发额外 `<context>` 兄弟(如 `columnnumber`),但
**不得**重命名这四个。

**PO**(`#:` 引用注释):

```po
#: scenes/day1/scene_001.rpy:42
#: scenes/day1/scene_001.rpy:43
#: scenes/day1/scene_001.rpy:44
msgid "Hello {player}."
msgstr "你好 {player}。"
```

PO 没有结构化上下文字段;四字段模型坍缩为每行一个 `#: file:line` 注释。
`file` 隐含在注释目标中;`line` 与 `end_line` 由注释范围表达。
PO 无法承载 `snippet` 文本 —— 见下"有损格式"。

**JSON**:

```json
{
  "id": "tu-0042",
  "source": "Hello {player}.",
  "target": "你好 {player}。",
  "context": {
    "file": "scenes/day1/scene_001.rpy",
    "line": 42,
    "end_line": 44,
    "snippet": "41 │     if player.gender == \"male\":\n42 │         narrator(\"Hello {player}.\")\n43 │     else:"
  }
}
```

JSON 键**必须**恰好为:`file`、`line`、`end_line`、`snippet`。
允许额外键,但**不得**替换四个中的任何一个。

##### 有损格式

PO 天然有损:`snippet` 文本在标准 PO 中无法表示。Wrapper / OmegaT 应回退到:

1. 解析 `#: file:N` 注释,恢复 `file` 与 `line` / `end_line`。
2. 按恢复的行范围重新读取源文件,重建 `snippet`(CLI 不需嵌入)。

JSON 无损。XLIFF 无损。

CLI 在用户要求无损格式时**不得**挑有损格式。`text.format: po`
是刻意的信息损失选择;`text.format: xliff` 或 `json` 保留所有四个字段。

##### 引擎无法定位源时

引擎无法定位字符串源(二进制 blob、混淆字节码)时,四字段坍缩为:

```yaml
context:
  file: <字符串来自的资源文件>
  line: 0
  end_line: 0
  snippet: ""
```

CLI **必须**用这些哨兵值发出四字段记录,而**不得**省略 `context-group` /
`context:` 对象。

#### `location`

CLI 已知的位置信息(XLIFF 写为 `<context context-type="linenumber">`;PO 写为 `file:line`)。未知时省略。

`location` 在 **extract** 时写入(此时读源代码)。
inject 时保留。

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