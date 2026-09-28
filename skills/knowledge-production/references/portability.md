# 不同设备和 agent 的执行方式

本包不要求任何特定模型、插件名、桌面路径、发布账户或个人记忆。请根据当前宿主实际能力执行，不把其他设备的检查结果当成本机已通过。

## 第一次使用

1. 阅读根目录 `SKILL.md`。文案规则已经在 `vendor/text-cleanup/RULES.md`，不要要求用户另外安装去 AI 味 skill。
2. 根据当前阶段检查是否有文件阅读/保存、在线检索、命令执行、图像/声音理解、目标应用操作能力。工具名称由宿主决定：没有异步问答工具就直接提问；没有项目面板就交付可访问文件；不得虚构工具调用。
3. 只有任务需要时才检查相应依赖。写文章不要求安装剪映或 Python。用户的观点、风格、默认目录和账号从当前用户获取，不带入原作者偏好。
4. 有命令执行时可运行 `python scripts/doctor.py --mode text`，视频阶段换成 `--mode jianying --drafts-root "实际目录"`。这是只读探测，不安装软件、不创建草稿、不扫描私人目录。

## 通用边界

- 无网络：可以整理用户给定材料，但不得声称最新信息或在线来源已核实。
- 无文件操作：可以交付聊天文本，不能声称文件已保存、工程已建立。
- 无音频理解或播放：可以做已有时码的技术检查，不能声称逐句听辨或主观听感验收通过。
- 无剪映界面操作：可以在依赖齐全时生成待验证草稿；不得声称工程已在剪映打开或已导出。
- 无必要工具：继续可独立完成的阶段，把具体缺口和可行替代交给用户。需要改变成品形式时先询问。

## 视频运行环境

基础剪辑入口要求 Python 3.10+ 和 `requirements-video.txt` 中的 `pymediainfo`。推荐在虚拟环境内安装，读取并说明依赖后按当前宿主权限执行；不更改全局 Python 或使用自己的账号代替用户账号。

Windows 示例（在包根目录）：

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-video.txt
.\.venv\Scripts\python.exe scripts/doctor.py --mode jianying --drafts-root "用户选定的目录"
```

macOS / Linux 示例：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-video.txt
.venv/bin/python scripts/doctor.py --mode jianying --drafts-root "用户选定的目录"
```

MediaInfo 的 Python 包还可能需要系统原生库；缺失时按本机软件管理器安装对应 MediaInfo 库，例如 macOS 的 `libmediainfo`、Linux 的 `libmediainfo0v5`。具体名称先核对本机发行版，不能在不同系统上照搬命令。FFmpeg/ffprobe 用于转码和进一步检查，安装方式也按平台确定。基础 MP4/WAV 草稿生成不依赖浏览器自动化、云端账户或 TTS。

剪映草稿目录由用户提供或通过本机应用设置确认，并显式传给脚本。不要默认使用 `Administrator`、原作者用户名或固定盘符。跨设备迁移时，不依赖原系统的缓存目录或字体路径。

## 作品换设备

源作品目录携带 `edit-plan.json`、实际媒体、文稿、来源和工作简报。计划中的媒体路径相对于计划文件，使用 `/`；不能写另一台电脑的绝对路径。

运行生成器会在新草稿中复制使用到的媒体，并保存 `production-plan.json`。把整个草稿目录移到别的设备后，优先在新设备用该计划重建一个新名字的工程，使剪映中的绝对引用重新指向新设备。不能保证仅移动 JSON 就不会丢素材。

转移的是文件，不包括软件授权、登录状态、付费素材权限、声音授权和平台发布许可。目标设备仍需实际打开、检查与导出。用户已经明确只要草稿时无需追加导出。

## 安装与宿主说明

目录符合 Agent Skills 格式。支持该格式的宿主可读取完整 `knowledge-production/`；也可以让有文件能力的 agent 直接阅读该目录的 `SKILL.md`。

Codex 的 `agents/openai.yaml` 仅是可选界面元数据，其他 agent 可以忽略。流程没有依赖 Codex 专属工具名称。未识别 skill 的聊天环境使用发布包中的 `knowledge-production-prompt.md`；它包含核心工作流和完整文案规则，但不包含可执行运行时。

安装路径参考官方文档：[Agent Skills](https://agentskills.io/specification)、[Codex](https://learn.chatgpt.com/docs/build-skills)、[Claude Code](https://code.claude.com/docs/en/skills)。具体宿主以后改变目录规则时，使用它的新说明，不改动作品内容来适配安装差异。
