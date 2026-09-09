# 10. 配置

> 状态:**规范性**。定义 Wrapper 如何把 `gallate.yaml` 转成 GCWP 操作请求。

## 两层分明

```text
gallate.yaml   →  项目配置          (用户面对)
                  "我想对这个项目做什么"

GCWP request   →  运行时通信        (Wrapper ↔ CLI)
                  "已解析的、机器就绪的指令"
```

CLI 永远看不到原始 `gallate.yaml`。Wrapper 做解析,发扁平请求。

## 转换管线

```text
gallate.yaml
       ↓
    Wrapper
       ↓
    Request (over stdin)
       ↓
      CLI
```

Wrapper 责任:

1. 加载 `gallate.yaml`
2. 相对于 Project Root 解析路径
3. 应用 CLI `--engine.*` 覆盖
4. 构造 GCWP request
5. 发给 CLI

CLI 责任:

1. 接收 request
2. 执行
3. 发 events / statistics
4. exit

## gallate.yaml 字段到 GCWP 的映射

完整 `gallate.yaml` schema 在 [`Documents/通用行为规范.txt`](https://github.com/grill-glitch/Documents)。GCWP 只消费子集:

| `gallate.yaml` 字段 | GCWP request 字段 |
| --- | --- |
| `input` | `request.input` |
| `output` | `request.output` |
| `ignore` | `request.ignore` |
| `scripts.pre / post` | 由 Wrapper 处理,不进 GCWP |
| `engine.*` | 摊平到 `request.options` |
| `wrapper` | CLI 选择(决定 spawn 哪个可执行) |

## 路径解析

请求中所有路径在发出前都已解析:

```text
相对路径   → 相对于 gallate.yaml Project Root 解析
绝对路径   → 原样使用
```

例:

```yaml
# gallate.yaml
input: ./game.pfs
```

变成

```yaml
# GCWP request
input:
  - path: ./game.pfs       # 仍相对
    kind: file
```

CLI 仍需自行解析路径,但沿用同一约定。这避免 CLI 耦合到特定调用目录。

## Wrapper 作为翻译器

```python
# Wrapper 翻译器伪代码

def translate(yaml_path, cli_overrides):
    project = load_gallate_yaml(yaml_path)
    project_root = dirname(yaml_path)

    request = {
        "type": "request",
        "id": generate_id(),
        "operation": project["operation"],  # 来自 --operation
        "input": resolve_paths(project["input"], project_root),
        "output": resolve_paths(project["output"], project_root),
        "ignore": project.get("ignore", []),
        "options": merge_engine_options(project["engine"], cli_overrides),
    }

    return request
```

CLI 实现**不得**依赖此伪代码;这是给 Wrapper 作者看的。

## Script 处理

pre/post scripts 写在 `gallate.yaml`,属于 **Wrapper** 的事:

```yaml
scripts:
  pre:
    - ./scripts/unpack.py
  post:
    - ./scripts/repack.py
```

Wrapper 在 CLI 操作前后运行它们,CLI 看不见。

## Project Root 与 CLI 工作目录

CLI 工作目录默认为 gallate.yaml Project Root,**不是** Shell 当前目录。这让操作跨机器可复现。

见 [11-进程.md § Working Directory](./11-process.md)。

## CLI 不接收什么

CLI 永远不接收:

- `gallate.yaml` 本身
- Script 定义
- TM / glossary 数据
- 任何 OmegaT 内部数据

CLI 只接收**已解析的** GCWP request。这是协议与引擎无关的根因。