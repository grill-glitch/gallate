# 08. 引擎扩展

> 状态:**规范性**。定义 CLI 如何在标准 Shell 层行为之上扩展而不破坏它。

## 8.1 什么是引擎扩展

CLI 在标准 Shell 层行为之外添加的任何东西:

- 新的 `--engine.*` 选项
- 新的媒体标识符(audio、video、font 等)
- 标准或扩展媒体下的 Sub-Media
- `-e` / `-i` 之外的新操作(罕见)

兼容的 CLI 可加以上任何项。必须放在清晰的引擎命名空间下,且不得重定义标准行为。

## 8.2 命名约定

引擎扩展选项使用 `--engine.KEY[.SUBKEY]=VALUE` 形式:

```bash
artemis-tool \
  -et ./gallate.yaml \
  --engine.text-encoding=shift-jis

pfs-tool \
  -i ./gallate.yaml \
  --engine.rebuild-index
```

规则:

- 引擎选项键是任意字符串;引擎决定 schema。
- `engine.` 前缀保留给引擎扩展。
- 标准 CLI **不**解释 `--engine.*` 下的任何键。原样传递。
- 标准 CLI 必须把引擎选项放在帮助的独立标题下 —— 见 [02-cli-grammar.md § Help and version](./02-cli-grammar.md#help-and-version)。

## 8.3 引擎媒体(audio / video / font / ...)

标准媒体集合只有 `text` 与 `image`。其他都是引擎扩展。完整分类见 [04-media.md](./04-media.md)。

引擎暴露 audio/video 时,通常使用:

```bash
--engine.audio.includes=voice
--engine.video.includes=cutscene
--engine.font.subset=true
```

具体键由引擎定义。引擎**也可**将 audio/video 暴露为 Shell 层 flag(`-a` / `-v`)—— 见 [04-media.md § 引擎扩展媒体](./04-media.md#引擎扩展媒体)。

## 8.4 Sub-Media

Sub-media(`text.hardcoded`、`image.portrait_diff` 等)通过 `--engine.<media>.includes` 与 `--engine.<media>.excludes` 配置。完整语法与语义见 [04-media.md § Sub-Media](./04-media.md#sub-media)。

机制对标准与扩展媒体同样适用 —— `--engine.audio.includes=voice` 对任何声明了 `audio` 与 `voice` sub-media 的引擎都合法。

## 8.5 `gallate.yaml` 中的引擎选项

引擎选项也在 YAML 的 `engine:` 下:

```yaml
engine:
  text_encoding: utf-8
  rebuild_index: true

  text:
    includes:
      - dialog
      - menu
      - hardcoded
    excludes:
      - debug_log

  audio:
    includes:
      - voice
    excludes:
      - bgm
```

标准 CLI 忽略这些。引擎 wrapper 读取。同一优先级规则适用(CLI > YAML > 引擎默认)。

## 8.6 引擎扩展的硬规则

1. **不得修改标准参数语义。** `-e` 仍是 `-e`(extract)。`-t` 仍是 `-t`(text)。`--output` 仍是 `--output`。
2. **不得重定义标准参数。** 不要发明与 `--output` 语义冲突的 `--output-dir`。
3. **使用引擎命名空间。** 每个新 flag 都带 `--engine.` 前缀。
4. **文档分开。** `tool --help` 必须先列标准选项,再单独的"Engine Options"标题。

违反任何一条都是合同违约。Wrapper 依赖标准 CLI 表面保持稳定。

## 8.7 帮助输出约定

```text
Standard Options:
   -e, -i                  operations
   -t, -i                  standard media
   --output, --ignore, --dry-run,
   --force, -v, -q

Engine Options (artemis):
   --engine.text-encoding=SHIFT-JIS|UTF-8|...
   --engine.rebuild-index[=true]
   --engine.text.includes=LIST
   --engine.image.excludes=LIST
```

"Engine Options"标题必须包含引擎 id(从 [manifest](../../protocol/03-discovery.md#manifest) 获取),以便用户知道这些选项属于哪个引擎。Wrapper 可在 UI 中分开呈现这个列表。