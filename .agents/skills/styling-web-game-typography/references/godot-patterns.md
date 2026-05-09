# Godot 4.2+ 排版实现模式

当目标引擎为 Godot 4.2+ 时，`styling-web-game-typography` 的引擎专项实现模式。请先阅读 `typography-implementation-guide.md` 中的引擎无关原则；本文件仅补充 Godot 专有内容（资源类型、路径、绘制 API、Web 导出注意事项）。

范围：
- Godot 4.2+（Godot 3.x 不在范围内）。

## Theme 和字体资源

- 将 `Theme` 视为项目的排版单元。将指南 §4 中引擎无关的 token 集映射到 Godot `Theme` 属性上：
  - 字体族 → `font_*` 主题条目，持有 `FontFile` 资源
  - 尺寸 → `default_font_size` 以及通过主题类型进行的逐控件尺寸覆盖
  - 颜色 → 主题颜色条目（`font_color`、`font_color_disabled` 等）
  - 效果 → `font_outline_color`、`outline_size`、阴影偏移/颜色
- 将项目主题放置在 `res://themes/default_theme.tres` 并全局应用，使各个控件默认继承。
- 仅在明确的逐实例例外情况下，才在 `Label` / `RichTextLabel` 上使用 `theme_override_*` 属性。

## 回退字体阶段

- 仅通过 `ThemeDB.fallback_font` 实现，此时不要打包外部字体文件。
- 在 `Theme` 资源中照常定义基于角色的尺寸/颜色 token；字体槽位保持空置。
- 在 `TYPOGRAPHY_DECISION.md` 中记录字体尚未选定，当前使用 `ThemeDB.fallback_font`。
- 在仅使用回退字体期间，不要创建 `res://licenses/fonts/` 或在 `THIRD_PARTY_LICENSES.md` 中添加字体条目。

## 采用阶段

- 仅将选定的字体字重打包到 `res://assets/fonts/` 下。
- 将对应的许可证文本放置在 `res://licenses/fonts/` 下。
- 更新 `THIRD_PARTY_LICENSES.md`，记录字体名称、来源 URL/版本、打包文件名、字重和许可证。
- 确认代码不再仅依赖 `ThemeDB.fallback_font`；`FontFile` 资源已显式加载到 `Theme` 中。

## Label 与 `_draw()` 的选择

Godot 提供两种文本渲染路径，选择应是有意的：

- 常规 UI：`Label` / `RichTextLabel`（可维护性优先）。
- 效果 UI：`CanvasItem._draw()` + `draw_string()`（效果优先；用于一次性动画文本，如得分弹出、`GAME OVER`、连击提示）。

规则：信息性文本使用节点方式；效果文本使用绘制方式。

## `draw_string()` 布局注意事项（重要）

- `draw_string()` 的 `position` 是基于基线的，不是基于视觉中心的。
- 使用 `HORIZONTAL_ALIGNMENT_CENTER` 时，`width = -1` 可能不会如预期般居中。
- 对于居中固定文本（如 `GAME OVER`），使用以下方式之一：
  1. 设置 `width = viewport_width` 并居中对齐绘制。
  2. 使用 `font.get_string_size()` 测量文本并手动应用 `x -= width / 2`。
- 使用字体的 ascent/descent 进行正确的垂直居中，而不是将基线当作中心。
- 额外的阴影/描边绘制会将视觉中心偏移到右下角；需补偿合成偏移，或使用对称描边绘制，然后在屏幕上验证最终位置。

### 最小居中模式（GDScript）

```gdscript
var viewport_size := get_viewport_rect().size
var text_size := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size)
var ascent := font.get_ascent(font_size)
var descent := font.get_descent(font_size)
var composite_offset := Vector2.ZERO

# Example: a single positive shadow at Vector2(4, 4) shifts the perceived center.
# Shift the whole composite back by half of the min/max effect offset span.
composite_offset = Vector2(-2, -2)

var baseline := Vector2(
    viewport_size.x * 0.5 - text_size.x * 0.5,
    viewport_size.y * 0.5 + (ascent - descent) * 0.5
) + composite_offset
```

## 推荐的 Godot 目录结构

```text
res://
  assets/fonts/
    UiBase-Regular.ttf
    UiDisplay-Bold.ttf
    UiNumeric-Semibold.ttf
  themes/
    default_theme.tres
  licenses/fonts/
    OFL-UiBase.txt
    LICENSE-UiDisplay.txt
```

## Web 导出过滤

Godot 的 Web 导出预设可能会丢弃非资源文本文件，除非通过"Resources → Filters to export non-resource files/folders"将其包含。要在 Web 构建中保留许可证文本：

- 将 `licenses/fonts/*.txt`（以及在导出中附带的任何 `THIRD_PARTY_LICENSES.md`）添加到导出过滤器。
- 导出后通过检查 `.pck` / `.zip` 内容来重新验证，确认许可证文本存在。

## 交叉引用

- 角色分离、分阶段流程、许可证操作、交付物、审查清单和最终目标视觉检查，见 `typography-implementation-guide.md`。
- 迭代期间使用的 headless Godot CLI 工作流（运行测试、导出、脚本化场景编辑），见同级 `running-headless-godot` 技能。
