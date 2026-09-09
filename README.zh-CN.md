# gallate(中文版)

<p align="center">
  <img src="./docs/assets/gallate-logo.png" alt="gallate logo" width="640">
</p>

**[English](./README.md) | [简体中文](./README.zh-CN.md)**

**Gallate** —— 游戏本地化工作流中 CLI 与 Wrapper 通信的中立规范集合。

> ⚠️ **草稿状态 — 可能出现破坏性变更。**
> 规范仍在活跃起草中。在 1.0 发布之前,字段名、schema 形状与协议行为
> **随时可能变更**,不再另行通知。依赖本仓库时请 pin 到 commit hash,
> 而非版本号。

---

## 项目哲学

> **一个通用 Wrapper,连接 OmegaT 与无数独立 CLI;标准化协议,而不是标准化实现。**

`gallate` 不是"又一个翻译工具"。它是**协议层** —— 让一个 OmegaT 集成点
能与任意数量的、面向具体引擎的独立 CLI 对话,而 OmegaT、Wrapper、CLI
彼此都不需要知道对方的存在。

```text
                OmegaT
                  │
                  │  (一个 Wrapper API)
                  ▼
                Wrapper
                  │
                  │  GCWP
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    CLI #1     CLI #2     CLI #N
    Artemis    Ren'Py     Unity ...
       │          │          │
    Engine     Engine     Engine
```

### 为什么重要

1. **高度解耦。** OmegaT、Wrapper、每个 CLI、每个游戏引擎各自独立演进。
   替换任何一层都无需重写其他层。
2. **真正的 Unix 哲学。** 每个 CLI 都是独立、聚焦的工具。能脱离 OmegaT
   单独运行,也能从 shell、CI、GUI 调用 —— 同一份二进制,同一套 flag。
3. **无限扩展能力。** 一个 Wrapper,*N* 个 CLI,数量无上限:

   ```text
   Wrapper
   ├── CLI A
   ├── CLI B
   ├── CLI C
   └── ...
   ```

   增加第 100 个引擎,Wrapper 不需要改 —— 只要新 CLI 遵循 GCWP。
4. **协议优先,而不是语言优先。** CLI 不必是 Rust、Go 或 Python。
   遵循 GCWP 即可加入生态。
5. **Wrapper 负责部署。** Wrapper 发现、下载、验证、更新 CLI。
   用户无需手动配置各引擎的运行时。
6. **OmegaT 只是一个消费者。** Wrapper 不把翻译逻辑绑死在 OmegaT;
   CLI 不依赖 OmegaT。任何未来的 GUI、CLI 或自动化流水线
   都可以驱动同样的 CLI。
7. **生态可独立演进。** CLI 按自己节奏发版,Wrapper 独立更新,OmegaT 独立升级
   —— 没有 co-release 压力。
8. **能力动态发现。** `manifest`、`features`、`status`、`statistics` —
   Wrapper 询问 CLI 能做什么,而不是假设。

最终是一个**小而稳定的协议**核心,让许多专业工具自由组合 —— 而
不是"大而美的翻译软件",让所有人都去 fork。

---

## 什么是 gallate?

`gallate`(原名 `gamelate`)定义两份契约:

| 契约 | 层级 | 受众 |
| --- | --- | --- |
| **GCWP**(Gamelate CLI–Wrapper Protocol) | 进程 / IPC 层 | Wrapper 与 CLI 实现者 |
| **`gallate.yaml`** 规范 | Shell / 项目配置层 | CLI 作者与终端用户 |
| **`.meta.json`**(派生项目元数据) | 项目状态 | CLI(写) / Wrapper(读) |

`gallate.yaml` 是**意图** —— 项目"应该"做什么;`.meta.json` 是**状态** ——
项目"实际"做了什么。两者互补,不可互换。见
[docs/shell-layer/13-meta-json.md](./docs/shell-layer/13-meta-json.md)。

**GCWP** 位于 [`docs/protocol/`](./docs/protocol/)。**Shell 层规范**
位于 [`docs/shell-layer/`](./docs/shell-layer/),覆盖 CLI 语法、项目
布局与 `gallate.yaml` schema。二者合在一起,涵盖 OmegaT、Wrapper
与任何 CLI 实现所需的一切。

> **Wrapper 是 OmegaT 的唯一集成点。CLI 数量不受限制。**
> 增加第 100 个引擎,OmegaT 与 Wrapper 都不需修改 —— 只需新增一个遵守 GCWP 的 CLI。

Shell 层规则的历史叙述参考在
[`Documents/通用行为规范.txt`](https://github.com/grill-glitch/Documents),
是其被提炼为 Shell 层规范的散文来源。

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
│   ├── assets/
│   │   └── gallate-logo.png    # 项目 logo (README hero)
│   │
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
│   ├── identify.schema.yaml
│   └── cancel-command.schema.yaml
│
├── examples/                    # GCWP IPC trace
│   ├── README.md
│   ├── minimal-cli/
│   │   ├── manifest.yaml
│   │   ├── features.yaml
│   │   └── extract.jsonl
│   └── full-cli/
│       ├── manifest.yaml
│       ├── features.yaml
│       ├── validation.yaml
│       ├── validation-result.jsonl
│       ├── extract.jsonl
│       ├── inject.jsonl
│       ├── build.jsonl
│       ├── cancel.jsonl
│       ├── identify.jsonl
│       └── errors.jsonl
│
└── shell-layer-examples/        # 项目树示例
    ├── README.md
    ├── minimal-project/
    │   ├── gallate.yaml
    │   ├── .meta.json
    │   ├── text/  image/
    └── full-project/
        ├── gallate.yaml
        ├── .meta.json
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