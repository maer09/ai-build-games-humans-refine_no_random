---
name: creating-godot-procedural-audio
description: "为 Godot 游戏设计和实现程序化音频。在需要使用 Godot 内置音频 API 创建运行时 SFX、将游戏事件映射到音色，或避免使用外部音频资源时使用此技能。"
---

此技能用于在项目内部通过合成或生成方式产生音频的 Godot 游戏音效。

默认产出物：
- 如果已知项目目录，将完整的音频方案写入 `<PROJECT_DIR>/SOUND_DESIGN.md`。
- 如果项目 README 中已有"视觉与音频方向"或"所需音效"章节，保持为简短摘要，仅在音频方向变更时更新。
- 通过小型项目专用模块实现，例如 `<PROJECT_DIR>/audio_controller.gd`；保持 `main.gd` 作为编排层。
- 复用 `.agents/skills/creating-godot-procedural-audio/assets/audio_synth.gd` 或模板中已有的 `audio_synth.gd` 基元。仅在项目中缺失或存在实质性差异时才复制该辅助模块。
- 如果视觉标签是项目特定或概念衍生的（而非指南中的精确条目），按最接近的材料、几何、运动或氛围族进行映射，并将该映射记录在 `SOUND_DESIGN.md` 中。
- 持续音效应暴露最小控制接口：`start_<sound>()`、`update_<sound>(params)`、`release_<sound>()` 和 `stop_<sound>()`。Headless/空操作句柄必须保持相同的调用签名，以便测试可以在不播放的情况下验证状态转换。

核心规则：
- 仅使用 Godot 内置音频；除非项目明确允许，否则避免使用外部音频文件。
- 事件族在单个游戏内保持语义稳定：得分、危险、伤害和状态变化应有不同的音色特征。
- 在不同游戏之间变换波形、音高范围、包络、调制、节奏和密度，而不是复用全局蜂鸣词汇。
- 持续音效需要明确的启动、停止和释放行为。
- 在可能的情况下优先使用简单的生成采样流；仅在需要实时合成时使用 `AudioStreamGenerator`。

工作流程：
1. 从视觉方向和机制中推导音效特征。
2. 选择 1-2 种基础波形及调制方法。
3. 定义事件到音色的映射。
4. 链接动态参数（连击 / 速度 / 危险 / 难度），使其在听觉上至少调制一个事件，而不仅仅是分数数字。
5. 通过小型音频职责模块实现。

阅读 `references/sound-design-guide.md` 获取事件目录、程序化音频模式和设计检查清单。
可复用的基元位于 `assets/audio_synth.gd`。

## 配套技能

- `directing-game-visuals` 产出 `<PROJECT_DIR>/VISUAL_DESIGN.md`，音效特征应从中推导。
- `scaffolding-godot-mini-games` 附带上述引用的模板 `audio_synth.gd`；仅在项目中不存在模板副本时才复制此技能的 `assets/audio_synth.gd`。
