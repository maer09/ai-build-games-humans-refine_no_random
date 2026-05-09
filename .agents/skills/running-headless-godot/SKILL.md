---
name: running-headless-godot
description: "运行可复现的 Godot 4.2+ 无头工作流，涵盖 CLI 命令、导出、脚本化场景编辑和测试。适用于运行 Godot CLI 命令、通过脚本编辑 .tscn、捕获日志或在无头模式下进行导出。"
---

使 Godot (4.2+) 无头开发可复现的规则，避免环境漂移和特定环境故障。

适用范围：
- Godot 4.2+（Godot 3.x 不在范围内）

必选规则（最高优先级）：
- **GDScript 必须使用静态类型**：所有变量、函数参数和返回值必须声明类型；代码必须无警告地通过 Godot 的编译（`strict` 模式）。
- 始终使用 `--headless --path <PROJECT_DIR>`（消除对 `cwd` 的依赖）
- 始终将日志捕获到项目目录下：`2>&1 | tee <PROJECT_DIR>/logs/<name>.log`
- 任何脚本化的 Godot 运行都必须设置项目本地的 `XDG_DATA_HOME`、`XDG_CONFIG_HOME` **和** `XDG_CACHE_HOME`。三个变量必须同时设置，因为 Godot 会向这三个目录写入数据，部分重定向仍会导致未设置的目录使用不可写的默认路径。此规则可避免 CI/沙箱写入失败（`Can't open file for writing: ~/.config/godot/...`）；在开发者机器上无害，因为唯一的效果是项目的元数据/缓存存放在 `<PROJECT_DIR>/.godot-xdg/` 而非用户全局目录中。将 `.godot-xdg/` 添加到 `.gitignore`。
- 禁止直接以文本方式编辑 `.tscn`（编辑必须通过 `--headless --script` 进行）
- 对于重复使用的验证命令，将其标准化为 `tools/*.sh`；手动调整后，通过相同的脚本重新运行
- 如果 `res://tools/godot_apply_patch.gd` 不存在，在运行补丁命令之前，将 `.agents/skills/running-headless-godot/tools/godot_apply_patch.gd` 复制到 `<PROJECT_DIR>/tools/godot_apply_patch.gd`
- 将启动冒烟测试和逻辑测试分开：冒烟测试启动 `run/main_scene`；`run_tests.gd` 用于项目特定的逻辑检查

## 最小冒烟测试包装模板

对于重复的启动验证，将其标准化为 `<PROJECT_DIR>/tools/smoke.sh`。其他重复调用的脚本（`run_tests.sh`、`export_web.sh` 等）遵循相同的结构，仅 godot 参数和日志文件名不同。

```bash
#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 项目本地 XDG（始终设置；参见上方必选规则）。
export XDG_DATA_HOME="$PROJECT_DIR/.godot-xdg/data"
export XDG_CONFIG_HOME="$PROJECT_DIR/.godot-xdg/config"
export XDG_CACHE_HOME="$PROJECT_DIR/.godot-xdg/cache"
mkdir -p "$XDG_DATA_HOME" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$PROJECT_DIR/logs"

# 冒烟测试 = 无头启动 run/main_scene，运行几帧后退出。
# --quit-after <N> 按帧数限制运行时长。
godot --headless --path "$PROJECT_DIR" --quit-after 60 \
  2>&1 | tee "$PROJECT_DIR/logs/smoke.log"
echo "godot_exit=${PIPESTATUS[0]}"
```

冒烟测试通过标准：
- 捕获的退出码（`${PIPESTATUS[0]}`）为 `0`。
- `logs/smoke.log` 中不包含项目已知警告白名单之外的 `ERROR`、`SCRIPT ERROR`、`Failed to load` 或 `Parse Error` 行（参见 `references/headless_cli.md`）。
- 存在启动可见标记（例如主场景 `_ready` 中的 `print()`，或不存在 "Main scene can't be loaded" 错误）。

如果遇到问题，请提供：
- 完整的命令行和 `logs/*.log`
- `godot --version` 的输出
- `export_presets.cfg` 是否存在（导出时）

不在范围内：
- 项目本地 XDG 包装器之外的 GUI/操作系统特定设置
- 关卡设计、渲染验证、性能调优
- 游戏特定的计分、胜负规则、控制和模拟策略

需要详细信息时，阅读以下文件（相对于此技能的基础目录）：
- `references/headless_cli.md` — CLI 约定、XDG 设置、已知警告
- `references/export_and_import.md` — 导出/导入规则
- `references/scene_editing_via_godot.md` — 安全的 `.tscn` 编辑、补丁 JSON 模式和操作
- `references/testing_headless.md` — 无头测试策略

如果对 Godot CLI 或功能不确定，请参考：
- https://docs.godotengine.org/en/4.4/tutorials/editor/command_line_tutorial.html
- https://docs.godotengine.org/en/4.4/tutorials/export/exporting_for_dedicated_servers.html
- https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html
