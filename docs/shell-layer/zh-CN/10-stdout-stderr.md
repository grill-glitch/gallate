# 10. stdout/stderr 与退出码

> 状态:**规范性**。定义 gallate CLI 如何使用 stdout、stderr 和整数退出码。

## 10.1 stdout / stderr 分离

```text
stdout  →  操作结果;机器可读
stderr  →  进度、警告、诊断、错误
```

两条硬规则:

1. **stdout 只含操作结果。** 没有进度条、没有横幅文本、没有 "Extracting…" 消息。
2. **stderr 包含人类想看的一切。** 进度、警告、诊断、错误。

原因:把 CLI 包在脚本或其他工具中时:

```bash
result=$(tool -e ./gallate.yaml -q)
echo "$result"
```

捕获到的输出**不得**被进度消息污染。

## 10.2 stdout 形状

写入 stdout 的结果由引擎决定。CLI 实现决定格式。两种惯例被推荐但不标准化:

- 在 stdout 最后一行打印单一结果路径(便于 `result=$(...)`)
- 引擎特定机器可读输出的结构化 YAML

[GCWP 层](../../protocol/) 是一个完全结构化的变体,在 stdout 上发每个事件的 YAML。Wrapper 驱动 CLI 时使用 GCWP,**不**使用 Shell 层 stdout。两者独立。

## 10.3 退出码

标准退出码 —— 语义**不得**改变:

| Code | 含义                  |
| ---- | ----------------------- |
| 0    | Success                 |
| 1    | General Error           |
| 2    | Invalid CLI Usage       |
| 3    | Invalid Project Configuration |
| 4    | Input Not Found         |
| 5    | Unsupported Operation   |
| 6    | Unsupported Media       |
| 7    | Extraction Failure      |
| 8    | Injection Failure       |
| 9    | Output Failure          |
| 10   | Script Failure          |

引擎扩展**可**使用 >= 11 的 code 作引擎特定失败。标准 0–10 保持其含义。

## 10.4 退出码 vs 事件

对 Shell 层使用而言,退出码**就是**最终结果。与协议层不同,没有并行的事件流。

```text
operation runs
  ↓
exit code N
```

包裹 CLI 的脚本**必须**仅基于退出码处理错误:

```bash
if ! tool -e ./gallate.yaml; then
    case $? in
        4) echo "input not found" ;;
        6) echo "media not supported" ;;
        *) echo "other failure" ;;
    esac
fi
```

Wrapper 驱动的协议层有更多微妙(见 [GCWP § Exit Code vs Event](../../protocol/02-core-protocol.md#exit-code-vs-event)),但 Shell 层保持简单。

## 10.5 In-Place 行为

In-Place 是**输出行为**,不是独立的 CLI 参数。

```text
Input
  ↓
Operation
  ↓
same Input
```

CLI **不得**静默将操作转为 in-place。是否允许 in-place 是引擎特定的;支持它的引擎在 [features](../../protocol/03-discovery.md#features) 文档中声明,并**可**暴露 `--engine.in-place=true` 选项以启用。

如果引擎不支持安全的 in-place 修改,in-place 必须以退出码 9(Output Failure)报错。

## 10.6 Verbose / quiet 与退出码

`-v` / `-vv` / `-q` 改变 CLI 在 stderr 上打印多少。**不得**改变退出码。

verbose 的 dry run 仍以退出码 0 退出(若规划成功)。quiet 的真实操作若失败仍以退出码 1 退出。verbosity 仅是呈现。