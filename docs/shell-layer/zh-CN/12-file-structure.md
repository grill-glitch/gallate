# 12. 文件结构

> 状态:**规范性**。定义标准媒体目录(`text/`、`image/`、`audio/`、`video/` 等)里文件的命名、组织与结构约定。

[06-project-structure.md](./06-project-structure.md) 章节讲 Project Root 下有**哪些目录**。本章讲目录**里面**放什么。

---

## 12.1 惯例而非规则

CLI 决定目录内布局。本章是**推荐惯例**,不是合同 —— 引擎可以偏离,但偏离后会失去 `gallate-standard-layout` 标签,也就无法跨引擎共享工具。

```text
标准媒体目录:

  text/       每个翻译单元一个文件(JSON / ...)
  image/      每张图一个文件
  audio/      每段音频一个文件
  video/      每个视频一个文件
```

---

## 12.2 `text/`

### 顶层布局

```text
text/
├── manifest.yaml          # 可选:本次 extract 的元数据(谁、何时、多少)
├── units/                 # 每个翻译单元一个文件(默认位置)
│   ├── scenes_intro.json
│   ├── scenes_day1_scene_001.json
│   ├── scenes_day1_scene_002.json
│   └── ...
└── reports/               # 可选:验证发现、术语表 dump
    └── validation.yaml
```

CLI 可以把 `units/` 拍平让文件直接落在 `text/` 下。默认是 `text/units/`,以免人工浏览项目目录时被单元文件刷屏。

### 命名约定

推荐的文件名形状:

```text
<media-resource-path>.<translation-format-extension>
```

例子:

```text
scenes/intro.bin            →  text/units/scenes_intro.json
scenes/day1/scene_001.bin   →  text/units/scenes_day1_scene_001.json
fonts/ascii.glyph_table     →  text/units/fonts_ascii_glyph_table.json
```

