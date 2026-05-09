# 无头测试

继承自 `SKILL.md` 的前提条件：XDG 配置块和 `--headless --path <PROJECT_DIR>` 结构（来自"必选规则"/"最小冒烟测试包装模板"）适用于下方所有命令。

适用范围（仅限以下）：
- 逻辑、资源加载和最小场景启动
- 依赖渲染的检查、渲染输出验证以及输入/窗口操作不在范围内

最小策略：
- 在项目中保留 `res://tools/tests/run_tests.gd` 并通过 `--script` 运行
- 将 `res://tools/tests/run_tests.gd` 视为由 agent 维护的项目文件（不包含在此技能中）
- 可以从此技能的 `tools/templates/run_tests.gd` 模板引导，并将其复制到项目中
- 保持 `run_tests.gd` 专注于项目特定的逻辑/资源检查；不要依赖它来覆盖 `run/main_scene` 启动
- `assert` 失败/异常时调用 `quit(1)`；成功时调用 `quit(0)`
- 应用补丁后，添加一个实际启动 `run/main_scene` 的冒烟运行（以捕获 `_ready` 错误）
- 不要假设 `score`、`game_over`、敌人数量或固定输入动作等指标，除非项目已经定义了它们

已知脚本警告（RID/Object 泄漏等）参见 `headless_cli.md`。

启动冒烟测试（最小）：
```bash
mkdir -p <PROJECT_DIR>/logs
timeout 5s godot --headless --path <PROJECT_DIR> 2>&1 | tee <PROJECT_DIR>/logs/smoke_main.log
```
- 将 `Node not found` 和脚本错误视为失败
- 补丁后，添加重要节点数量的检查（例如验证预期的单例节点恰好存在一次）

要求：
- 通过 `--script` 运行的脚本必须继承 `SceneTree` 或 `MainLoop`（Godot 4）
- 使用启动冒烟测试来覆盖复制后和场景启动。当这些系统存在后，使用 `res://tools/tests/run_tests.gd` 进行项目特定的逻辑、计分、遥测和平衡检查。

可选：
- 可以使用外部测试框架（GUT 等），但此技能不记录这些工作流。
