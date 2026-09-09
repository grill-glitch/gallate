# 01. 概述

> 状态:**规范性**。定义 Shell 层三大设计原则。

## 1.1 Unix 哲学

gallate CLI 专注于资源处理:

```text
extract    (-e)
inject     (-i)
```

CLI **不**负责:

- 翻译
- 审校
- 术语管理
- 翻译记忆
- AI 翻译

这些功能由独立工具/处理器(OmegaT、MT 管线、术语库等)实现。gallate CLI 是引擎与这些工具之间的桥梁。

## 1.2 引擎专一

一个 CLI 面向**一个**具体引擎、引擎家族或资源格式:

```text
artemis-tool
pfs-tool
renpy-tool
unity-tool
```

不同 CLI 可以有截然不同的实现,但**必须**遵守相同的 Shell 层行为契约。

这与[协议层原则](../../protocol/01-architecture.md#engine-cli)互补:Shell 层的规则是"一个 CLI 一个引擎";协议层的规则是"Wrapper 通过 GCWP 与它们中任何一个对话"。

## 1.3 项目中心

标准 Project Target 是 `gallate.yaml`。CLI 不直接接受游戏文件或游戏目录。

### 合法

```bash
tool -e ./gallate.yaml
```

### 非法

```bash
tool -e ./game.pfs
tool -e ./www/
```

游戏文件、目录与资源位置均由 `gallate.yaml` 描述。

这给出一个稳定层:

```text
CLI Interface
    ↓
稳定

Project Configuration
    ↓
可变
```

项目内部布局可改,CLI 调用方式永不需要改。

## 1.4 配置 vs 操作

`gallate.yaml` 描述:

> 本项目的**默认**行为。

CLI flags 描述:

> 本次执行的**覆盖**。

CLI 覆盖项目配置,但默认不修改它。

## 1.5 配置优先级

```text
CLI
 ↓
gallate.yaml
 ↓
Engine Default
```

CLI 显式参数优先于 YAML;YAML 优先于引擎默认值。

**不同配置项有不同的覆盖语义。** 不要统一处理:

```text
Media       CLI → 完全覆盖 YAML
Ignore      CLI → 与 YAML 合并
Output      CLI → 覆盖 YAML
Scripts     CLI → 无法覆盖 YAML(pre/post 仅在 YAML)
```

详见各章节:

- Media:[04-media.md](./04-media.md)
- Ignore:[09-std-flags.md § Ignore](./09-std-flags.md#ignore)
- Output:[09-std-flags.md § Output](./09-std-flags.md#output)
- Scripts:[05-config-file.md § scripts](./05-config-file.md#scripts)

## 1.6 本规范是/不是

本规范定义:

> **CLI 行为契约** —— gallate CLI 在 shell 下被调用时做什么。

本规范**不**定义:

> 任何具体游戏引擎的内部实现。

那是引擎 wrapper 的事。