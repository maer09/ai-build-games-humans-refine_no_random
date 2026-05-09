# Godot 视觉实现模式

仅在视觉方向已由 `directing-game-visuals` 定义后使用本参考文档。
这些是 Godot 特定的实现示例，而非设计要求。

## 目录

- 渲染方式
- Shader 示例
- 节点与绘制模式
- 反馈模式

## 渲染方式

| 视觉需求 | Godot 实现 |
|:---|:---|
| 轮廓和描边 | `_draw()` 配合 `draw_arc()`、`draw_polyline()`、`draw_line()` |
| 发光和泛光 | `WorldEnvironment` + `Environment.glow_enabled`，或 `ShaderMaterial` |
| 基础几何体 | `_draw()` 基本图形或 `Polygon2D` 节点 |
| 运动可视化 | `_process()` + `_draw()` 中的 GDScript 逻辑，或 `GPUParticles2D` |
| 程序化背景 | `ParallaxBackground` + `ShaderMaterial`，或直接 `_draw()` 循环 |
| 屏幕空间模拟效果 | `CanvasLayer` 上的 `ShaderMaterial` |
| 排版作为游戏几何体 | `Label` / `RichTextLabel`，或 `_draw()` 绘制字形形态 |
| 构图参考线 | 节点定位、`Camera2D` 取景、`Marker2D` 参考线 |

## Shader 示例

```gdshader
// Chromatic offset
shader_type canvas_item;
uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;
uniform float offset_amount : hint_range(0.0, 5.0) = 1.5;

void fragment() {
    vec2 uv = SCREEN_UV;
    float r = texture(screen_texture, uv + vec2(offset_amount / 1000.0, 0.0)).r;
    float g = texture(screen_texture, uv).g;
    float b = texture(screen_texture, uv - vec2(offset_amount / 1000.0, 0.0)).b;
    COLOR = vec4(r, g, b, 1.0);
}
```

```gdshader
// Noise field background
shader_type canvas_item;
uniform float time_scale : hint_range(0.1, 5.0) = 1.0;
uniform float grain_intensity : hint_range(0.0, 1.0) = 0.15;

void fragment() {
    float noise = fract(sin(dot(UV + TIME * time_scale, vec2(12.9898, 78.233))) * 43758.5453);
    COLOR = vec4(vec3(noise * grain_intensity), 1.0);
}
```

## 节点与绘制模式

```gdscript
# Impact ripple
class RippleEffect extends Node2D:
    var radius: float = 0.0
    var max_radius: float = 60.0
    var lifetime: float = 0.4
    var age: float = 0.0
    var color: Color = Color.CYAN

    func _process(delta):
        age += delta
        radius = max_radius * (age / lifetime)
        if age >= lifetime:
            queue_free()
        queue_redraw()

    func _draw():
        var alpha = 1.0 - (age / lifetime)
        draw_arc(Vector2.ZERO, radius, 0, TAU, 64, Color(color, alpha), 2.0)
```

```gdscript
# Afterimage trail
var trail_positions: Array[Vector2] = []
const TRAIL_LENGTH = 8

func _process(delta):
    trail_positions.push_front(global_position)
    if trail_positions.size() > TRAIL_LENGTH:
        trail_positions.resize(TRAIL_LENGTH)
    queue_redraw()

func _draw():
    for i in range(trail_positions.size()):
        var alpha = 1.0 - float(i) / TRAIL_LENGTH
        var size = base_size * (1.0 - float(i) / TRAIL_LENGTH * 0.5)
        draw_circle(to_local(trail_positions[i]), size, Color(color, alpha * 0.4))
```

```gdscript
# Flow lines
var flow_particles: Array[Dictionary] = []

func _ready():
    for i in range(40):
        flow_particles.append({
            "pos": Vector2(randf() * get_viewport_rect().size.x,
                          randf() * get_viewport_rect().size.y),
            "speed": randf_range(20.0, 60.0),
            "length": randf_range(10.0, 30.0),
        })

func _process(delta):
    for p in flow_particles:
        p.pos.x += p.speed * delta
        if p.pos.x > get_viewport_rect().size.x + p.length:
            p.pos.x = -p.length
            p.pos.y = randf() * get_viewport_rect().size.y
    queue_redraw()

func _draw():
    for p in flow_particles:
        var end = p.pos + Vector2(p.length, 0)
        draw_line(p.pos, end, Color(1, 1, 1, 0.1), 1.0)
```

## 反馈模式

```gdscript
# Screen shake
var shake_intensity := 0.0
var shake_decay := 5.0

func trigger_shake(intensity: float) -> void:
    shake_intensity = intensity

func _process(delta: float) -> void:
    if shake_intensity > 0.1:
        offset = Vector2(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0)) * shake_intensity
        shake_intensity = lerpf(shake_intensity, 0.0, shake_decay * delta)
    else:
        offset = Vector2.ZERO
        shake_intensity = 0.0
```

```gdscript
# Pulse or breathe animation
var base_scale := Vector2.ONE
var pulse_speed := 2.0
var pulse_amount := 0.05

func _process(delta: float) -> void:
    var t := sin(Time.get_ticks_msec() / 1000.0 * pulse_speed) * pulse_amount
    scale = base_scale * (1.0 + t)
```

```gdscript
# Smooth palette shift on state change
var target_color := Color.WHITE
var current_color := Color.WHITE
const COLOR_LERP_SPEED := 4.0

func set_state_color(new_color: Color) -> void:
    target_color = new_color

func _process(delta: float) -> void:
    current_color = current_color.lerp(target_color, COLOR_LERP_SPEED * delta)
    modulate = current_color
```

```gdscript
# Flash on hit
func flash_hit() -> void:
    modulate = Color(3.0, 3.0, 3.0, 1.0)
    var tween := create_tween()
    tween.tween_property(self, "modulate", Color.WHITE, 0.15)
```
