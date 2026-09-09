# 11. 一致性

> 状态:**规范性**。定义"兼容 Shell 层"的含义。

声称兼容 Shell 层规范的 CLI **必须**遵守以下规则。引擎扩展被欢迎;标准行为必须保持稳定。

## 11.1 Shell 层兼容契约

兼容 CLI **必须**:

1. 接受标准语法 `tool [op][media] project [options]`。
2. 接受 `-e`(extract),理想情况下也接受 `-i`(inject)。
3. 接受标准 media flag `-t`(text)与 `-i`(image)。
4. 将 `gallate.yaml` 视为唯一的 Project Target。
5. 从位置参数加载 `gallate.yaml`。
6. 相对 Project Root 解析路径。
7. 支持 `--output`、`--ignore`、`--dry-run`、`-v`、`-q`、`--force`。
8. 实现 `init`。
9. 应用配置优先级 CLI > YAML > 引擎默认。
10. `--ignore` 应用合并语义,media 与 `--output` 应用覆盖语义。
11. stdout 用于结果,stderr 用于诊断(绝不相反)。
12. 返回标准退出码之一(0–10)。
13. 所有扩展 flag 放在 `--engine.*` 下,并在 `--help` 中单独文档化。
14. 在没有 `--force` 时,从 `init` 拒绝覆盖现有 `gallate.yaml`。

## 11.2 非要求项(引擎自由度)

兼容 CLI **可**自由选择:

- 是否在 Shell 层暴露 audio/video 作为 `-a` / `-v` flag(标准仅要求 `text` 与 `image`)。
- 在任何媒体下声明哪些 sub-media。
- 是否完全支持 `-i`(inject)(只读 extractor 可以;无 extract 的 CLI 不行)。
- 是否使用 in-place 作为输出模式。
- pre/post 脚本使用哪种脚本解释器。
- 项目内的精确输出目录布局。
- 输出归档内的精确路径布局。
- `--engine.*` 下的引擎特定 flag。

## 11.3 三级(建议)

Shell 层不像 GCWP 那样正式分级(见 [GCWP § 13 Conformance](../../protocol/13-conformance.md))。大多数 CLI 要么全有要么全无。以下宽松等级仅用于文档:

### Minimal

支持 `-e` 与 `-t`(仅文本)。grep 式 extractor 或可脚本化 CLI。

### Standard

支持 `-e` + `-i`、两种标准 media、完整标准 flag 集合、`init`、完整项目布局。

### Full

Standard + 所有引擎扩展 media 暴露、完整 pre/post 脚本支持、in-place、dry-run 带详细报告。

这些等级仅是文档,没有 schema 或机器可校验的声明。

## 11.4 "兼容 GCWP"的含义

带 Shell 层兼容的 CLI **也可**声称 [GCWP 兼容](../../protocol/13-conformance.md)。两者独立:

```text
Shell layer  →  tool 从 shell 调用
GCWP         →  tool 由 Wrapper 通过 stdin/stdout 调用
```

完整 gallate CLI 同时实现两者。Minimal CLI 可能仅实现 Shell 层。

见 [README.md § Relationship between layers](../../README.md#relationship-between-layers) 了解整体架构。

## 11.5 验证

Shell 层不附带 JSON Schema(配置就是 YAML)。验证靠检查:

- CLI 接受标准语法。
- `gallate.yaml` 遵循标准顶层结构([05-config-file.md](./05-config-file.md))。
- `tool --help` 先列 Standard Options 再列 Engine Options。
- 退出码 0–10 携带标准含义。

引擎作者**应**手动对照实现验证这些。