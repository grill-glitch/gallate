# 06. 项目结构

> 状态:**规范性**。定义 `init` 生成的标准布局以及引擎扩展目录规则。

## 6.1 标准布局

```text
my-game/
├── gallate.yaml
├── text/
├── image/
├── audio/                # 引擎扩展 (audio)
├── video/                # 引擎扩展 (video)
└── scripts/
```

`text/` 与 `image/` 是标准目录 —— 任何 gallate CLI 都存在。

`audio/` 与 `video/` 是**引擎扩展**目录,当引擎暴露 audio/video 作为媒体时创建。不处理这些的引擎直接跳过。

`scripts/` 存放用户自定义的 pre/post 脚本。

## 6.2 引擎扩展目录

CLI **可**在标准布局之上添加自己的目录。例如 Ren'Py CLI 可能创建 `audio/` 与 `font/`:

```text
my-game/
├── gallate.yaml
├── text/                # 标准
├── image/               # 标准
├── scripts/             # 标准
├── audio/               # 引擎扩展媒体(语音对白)
├── video/               # 引擎扩展媒体(过场)—— 可选
├── font/                # 引擎扩展媒体(TTF/OTF)
└── portrait/            # 引擎扩展 sub-media
```

这些额外目录是引擎选择;标准 CLI 不要求它们。

## 6.3 布局不变量

无论扩展如何,以下始终成立:

- `gallate.yaml` 是唯一的 Project Target。任何非 init 操作必须存在于 Project Root。
- 标准目录 `text/` 与 `image/` 即使为空也可存在(或在引擎永不接触该媒体时缺席)。
- Pre/post 脚本按惯例放在 `scripts/` 下,但 `gallate.yaml` 中的路径可以是相对 Project Root 的任何位置。

## 6.4 由 `init` 生成

`init` 是产生标准布局的规范方式。见 [07-init.md](./07-init.md)。

`init` 创建的项目必须至少包含:

```text
my-game/
└── gallate.yaml           # 最低要求;标准目录可选
```

`init` **可**创建标准目录;这是引擎特定的。用户**可**手动添加。

## 6.5 用户编辑时

用户编辑项目时,以下操作自由:

- 添加新目录。
- 删除不用的标准目录。
- 把 pre/post 脚本移到其他位置(只需更新 `gallate.yaml`)。

CLI **不得**假定 `gallate.yaml` 之外的任何目录存在。它**必须**在写入输出时按需创建缺失的目录。

## 6.6 与 media 的关系

标准目录映射到标准 media:

```text
text/   ↔  -t
image/  ↔  -i
```

引擎扩展 media 可有自己的目录:

```text
audio/   ↔  -a   (当引擎暴露 audio 时)
video/   ↔  -v   (当引擎暴露 video 时)
font/    ↔  --engine.font   (典型;不是 media flag)
```

但这是**惯例,不是规则**。CLI 决定每个 media 的输出位置。引擎**可**把所有 media 摊到一个输出目录,或使用更深的逐资源树。

## 6.7 各处放什么 —— 概要

```text
my-game/                            (Project Root)
├── gallate.yaml                    (Project Target,必填)
├── text/  image/                   (标准媒体目录,可选)
├── audio/  video/  font/           (引擎扩展目录,可选)
├── scripts/                        (惯例存放 pre/post 脚本)
└── <engine-extension dirs>/        (引擎特定,可选)
```

标准 CLI 必须接受满足前两行的任何项目;引擎**可**添加更多。