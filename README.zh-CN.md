# gallate(中文版)

**Gallate** —— 游戏本地化工作流中 CLI 与 Wrapper 通信的中立规范集合。

> ⚠️ 本仓库是 **规范仓库**,不是可运行的实现。
> 各种实现(Wrapper / CLI / OmegaT 插件)分布在各自独立的仓库。

---

## 什么是 gallate?

`gallate`(原名 `gamelate`)定义了两份契约:

| 契约 | 层级 | 受众 |
| --- | --- | --- |
| **GCWP**(Gamelate CLI–Wrapper Protocol) | 进程 / IPC 层 | Wrapper 与 CLI 实现者 |
| **gallate.yaml** 规范 | Shell / 项目配置层 | CLI 作者与终端用户 |

本仓库核心是 **GCWP**,规定通用 **Wrapper**(OmegaT 的唯一集成点)如何与大量独立 **CLI** 工具通信,每个 CLI 面向一个具体游戏引擎、引擎家族或资源格式。

```text
                OmegaT
                  │
                  │ Wrapper API
                  ▼
                Wrapper
                  │
                  │ GCWP
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    CLI #1     CLI #2     CLI #N
    Artemis    Ren'Py     Unity ...
```

> **OmegaT 只集成 Wrapper。CLI 数量不受限制。**
> 增加第 100 个引擎,OmegaT 与 Wrapper 都不需修改 —— 只需新增一个遵守 GCWP 的 CLI。

配套的 **`gallate.yaml`** 规范(CLI Shell 层行为契约、项目初始化、媒体模型、脚本模型、退出码等)独立维护于
[`Documents/通用行为规范.txt`](https://github.com/grill-glitch/Documents)
仓库。

---

## 仓库结构

```text
gallate/
├── README.md                  # 英文版入口
├── README.zh-CN.md            # 本文件(中文)
├── LICENSE                     # CC BY-SA 4.0
├── CHANGELOG.md               # 协议版本历史
│
├── docs/protocol/
│   ├── README.md              # 协议目录
│   ├── 00-glossary.md
│   ├── 01-architecture.md
│   ├── 02-core-protocol.md
│   ├── 03-discovery.md
│   ├── 04-operations.md
│   ├── 05-events.md
│   ├── 06-status.md
│   ├── 07-statistics.md
│   ├── 08-validation.md
│   ├── 09-diagnostics.md
│   ├── 10-configuration.md
│   ├── 11-process.md
│   ├── 12-compatibility.md
│   ├── 13-conformance.md
│   └── zh-CN/
│       ├── 00-glossary.md
│       ├── 01-architecture.md
│       ├── …
│       └── 13-conformance.md
│
├── schema/
│   ├── gcwp.schema.json
│   ├── manifest.schema.json
│   ├── features.schema.json
│   ├── request.schema.json
│   ├── response.schema.json
│   ├── event.schema.json
│   ├── status.schema.json
│   ├── statistics.schema.json
│   ├── validation.schema.json
│   └── cancel-command.schema.json
│
└── examples/
    ├── README.md
    ├── minimal-cli/
    │   ├── manifest.yaml
    │   ├── features.yaml
    │   └── extract.jsonl
    └── full-cli/
        ├── manifest.yaml
        ├── features.yaml
        ├── validation.yaml
        ├── extract.jsonl
        ├── inject.jsonl
        ├── build.jsonl
        └── errors.jsonl
```

---

## 三类文档的关系

```text
Markdown    → 解释  "为什么这样设计 / 怎么设计"
JSON Schema → 规定  "到底必须长什么样"
Examples    → 示范  "一段完整可运行的范例"
```

| 制品 | 作者读…… | 作者写…… |
| --- | --- | --- |
| Markdown 规范 | 理解设计意图 | 通过 PR 提建议 |
| JSON Schema | 了解字段要求 | 生成类型 / 代码 |
| Examples | 看完整行为 | 复制作为模板 |

---

## 快速开始:实现一个 Basic CLI

最简可兼容 GCWP 的 CLI 必须提供:

```text
manifest
features
one operation
exit codes
```

具体而言:

```bash
$ cli manifest --yaml
$ cli features --yaml
$ cli extract ./game.pfs --yaml
```

一份完整的 minimal 示例见
[`examples/minimal-cli/`](./examples/minimal-cli/)。

三级兼容等级(Basic / Standard / Full)见
[`docs/protocol/13-conformance.md`](./docs/protocol/13-conformance.md)。

---

## 当前协议版本

```text
name      : gcwp
version   : 1.0
status    : Draft
license   : CC BY-SA 4.0
```

详见 [`CHANGELOG.md`](./CHANGELOG.md)。

---

## 许可证

本规范以
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 发布。

参考实现可自选许可证,但 `schema/` 下定义的 GCWP 线缆格式必须按
[`docs/protocol/12-compatibility.md`](./docs/protocol/12-compatibility.md)
的兼容性规则保持稳定。

---

## 作者

Samuel Flores
<5uniljdst@mozmail.com>

GitHub: [@grill-glitch](https://github.com/grill-glitch)