# 无头 CLI

继承自 `SKILL.md` 的前提条件：XDG 配置块和 `--headless --path <PROJECT_DIR>` 结构（来自"必选规则"和"最小冒烟测试包装模板"）适用于下方所有命令。

推荐的 `--script` 运行 CLI 结构（假设上方 XDG 前提条件已设置）：
```bash
mkdir -p <PROJECT_DIR>/logs
godot --headless --path <PROJECT_DIR> --script <SCRIPT_PATH> -- <ARGS...> 2>&1 | tee <PROJECT_DIR>/logs/run.log
```

约定：
- 编写脚本时，假设**相对路径从 `project.godot`（即项目根目录）解析**
- 如果目标二进制文件不支持 `--headless`，回退使用 `--display-driver headless --audio-driver Dummy`
- 通过 `--script` 运行的脚本必须始终调用 `quit(0|1)`（不要挂起）

已知脚本警告：
- `Failed to open 'user://logs/...'` 后跟崩溃是环境故障；在调试项目代码之前，先使用 XDG 安全包装器重新运行
- `RID/Object leak` 警告可能在 `--script` 场景生成/保存后出现，即使执行成功
- 如果退出码为 `0` 且已生成预期输出，则视为已知警告（不是立即失败）
- 如果退出码非零，或缺少预期测试输出，无论警告类型如何，均视为失败
- 建议通过显式释放临时节点/资源并在 `quit(0|1)` 之前保持脚本生命周期简短来减少泄漏

最小健全性检查：
```bash
godot --version
mkdir -p <PROJECT_DIR>/logs
godot --headless --path <PROJECT_DIR> --version 2>&1 | tee <PROJECT_DIR>/logs/version.log
```
