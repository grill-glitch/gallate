# 02. CLI 语法

> 状态:**规范性**。gallate CLI 必须接受的精确命令行语法。

## 命令语法

```text
tool [operation][media] project [options]
```

其中:

```text
operation  = e | i                必填(其一)
media      = (t|i|a|v)*          可选,任意子集
project    = gallate.yaml 路径    必填,位置参数
options    = 零或多个 flag        见 09-std-flags.md
```

`tool` 是占位符;每个 CLI 用自己的二进制名(`artemis-tool`、`pfs-tool` 等)。

`project` 必须指向 `gallate.yaml`。路径是位置参数;CLI **不得**在当前目录里找。

## Operation + Media 简写

operation flag 是 `-e` 或 `-i`;标准 media flag 是 `-t` (text) 和 `-i` (image),直接追加。media flag 之间没有分隔符:

```text
-et     = 提取文本
-ei     = 提取图片
-eti    = 提取文本 + 图片
```

引擎扩展 media(`-a` 音频、`-v` 视频等)在**引擎决定暴露它们时**以同样方式追加:

```text
-ea     = 提取音频(引擎扩展 media,仅在引擎暴露时存在)
-ev     = 提取视频(引擎扩展 media,仅在引擎暴露时存在)
-etiav  = 提取引擎支持的全部(仅暴露 audio+video 的引擎可用)
```

operation 与 media flag 形成**单个 flag token**,没有分隔符。同一 token 中 media flag 的顺序无意义(都存在时)。当 audio 是扩展 media 时,不要用 `-t` 和 `-i` 的位置组合改变含义 —— 顺序对集合仍无意义,但 flag 字母必须是引擎实际暴露的那些。

### 示例

```bash
tool -e ./gallate.yaml         # 用项目默认 media 提取
tool -et ./gallate.yaml        # 只提取文本
tool -etiav ./gallate.yaml     # 提取全部(仅暴露 audio+video 的引擎可用)

tool -i ./gallate.yaml         # 用项目默认 media 注入
tool -it ./gallate.yaml        # 只注入文本
tool -itai ./gallate.yaml      # 注入文本 + 音频 + 图片(仅当引擎暴露 -a)
```

## Project Target

位置参数是 `gallate.yaml` 的路径:

```bash
tool -e ./gallate.yaml
tool -e ./projects/gamelate.yaml
tool -e /absolute/path/to/gallate.yaml
tool -e ../sibling-project/gallate.yaml
```

如果位置参数不指向可读的 `gallate.yaml`,CLI **必须**拒绝执行。(部分 CLI 可接受 `gallate.yml` 等扩展名;这是引擎特定的,非标准化。)

## 标准 options

除 operation/media 简写外,gallate CLI 接受以下标准长 flag:

```text
--output PATH       覆盖 output 目的地(文件或目录)
--ignore PATTERN    添加临时 ignore 模式(可重复)
--dry-run           仅计划,不执行
--force             绕过安全检查(目前用于:init 覆盖)
-v / --verbose      增加诊断信息(可重复:-vv)
-vv                 最详细
-q / --quiet        减少非必要输出
--engine.KEY=VALUE  引擎扩展选项
```

media 短 flag(`-t`、`-i`,以及引擎暴露的扩展 `-a` / `-v`)是 operation flag 的一部分,**不是**独立 option。完整语义见 [09-std-flags.md](./09-std-flags.md)。

## 帮助与版本

标准:

```bash
tool --help
tool --version
```

`--version` 应打印 CLI 版本(从 `manifest.version`,见 [协议层 § Manifest](../../protocol/03-discovery.md#manifest))、所遵循的协议版本以及它包装的引擎 id。精确格式由引擎决定;**最低要求**是 CLI 版本字符串。

`--help` 应把选项分到两个标题下:

```text
Standard Options:
  -e, -i                  operations
  -t, -i                  media
  --output, --ignore,
  --dry-run, -v, -q,
  --force
  --engine.KEY=VALUE

Engine Options:
  (engine-specific options listed here)
```

引擎选项必须在单独标题下,以便用户区分标准选项与引擎特定选项。

## 必须接受的调用

以下调用必须都能解析:

```bash
tool -e ./gallate.yaml
tool -e ./gallate.yaml --output ./out/
tool -et ./gallate.yaml --ignore "*.tmp" --ignore "cache/"
tool -i ./gallate.yaml --dry-run
tool -etiav ./gallate.yaml -vv -q   # 等同于 -vv;-q 按"最后胜出"规则胜出
```

CLI **可**接受额外的非标准长 flag,但**不得**用不同语义复用标准 flag 名。