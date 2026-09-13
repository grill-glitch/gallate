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
# standard CLI 默认把每条翻译单元写到 text/units/*.json,并附带
# original-file / source-context 等元数据。
text:
  format: json
  layout: flat
  metadata:
    original_file: true
    source_context: true
    location: true
    placeholders: true
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
    original_file:  original_file
    source_context: source_context
    location:       location
    placeholders:   placeholders
    engine_path:    engine_path
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
  format: json             # json | engine-extension
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

|| 字段 | 类型 | 含义 |
|| --- | --- | --- |
|| `format` | enum | 输出格式。标准:`json`。 |
|| `layout` | enum | 文件布局。标准:`flat` / `mirror` / `single`。见 [12-file-structure.md](./12-file-structure.md)。 |
|| `metadata.original_file` | bool | 若为 true,每个条目携带 `original_file` 键,标明游戏归档内的源资源路径。默认 `true`。 |
|| `metadata.source_context` | bool | 若为 true,每个 `text.hardcoded` 条目携带四字段 `source_context` 记录(`file` / `line` / `end_line` / `snippet`),详见下文 [`source_context`](#source_context) 一节。默认 `true`。 |
|| `metadata.location` | bool | 若为 true,非 hardcoded 条目携带 `line` / `offset` / `length`,标识源字符串在文件内的位置。默认 `true`。`text.hardcoded` 条目的位置走 `source_context` 而非此处。 |
|| `metadata.placeholders` | bool | 若为 true,条目携带自动检测的 `placeholders[]` 列表。默认 `true`。 |
|| `metadata.engine_path` | bool | 若为 true,条目携带引擎内部逻辑路径(引擎定义)。默认 `true`。 |
|| `hardcoded.context_lines` | int | `text.hardcoded` 条目捕获周边代码行数。默认 `3`。 |
|| `hardcoded.max_bytes` | int | 每条目捕获的 payload 上限。默认 `4096`。 |
|| `hardcoded.engine_extensions` | list | 引擎视作代码的文件扩展名。空列表 = 引擎自决。 |
|| `lifecycle.written_on` | enum | `extract`(默认)或 `never`。CLI 仅在 extract 时写入元数据,inject 时保留。build 阶段从不写元数据。 |
|| `lifecycle.read_on` | list | Wrapper / OmegaT 应展示元数据的阶段。默认:`post-extract` 与 `pre-inject`。**build 阶段 MUST NOT 读 `source_context`**。 |

#### `meta:`(可选映射)

```yaml
text:
  meta:
    # 可选:声明每个元数据字段落到哪个 JSON 键。
    # 没有这个块时,使用规范的默认映射。
    # 这块**纯声明** —— 它不改变数据形状,只声明输出键。
    # 下面五个值同时也是规范的默认键名。
    original_file:  original_file      # 条目级 JSON 键
    source_context: source_context     # 条目级 JSON 对象
    location:       location           # 条目级 JSON 对象
    placeholders:   placeholders       # 条目级 JSON 数组
    engine_path:    engine_path        # 条目级 JSON 键
```

`meta:` 块**纯声明** —— 它告诉 CLI 规范规定的数据形状使用哪些输出键。
它**不得**增加、重命名、删除字段。数据形状(`source_context` 的
`file` / `line` / `end_line` / `snippet`)由本规范固定,不可协商。

引擎可为自己的扩展媒体定义 `meta:` 块。键名引擎定;约束同上
(不改变形状,只映射键)。

#### `id`(位置派生)

每条翻译条目都有一个 `id`。`id` **必须**由条目在源文件中的**位置派生**,
而**不得**由提取顺序计数器生成。计数器会在插入一条后重编号其后的所有
条目,静默使翻译记忆失效;位置派生 id 在重新提取后保持不变。

形状:

```text
<resource-path>:L<line>
```

| 部分 | 规则 |
| --- | --- |
| `<resource-path>` | 游戏归档内的源资源路径(如 `scenario/0083_SS_01_x.lua`),引擎定义。CLI **必须**使用完整路径 —— 单 basename 不够,因为两个源文件可以共享 basename。 |
| `L` | 字面量,大写。标记其后的数字为行号。 |
| `<line>` | 1-based 行号,**至少**零填充到 4 位(`L0142`)。超过 9999 的行用所需位数(`L12345`)。 |
| `#<n>` | 同一行第二个及之后条目的消歧后缀,按源顺序计数,从 `2` 开始(`…#2`、`…#3`)。每行第一个条目省略。 |

示例:

```text
scenario/0083_SS_01_x.lua:L0142        第 142 行上的第一个条目
scenario/0083_SS_01_x.lua:L0142#2      同一行上的第二个条目
```

规则:

- CLI **不得**把运行顺序计数器(`tu-0001`、`U000001`)当作条目 `id`。
  这类 id 在重新提取后不稳定。
- 只要源文件未变,`id` **必须**稳定。
- 位置未知时(二进制 blob、混淆字节码),`line` 取哨兵值 `0`,该文件的
  条目按引擎定义的确定性顺序以 `…#1`、`#2`… 排序。
- `id` **必须**在所在输出文档内唯一。完整资源路径在实践中使这条几乎
  自动成立;`#<n>` 后缀处理剩余的"同一行两条"情况。

#### `state`

一个**当前标签**,不是状态机。标签告诉 Wrapper / OmegaT `target` 是怎么
产生的、应给多少信心。

| 取值 | 含义 |
| --- | --- |
| `initial` | `target` 为空或未动过。CLI 在 extract 时设置。 |
| `translated` | `target` 已被填入(人、AI、或之前的翻译记忆导入)。 |
| `reviewed` | 人类审校已确认 `target`。 |
| `final` | QA 通过。 |
| `needs_review` | 在 `final` / `reviewed` 之后源文本变了,或校验拒绝了 `target`。回退是正常的、预期的。 |

规则:

- 标签**必须**可逆。`final` 条目在源变化时**必须**允许降到
  `needs_review`;CLI **不得**抛错。
- CLI **不得**强制状态机。`translated` → `final` 跳过的 `reviewed` 是允许的。
- CLI 在 extract 时把 `state` 设为 `"initial"`(或保留前值,若条目已存在
  且 `target` 非空)。
- `state` 是**人工**字段 —— CLI **不得**在重提取时静默重写它。

#### `source`

源文本。可从源资源重新提取。

#### `target`

翻译后文本。唯一真正由人/AI 写入的字段。翻译前为空。CLI **不得**在
重提取时静默覆盖它。

#### `source_context`(对 hardcoded sub-media)

> ⚠ **规范性数据模型。** CLI **必须**把每个 `text.hardcoded` 条目的源代码
> 上下文捕获为一个固定数据模型。JSON 输出只是一种序列化 ——
> Wrapper / OmegaT 按同一组字段读取,与格式无关。

**`source_context` 何时写?**

源代码只在 **extract** 时读。CLI 在那里捕获四字段记录并嵌入条目。
**inject** 时,CLI 读翻译文本;它**不重捕源代码**(源代码没变)。
捕获的 `source_context` **必须**在任意次 extract → inject 循环中原样保留。

**`source_context` 何时读?**

Wrapper / OmegaT 应在 extract 后(`post-extract`)向译者展示
`source_context`,并在 inject 前(`pre-inject`)向 QA 展示。**build** 阶段
**不得**读 `source_context` —— 引擎已经知道代码,捕获的 snippet 只
供人读。

这些阶段由 `lifecycle.read_on`(见上)控制。默认覆盖两个预期消费者;
build 阶段被故意排除。

**数据模型**

CLI 提取 `text.hardcoded` 字符串(嵌入脚本或二进制资源的字符串)时,
把源代码上下文捕获为一个**四字段记录**:

| 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `file` | path | 是 | 字符串所在文件的源路径。与条目的 `original_file` 相同。 |
| `line` | int | 是 | 字符串所在行(1-based)。 |
| `end_line` | int | 是 | 捕获片段最后一行(1-based)。单行字符串时与 `line` 相等。 |
| `snippet` | string | 是 | 捕获的源行,以 `\n` 连接。前导行号可选但建议。 |

`snippet` 长度受 `hardcoded.max_bytes`(默认 4096)限制。CLI 需要截断时
**必须**保留第一行(含字符串的那一行)完整。

##### 数据模型示例

字符串 `"……どうしたの？"` 在 `scenario/0083_SS_01_x.lua:142`,
配置 3 行上下文时产出此记录:

```yaml
source_context:
  file: scenario/0083_SS_01_x.lua
  line: 142
  end_line: 144
  snippet: |
    141 │ if FLAG("opening") then
    142 │     COMMAND("セリフ", "アキト", "……どうしたの？")
    143 │ end
```

##### 序列化(JSON)

JSON 是唯一的标准输出格式,所以只有一个序列化。Wrapper / OmegaT
转换器**必须**无损往返该模型。

```json
{
  "id": "scenario/0083_SS_01_x.lua:L0142",
  "source": "……どうしたの？",
  "target": "……怎么了？",
  "state": "translated",
  "original_file": "scenario/0083_SS_01_x.lua",
  "location": {
    "line": 142,
    "offset": 29,
    "length": 7
  },
  "source_context": {
    "file": "scenario/0083_SS_01_x.lua",
    "line": 142,
    "end_line": 144,
    "snippet": "141 │ if FLAG(\"opening\") then\n142 │     COMMAND(\"セリフ\", \"アキト\", \"……どうしたの？\")\n143 │ end"
  }
}
```

`source_context` 键**必须**恰好为:`file`、`line`、`end_line`、`snippet`。
允许额外键,但**不得**替换四个中的任何一个。

`id` 是位置派生的 —— 见上文 [`id`](#id位置派生)。本例中的
`scenario/0083_SS_01_x.lua:L0142` 直接由 `source_context.file` + `source_context.line` 得出。

##### 引擎无法定位源时

引擎无法定位字符串源(二进制 blob、混淆字节码)时,四字段坍缩为:

```yaml
source_context:
  file: <字符串来自的资源文件>
  line: 0
  end_line: 0
  snippet: ""
```

CLI **必须**用这些哨兵值发出四字段记录,而**不得**省略 `source_context:` 对象。
条目 `id` 遵循 [`id`](#id位置派生) 中的位置未知规则。

#### `context`(译者帮助字段,人工)

译者(或引擎)写入的自由格式数据,用来让条目对人可理解。**不是**源代码
上下文 —— 那个在 `source_context`(上)中,是**派生**自源文件的。
这里的 `context` 是译者伸手去记"这是 Alice 第一次出场"或"这行
在校园场景中念出"的字段。

```json
{
  "context": {
    "speaker": "Alice",
    "scene": "0083_SS_01",
    "location": "school"
  }
}
```

规则:

- CLI **不得**自动往 `context` 加键。`context` 中的任何键要么是译者
  写入,要么是引擎按自有合约写入。
- CLI **不得**在重提取时删除 `context` 中的键。这是**人工**数据;
  见 [12-file-structure.md § 设计原则](./12-file-structure.md#1213-设计原则)。
引擎**可以**定义子命名空间(如 `context.engine:artemis`)放
引擎私有的笔记,避免和译者笔记撞车。

#### `placeholders`

在 `source` 内检测到的占位符。CLI 在 extract 时扫描源文本并记录每条;
inject 时校验 `target` 携带同样的占位符且顺序一致。

```json
{
  "placeholders": [
    {"id": "player",   "syntax": "{player}",   "type": "variable"},
    {"id": "score",    "syntax": "%d",         "type": "format"},
    {"id": "FADE_IN",  "syntax": "[FADE_IN_3]","type": "control"},
    {"id": "kanji",    "syntax": "{ruby:漢字|かんじ}", "type": "ruby"}
  ]
}
```

| `type` | 含义 |
| --- | --- |
| `variable` | 替换变量:`{name}`、`${name}`、`<name>`。 |
| `format` | printf 风格的位置占位符:`%d`、`%1$s`。 |
| `control` | 引擎控制码:`[FADE_IN_3]`、`[B]`。`id` 是控制码的名字,`syntax` 是字面量。 |
| `ruby` | Ruby / 振假名注音:`{ruby:漢字|かんじ}`。 |
| `engine` | 引擎定义占位符。CLI **可以**添加它能识别的其他 `type` 值。 |

规则:

- `id` **必须**在条目自身的 `placeholders[]` 内唯一。
- inject 时,CLI **必须**拒绝 `target` 的占位符在 id 集合或顺序上与
  `source` 不一致的条目。`type` 不一致是 warning 而非 error —— 译者
  在引擎接受的前提下,可以把 `%d` 升级为 `{score:d}`。
- `placeholders` 是**派生**字段。CLI **可以**在没扫到东西的条目上省略它。

#### `notes`

译者与审校笔记,挂在条目上。与 `context` 不同,`notes` 是一个**栈**——
每条笔记都有作者与正文,顺序保留。

```json
{
  "notes": [
    {"text": "角色第一次登场，语调要轻快。", "author": "translator"},
    {"text": "原文「いい天気ですね」是感叹而不是疑问，译文已调整。", "author": "reviewer"}
  ]
}
```

| 键 | 必填 | 含义 |
| --- | --- | --- |
| `text` | 是 | 笔记正文,纯文本。 |
| `author` | 是 | 自由字符串:`translator` / `reviewer` / `ai` / `cli` / `editor:<name>`。不强制枚举,新作者不需规范升级即可。 |

`notes` 是**人工**字段 —— CLI **不得**在重提取时删除、重排或覆盖笔记。

#### `provenance`

当前 `target` 的来源。Wrapper / Editor 把这个画成 `target` 字段旁的小徽章。

```json
{
  "provenance": {"type": "human"}
}
```

```json
{
  "provenance": {"type": "machine", "model": "Qwen2.5-7B-Instruct", "method": "machine_translation"}
}
```

```json
{
  "provenance": {"type": "tm",      "match": "fuzzy", "score": 0.92, "source": "previous_project.xlf"}
}
```

| `type` | 必填的额外字段 | 含义 |
| --- | --- | --- |
| `human` | — | `target` 由人写入或确认。 |
| `machine` | `model`,可选 `method` | `target` 来自机器翻译系统。`method` 区分 `machine_translation` / `llm` / `embeddings_kNN` 等。 |
| `tm` | `match`,`source`,可选 `score` | `target` 来自翻译记忆库。`match` 是 `exact` / `fuzzy` / `context`。 |
| `mt+review` | 继承自 `human` 和上述之一 | `target` 机器翻译后由人编辑。`provenance` 反映**当前** `target`,所以一次人工编辑会把它移到 `mt+review`,原机器信息保留。 |

规则:

- `provenance` 是**人工**字段。CLI **只**在 `target` 本身通过有据可查
  的路径变化时(比如 Wrapper 的"接受机器翻译"操作)更新它。
- CLI **不得**捏造用户没有产出的 `model` / `score` 值。

#### `metadata`

引擎定义扩展命名空间。引擎**可以**在 `metadata` 下写任何东西。规范
不解释这些键。

```json
{
  "metadata": {
    "engine:artemis": { "engine_specific_key": "value" }
  }
}
```

> 上面字面量 `engine:artemis` 仅作示例;真实前缀是 `engine:` 加 CLI 的
> `manifest.id`。正文里尖括号占位符 `engine:<engine-id>` 是**文档简写**,
> **不是**合法 JSON 语法。

CLI **必须**文档化它写的键。共享一个项目的两个引擎**不得**写到同一个
`metadata` 子命名空间。

#### `original_file`

`original_file` 键让译者知道翻译条目来自游戏归档的哪个文件。
没有它,QA 无法把丢失的翻译溯源到原始位置。

JSON 条目示例:

```json
{
  "id": "scenario/day1/scene_001.bin:L0042",
  "source": "Hello {player}",
  "target": "你好 {player}",
  "original_file": "scenes/day1/scene_001.bin"
}
```

CLI **必须**在能拿到值时发出 `original_file`。当 `metadata.original_file` 为 `false` 时,CLI 可以省略,但 Wrapper / OmegaT 应把缺席视为"未知来源"。

`original_file` 在 **extract** 时写入(此时读源代码),在 inject 时
**原样保留**(源代码未变,CLI 不重读)。

#### `location`

CLI 已知的位置信息 —— 源字符串在文件内的 `line` / `offset` / `length`。
未知时省略。

`location` 在 **extract** 时写入(此时读源代码)。
inject 时保留。

#### `engine_path`

引擎内部逻辑路径。引擎定义;CLI 原样传递。省略则 Wrapper 回退 `original_file`。

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