# 通过 Godot 编辑场景

继承自 `SKILL.md` 的前提条件：
- 在此文件中的任何 `godot` 调用之前，设置项目本地的 `XDG_DATA_HOME` / `XDG_CONFIG_HOME` / `XDG_CACHE_HOME`（参见 SKILL.md "必选规则"和"最小冒烟测试包装模板"，下方所有命令均适用相同的 XDG 配置块前缀）。

目标：
- 安全地更新 `.tscn`（**禁止直接文本编辑**）

单向流程：
- `patch.json`（可审查）-> `godot_apply_patch.gd`（应用）-> 保存 `.tscn`

标准补丁命令（假设上方 XDG 前提条件已设置）：
```bash
mkdir -p <PROJECT_DIR>/logs
godot --headless --path <PROJECT_DIR> --script res://tools/godot_apply_patch.gd -- <PATCH_JSON_PATH> --dry-run 2>&1 | tee <PROJECT_DIR>/logs/patch_dry_run.log
godot --headless --path <PROJECT_DIR> --script res://tools/godot_apply_patch.gd -- <PATCH_JSON_PATH> 2>&1 | tee <PROJECT_DIR>/logs/patch_apply.log
```

补丁输入要求：
- `<PATCH_JSON_PATH>` 必须是绝对路径或 `res://` 路径（不接受相对路径）
- 先运行 `--dry-run` 进行 NodePath/类型预验证

补丁 JSON 最小模式：
```json
{
  "scene_path": "res://path/to/scene.tscn",
  "operations": [
    { "op": "set_property", "node": "SomeNode", "property": "visible", "value": true }
  ]
}
```

允许的操作：
- `set_property`：`node` `property` `value`（基本类型）/ `value_variant`（用于 `str_to_var`）
- `rename_node`：`node` `new_name`
- `add_child_scene`：`parent` `child_scene`（PackedScene）`name`（可选）
- `delete_node`：`node`（需要 `--allow-delete`；默认禁止）

`rename_node` 的额外规则：
- 重命名后，始终更新对旧节点名的代码引用（`$OldName`、`get_node("OldName")` 等）
- 如果不打算更新引用，不要使用 `rename_node`（使用 `set_property` 等）

补丁运行规则：
- 如果 `add_child_scene` 指定了 `name`，替换同名现有节点以实现幂等应用
- 不要在同一补丁中对通过 `add_child_scene` 添加的实例下的节点使用 `set_property`；实例化场景已定义这些属性，覆盖会导致保存后出现重复或静默冲突，应编辑原始场景

安全性：
- 先运行 `--dry-run`（仅 NodePath 解析/类型检查）
- 保存前创建 `.bak` 备份（失败时恢复并 `quit(1)`）
- 如果 NodePath 解析失败，立即中止（不进行部分应用）
- `--dry-run` 不会捕获运行时错误（例如 `_ready` 中的损坏引用），应用后始终运行冒烟启动

保存策略：
- `PackedScene.load -> instantiate -> edit -> PackedScene.pack -> ResourceSaver.save`
- 保存可能改变 `owner` 和其他细节，因此保持补丁尽量小且精简。
