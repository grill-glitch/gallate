# 01. 架构

> 状态:**规范性**。定义 OmegaT / Wrapper / CLI 的职责边界,任何实现必须遵守。

## 三层模型

```text
┌─────────────────────────────────────────┐
│                  OmegaT                 │
│       翻译 / 校对 / XLIFF                │
└────────────────────┬────────────────────┘
                     │ Gamelate Wrapper API
                     │  (Wrapper 是唯一集成点)
                     ▼
┌─────────────────────────────────────────┐
│                 Wrapper                 │
│   GCWP client · 项目加载 · 集成胶水      │
└────────────────────┬────────────────────┘
                     │ GCWP (JSON Line Protocol)
                     │  (CLI 数量不受限)
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
   CLI #1         CLI #2         CLI #N
   Artemis         Ren'Py         Unity ...
```

层与层之间**不得**跨越下述职责边界。特别强调:

- OmegaT **不得**直接集成 CLI。
- CLI **不得**要求 OmegaT 特定接口。

## OmegaT

职责:

| 关注点 | 备注 |
| --- | --- |
| XLIFF 读写 | 标准双语交换格式 |
| 翻译 | 由人类译者完成;GCWP 不规定 |
| 翻译记忆库(TM) | 项目级 / 共享 |
| 术语库 / 词汇表 | 可选,与引擎无关 |
| 校对与冲突解决 | 工作流 UI |
| 过滤、搜索、编辑 | UI 行为 |
| AI provider | 可选,通用 |
| 验证 UI | 可视化验证引擎的结果 |
| 通用验证引擎 | 对从 Wrapper 收到的规则做应用 |

OmegaT 不得:

- 直接说 GCWP。
- 引入引擎专有逻辑。
- 直接读写游戏引擎格式。

## Wrapper

职责:

| 关注点 | 备注 |
| --- | --- |
| CLI 发现 | 找可用 CLI(文件系统、注册表) |
| CLI 进程管理 | 启动、监控、终止、清理 |
| 协议转换 | JSON Line Protocol ↔ OmegaT 数据结构 |
| `gallate.yaml` 加载 | 项目配置文件 |
| Input / Output 配置 | 转为操作请求 |
| 事件转发 | CLI 事件 → OmegaT UI |
| 状态聚合 | 快照 + 轮询 |
| 统计聚合 | 收集 / 暴露 / 传递给 OmegaT |
| 验证规则导入 | 把 CLI 规则转给 OmegaT Validator |
| 错误归一化 | CLI `error.code` → OmegaT 对话框 |
| OmegaT 集成 | 唯一的 OmegaT 集成面 |

Wrapper 不得:

- 解析引擎资源。
- 实现任何 extract / inject 算法。
- 修改图片、音频、视频、字体。
- 理解引擎语法。
- 自建翻译工作流。

Wrapper 必须:

- 与引擎无关。
- 完全由 CLI 返回的 `manifest`、`features`、`validation` 与事件流驱动。

## CLI

职责:

| 关注点 | 备注 |
| --- | --- |
| 游戏引擎解析 | 所有引擎相关知识 |
| `extract` | 读引擎资源,写翻译资产 |
| `inject` | 读翻译资产,写引擎资源 |
| `build` | 最终打包输出(引擎相关) |
| `unpack` / `repack` | 引擎归档管理 |
| 资源处理 | 任何引擎特有事项 |
| Manifest / features / validation 规则 | 自描述 |
| Event / status / statistics 输出 | 按 GCWP |
| 退出码语义 | 按 [02-核心协议.md](./02-core-protocol.md) |

CLI 不得:

- 显示引擎专有 GUI 对话框。
- 发 `openArtemisDialog` / `showArtemisPanel` 这类消息。
- 以任何形式依赖 OmegaT。
- 要求 Wrapper 理解引擎内部。

## 单一集成点

```text
OmegaT  ──┐
          │  一个 Wrapper 实例 / 一个 OmegaT 进程。
Wrapper ──┘  增加 CLI 双方都不用改。
          │
          ├─ CLI #1
          ├─ CLI #2
          └─ CLI #N
```

Wrapper 是 OmegaT 的**唯一**集成点。增加第 100 个 CLI 不需要改 OmegaT 或 Wrapper —— 只需新增一个遵守 GCWP 的 CLI。这就是防止"per-engine 适配器"反模式的架构契约。

## 架构防止的反模式

```text
反模式 A —— OmegaT 内部 per-engine adapter:

  OmegaT
   ├── ArtemisAdapter
   ├── RenPyAdapter
   ├── KiriKiriAdapter
   ├── UnityAdapter
   ├── ...
   └── 永无止境

反模式 B —— CLI 依赖 OmegaT:

  CLI ←→ OmegaT API    ← CLI 随 OmegaT 变而坏
  CLI ←→ Wrapper API   ← 每换 Wrapper 都要重写
```

GCWP 同时禁止两者。[12-兼容性.md](./12-compatibility.md) 给出让架构长期稳定的规则。