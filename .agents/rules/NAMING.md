# GDScript 命名规范

来源：[Godot 4.x 官方风格指南](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html)。

## 命名约定表

| 类型 | 约定 | 示例 |
|---|---|---|
| 文件名 | `snake_case` | `yaml_parser.gd` |
| 类名 | `PascalCase` | `class_name YAMLParser` |
| 节点名称 | `PascalCase` | `Camera3D`、`Player` |
| 函数 | `snake_case` | `func load_level():` |
| 变量 | `snake_case` | `var particle_effect` |
| 信号 | `snake_case`（**过去时态**） | `signal door_opened` |
| 常量 | `CONSTANT_CASE` | `const MAX_SPEED = 200` |
| 枚举名称 | `PascalCase`（**单数**） | `enum Element` |
| 枚举成员 | `CONSTANT_CASE` | `{EARTH, WATER, AIR, FIRE}` |

## 关键细节

- **私有函数/变量**：前缀 `_`（`_counter`、`_recalculate_path`）
- **信号**：使用**过去时态**（`door_opened`，非 `on_door_open`）
- **枚举**：名称单数形式（表示类型）；成员**每行一个**，末尾有逗号
- **文件名**：具名类 `PascalCase` → `snake_case`（`YAMLParser` → `yaml_parser.gd`）
- **节点名称**：`PascalCase`，与 Godot 内置节点风格一致

## 示例

```gdscript
# 枚举：每个值一行，末尾逗号
enum Element {
    EARTH,
    WATER,
    AIR,
    FIRE,
}

# 信号：过去时态
signal door_opened
signal score_changed

# 私有变量：下划线前缀
var _counter = 0
```

## 审查清单

- [ ] 命名符合约定表
- [ ] 私有成员有 `_` 前缀
- [ ] 信号使用过去时态
- [ ] 枚举名称单数，成员每行一个，末尾有逗号
- [ ] 文件名 snake_case，类名 PascalCase
