# 07. Init

> 状态:**规范性**。定义项目初始化的 `init` 子命令。

## 7.1 用途

`init` 创建并初始化一个标准 gallate 项目。它**不是**资源处理操作 —— 它不读/写游戏数据。

## 7.2 基本形式

```bash
tool init
```

在当前目录创建项目。等于:

```bash
tool init ./
```

指定目标路径:

```bash
tool init ./projects/my-game
```

创建 `./projects/my-game/` 并在里面写 `gallate.yaml`。

## 7.3 选项

| Flag | 用途 |
| --- | --- |
| `--input PATH` | 设置初始 `input:` 值 |
| `--output PATH` | 设置初始 `output:` 值 |
| `--ignore PATTERN` | 添加 ignore 模式(可重复) |
| `--media text,image` | 设置默认 `media:` 列表 |
| `--force` | 覆盖现有 `gallate.yaml` |

## 7.4 生成的配置

`init` 在项目根写 `gallate.yaml`。确切内容取决于传入的 flag:

```bash
tool init ./projects/my-game \
  --input ./game.pfs \
  --output ./game-zh.pfs
```

生成:

```yaml
input: ./game.pfs
output: ./game-zh.pfs
```

带 ignore flags:

```bash
tool init ./projects/my-game \
  --input ./game.pfs \
  --output ./game-zh.pfs \
  --ignore "*.tmp" \
  --ignore "cache/"
```

生成:

```yaml
input: ./game.pfs

ignore:
  - "*.tmp"
  - "cache/"

output: ./game-zh.pfs
```

带 media flags:

```bash
tool init ./projects/my-game \
  --input ./game.pfs \
  --media text,image
```

生成:

```yaml
input: ./game.pfs

media:
  - text
  - image
```

`--media` 可重复;最终 `media:` 列表是去重的并集:

```bash
tool init ./projects/my-game \
  --media text,image \
  --media audio
```

生成 `media: [text, image]`(因为 `audio` 是引擎扩展,`init` 默认仅写标准 baseline —— 见下)。

## 7.5 init 期间的路径解析

传给 `init` 的所有路径相对**最终项目根**解析,而不是 shell 的当前目录。

```bash
tool init ./projects/my-game --input ./game.pfs
```

`./game.pfs` 变为 `projects/my-game/game.pfs`,不是 `<shell-cwd>/game.pfs`。

这让生成的项目可移植 —— 移动项目目录不会引入隐藏的路径不匹配。

## 7.6 init 中的默认 media

如果省略 `--media`,`init` 只写标准 baseline:

```yaml
media:
  - text
  - image
```

引擎扩展 media(`audio`、`video`、`font` 等)没有显式 flag 时**绝不**被 `init` 写入。希望默认包含 audio 的引擎应通过项目初始化后的配置由用户主动启用。

这条规则防止 `init` 对能力说谎 —— `text` 与 `image` 由规范保证;其余取决于引擎。

## 7.7 Force / 覆盖保护

如果目标目录已包含 `gallate.yaml`,`init` 默认**必须**拒绝覆盖:

```text
Error: gallate.yaml already exists in ./projects/my-game.
Use --force to overwrite.
```

带 `--force`,`init` 覆盖现有文件。`--force` 是标准逃生口,只适用于 `init`。

## 7.8 init 创建的项目布局

`init` **必须**创建目标目录并写 `gallate.yaml`。`init` 是否创建 `text/` / `image/` 目录是引擎特定的;标准 CLI **可**创建它们作为空占位符,但**不是必需的**。

引擎扩展目录(`audio/`、`video/`、`font`、...) `init` **绝不**创建 —— 它们只在引擎决定往里写东西时出现,或用户手动创建。

## 7.9 init 不做的事

- 不扫描 input 文件(可能尚不存在)。
- 不预提取任何东西。
- 不验证引擎是否支持声明的 `media:` —— 那是首次 `-e / -i` 时的运行时检查。

## 7.10 示例

创建空项目:

```bash
tool init ./projects/my-game
```

带 input + output:

```bash
tool init ./projects/my-game \
  --input ./game.pfs \
  --output ./game-zh.pfs
```

带全部默认:

```bash
tool init ./projects/my-game \
  --input ./game.pfs \
  --output ./game-zh.pfs \
  --ignore "*.tmp" \
  --ignore "cache/" \
  --media text,image
```

覆盖现有项目:

```bash
tool init ./projects/my-game --force
```