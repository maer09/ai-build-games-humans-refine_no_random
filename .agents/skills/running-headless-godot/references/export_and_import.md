# 导出与导入

继承自 `SKILL.md` 的前提条件：XDG 配置块和 `--headless --path <PROJECT_DIR>` 结构（来自"必选规则"/"最小冒烟测试包装模板"）适用于下方所有命令。

最小规则：
- 根据目标使用 `--export-release` / `--export-debug` / `--export-pack`
- `--export-*` 仅在**编辑器构建**中可用（导出模板二进制文件中不可用）
- 将 `--export-*` 视为隐含包含 `--import`
- 如果输出路径是相对路径，则从**`project.godot`（即项目根目录）**解析
- 对于 `--export-pack`，输出格式由扩展名决定（`.pck` 或 `.zip`）

前置条件（最小）：
- `export_presets.cfg` 存在
- 导出模板已安装

## Web 导出

命令：
```bash
mkdir -p <PROJECT_DIR>/build/web <PROJECT_DIR>/logs
godot --headless --path <PROJECT_DIR> \
  --export-release "Web" build/web/index.html \
  2>&1 | tee <PROJECT_DIR>/logs/web_export.log
```

`export_presets.cfg` 示例：
```ini
[preset.0]
exclude_filter="build/web/*"

[preset.0.options]
custom_template/debug="/home/alice/.local/share/godot/export_templates/4.6.1.stable/web_nothreads_debug.zip"
custom_template/release="/home/alice/.local/share/godot/export_templates/4.6.1.stable/web_nothreads_release.zip"
```

- `exclude_filter`：防止之前生成的输出被重新包含在下一次导出中
- `custom_template/*`：将导出模板的绝对路径固定（在切换 XDG 目录时必须使用）

### XDG 与导出模板

XDG 配置块按照 `SKILL.md` 中的"必选规则"设置。导出特定的影响：

- 一旦 `XDG_DATA_HOME` 指向项目目录（按照规则），导出模板的查找路径也会移至 `XDG_DATA_HOME/godot/export_templates/...`，Godot 将无法找到安装在用户全局 `~/.local/share/godot/` 下的模板。
- 要继续使用全局安装的模板集，在 `export_presets.cfg` 中的 `custom_template/*` 下固定绝对路径（如上例所示）。
- 在设置 `custom_template/*` 之前，运行 `godot --version` 并在全局用户数据目录中查找匹配的 Web 模板，例如 `~/.local/share/godot/export_templates/<version>/web_nothreads_release.zip`。如果找不到模板，请报告缺失的模板路径和导出日志，而不是猜测。

### 已知警告

在无头运行中可能会看到 `TCP listen` 警告。如果 `build/web/index.html` / `index.pck` / `index.wasm` 已生成，通常可以忽略。
