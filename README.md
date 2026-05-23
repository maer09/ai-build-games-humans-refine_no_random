# ai-build-games-humans-refine (非随机版)

基于 [ai-builds-games-humans-refine](https://github.com/abagby/ai-builds-games-humans-refine) 项目的中文本地化版本，移除了随机标签选择流程，改为由人类直接指定创意标签来设计 Godot 4.2+ 小游戏。本项目仅在Godot 4.6+ 版本上测试过。

> **使用方式**：本项目不是独立的 Godot 项目。需要先在 Godot 编辑器中创建项目，然后将本项目的文件复制到该 Godot 项目目录下使用。

## 项目来源

以下目录的内容来源于 [ai-builds-games-humans-refine](https://github.com/abagby/ai-builds-games-humans-refine)，并进行了中文翻译：

- **`.agents/`** — AI 智能体的 Skill 定义、参考文档和项目模板。包含游戏设计、视觉指导、程序化音频、平衡性评估等完整工作流。
- **`data/`** — 标签数据（机制标签、视觉标签、结构标签），用于阶段 1 的创意输入。

原始项目采用随机标签选择机制（`random_tag_selector.js`），本版本移除了该机制，支持三种创意输入模式：纯标签、游戏策划案、游戏点子。详见 `AGENTS.md`。

## godot-init 命令

`setup_godot_project.py` 是一键初始化 Godot 4 项目开发环境的脚本，自动化执行以下 4 个步骤：

| 步骤 | 操作 | 目标文件 |
|------|------|----------|
| 1 | 写入 GDScript 严格类型警告配置 | `project.godot` → `[debug]` |
| 2 | 添加 Gopeak MCP 服务配置 | `opencode.json` → `mcp.godot` |
| 3 | 下载安装 Gopeak 编辑器插件 | `addons/` |
| 4 | 自动启用已安装的插件 | `project.godot` → `[editor_plugins]` |

全部步骤**幂等**——重复运行不会产生重复条目或副作用。

### 前置条件

- Python ≥ 3.10
- [pipx](https://pypa.github.io/pipx/)（用于全局安装）
- [Node.js](https://nodejs.org/) ≥ 18（MCP 服务运行需要 npx）
- Windows（插件安装步骤使用 PowerShell）

### 安装

```bash
pipx install ./scripts/python/godot-init
```

如果提示已安装，可以加 `--force` 参数强制重新安装：

```bash
pipx install --force ./scripts/python/godot-init
```

安装后 `godot-init` 命令全局可用。**一次安装，所有项目通用**——后续新建 Godot 项目时无需再次安装，也无需将脚本复制到新项目目录中，直接在新项目目录内运行 `godot-init` 即可。如遇 PATH 未生效，执行：

```bash
pipx ensurepath
```

然后重新打开终端。

### 使用

```bash
# 在 Godot 项目目录内运行
cd my-godot-game
godot-init

# 或指定任意项目路径
godot-init path/to/my-game
```

运行后项目结构：

```
my-godot-game/
├── project.godot          # 新增 [debug] + [editor_plugins] sections
├── opencode.json          # 新增 mcp.godot 配置
└── addons/
    ├── auto_reload/       # 自动重载插件
    ├── godot_mcp_editor/  # MCP 编辑器桥接
    └── godot_mcp_runtime/ # MCP 运行时通信
```

详细的命令使用说明参见 [`godot-init命令使用说明.md`](./scripts/python/godot-init/godot-init命令使用说明.md)。

### 卸载

```bash
pipx uninstall godot-init
```

## 许可证

本项目中的 `.agents/` 和 `data/` 目录内容遵循原始项目 [ai-builds-games-humans-refine](https://github.com/abagby/ai-builds-games-humans-refine) 的许可证。
