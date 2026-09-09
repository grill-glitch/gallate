# 04. 操作

> 状态:**规范性**。定义 Wrapper 要求 CLI 执行的工作单元:形状、参数、输入、输出与选项。

## 标准操作

```text
extract       读引擎资源,写翻译资产
inject        读翻译资产,写引擎资源
build         产出最终打包
unpack        打开引擎归档
repack        关闭引擎归档
```

CLI 可支持额外操作。**不得**重定义标准操作名;新增操作必须使用标准列表外的名称。

## 操作请求

Schema:[`schema/request.schema.yaml`](../../schema/request.schema.yaml)。

Wrapper 在 stdin 发一条 `request`:

```yaml
type: request
id: 01HXYZABCDEF
operation: extract

input:
  - ./game.pfs

output:
  - ./translation

options: {}
```

### 字段

| 字段 | 必填 | 备注 |
| --- | --- | --- |
| `type` | ✓ | 必须为 `request` |
| `id` | ✓ | 操作 ID,关联所有事件 / 状态 / 最终退出 |
| `operation` | ✓ | 标准名之一,或引擎扩展名 |
| `input` | 可选 | 路径列表(字符串或结构化对象) |
| `output` | 可选 | 路径列表,同 input |
| `options` | 可选 | 操作级结构化配置 |
| `ignore` | 可选 | 忽略模式列表 |

`id` 对 CLI 不透明,但贯穿事件流的唯一关联键。Wrapper 应使用 ULID 或 UUIDv7。

## 输入 / 输出

路径可为纯字符串或结构化对象:

```yaml
# 纯字符串(CLI 推断 file / directory)
- ./game.pfs

# 结构化(显式 kind)
- path: ./game.pfs
  kind: file

- path: ./data
  kind: directory
```

CLI 必须能同时处理文件和目录。Wrapper 在歧义时应使用结构化形式。

### 路径解析

```text
相对路径   → 相对于 Project Root 解析
绝对路径   → 原样使用
```

见 [10-配置.md § 路径解析](./10-configuration.md)。

## Ignore

Ignore 规则属于**操作配置**,不属于 CLI 自身。

```yaml
ignore:
  - "**/*.tmp"
  - "**/cache/**"
  - system.dat
```

glob 实现细节写在 CLI 文档。GCWP 不固定 glob 风味。

Wrapper **不得**静默修改 ignore 列表。见
[`Documents/通用行为规范.txt § Ignore`](https://github.com/grill-glitch/Documents)。

## Options

引擎专有选项放在 `options` 下,使用引擎命名空间:

```yaml
options:
  artemis.text_encoding: shift-jis
  artemis.rebuild_index: true
```

保留命名空间:

- `gallate.*` —— Wrapper 自身未来使用
- `gcwp.*` —— 协议级选项未来使用

## 引擎扩展操作

CLI 可定义引擎专有操作:

```text
analyze
list
verify
patch
```

Wrapper 遇到未知操作类型必须**在启动 CLI 前**拒绝。CLI 收到未知操作必须以退出码 `4`(`unsupported operation`)拒绝。

## 操作生命周期

一次请求最终落到三种状态之一:

```text
completed      成功
failed         退出码 != 0
cancelled      通过 stdin 命令
```

进程层面见 [11-进程.md](./11-process.md)。