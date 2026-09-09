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

配套的 **`gallate.yaml`** 规范(CLI Shell 层行为契约、项目初始化、媒体模型、脚本模型、退出码等)在两处共同定义:

- 本仓库的 [Shell 层规范](./docs/shell-layer/) 定义项目布局、CLI 语法、`gallate.yaml` 完整 schema。
- 历史参考 [`Documents/通用行为规范.txt`](https://github.com/grill-glitch/Documents) 保留由其提炼出的散文式叙述。

---

## 仓库结构

```text
gallate/
├── README.md                  # 英文版入口
├── README.zh-CN.md            # 本文件(中文)
├── LICENSE                     # CC BY-SA 4.0
├── CHANGELOG.md               # 占位文件(草稿期间无条目)
│
├── docs/
│   ├── protocol/                # GCWP — Wrapper ↔ CLI 进程层
│   │   ├── README.md              # 协议目录
│   │   ├── 00-glossary.md
│   │   ├── 01-architecture.md
│   │   ├── …
│   │   ├── 13-conformance.md
│   │   └── zh-CN/                # 中文版
│   │
│   └── shell-layer/             # Shell / 项目配置层
│       ├── README.md              # shell-layer 目录
│       ├── 00-glossary.md
│       ├── 01-overview.md
│       ├── 02-cli-grammar.md
│       ├── 03-operations.md
│       ├── 04-media.md
│       ├── 05-config-file.md
│       ├── 06-project-structure.md
│       ├── 07-init.md
│       ├── 08-engine-extensions.md
│       ├── 09-std-flags.md
│       ├── 10-stdout-stderr.md
│       ├── 11-conformance.md
│       └── zh-CN/                # 中文版
│
├── schema/                      # GCWP YAML Schemas(JSON Schema draft-07)
│   ├── gcwp.schema.yaml
│   ├── manifest.schema.yaml
│   ├── features.schema.yaml
│   ├── request.schema.yaml
│   ├── response.schema.yaml
│   ├── event.schema.yaml
│   ├── status.schema.yaml
│   ├── status-query.schema.yaml
│   ├── statistics.schema.yaml
│   ├── validation-rules.schema.yaml
│   ├── validation-result.schema.yaml
│   └── cancel-command.schema.yaml
│
├── examples/                    # GCWP IPC trace
│   ├── README.md
│   ├── minimal-cli/
│   │   ├── manifest.yaml
│   │   ├── features.yaml
│   │   └── extract.yaml-stream
│   └── full-cli/
│       ├── manifest.yaml
│       ├── features.yaml
│       ├── validation.yaml
│       ├── validation-result.yaml-stream
│       ├── extract.yaml-stream
│       ├── inject.yaml-stream
│       ├── build.yaml-stream
│       ├── cancel.yaml-stream
│       └── errors.yaml-stream
│
└── shell-layer-examples/        # 项目树示例
    ├── README.md
    ├── minimal-project/
    │   ├── gallate.yaml
    │   ├── text/  image/
    └── full-project/
        ├── gallate.yaml
        ├── engine-options.md
        ├── text/  image/  audio/  video/  font/
        └── scripts/
            ├── unpack.py
            ├── repack.py
            └── .gitignore
```

---

## 三类文档的关系

```text
Markdown        → 解释  "为什么这样设计 / 怎么设计"
YAML Schemas    → 规定  "到底必须长什么样"
Examples        → 示范  "一段完整可运行的范例"
```

| 制品 | 作者读…… | 作者写…… |
| --- | --- | --- |
| Markdown 规范 | 理解设计意图 | 通过 PR 提建议 |
| YAML Schemas(JSON Schema 语义) | 了解字段要求 | 生成类型 / 代码 |
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

## 当前状态

```text
name      : gallate (umbrella: GCWP + Shell layer)
status    : Draft — 版本号在 CHANGELOG.md 按协议条目追踪
license   : CC BY-SA 4.0
```

本仓库仍在活跃起草中。协议/线缆格式版本见 [`CHANGELOG.md`](./CHANGELOG.md);
文档本身没有版本号,跟随仓库 git 历史。

Shell 层(项目布局、CLI 语法、`gallate.yaml`)是 [`docs/shell-layer/`](./docs/shell-layer/)
下的独立文档集。其内容与协议层同步演进。

---

## 许可证

本规范以 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 发布。

参考实现可自选license但 `schema/` 下定义的 GCWP 线缆格式与
`docs/shell-layer/` 下定义的 Shell层语法必须按
[`docs/protocol/12-compatibility.md`](./docs/protocol/12-compatibility.md)
的兼容性规则保持稳定。

---

## 作者

Samuel Flores
<5uniljdst@mozmail.com>

GitHub: [@grill-glitch](https://github.com/grill-glitch)