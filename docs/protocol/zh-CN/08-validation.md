# 08. 验证

> 状态:**规范性**。定义 CLI 如何向 Wrapper 暴露引擎专有文本验证规则,Wrapper 再转发给 OmegaT 的通用验证引擎。

验证是 GCWP 对 OmegaT 最有价值的能力:它是引擎知识通向译者 UI 的唯一路径。

## 验证流

```text
CLI
  ↓
Engine Validation Rules       (声明式)
  ↓
Wrapper
  ↓
OmegaT Validation Engine      (通用,应用规则)
  ↓
JSON 单元                     (按翻译单元附带发现)
```

CLI 不得自建审校 UI。Wrapper 不得实现引擎专有验证。OmegaT Validator 不得硬编码引擎知识。

## 验证规则文档

Schema:[`schema/validation.schema.yaml`](../../schema/validation.schema.yaml)。

接口:

```bash
cli validation
```

示例:

```json
{
  "type": "validation",

  "rules": [
    {
      "id": "control-code",
      "type": "regex",
      "scope": "text",
      "pattern": "\\[A-Z]+(?:_[0-9]+)?",
      "flags": [],
      "severity": "error"
    },
    {
      "id": "player-name",
      "type": "placeholder",
      "scope": "text",
      "pattern": "\\{player\\}",
      "preserve": true,
      "severity": "error"
    },
    {
      "id": "max-length",
      "type": "constraint",
      "scope": "text",
      "constraint": {"maxLength": 80},
      "severity": "warning"
    }
  ]
}
```

## 规则字段

| 字段 | 必填 | 备注 |
| --- | --- | --- |
| `id` | ✓ | 稳定规则 id |
| `type` | ✓ | `regex` / `placeholder` / `constraint` 之一 |
| `scope` | ✓ | 规则作用范围 |
| `severity` | ✓ | `info` / `warning` / `error` |
| `message` | 可选 | 覆盖结果消息 |
| `description` | 可选 | 人类可读说明 |

## Regex Rule

最基本的引擎专有检查。

```json
{
  "id": "control-code",
  "type": "regex",
  "scope": "text",
  "pattern": "\\[A-Z]+(?:_[0-9]+)?",
  "flags": [],
  "severity": "error"
}
```

pattern 是正则表达式(风味由引擎定;Wrapper 缺省 PCRE/RE2)。

## Placeholder Rule

占位符建议用 placeholder 而非 regex。

```json
{
  "id": "player-name",
  "type": "placeholder",
  "scope": "text",
  "pattern": "\\{player\\}",
  "preserve": true,
  "severity": "error"
}
```

语义:

```text
Source:
    Hello {player}

Target:
    你好 {player}        ✓ 通过

Target:
    你好                  ✗ 失败:缺必需占位符
```

`preserve: true` 表示占位符必须在目标中原文出现。

## Constraint Rule

不适合 regex 的规则:

```json
{
  "id": "max-length",
  "type": "constraint",
  "scope": "text",
  "constraint": {"maxLength": 80},
  "severity": "warning"
}
```

标准 constraint 字段:

| Constraint | 含义 |
| --- | --- |
| `maxLength` | 目标文本最大字符数 |
| `minLength` | 最小字符数 |
| `maxBytes` | UTF-8 编码后最大字节 |
| `noLineBreak` | 目标不得含换行 |

## Scope

```text
text        任意文本
source      仅源文本
target      仅翻译文本
placeholder 占位符区域
metadata    元数据字段
resource    整资源
```

例:

```json
{ "scope": "target" }
```

表示规则仅作用于译文,不作用于源文。

## Severity

| Severity | 含义 |
| --- | --- |
| `info` | 信息;不阻塞流程 |
| `warning` | 警告;继续 |
| `error` | 错误;默认阻塞最终 commit/build |

OmegaT 可让用户改视觉展示,但**不得**改 CLI 给出的规则定义。

## 验证结果

CLI 评估规则后,发出:

```json
{
  "type": "validation",
  "rule": "placeholder",
  "severity": "error",

  "source": "Hello {player}",
  "target": "你好",

  "message": "Required placeholder is missing: {player}",

  "file": "script/scene_037.bin",
  "line": 42,
  "offset": 12,
  "length": 8
}
```

可选上下文字段:

```text
file
line
offset
length
resource
translation_unit
```

## 多层规则

三类规则源组合:

```text
Engine    from cli validation
Project   from gallate.yaml  (项目级覆盖 / 新增)
User      from OmegaT user preferences (最后一行,最高优先级)
```

合并后:

```text
Effective = Engine + Project + User
```

优先级:

```text
User > Project > Engine
```

CLI **不得**用规则覆盖用户规则。CLI 可提供合理默认值,但最终合成由 Wrapper 负责。

## 验证器位置

CLI **不得**自建 UI 验证。

```text
错误:
    CLI 跑 regex → 弹对话框"控制码缺失"

正确:
    CLI 发出规则描述
    Wrapper 在 OmegaT Validator 注册规则
    OmegaT 在标准 UI 显示发现
```