CLI 用 `_` 替换 `/` 以便平铺目录列表仍然可读。引擎可以使用更深的布局(镜像源目录)—— 见 [12.3 布局模式](#123-布局模式)。

### `text/manifest.json`

CLI 在 extract 结束时可写此文件,记录提取了哪些、何时、由哪个 CLI 提取:

```json
{
  "extracted_at": "2026-09-09T12:34:56Z",
  "cli": {
    "id": "artemis",
    "version": "1.2.0",
    "protocol": "gcwp-1.0"
  },
  "counts": {
    "files_scanned": 1524,
    "files_matched": 318,
    "strings_extracted": 8421,
    "by_sub_media": {
      "dialog": 6320,
      "menu": 480,
      "hardcoded": 1621
    }
  }
}
```

此文件**可选**。Wrapper / OmegaT 可用于项目仪表盘,但**不得**依赖。

---

## 12.3 布局模式

CLI 可选三种布局之一。选择记录在 `gallate.yaml`:

```yaml
text:
  layout: flat              # default
  # alternatives:
  #   flat     — text/units/<path-with-_>.json
  #   mirror   — text/units/<engine-path>/<file>.json
  #   single   — text/translation.json  (所有 unit 一个文件)
```

| 模式 | 优点 | 缺点 |
| ---- | ---- | ---- |
| `flat`   | git diff 友好;可部分提交。 | 源路径仅差 `/` 时会冲突。 |
| `mirror` | 与源 1:1 映射;无冲突。 | 目录深;难发现重复。 |
| `single` | 单个文档 —— OmegaT 只开一个文件。 | 一文件巨大;无法分块审校;merge 必然冲突。 |

### `flat`(默认)

```text
text/units/
├── scenes_intro.json
├── scenes_day1_scene_001.json
├── scenes_day1_scene_002.json
└── fonts_ascii_glyph_table.json
```

### `mirror`

```text
text/units/
├── scenes/
│   ├── intro.json
│   └── day1/
│       ├── scene_001.json
│       └── scene_002.json
└── fonts/
    └── ascii/
        └── glyph_table.json
```

### `single`

```text
text/
└── translation.json      # 所有翻译单元在一个文档中
```

---

## 12.4 单元文件格式(`gallate.translation` v1)

JSON 是唯一的标准单元文件格式。XLIFF 与 PO **不是**标准格式;需要它们的
引擎可以把它们作为引擎扩展格式暴露,但 Wrapper / OmegaT 不必须处理
JSON 以外的格式。

单元文件是 gallate 项目的**规范化翻译状态**。它是一个工作文件,
而不是数据库。控制下面每个字段的规则见
[§12.13 设计原则](#1213-设计原则)。

### 12.4.1 容器

```json
{
  "format": "gallate.translation",
  "version": 1,
  "source": "ja",
  "target": "zh-CN",
  "entries": []
}
```

`entries[]` 是扁平数组;容器可以为空(刚 extract 完但没找到字符串)或
装上千条条目。上面的例子展示空容器;下一小节给出已填充的。

| 键 | 必填 | 含义 |
| --- | --- | --- |
| `format` | 是 | 字面量 `"gallate.translation"`,标识文件种类。 |
| `version` | 是 | 格式版本。这里记录的是 v1。CLI 拒绝加载 `version` 高于自身已知版本的文档。 |
| `source` | 是 | BCP-47 源语言标签(`ja`、`en-US` 等)。 |
| `target` | 是 | BCP-47 目标语言标签。 |
| `entries[]` | 是 | 翻译条目,每条可提取字符串一个。 |

容器本身**与语言无关** —— `entries[].source` 与 `entries[].target` 都不带
语言标签。语言对放在文档级,因为文档内每条条目按定义都同属这一对。

### 12.4.2 条目

```json
{
  "id": "scenario/0083_SS_01_x.lua:L0142",
  "source": "今日はいい天気ですね。",
  "target": "今天天气真好呢。",
  "state": "translated",

  "source_context": {
    "file": "scenario/0083_SS_01_x.lua",
    "line": 142,
    "end_line": 144,
    "snippet": "141 │ if FLAG(\"opening\") then\n142 │     COMMAND(\"セリフ\", \"アキト\", \"…どうしたの？\")\n143 │ end"
  },

  "context": {
    "speaker": "Alice",
    "scene": "0083_SS_01",
    "location": "school"
  },

  "placeholders": [
    {"id": "player", "syntax": "{player}", "type": "variable"}
  ],

  "notes": [
    {"text": "角色第一次登场。", "author": "translator"}
  ],

  "provenance": {"type": "human"},

  "metadata": {}
}
```

| 键 | 必填 | 默认 | 种类 | 含义 |
| --- | --- | --- | --- | --- |
| `id` | 是 | — | 派生 | 位置派生的身份标识。见 [05-config-file.md § `id`](./05-config-file.md#id位置派生)。 |
| `source` | 是 | — | 派生 | 源文本。可重提取。 |
| `target` | 是 | `""` | 人工 | 翻译后文本。翻译前为空。是真正由人/AI 写入的字段。 |
| `state` | 是 | `"initial"` | 人工 | 当前状态标签。见 [05-config-file.md § `state`](./05-config-file.md#state)。 |
| `source_context` | 可选 | 哨兵值 | 派生 | 四字段记录(`file` / `line` / `end_line` / `snippet`)。extract 时重捕,inject 时原样保留。见 [05-config-file.md § `source_context`](./05-config-file.md#source_context)。 |
| `context` | 可选 | `{}` | 人工 | 自由格式的译者帮助数据(`speaker` / `scene` / `location` 等)。见 [05-config-file.md § `context`](./05-config-file.md#context)。 |
| `placeholders` | 可选 | `[]` | 派生 | 在 `source` 中检测到的占位符。CLI 据此校验 `target` 是否保留它们。见 [05-config-file.md § `placeholders`](./05-config-file.md#placeholders)。 |
| `notes` | 可选 | `[]` | 人工 | 译者/审校笔记。见 [05-config-file.md § `notes`](./05-config-file.md#notes)。 |
| `provenance` | 可选 | `{"type": "human"}` | 人工 | 当前 `target` 的来源。见 [05-config-file.md § `provenance`](./05-config-file.md#provenance)。 |
| `metadata` | 可选 | `{}` | 引擎 | 引擎定义的扩展命名空间。见 [05-config-file.md § `metadata`](./05-config-file.md#metadata)。 |

**种类**这一列是规范性的:

- **派生** —— CLI **必须**能从源资源重新计算出该字段。持久化它只是
  缓存;重提取后字段缺失不是错误。
- **人工** —— 由人或 AI 写入。CLI **不得**重提取时静默重算或覆盖人工字段。
- **引擎** —— 语义由引擎定义。CLI 在引擎自有合约下**可以**读写;规范不解释。

### 12.4.3 多文件布局

一个逻辑域一个文件(标准布局下即一个源资源一个文件)。命名:

```text
text/units/<domain>.json
```

引擎可分组多个域:

```text
text/units/main.json
text/units/help.json
```

CLI **必须**在其引擎扩展章节文档化它发出的任何额外键。以上是
Wrapper / OmegaT 可可靠处理的最小形状。

---

## 12.5 `image/`

```text
image/
├── bg/
│   └── scenes_day1_scene_001_bg.png
├── portrait/
│   └── character_alice_default.png
├── portrait_diff/
│   └── character_alice_smile.png.json     # 差分占位文件
└── ui/
    └── button_save.png
```

子媒体目录(`bg/`、`portrait/` 等)与 CLI 调用中的 sub-media 标识符一一对应:

```yaml
image:
  sub_media_dirs: true
```

`false` 时所有 sub-media 拍平到 `image/`。默认 `true`。

`portrait_diff` 文件不替换源 portrait —— 是并排的差异。`.json` 占位记录基础图与差异区域:

```json
{
  "base": "character_alice_default.png",
  "diff": {
    "region": [120, 80, 240, 320],
    "kind": "expression_smile"
  }
}
```

此形状由引擎定义;以上只是一个示例。

---

## 12.6 `audio/`

```text
audio/
├── voice/
│   ├── scene_001_line_001.wav
│   └── scene_001_line_002.wav
├── bgm/
│   └── title_theme.ogg
└── sfx/
    └── ui_click.ogg
```

同 `image/` 的 sub-media 目录规则。CLI 也可在旁写一份 `audio/manifest.json` 记录时长 / 格式 / 配音。

---

## 12.7 `video/`

```text
video/
├── cutscene/
│   └── intro.mp4
├── cinematic/
│   └── trailer_e3.mp4
└── opening/
    └── op_credits.webm
```

同 sub-media 目录规则。视频通常很大;Wrapper 应当只重新复用(替换音轨),除非确实需要才重编码。

---

## 12.8 引擎扩展目录

引擎暴露 audio/video/font 时,对应目录沿用上述约定:

```text
font/
├── ascii/
│   └── font_ascii_8x16.fnt
└── cjk/
    └── font_cjk_notosans.fnt
```

`font/` 条目通常**不是**翻译目标(它们是二进制的),所以 CLI 只在引擎有显式"本地化字体"语义时才输出。详见 [04-media.md § 引擎扩展媒体](./04-media.md#引擎扩展媒体)。

---

## 12.9 标准不强制的事

- 各文件内的精确 JSON 形状(由引擎定义,仅由引擎自身校验)
- CLI 是按资源生成多个文件(推荐),还是单个汇总文件
- sub-media 目录是镜像还是拍平
- 是否生成 manifest 文件
- 是否生成 `reports/`

这些是引擎 wrapper 文档化的实现选择。Shell 层只强制:

- 标准媒体目录存在于对应位置
- 路径解析跨次运行一致(同输入→同输出路径)
- 文件名稳定(便于 git diff 与 OmegaT 引用不失效)

---

## 12.10 可发现性

Wrapper 通过读取以下文件自省项目:

```text
text/manifest.json          # 如存在
text/units/*.json           # 或 CLI 实际放置的位置
```

Wrapper 不需要猜测。有 manifest 用 manifest,否则用 glob。引擎 wrapper
可加 `engine.manifest_path` 提示:

```yaml
engine:
  manifest_path: ./text/manifest.json
```

标准 CLI 忽略此键;Wrapper 在存在时使用。

---

## 12.11 媒体文件中的工作目录

`scripts/pre` 与 `scripts/post` 中的脚本看到 Project Root 处的标准媒体目录。它们可以就地修改文件(例如归一化编码),然后引擎读取。CLI **不**假设任何后处理发生 —— 它读原始字节。

---

## 12.12 概要

| 目录 | 默认模式 | Sub-Media 目录? |
| --- | --- | --- |
| `text/`        | `text/units/*.json`       | 不(单元在文件内) |
| `image/`       | `image/<sub-media>/*`    | 是 |
| `audio/`       | `audio/<sub-media>/*`    | 是 |
| `video/`       | `video/<sub-media>/*`    | 是 |
| `font/` (扩展) | `font/<sub-media>/*`      | 是 |

所有路径相对 Project Root 解析。CLI 必须**确定** —— 同输入、同输出路径,只时间戳变。

---

## 12.13 设计原则

`entries[]` 上的每个字段遵循一条规则:

> **源是派生的。身份是派生的。翻译是人工的。笔记是人工的。
> 出处是人工的。引擎元数据由引擎定义。**

一个字段**派生**当且仅当 CLI 能仅从源资源重新算出它:`source`、
`id`、`source_context`、`placeholders`。这些是缓存。CLI 可以丢弃
并重新提取;Wrapper **必须**能通过重新跑 extract 重建它们。

一个字段**人工**当且仅当它由人或 AI 写入:`target`、`state`、
`context`(被译者填充时)、`notes`、`provenance`。CLI **不得**在
重提取时静默重算或覆盖人工字段。

一个字段**引擎**当其语义由引擎定义(`metadata`,以及引擎定义的扩展)。
规范不解释引擎字段。

后果是:

```text
源资源
  │
  ▼
Gallate CLI extract
  │
  ▼
text/units/*.json   ← 派生字段重算;人工字段保留
  │
  ▼
人 / AI / editor   (只修改人工字段)
  │
  ▼
Gallate CLI inject
```

`text/units/*.json` 是**可丢弃的**。删掉它并重跑 extract 不损失人工
工作 —— CLI 重新算出派生字段,定位到匹配的源,下一次 inject 重走条目。
(实际中 Wrapper 会保留文件,因为每个 `target` 重打一遍代价高;但规范
不依赖这一点。)

CLI 不需要 UUID 注册表,不需要翻译记忆库,也不需要 `id → 单元` 的映射。
`id` 可重算,`source` 可重算,人工字段是 git diff。
