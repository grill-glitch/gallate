# 13. 一致性

> 状态:**规范性**。定义三个一致性等级,实现者挑目标层级,Wrapper 作者据此判定能驱动哪些 CLI。

CLI 必须通过 `features` 文档声明其等级。

## 等级概览

```text
Basic      manifest + features + 一个操作 + exit codes
           → 能回答"你是什么、能做什么、跑一次活"

Standard   Basic + events + statistics + validation
           → 能驱动真正的 OmegaT 工作流

Full       Standard + cancellation + status 流式 + diagnostics
           → 能驱动交互式、可取消的 Wrapper UI
```

## Basic

### 必选

- Manifest
- Features
- 至少一个操作(`extract` / `inject` / `build` / `unpack` / `repack`,或引擎扩展名)
- 标准 exit codes
- Operation Request 解析
- stdout / stderr 分离(标准输出不得含自由文本)

### features 必须为 true

```yaml
operations:
  extract: true   # 或任意一个标准 / 引擎扩展操作
```

### 本层可选

- `started` / `completed` 之外的事件
- Statistics
- 验证规则
- 取消
- 状态查询

### 范例

[`examples/minimal-cli/`](../../examples/minimal-cli/) 实现 Basic。

```bash
$ minimal-cli manifest --yaml
$ minimal-cli features --yaml
$ minimal-cli extract ./game.pfs --yaml
```

## Standard

### 必选

- Basic 全部
- 至少发 `started` / `progress` / `file` / `completed` 事件流
- Statistics 输出(`completed` event 携带,或单独 `statistics` event)
- 至少一种 validation 规则(regex / placeholder / constraint 之一),通过 `cli validation --yaml`

### features 必须为 true

```yaml
runtime:
  events: true
  statistics: true
validation:
  regex: true       # regex / placeholder / constraint 至少一个
```

### 本层可选

- 取消
- 状态查询
- 全部 validation 类型

### Wrapper 假设

支持 Standard 的 Wrapper 必须能在不 inspect `id` 的前提下驱动任何 Standard CLI。

## Full

### 必选

- Standard 全部
- 通过 `cancel` 命令支持取消
- 通过 `cli status --yaml` 支持状态查询
- 全部 validation rule 类型
- 标准 error code(或文档中说明的引擎等价物)
- stderr 诊断流(人类可读进度、警告)

### features 必须为 true

```yaml
runtime:
  events: true
  status: true
  statistics: true
  cancellation: true
validation:
  regex: true
  placeholder: true
  constraint: true
```

### Wrapper 假设

支持 Full 的 Wrapper 必须能驱动任何 Full CLI,包括交互式取消与实时状态轮询。

## 等级如何叠加

| 等级 | Wrapper 要求 | CLI 要求 |
| --- | --- | --- |
| Basic | 启动一次 CLI,读 exit code | 实现 Basic |
| Standard | 驱动 OmegaT 循环带进度 | 实现 Standard |
| Full | 驱动交互式 UI 带取消 | 实现 Full |

支持等级 X 的 Wrapper 也必须能驱动所有等级 Y < X 的 CLI(只是不调用额外能力)。

## 如何选等级

```text
裸提取脚本 → Basic
引擎的生产 CLI → Standard
交互式 Wrapper 用的 CLI → Full
```

CLI 至少应瞄准 Standard,除非用例严格脚本化。

## 一致性声明

CLI 文档必须声明其等级:

```text
本 CLI 符合 GCWP 1.0 (Standard)。
```

声明应与 `features` 文档的真相一致。

## 测试套件

参考测试夹具(规划中)将覆盖:

```text
Basic     握手 + 一次操作 + exit code 矩阵
Standard  事件流 + statistics + 一种 validation rule
Full      取消 + status 流式
```

在夹具落地前,作者应自测对照两个 worked examples:

```text
examples/minimal-cli/    ← 对应 Basic
examples/full-cli/       ← 对应 Full
```