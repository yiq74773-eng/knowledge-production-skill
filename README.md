# 知识作品制作 / Knowledge Production

从一句选题开始，完成研究、文稿、去 AI 味、素材整理与制作。**观点先来自用户；形式由用户选定；方向不明就暂停询问。**

这是可复制给不同设备和 agent 的 Agent Skill，核心规则与剪映草稿运行时随包附带，不需要原作者的电脑、账号、历史聊天或其他同名 skill。

## 下载与开始

- 支持 Skill 的 agent：下载 [knowledge-production.zip](dist/knowledge-production.zip)，解压后将整个 `knowledge-production` 文件夹放入该 agent 的技能目录。
- 只支持聊天/附件：将 [完整工作流文本](dist/knowledge-production-prompt.md) 交给它阅读，再说明选题。普通聊天界面没有文件和应用操作能力时，不能直接完成剪映制作。
- 从仓库安装：克隆仓库，运行下方安装命令；安装器只复制文件，不安装依赖或改写已有 skill。

```text
python scripts/install_skill.py --agent codex
python scripts/install_skill.py --agent claude
python scripts/install_skill.py --agent generic --destination "你的 agent 技能目录"
```

运行时选择其中一条即可。Python 3.10+；Windows 也可使用 `py`，macOS/Linux 常使用 `python3`。没有 Python 的设备可直接复制整个文件夹。

Codex 默认安装到 `~/.agents/skills/knowledge-production`；Claude Code 默认到 `~/.claude/skills/knowledge-production`。其他宿主用其实际技能目录，不能假设所有产品安装入口一致。[Codex 官方说明](https://learn.chatgpt.com/docs/build-skills)、[Claude Code 官方说明](https://code.claude.com/docs/en/skills)。

安装后可以说：

> 使用 knowledge-production。我今天想做一个关于二元论的作品。

AI 会先澄清你所说的二元论范围、你的观点或困惑，并建议作品形式；不会直接替你选定立场和剪成视频。Codex 可用 `$knowledge-production`，Claude Code 可用 `/knowledge-production`。

## 包里有什么

| 部分 | 作用 |
|---|---|
| `skills/knowledge-production/SKILL.md` | 通用协作流程和询问边界 |
| `references/` | 研究、不同作品形式、文案与剪映衔接、设备适配 |
| `vendor/text-cleanup/` | 完整去 AI 味白名单及原始许可 |
| `vendor/jianying-editor/` | 剪映运行时源码及许可，不含私人素材或应用缓存 |
| `scripts/doctor.py` | 只读环境检查 |
| `scripts/build_jianying.py` | 相对路径剪辑计划 → 新的可编辑草稿 |
| `assets/` | 工作简报与剪辑计划模板 |

## 能迁移到什么环境

| 环境 | 可以做什么 | 仍需要什么 |
|---|---|---|
| 支持文件阅读的 agent | 选题、观点梳理、写作、去 AI 味 | 最新事实查证需要联网/搜索能力 |
| Windows / macOS 桌面 agent | 上述工作，以及生成剪映草稿 | Python、MediaInfo、实际素材；打开/验收需剪映及可用操作工具 |
| Linux / 云端 agent | 文字与素材工作；依赖齐全时可构建待迁移草稿 | 原生剪映界面不能据此视为可用，需桌面设备完成打开和导出 |
| 手机或纯聊天 agent | 读取文本规则、交互、研究/写稿（依宿主能力） | 不能仅靠提示词获得桌面文件和剪映控制能力 |

遵循 [Agent Skills 目录规范](https://agentskills.io/specification)。兼容标准格式不代表所有模型都能同样可靠地执行，也不代表所有剪映版本均已验证。

## 自动剪辑快速入口

先让 agent 确认方向、清理文稿、准备最终录音和本地素材，生成相对路径的剪辑计划。第一次设置可用独立虚拟环境安装：

```text
python -m venv .venv
# 使用该虚拟环境的 Python 执行下一条
python -m pip install -r skills/knowledge-production/requirements-video.txt
python skills/knowledge-production/scripts/doctor.py --mode jianying --drafts-root "你的草稿目录"
python skills/knowledge-production/scripts/build_jianying.py "作品/edit-plan.json" --drafts-root "你的草稿目录" --validate-only
python skills/knowledge-production/scripts/build_jianying.py "作品/edit-plan.json" --drafts-root "你的草稿目录"
```

路径是使用者自己的位置。完整依赖、迁移与运行步骤见 [设备适配](skills/knowledge-production/references/portability.md) 和 [剪辑接口](skills/knowledge-production/references/jianying-runtime.md)。

生成器拒绝覆盖同名草稿，复制所需素材，保留画面、口播、原声、BGM 和字幕轨。它不默认合成声音，不上传素材，不操纵剪映界面，也不默认导出 MP4。目标应用打开、声音画面检查与发布分别记录结果。

## 测试与修改

```text
python -m unittest discover -s tests -v
python scripts/validate_package.py
python scripts/package_release.py
```

已验证的范围和未验证项见 [测试说明](docs/TESTING.md)。修改技能后重新打包，不能只改源码而继续分发旧 ZIP。

第三方来源和本包修改见 [THIRD_PARTY_NOTICES.md](skills/knowledge-production/THIRD_PARTY_NOTICES.md)。本仓库不携带原作者的实际录音、剪映工程、云端音乐缓存、账号配置或凭据。
