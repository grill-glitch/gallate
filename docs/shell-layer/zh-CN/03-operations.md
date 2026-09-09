# 03. 操作

> 状态:**规范性**。定义两个标准操作以及 media flag 与它们的组合方式。

## 3.1 Extract

```text
-e
```

含义:

> 读取项目定义的输入资源,产出项目定义的翻译资产。

```bash
tool -et ./gallate.yaml        # 提取文本
tool -etiav ./gallate.yaml     # 提取全部(仅当引擎暴露 audio+video)
```

如果未给出 media flag,则使用项目的 `media:` 列表。见 [04-media.md § Default Media](./04-media.md#default-media)。

## 3.2 Inject

```text
-i
```

含义:

> 读取项目定义的已翻译资产,按 Output 规则写回项目定义的输入资源,产出结果。

```bash
tool -it ./gallate.yaml        # 注入文本
tool -itai ./gallate.yaml     # 注入文本 + 音频 + 图片(仅当引擎暴露 -a)
```

## 3.3 Operation × Media 矩阵

两个操作与标准 media flag 完全正交。引擎扩展 media 在 [04-media.md](./04-media.md) 中单独列出。

```text
        text   image
-e      ✓      ✓
-i      ✓      ✓
```

标准 media 是 `text` / `image`,由 `-t` / `-i` flag 标识。`audio` 与 `video` 是引擎扩展 media —— 引擎暴露时它们可能以 `-a` / `-v` 形式出现在 CLI 上,但**不**是标准化的。

## 3.4 必需的标准操作

每个 gallate CLI **必须**至少支持 `-e`(extract)。`-i`(inject)强烈推荐;某些只读 extractor 可能不支持。

引擎可以通过 [engine-extension 机制](./08-engine-extensions.md) 增加额外操作,但 `-e` 和 `-i` 保持标准语义。

## 3.5 无 media 的操作

```bash
tool -e ./gallate.yaml
```

使用项目的 `media:` 列表。见 [04-media.md § Default Media](./04-media.md#default-media)。

如果 `media:` 也缺失,则使用引擎默认值。引擎默认值是引擎特定的,非标准化。

## 3.6 Media 顺序无意义

```bash
tool -et ./gallate.yaml
tool -eit ./gallate.yaml
tool -etiv ./gallate.yaml
tool -eitav ./gallate.yaml
```

四者提取的 media 集合完全相同。CLI 必须同等对待。

## 3.7 交叉引用

从 Shell 层调用到 GCWP 请求的映射详见
[协议层 § Configuration](../../protocol/10-configuration.md)。Wrapper(若存在)处理这种翻译;直接调用的 CLI 内部自己做翻译。