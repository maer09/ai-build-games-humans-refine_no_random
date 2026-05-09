---
name: scaffolding-godot-mini-games
description: "从可复用的纯基础设施模板搭建一个最小的 Godot 小游戏项目。适用于启动需要 headless 测试、Web 导出默认配置、canvas shell、遥测辅助工具和程序化音频原语的 Godot 4.2+ 小游戏。"
---

使用此 skill 从捆绑的基础项目初始化 Godot 小游戏。

模板路径：
- `assets/godot-base/`

核心规则：
- 模板仅包含基础设施。不要将其视为游戏玩法、视觉身份或音频身份。
- 复制后在目标项目中实现游戏特定的机制、视觉和音效。
- 保持 `main.gd` 作为编排器，将职责拆分为独立的脚本。
- 除非项目同时更新 `project.godot`、`export_presets.cfg` 和 `web/custom_shell.html`，否则保留 Web 导出的 canvas 尺寸规则。
- 不要在捆绑模板中硬编码特定于机器的导出模板路径。复制后，项目可以在使用项目本地 XDG 目录时将 `custom_template/debug` 和 `custom_template/release` 设置为本地绝对路径。

标准脚手架命令：

```bash
PROJECT_DIR=.<slug>
mkdir -p "$PROJECT_DIR"
cp -R .agents/skills/scaffolding-godot-mini-games/assets/godot-base/. "$PROJECT_DIR"/
mkdir -p "$PROJECT_DIR/logs" "$PROJECT_DIR/build/web"
```

此命令将模板内容直接复制到 `<PROJECT_DIR>`。如果 `<PROJECT_DIR>` 已包含文件，复制前应检查，不要覆盖无关工作，除非用户明确要求重新搭建。

复制后验证：

`running-headless-godot` 中的 XDG 前提条件（"必要规则"，始终设置项目本地的 `XDG_DATA_HOME` / `XDG_CONFIG_HOME` / `XDG_CACHE_HOME`）也适用于此。最简单的方式是在验证命令前内联设置：

```bash
export XDG_DATA_HOME="$PROJECT_DIR/.godot-xdg/data"
export XDG_CONFIG_HOME="$PROJECT_DIR/.godot-xdg/config"
export XDG_CACHE_HOME="$PROJECT_DIR/.godot-xdg/cache"
mkdir -p "$XDG_DATA_HOME" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME"

godot --headless --path "$PROJECT_DIR" --version 2>&1 | tee "$PROJECT_DIR/logs/version.log"
timeout 5s godot --headless --path "$PROJECT_DIR" 2>&1 | tee "$PROJECT_DIR/logs/smoke_main_initial.log"
```

验证命令通过标准：
- `version.log` 显示 Godot 4.2+ 版本行，没有"Project file not found"/GDScript 解析错误。
- `smoke_main_initial.log` 显示正常启动直到 `timeout` 触发的退出（`timeout` 返回的退出码 124 在此是**预期行为**，模板没有退出钩子）。将任何不在项目已知警告白名单中的 `SCRIPT ERROR` / `ERROR:` 行视为失败。

验证里程碑：
- 复制后：版本检查加启动冒烟测试即可，模板有意不包含游戏特定逻辑。
- 实现后：在声称覆盖了逻辑、遥测、得分或平衡之前，添加或更新项目特定的 `res://tools/tests/run_tests.gd`。
- 导出前：再次运行启动冒烟测试，存在时运行项目特定测试，然后导出 Web 到 `build/web/index.html`。

复制后，使用 `running-headless-godot` 进行场景编辑、运行时验证和 Web 导出。
在修改模板本身之前，阅读 `assets/godot-base/TEMPLATE_SCOPE.md`。
在 Godot 中实现 `directing-game-visuals` 的视觉方向时，阅读 `references/visual-implementation-patterns.md`。
在 GDScript 中应用 `evaluating-gameplay-balance` 模式时，阅读 `references/godot-balance-pattern-examples.md`。
