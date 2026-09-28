# 随包剪映接口

基础入口是 `scripts/build_jianying.py`。它复用内置 `jianying-editor` / `pyJianYingDraft` 源码，把已决定的剪辑计划写成可编辑草稿。它不替用户决定选题、观点、素材语义、配音或发布。

## 剪辑计划

复制 `assets/edit-plan.example.json` 到作品目录，替换全部示例。素材本身不在包里。

| 字段 | 含义 |
|---|---|
| `schema_version` | 当前为 `1` |
| `name` | 新草稿名，1–80 位英文字母、数字、`-` 或 `_`，同名存在就停止 |
| `width` / `height` / `fps` | 用户选择的画幅和帧率，正整数 |
| `clips[].kind` | `video` / `narration` / `original` / `bgm` |
| `clips[].media` | 相对计划文件的路径，使用 `/`，须指向真实文件 |
| `start` / `source_start` / `duration` | 成片起点、源入点和取用时长，单位秒；不能混用 |
| `volume` | 线性倍率，画面默认静音，音轨默认 1；实际混音应按听感和测量调整 |
| `track` | 可选轨名；不同声音用途保持独立，同轨不允许意外重叠 |
| `captions[]` | 实际台词文本、起点和持续时间，时间来自最终声音 |

默认画面静音，原片声音放 `original` 音轨，避免一段原声播放两次。旁白、原声和 BGM 都支持源入点。需要分屏、转场、关键帧或特定构图时，先明确意图，再用运行时真实支持的接口扩展作品脚本；不能用基础 JSON 声称完成未实现的高级效果。

## 命令

```text
python scripts/build_jianying.py "作品/edit-plan.json" --drafts-root "已确认目录" --validate-only
python scripts/build_jianying.py "作品/edit-plan.json" --drafts-root "已确认目录"
```

校验模式只检查计划结构、素材存在和目标不被覆盖，不解码媒体。构建模式实际导入媒体、建轨、复制素材并保存，输出 JSON 结果；日志输出到 stderr。失败返回非零状态，若有 `BUILD_INCOMPLETE.txt` 则工程未完成。

`build-report.json` 中 `application_open_verified` 和 `exported` 默认都是 false；只有另外实际验证后才可在作品验收记录中记为通过。不要仅把返回值手改成 true。

## 版本与保护

同名目录无论是不是有效草稿，都拒绝覆盖。修改原工程请新建版本或明确克隆后操作。不要用底层 `overwrite=True` 规避这一保护。

内置源码快照含部分上游尚依赖云端数据或额外模块的功能，基础入口没有启用它们。不随包分发私人缓存、素材库和账号配置；不能引用原作者机器上的音乐或把测试声音当正式旁白。

运行时文件由项目相对定位。新设备安装 requirements 并确认 MediaInfo 原生库后再实际构建；Windows、macOS 和 Linux 上的 Python 测试不等于对应剪映应用已验收。
