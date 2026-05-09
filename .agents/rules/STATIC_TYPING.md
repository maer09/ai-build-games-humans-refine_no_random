# GDScript 静态类型（强制）

来源：[Godot 4.x 官方风格指南](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html) + [严格类型检查配置](https://juejin.cn/post/7637078059725996086)。

本项目所有 GDScript **必须使用静态类型**，代码必须**无警告**通过 `strict` 模式编译。

## 类型声明规则

- 类型明确时用 `:=`：`var direction := Vector3(1, 2, 3)`
- 类型不明确时**显式声明**：`var health: int = 0`（非 `var health := 0`，因为可能被推断为 float）
- 冗余类型提示避免：`var direction: Vector3 = Vector3(...)` → 用 `:=`
- `get_node()` 等无法推断时，用显式类型或 `as` 转换

```gdscript
# 正确：显式类型
@onready var health_bar: ProgressBar = get_node("UI/LifeBar")

# 正确：as 转换（类型安全但空值安全性较低）
@onready var health_bar := get_node("UI/LifeBar") as ProgressBar
```

## 审查清单

- [ ] 所有变量有类型声明
- [ ] 所有函数参数有类型声明
- [ ] 所有函数返回值有类型声明
- [ ] strict 模式编译无警告
- [ ] `get_node()` 结果有显式类型或 `as` 转换
