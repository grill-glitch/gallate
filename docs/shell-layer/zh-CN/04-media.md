# 04. 媒体

> 状态:**规范性**。定义标准媒体标识符、引擎扩展媒体的规则,以及 Sub-Media 子分类机制。

## 4.1 标准媒体

只有两种媒体是**标准**:每个 gallate CLI 都必须能声明支持它们,Wrapper 可视它们为 baseline。

| Flag | 名称    | 说明                                |
| ---- | ------- | ------------------------------------------ |
| `-t` | `text`  | 文本、本地化字符串、文本资源    |
| `-i` | `image` | 图片、纹理、插图等     |

`text` 和 `image` 是**标准 baseline**。纯文本引擎可以省略 `image`;无文本引擎不是合法 gallate CLI。

## 4.2 引擎扩展媒体

Audio、video、fonts 以及任何超出 text/image 的资源类型都是**引擎扩展媒体**。由 CLI 定义;标准规范不要求任何引擎实现它们。

示例:

```text
audio
  voice      # 语音对白
  bgm      # 背景音乐
  sfx      # 短音效

video
  cutscene   # 游戏内过场
  cinematic  # 电影化镜头
  opening    # 片头/片尾

font         # 字体(TTF、OTF、字形表)
```

引擎暴露这些时,它们在 Shell 层获得同样的 flag 待遇:

```text
-a          = 音频(引擎决定是单个 audio 媒体还是 audio sub-media;见 4.3)
-v          = 视频
--engine.font=...      # font 通常不是 media flag;见下
```

### 规则

1. 扩展媒体标识符必须使用引擎命名空间 —— 单引擎 CLI 用裸 `font`,跨 CLI 共享引擎名时用 `artemis.font` 等。
2. CLI 必须在 `manifest` / `features` 文档中声明每个扩展媒体,以便 Wrapper 知道。
3. 标准 CLI 不得识别引擎未声明的任何扩展媒体。
4. 引擎**可**暴露 `-a` / `-v` flag,也可不暴露。不暴露时,引擎 sub-media 只能通过 `--engine.*.includes` Sub-Media 机制访问(见 4.3)。
5. `font` 通常作为引擎选项(`--engine.font=…`)处理,因为它通常与文本一起处理。如果引擎架构需要,也可作为 media。

### 为何 audio / video 不是标准

大多数游戏引擎都有文本和图片资源。Audio、video、fonts 差异巨大:ASCII 冒险游戏三者全无;视觉小说有 voice 但无 video;3D RPG 三者皆有,还有字字形表。强制所有 CLI 宣传四种 media 而其中三分之二在多数引擎中并不存在,是不不诚实的。把 text/image 视作标准、其余视作扩展,让每个 CLI 准确地声明它支持什么,无需扭曲。

## 4.3 Sub-Media

CLI 可以为任何 media(标准或扩展)定义**sub-media**。Sub-media 区分同一资源类型的不同*种类*。

示例:

```text
text
  ├── dialog       # 对话文本
  ├── menu         # 菜单选项
  └── hardcoded    # 嵌入脚本或二进制的字符串

image
  ├── background   # 背景图
  ├── portrait     # 立绘
  ├── portrait_diff  # 立绘差分(表情、姿势)
  └── ui           # UI 贴图

audio
  ├── voice        # 语音对白
  ├── bgm          # 背景音乐
  └── sfx          # 短音效

video
  ├── cutscene     # 游戏内过场
  ├── cinematic    # 电影化镜头
  └── opening      # 片头/片尾
```

### Shell 形式

```bash
# Include(白名单)—— 只处理列出的 sub-media
tool -et ./gallate.yaml \
  --engine.text.includes=hardcoded

tool -ei ./gallate.yaml \
  --engine.image.includes=portrait_diff

tool -ea ./gallate.yaml \
  --engine.audio.includes=voice,bgm

# Exclude(减法)—— 从 includes 集合中移除
tool -ei ./gallate.yaml \
  --engine.image.includes=portrait \
  --engine.image.excludes=portrait_diff
```

### YAML 形式(`gallate.yaml`)

```yaml
engine:
  text:
    includes:
      - dialog
      - menu
      - hardcoded
    excludes:
      - debug_log

  image:
    includes:
      - background
      - portrait
      - portrait_diff
      - ui
    excludes:
      - ui

  audio:
    includes:
      - voice
      - bgm
      - sfx
    excludes:
      - sfx

  video:
    includes:
      - cutscene
      - cinematic
      - opening
```

### 规则

1. Sub-media 标识符必须由引擎声明(在 `manifest` / `features` / Sub-Media 发现命令中)。
2. 未声明的 sub-media 非法;CLI **必须**拒绝。
3. `includes` 是白名单:未列出的 sub-media 不处理。
4. `excludes` 是减法:从 includes 集合中移除。
5. `excludes` 中出现的项若不在 `includes` 中,即为错误(尽早发现配置错误)。
6. 扩展媒体(如 `font`)也可以用相同语法声明 sub-media。
7. Sub-media **不得**替代标准 media 语义 —— `t` 仍表示"任意文本",而非"特定文本子类型"。

## 4.4 Default media

未给出 media flag 时:

```bash
tool -e ./gallate.yaml
```

CLI 使用项目的 `media:` 列表:

```yaml
# gallate.yaml
media:
  - text
  - image
```

则:

```bash
tool -e ./gallate.yaml
```

等价于:

```bash
tool -eti ./gallate.yaml
```

如果 `media:` 也缺失,则使用引擎默认值(引擎特定,非标准化)。

## 4.5 CLI media 覆盖

显式给出 media flag 时,它们**完全覆盖**YAML media 列表(不是合并)。

```yaml
# gallate.yaml
media:
  - text
  - image
```

```bash
tool -ea ./gallate.yaml
```

只处理 `audio`(前提是此引擎已声明支持 audio 并暴露了 `-a`)。`text` 与 `image` 默认值在此次执行中被忽略。

未暴露 `-a` 的 CLI 在读取 `gallate.yaml` 之前就会以退出码 2(invalid CLI usage)拒绝 `-ea`。

## 4.6 引擎裁剪媒体

引擎不必支持它已声明的每个媒体。纯文本引擎只声明 `text`;视觉小说声明 `text` + `image` + `audio` 但无 `video`。引擎在[协议层 features](../../protocol/03-discovery.md#features) 文档中记录支持的子集:

```yaml
resources:
  text: true
  image: true
  audio: true
  video: false
```

当用户调用引擎不支持的媒体:

```bash
artemis-tool -ev ./gallate.yaml
```

CLI **必须**报错(不是**静默跳过**):

```text
Error: media 'video' is not supported by this engine.
```

退出码:6(`Unsupported Media`)。

flag 字母保留其身份(`-a` 音频、`-v` 视频等,仅当引擎选择暴露时)。引擎选择在 Shell 层不暴露时,flag 不会出现在 `tool --help` 中。