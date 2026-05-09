# 游戏平衡日志契约

此数据格式与引擎无关。Godot、Unity、Web、原生或自定义模拟框架均可使用，只要各次运行间的数值可对比。

必需的顶层字段：

```json
{
  "version": "1.0",
  "timestamp_utc": "2026-03-05T12:00:00Z",
  "run_config": {
    "seed_set": [2001, 2002, 2003],
    "fixed_dt": 0.0166667,
    "max_ticks": 3600,
    "policy_budget": "same before and after",
    "input_schema": {
      "primary": {"type": "boolean", "timing": ["pressed", "held", "released"]},
      "move_x": {"type": "axis", "range": [-1, 1], "neutral": 0}
    },
    "visible_state_schema": ["player_position", "hazards", "rewards"],
    "policy_visibility": {
      "hold_action": [],
      "exploratory": ["player_position", "hazards", "rewards"]
    }
  },
  "monotonous": {
    "cases": {
      "no_input": {"score": 0, "elapsed": 4.2, "ended": true},
      "hold_action": {"score": 30, "elapsed": 16.7, "ended": true},
      "spam_action": {"score": 42, "elapsed": 18.1, "ended": true}
    },
    "max_score": 42
  },
  "exploratory": {
    "best": {"score": 95, "elapsed": 24.9, "ended": true},
    "best_seed": 2001,
    "best_variant": 3
  },
  "exploratory_ratio": 2.26,
  "telemetry": {
    "death_analysis": {},
    "spawn_analysis": {},
    "scoring_analysis": {},
    "input_analysis": {}
  }
}
```

策略期望：

- `run_config` 应明确对比条件：种子、固定步长计时或等效的确定性步进、最大时长、策略/搜索预算、公开输入模式、策略可用的可见状态特征，以及策略可见性。
- `input_schema` 应说明每个公开控制的类型、范围或有效值、相关时的中间值、时机语义，以及同时输入约束（当其有意义时）。
- `policy_visibility` 应列出每个策略可以读取的可见状态特征。隐藏状态的访问必须标记为仅限预言机的上限运行。
- `monotonous.cases` 应包含与游戏相关的闲置/无输入和简单重复动作策略。
- `exploratory.best` 应来自多次试验的随机、启发式或搜索策略。
- 探索策略应仅使用公开输入和可见或玩家可推断的状态，除非明确标记为上限预言机。
- `exploratory_ratio` 为 `exploratory.best.score / monotonous.max_score`。
- 如果 `monotonous.max_score` 为零，应以明确约定报告该比率并在分析中解释。
- 遥测的具体内容可能因引擎而异，但应保留四个分析视角。
- 仅包含得分、经过时间和 `exploratory_ratio` 的报告是摘要，不足以做出根本原因层面的平衡判断。

解读指南：

- `<= 1.0`：不通过；单调游玩为最优或持平。
- `1.0-1.5`：需要改进；技巧差异较弱。
- `> 1.5`：通过（作为检测器），需遵守体验护栏。
