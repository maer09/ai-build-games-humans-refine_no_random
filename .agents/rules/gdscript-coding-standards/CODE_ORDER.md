# GDScript 代码顺序

来源：[Godot 4.x 官方风格指南](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html)。

## 声明顺序（从上到下）

```
01. @tool, @icon, @static_unload
02. class_name
03. extends
04. ## 文档注释

05. signals
06. enums
07. constants
08. static variables
09. @export variables
10. remaining regular variables
11. @onready variables

12. _static_init()
13. remaining static methods
14. 内置虚方法覆盖：_init → _enter_tree → _ready → _process → _physics_process → 其余
15. 自定义方法覆盖
16. 其余方法
17. 内部类
```

## 访问修饰符顺序

每个分类内：**public → private**

## 经验法则

1. 先信号和属性，再方法
2. 先公共成员，再私有成员
3. 先虚函数回调，再类接口
4. 先构造/初始化（`_init`、`_ready`），再运行时修改

## 变量作用域

- 仅方法内使用 → **局部变量**（不声明为成员变量）
- 局部变量声明离首次使用**越近越好**

## 审查清单

- [ ] 声明顺序符合 01-17 序号
- [ ] 每个分类内 public 在 private 之前
- [ ] 仅方法内使用的变量为局部变量
- [ ] 局部变量声明位置靠近首次使用
