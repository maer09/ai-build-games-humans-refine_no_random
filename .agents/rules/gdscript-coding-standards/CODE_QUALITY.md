# GDScript 编码要求

来源：[为 Godot 项目配置严格的 GDScript 静态类型检查](https://juejin.cn/post/7637078059725996086)。

所有 GDScript 代码**必须**遵守以下正面编码要求。这些要求从 Godot 4.2+ 的编译警告系统中提炼，以"应该怎么做"而非"不要怎么做"的方式表达。

## 类型安全（必须满足）

**所有变量、参数、返回值必须声明具体类型。** 不允许无类型的声明、访问或调用。

- 为每个变量、函数参数和返回值提供明确的类型注解
- 在静态类型上访问属性和方法，避免在 Variant 或动态类型上操作
- 使用可验证的类型转换；避免无法静态验证的 `as` 转换
- 传递与目标参数类型匹配的实参
- 三元运算符的两个分支返回**相同类型**
- 显式处理类型转换，避免隐式精度损失（如 `float → int` 需用 `int()` 显式转换）
- 将整数赋值给枚举变量时，使用枚举成员或显式类型转换，不直接赋整数值
- 选择与现有枚举成员匹配的整数值
- 避免使用与内置类型或类名极度相似的标识符
- `@static_unload` 中只编写可达代码

**示例**：

```gdscript
# 正确：完整类型注解
var health: int = 0
var speed: float = 5.0
func deal_damage(amount: int, target: CharacterBody2D) -> bool:
    pass

# 正确：三元分支类型一致
var result: int = 10 if flag else 20

# 正确：显式精度转换
var count: int = int(distance / step_size)

# 正确：使用枚举成员
var element: Element = Element.FIRE

# 错误：缺少类型注解
var health = 0

# 错误：三元分支类型不一致
var result = 10 if flag else "hello"

# 错误：隐式窄化转换
var count: int = 3.14
```

## 变量整洁（应该满足）

**每个声明的变量、参数、信号、常量都必须被使用。** 不声明冗余标识符。

- 只声明实际使用的变量和参数
- 每个声明的信号必须在某处 `connect` 或 `emit`
- 每个声明的常量必须被引用
- `_` 前缀的私有类变量同样必须被使用
- 不在嵌套作用域中声明与外层同名的变量
- 子类不声明与基类同名的成员变量
- 局部变量不遮蔽全局类名或常量

**示例**：

```gdscript
# 正确：声明的变量都被使用
var _timer: Timer
var score: int = 0

func _ready() -> void:
    _timer.start()
    print(score)

# 正确：信号被使用
signal score_changed
func emit_score() -> void:
    score_changed.emit()

# 错误：变量声明后未使用
var _unused: int = 0

# 错误：参数声明后未使用
func process(_data: Dictionary) -> void:
    pass

# 错误：局部变量遮蔽外部变量
var name: String = "player"
func inner() -> void:
    var name: String = "npc"  # 遮蔽了外部 name
```

## 代码质量（应该满足）

**每条语句都必须有明确目的。** 不编写无效果或无法到达的代码。

- `return`/`break` 之后不放置任何代码
- `match` 中每个分支都有可匹配的 pattern
- 每个表达式语句的结果都被使用或产生副作用
- 三元表达式的结果被赋值或作为参数传递，不作为独立语句
- 使用当前版本的 GDScript 关键字，不使用已弃用的旧关键字
- 局部变量名与外部作用域的标识符有足够区分度
- 赋值表达式的左侧和右侧是不同的值（不自我赋值）
- 有返回值的函数调用结果必须被使用；如需忽略返回值，将其赋给 `_`

**示例**：

```gdscript
# 正确：有返回值的函数结果被使用
var result: int = calculate_score()
emit_signal("done", result)

# 正确：显式忽略返回值
_ = try_optional_action()

# 正确：match 分支都可匹配
match state:
    State.IDLE:
        idle()
    State.RUN:
        run()
    State.JUMP:
        jump()

# 错误：return 后有代码
func check() -> bool:
    return true
    print("unreachable")  # 永远不会执行

# 错误：独立三元（无赋值）
"yes" if flag else "no"

# 错误：自我赋值
health = health
```

## 推断风格（应该满足）

**优先使用显式类型声明 `: Type` 而非推断 `:=`。**

- 变量声明时优先写明类型：`var health: int = 0`
- 仅当类型冗余时使用 `:=`：`var pos := Vector2(1, 2)`

```gdscript
# 正确：显式类型
var health: int = 0
var name: String = "player"
var speed: float = 5.0

# 正确：类型显而易见时用 :=
var direction := Vector2.RIGHT
var color := Color.WHITE
```

## 内置约束（自动满足）

Godot 4.2 以下约束默认即为错误级别，无需额外配置：

- 不在 Variant 上使用 `:=` 推断类型
- 覆盖引擎内置虚方法时签名完全匹配
- 在 `_ready` 之外使用 `get_node()` 时配合 `@onready`
- 不同时使用 `@onready` 和 `@export`（两者语义冲突）

```gdscript
# 正确：get_node 与 @onready 配合
@onready var sprite: Sprite2D = get_node("Sprite2D")

# 错误：get_node 缺少 @onready（在类变量声明中）
var sprite: Sprite2D = get_node("Sprite2D")

# 错误：@onready 与 @export 共用
@export @onready var max_hp: int = 100
```

## 审查清单

- [ ] 所有变量/参数/返回值有具体类型注解
- [ ] 每个声明的变量、参数、信号、常量都被使用
- [ ] 无不可达代码、独立表达式、自我赋值
- [ ] 优先使用显式类型声明 `: Type`
- [ ] 未使用 `as any`、`@ts-ignore` 等绕过类型检查的手段
