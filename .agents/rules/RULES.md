# GDScript 编码规范

所有 GDScript 代码**必须**遵守本目录下的规则文件。在编写和审查代码时始终生效。

## 规则文件

| 文件 | 内容 | 来源 |
|---|---|---|
| [FORMATTING.md](gdscript-coding-standards/FORMATTING.md) | 格式规则（缩进、换行、空格、引号、数字等） | [Godot 官方风格指南](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html) |
| [NAMING.md](gdscript-coding-standards/NAMING.md) | 命名规范（文件、类、函数、变量、信号、常量、枚举） | 同上 |
| [CODE_ORDER.md](gdscript-coding-standards/CODE_ORDER.md) | 代码顺序（声明排列、访问修饰符、变量作用域） | 同上 |
| [STATIC_TYPING.md](gdscript-coding-standards/STATIC_TYPING.md) | 静态类型（强制类型声明、类型推断规则） | 同上 |
| [CODE_QUALITY.md](gdscript-coding-standards/CODE_QUALITY.md) | 编码要求（类型安全、变量整洁、代码质量、推断风格、内置约束） | [掘金文章](https://juejin.cn/post/7637078059725996086) |

## 核心要求

1. **强制静态类型**：所有变量、函数参数和返回值必须声明类型
2. **零警告编译**：代码必须无警告通过 `strict` 模式编译
3. **禁止降低警告级别**：遇到类型检查错误时，不得通过修改项目配置中的警告级别来使错误通过；必须修复代码中的类型问题
