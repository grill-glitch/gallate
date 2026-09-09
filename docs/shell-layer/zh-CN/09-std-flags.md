# 09. 标准 flags

> 状态:**规范性**。定义 gallate CLI 必须接受的每个标准长/短 flag。

## 9.1 `--output PATH`

覆盖输出目的地。

```bash
tool -i ./gallate.yaml --output ./game-zh.pfs
```

`--output` 接受文件或目录路径:

```bash
tool -e ./gallate.yaml --output ./extracted/
```

值相对 Project Root 解析,除非是绝对路径。CLI **不得**凭空发明新输出路径 —— 若既无 `--output` 也无 YAML `output:`,则使用引擎默认行为(通常是 in-place 或报错)。

见 [01-overview § Configuration Priority](./01-overview.md#15-configuration-priority)。

## 9.2 `--ignore PATTERN`

添加临时 ignore 模式。可重复。

```bash
tool -e ./gallate.yaml \
  --ignore "*.bak" \
  --ignore "cache2/"
```

模式使用 `.gitignore` 风格 glob:

```text
*        单段通配
**       多段通配
?        单字符
directory/   仅匹配目录
```

CLI 至少必须支持这些。引擎特定扩展允许但不标准化。

### 合并语义

CLI `--ignore` 模式与 YAML `ignore:` 列表**合并**(不是覆盖)。

```yaml
# gallate.yaml
ignore:
  - "*.tmp"
```

```bash
tool -e ./gallate.yaml --ignore "cache/"
```

最终 ignore 集合:`["*.tmp", "cache/"]`。

### 范围

Ignore 适用于**整个资源生命周期**:

```text
Resource Discovery
        ↓
Reading
        ↓
Extraction / Injection
        ↓
Writing
```

任何 ignore 模式匹配的资源都不会被读或写。

## 9.3 `--dry-run`

规划操作但不执行。

```bash
tool -i ./gallate.yaml --dry-run
```

Dry run **可**做:

- 读 `gallate.yaml`
- 解析 input、media、ignore
- 计算规划的 output 路径
- 报告会发生什么

Dry run **不得**:

- 修改游戏资源
- 写任何 output 文件
- 默认执行 pre/post 脚本

CLI 应报告摘要,例如:

```text
Operation : inject
Media     : text,image
Input     : ./game.pfs
Output    : ./game-zh.pfs
Ignored   : 13 resources
```

Wrapper **可**解释 `--dry-run` 以基于 [GCWP statistics](../../protocol/07-statistics.md) 形状驱动自己的预览 UI。

## 9.4 `--force`

绕过安全检查。目前只有一个用例:

```bash
tool init ./projects/my-game --force
```

允许 `init` 覆盖现有 `gallate.yaml`。其他操作忽略 `--force`(没有安全检查可绕),除非引擎在其引擎命名空间下定义。

## 9.5 `-v` / `--verbose`

增加 stderr 上的诊断详细度。可重复:

```text
-v       默认 verbosity
-vv      最详细(引擎内部)
-vvv     保留(引擎扩展如需要)
```

日志级别**不得**改变操作结果。更高级 verbose在 stderr 上显示更多诊断数据;stdout(机器输出)不变。

## 9.6 `-q` / `--quiet`

抑制非必要输出。用于脚本环境:

```bash
result=$(tool -e ./gallate.yaml -q)
```

CLI **仍可**在 stderr 上发警告与错误,但不发进度条或友好横幅。

最后 flag 胜出:`-q -v` ⇒ verbose;`-v -q` ⇒ quiet。

## 9.7 `--engine.KEY=VALUE`

引擎扩展选项。见 [08-engine-extensions.md](./08-engine-extensions.md) 完整语义。示例:

```bash
--engine.text-encoding=utf-8
--engine.rebuild-index=true
--engine.text.includes=dialog,hardcoded
--engine.image.excludes=portrait_diff
```

## 9.8 `--help`

显示帮助并退出。

```text
Standard Options:
   -e, -i                  operations
   -t, -i                  standard media (engine extensions if exposed)
   --output PATH
   --ignore PATTERN
   --dry-run
   --force
   -v, -vv
   -q

Engine Options (artemis):
   (engine-specific)
```

"Engine Options"标题必须包含引擎 id。

## 9.9 `--version`

打印 CLI 版本并退出。

```text
artemis-cli 1.2.0
protocol gcwp 1.0
engine artemis (2.x compatible)
```

最低要求是 CLI 版本字符串。完整格式由引擎决定。

## 9.10 概要表

| Flag                       | 短 | 可重复 | 标准? |
| -------------------------- | ----- | ------- | --------- |
| `--output`                 |       | no      | yes       |
| `--ignore`                 |       | yes     | yes       |
| `--dry-run`                |       | no      | yes       |
| `--force`                  |       | no      | yes       |
| `--verbose`                | `-v` | yes     | yes       |
| `--quiet`                  | `-q` | no      | yes       |
| `--engine.KEY=VALUE`       |       | yes     | yes(form) |
| `--help`                   | `-h`(推荐) | no | yes       |
| `--version`                |       | no      | yes       |

本表之外的 flag 是引擎扩展,必须放在 `--engine.*` 命名空间下,否则不可添加。