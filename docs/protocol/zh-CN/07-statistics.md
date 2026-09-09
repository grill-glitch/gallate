# 07. 统计

> 状态:**规范性**。定义 CLI 发出的累计结果指标。

统计是**数据模型**,不是日志。Wrapper 用它做项目仪表盘、OmegaT 侧栏、配额统计。

## 统计文档

Schema:[`schema/statistics.schema.yaml`](../../schema/statistics.schema.yaml)。

示例:

```yaml
type: statistics

files:
  scanned: 1524
  matched: 318
  processed: 317
  skipped: 1
  failed: 0

text:
  extracted: 8421
  injected: 0

images:
  extracted: 326
  injected: 0

audio:
  extracted: 0
  injected: 0

video:
  extracted: 0
  injected: 0

output:
  created: 643
  modified: 0
  bytesRead: 48392012
  bytesWritten: 7219382

duration: 12.84
```

## 字段

| 分组 | 字段 | 备注 |
| --- | --- | --- |
| files | `scanned` | 检查过的资源总数 |
| files | `matched` | 通过 include/exclude 的 |
| files | `processed` | 成功转换 |
| files | `skipped` | 主动跳过 |
| files | `failed` | 转换失败 |
| text | `extracted` | 本操作提取字符串数 |
| text | `injected` | 本操作注入字符串数 |
| images | `extracted` / `injected` | 图片媒体,同上 |
| audio | `extracted` / `injected` | 音频媒体,同上 |
| video | `extracted` / `injected` | 视频媒体,同上 |
| output | `created` | 创建的文件数 |
| output | `modified` | 原地修改的文件数 |
| output | `bytesRead` | 总读取字节 |
| output | `bytesWritten` | 总写入字节 |
| duration | (秒) | 操作墙钟时长 |

CLI 可添加自定义顶层键。Wrapper 必须按 [12-兼容性.md](./12-compatibility.md) 忽略未知键。

## 仅机器可读数字

```text
8421      ✓
8.4K      ✗   不要缩写
8,421     ✗   不要千位分隔符
```

## 自定义统计

CLI 可在自定义命名空间下加引擎专有统计:

```yaml
artemis:
  controls_decoded: 4218
  fonts_resolved: 14
```

Wrapper 必须先被告知含义才能显示/使用。展示需要 per-engine UI 插件。

## Status vs Event vs Statistics

```text
Status      → "正在发生什么"           (快照)
Event       → "刚刚发生了什么"          (实时)
Statistics  → "已做了多少"              (累计)
```

例:

```text
Status:
    当前处理 scene_072.bin

Statistics:
    已提取 8421 字符串
    已处理 317 文件

Event stream (tail):
    {type: event, event: file, action: extract, path: script/scene_072.bin}
```