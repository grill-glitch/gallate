# 12. 文件结构

> 状态:**规范性**。定义标准媒体目录(`text/`、`image/`、`audio/`、`video/` 等)里文件的命名、组织与结构约定。

[06-project-structure.md](./06-project-structure.md) 章节讲 Project Root 下有**哪些目录**。本章讲目录**里面**放什么。

---

## 12.1 惯例而非规则

CLI 决定目录内布局。本章是**推荐惯例**,不是合同 —— 引擎可以偏离,但偏离后会失去 `gallate-standard-layout` 标签,也就无法跨引擎共享工具。

```text
标准媒体目录:

  text/       每个翻译单元一个文件(XLIFF / PO / JSON / ...)
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
│   ├── scenes_intro.yaml
│   ├── scenes_day1_scene_001.xlf
│   ├── scenes_day1_scene_002.xlf
│   └── ...
└── reports/               # 可选:验证发现、术语表 dump
    └── validation.yaml
```

CLI 可以把 `units/` 拍平让文件直接落在 `text/` 下。默认是 `text/units/`,以免人工浏览项目目录时被 XLIFF 文件刷屏。

### 命名约定

推荐的文件名形状:

```text
<media-resource-path>.<translation-format-extension>
```

例子:

```text
scenes/intro.bin            →  text/units/scenes_intro.xlf
scenes/day1/scene_001.bin   →  text/units/scenes_day1_scene_001.xlf
fonts/ascii.glyph_table     →  text/units/fonts_ascii_glyph_table.xlf
```

CLI 用 `_` 替换 `/` 以便平铺目录列表仍然可读。引擎可以使用更深的布局(镜像源目录)—— 见 [12.3 布局模式](#123-布局模式)。

### `text/manifest.yaml`

CLI 在 extract 结束时可写此文件,记录提取了哪些、何时、由哪个 CLI 提取:

```yaml
extracted_at: 2026-09-09T12:34:56Z
cli:
  id: artemis
  version: 1.2.0
  protocol: gcwp-1.0
counts:
  files_scanned: 1524
  files_matched: 318
  strings_extracted: 8421
  by_sub_media:
    dialog: 6320
    menu: 480
    hardcoded: 1621
```

此文件**可选**。Wrapper / OmegaT 可用于项目仪表盘,但**不得**依赖。

---

## 12.3 布局模式

CLI 可选三种布局之一。选择记录在 `gallate.yaml`:

```yaml
text:
  layout: flat              # default
  # alternatives:
  #   flat     — text/units/<path-with-_>.xlf
  #   mirror   — text/units/<engine-path>/<file>.xlf
  #   single   — text/translation.xlf  (所有 unit 一个文件)
```

| 模式 | 优点 | 缺点 |
| ---- | ---- | ---- |
| `flat`   | git diff 友好;可部分提交。 | 源路径仅差 `/` 时会冲突。 |
| `mirror` | 与源 1:1 映射;无冲突。 | 目录深;难发现重复。 |
| `single` | OmegaT 只开一个 XLIFF。 | 一文件巨大;无法分块审校;merge 必然冲突。 |

### `flat`(默认)

```text
text/units/
├── scenes_intro.xlf
├── scenes_day1_scene_001.xlf
├── scenes_day1_scene_002.xlf
└── fonts_ascii_glyph_table.xlf
```

### `mirror`

```text
text/units/
├── scenes/
│   ├── intro.xlf
│   └── day1/
│       ├── scene_001.xlf
│       └── scene_002.xlf
└── fonts/
    └── ascii/
        └── glyph_table.xlf
```

### `single`

```text
text/
└── translation.xlf       # 所有翻译单元在一个文档中
```

---

## 12.4 各格式细节

### XLIFF(`.xlf` / `.xliff`)

标准 XLIFF 1.2,带 `<file>` 与 `<trans-unit>` 元素。每个 `<trans-unit>`
携带的元数据见 [05-config-file.md § text: format](./05-config-file.md#text-format)(`original-file`、`source-context` 等)。

### PO(`.po`)

GNU gettext。一个域一个文件。命名:

```text
text/units/<domain>.po
```

引擎可分组多个域:

```text
text/units/main.po
text/units/help.po
```

### JSON(`.json`)

任意引擎定义结构。标准键:

```yaml
schema:
  units:
    - id:        # 唯一字符串 id
      source:    # 源文本
      target:    # 翻译后文本,extract 时为空)
      context:   # 可选,引擎定义
      meta:      # 可选,自由格式的引擎元数据
```

CLI **必须**在其引擎扩展章节文档化精确的 JSON 形状。以上是 Wrapper / OmegaT 可可靠处理的最小 schema。

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

同 `image/` 的 sub-media 目录规则。CLI 也可在旁写一份 `audio/manifest.yaml` 记录时长 / 格式 / 配音。

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

- 各文件内的精确 XLIFF schema(由引擎定义,仅由引擎自身校验)
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
text/manifest.yaml          # 如存在
text/units/*.xlf            # 或 CLI 实际放置的位置
```

Wrapper 不需要猜测。有 manifest 用 manifest,否则用 glob。引擎 wrapper
可加 `engine.manifest_path` 提示:

```yaml
engine:
  manifest_path: ./text/manifest.yaml
```

标准 CLI 忽略此键;Wrapper 在存在时使用。

---

## 12.11 媒体文件中的工作目录

`scripts/pre` 与 `scripts/post` 中的脚本看到 Project Root 处的标准媒体目录。它们可以就地修改文件(例如归一化编码),然后引擎读取。CLI **不**假设任何后处理发生 —— 它读原始字节。

---

## 12.12 概要

| 目录 | 默认模式 | Sub-Media 目录? |
| --- | --- | --- |
| `text/`        | `text/units/*.xlf`        | 不(单元在文件内) |
| `image/`       | `image/<sub-media>/*`    | 是 |
| `audio/`       | `audio/<sub-media>/*`    | 是 |
| `video/`       | `video/<sub-media>/*`    | 是 |
| `font/` (扩展) | `font/<sub-media>/*`      | 是 |

所有路径相对 Project Root 解析。CLI 必须**确定** —— 同输入、同输出路径,只时间戳变。