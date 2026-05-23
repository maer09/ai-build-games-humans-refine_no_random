# godot-init

一键初始化 Godot 4 项目的开发环境：GDScript 严格类型检查、Gopeak MCP 集成、编辑器插件自动启用。

## 功能

| 步骤 | 操作 | 目标文件 |
|------|------|----------|
| 1 | 写入 30 项 GDScript 严格类型警告配置 | `project.godot` → `[debug]` |
| 2 | 添加 Gopeak MCP 服务配置 | `opencode.json` → `mcp.godot` |
| 3 | 下载安装 Gopeak 编辑器插件 | `addons/` |
| 4 | 自动启用已安装的插件 | `project.godot` → `[editor_plugins]` |

全部步骤**幂等**——重复运行不会产生重复条目或副作用。

## 前置条件

- Python ≥ 3.10
- [pipx](https://pypa.github.io/pipx/)（用于全局安装）
- [Node.js](https://nodejs.org/) ≥ 18（MCP 服务运行需要 npx）
- Windows（插件安装步骤使用 PowerShell）

## 安装

```bash
pipx install .
```

安装后 `godot-init` 命令全局可用。如遇 PATH 未生效，执行：

```bash
pipx ensurepath
```

然后重新打开终端。

### 更新

如果已经安装过，需要更新到最新版本，加 `--force` 参数重新安装：

```bash
pipx install --force .
```

## 使用

```bash
# 在 Godot 项目目录内运行
cd my-godot-game
godot-init

# 或指定任意项目路径
godot-init path/to/my-game
```

```bash
godot-init --help
```

```
usage: godot-init [-h] [project_dir]

Godot project init: GDScript warnings + Gopeak MCP + plugin auto-enable

positional arguments:
  project_dir  Godot project directory (default: current working directory)

options:
  -h, --help   show this help message
```

## 运行示例

```
Godot project init setup
project dir: my-godot-game

[1/4] read my-godot-game/project.godot
      OK wrote 30 GDScript warnings
[2/3] my-godot-game/opencode.json not found, will create
      OK wrote Gopeak MCP config
[3/4] installing Gopeak Godot MCP addon...
      OK plugin installed
[4/4] OK enabled plugins in project.godot: auto_reload, godot_mcp_editor, godot_mcp_runtime

Done!
  Open project in Godot Editor - plugins are already enabled.
```

再次运行同一项目：

```
[1/4] read project.godot
      GDScript warnings already up-to-date
[2/3] read opencode.json
      Gopeak MCP already configured, skipping
[3/4] Gopeak MCP addon already installed, skipping download
[4/4] plugins already enabled in project.godot
```

## 各步骤详解

### 步骤 1 — GDScript 严格类型警告

在 `project.godot` 的 `[debug]` section 写入 30 项警告配置，分为 4 个级别：

| 级别 | 数量 | 含义 |
|------|------|------|
| 类型安全 (ERROR) | 12 | 无类型声明、不安全的属性/方法/转换访问等 |
| 未使用/影子变量 (WARN) | 8 | 未使用的变量/参数/信号、变量遮蔽等 |
| 代码质量 (WARN) | 8 | 不可达代码、弃用关键字、空赋值等 |
| 推断风格 (WARN) | 1 | 隐式推断的类型声明 |

同时设置 `exclude_addons=true` 跳过第三方插件的检查。

写入策略为**重建式**：先移除 `[debug]` 中所有 `gdscript/warnings/*` 行，再写入干净的有序集合。即使文件中已有手动修改过的警告配置，也会被统一覆盖为标准配置。

### 步骤 2 — Gopeak MCP 配置

在项目的 `opencode.json` 中添加 MCP 服务声明：

```json
{
  "mcp": {
    "godot": {
      "type": "local",
      "command": ["npx", "-y", "gopeak"],
      "environment": {
        "GOPEAK_TOOL_PROFILE": "full"
      },
      "enabled": true
    }
  }
}
```

如果文件已存在，保留其他配置不变，仅合并 `mcp.godot` 字段。

### 步骤 3 — 插件安装

通过 PowerShell 从 [Gopeak-godot-mcp](https://github.com/HaD0Yun/Gopeak-godot-mcp) 下载安装 3 个编辑器插件：

| 插件 | 作用 |
|------|------|
| `auto_reload` | 外部修改脚本/场景时自动重新加载 |
| `godot_mcp_editor` | MCP 编辑器桥接——通过 API 操作场景和资源 |
| `godot_mcp_runtime` | MCP 运行时通信——实时检查场景、修改属性、调用方法 |

已安装（`addons/godot_mcp_editor/plugin.cfg` 存在）则跳过下载。

### 步骤 4 — 自动启用插件

扫描 `addons/*/plugin.cfg`，将所有发现的插件写入 `project.godot`：

```ini
[editor_plugins]
enabled=PackedStringArray("res://addons/auto_reload/plugin.cfg", "res://addons/godot_mcp_editor/plugin.cfg", "res://addons/godot_mcp_runtime/plugin.cfg")
```

打开 Godot 编辑器后插件即已启用，无需手动操作。

## 运行后的项目结构

```
my-godot-game/
├── project.godot          # 新增 [debug] + [editor_plugins] sections
├── opencode.json          # 新增 mcp.godot 配置
└── addons/
    ├── auto_reload/       # 自动重载插件
    ├── godot_mcp_editor/  # MCP 编辑器桥接
    └── godot_mcp_runtime/ # MCP 运行时通信
```

## 卸载

```bash
pipx uninstall godot-init
```

## 项目结构

```
scripts/python/godot-init/
├── pyproject.toml              # pipx 安装配置
├── setup_godot_project.py      # 主脚本
└── godot-init命令使用说明.md    # 本文档
```
