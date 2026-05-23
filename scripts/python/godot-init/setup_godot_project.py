#!/usr/bin/env python3
"""
Godot 项目初始化开发设置脚本。

自动化执行以下步骤：
1. 合并 GDScript 严格类型检查和警告配置到 project.godot
2. 添加 Gopeak MCP 配置到 opencode.json
3. 安装 Gopeak Godot MCP 编辑器插件
4. 自动启用已安装的插件（写入 project.godot）

用法：
    python setup_godot_project.py [项目目录]

如果不指定项目目录，默认使用脚本所在目录。
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# ─── 配置数据 ──────────────────────────────────────────────────────────────────

# Gopeak MCP 配置
GOPEAK_MCP_CONFIG = {
    "godot": {
        "type": "local",
        "command": ["npx", "-y", "gopeak"],
        "environment": {
            "GOPEAK_TOOL_PROFILE": "full"
        },
        "enabled": True
    }
}

# Godot LSP 配置
GODOT_LSP_CONFIG = {
    "godot": {
        "command": ["godot-lsp-bridge.cmd"],
        "extensions": [".gd"]
    }
}

# Gopeak 插件安装命令
GOPEAK_INSTALL_PS1 = (
    'iwr https://raw.githubusercontent.com/HaD0Yun/Gopeak-godot-mcp/main/install-addon.ps1 '
    '-OutFile "$env:TEMP\\install-addon.ps1" -UseBasicParsing; '
    '& "$env:TEMP\\install-addon.ps1" -Force'
)


# ─── 步骤 1: 合并 GDScript 警告到 project.godot ────────────────────────────────

# 按分组顺序定义的警告键列表（控制输出顺序和注释插入）
_WARNINGS_ORDERED = [
    ("gdscript/warnings/enable", "true", "; 启用警告系统"),
    ("gdscript/warnings/exclude_addons", "true", "; 跳过 addons/ 目录（第三方插件不检查）"),
    # 类型安全 — ERROR (level 2)
    ("gdscript/warnings/incompatible_ternary", "2", "; ====== 类型安全 — ERROR ======"),
    ("gdscript/warnings/untyped_declaration", "2", None),
    ("gdscript/warnings/inferred_declaration", "2", None),
    ("gdscript/warnings/unsafe_property_access", "2", None),
    ("gdscript/warnings/unsafe_method_access", "2", None),
    ("gdscript/warnings/unsafe_cast", "2", None),
    ("gdscript/warnings/unsafe_call_argument", "2", None),
    ("gdscript/warnings/narrowing_conversion", "2", None),
    ("gdscript/warnings/redundant_static_unreachable", "2", None),
    # 代码质量 — WARN (level 1)
    ("gdscript/warnings/empty_assignment", "1", "; ====== 代码质量 — WARN ======"),
]

# 用于快速查找期望值的 dict
GDSCRIPT_WARNINGS = {key: val for key, val, _ in _WARNINGS_ORDERED}


def _build_debug_section_lines() -> list[str]:
    """按分组顺序生成完整的 [debug] section 内容行。"""
    result = ["\n"]
    for key, value, comment in _WARNINGS_ORDERED:
        if comment:
            result.append(comment + "\n")
        result.append(f"{key}={value}\n")
    return result


def merge_project_godot(project_dir: Path) -> None:
    """将 GDScript 严格类型检查和警告配置写入 project.godot。

    策略：重建式 — 移除旧 [debug] 中所有 gdscript/warnings/* 行，
    写入干净的有序集合。完全幂等。
    """
    godot_file = project_dir / "project.godot"

    if godot_file.exists():
        raw = godot_file.read_text(encoding="utf-8")
        print(f"[1/4] read {godot_file}")
    else:
        raw = ""
        print(f"[1/4] {godot_file} not found, will create")

    lines = raw.splitlines(True)  # keep line endings

    # 定位 [debug] section 范围
    has_debug_section = False
    debug_start = -1
    debug_end = len(lines)

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower() == "[debug]":
            has_debug_section = True
            debug_start = i
        elif has_debug_section and stripped.startswith("[") and stripped.endswith("]"):
            debug_end = i
            break

    # 检查现有 [debug] 内容是否已经与目标完全一致
    desired_lines = _build_debug_section_lines()
    if has_debug_section:
        current_debug_lines = lines[debug_start + 1:debug_end]
        # 只比较有内容的行（忽略空行和注释）
        current_kv = {}
        for cl in current_debug_lines:
            s = cl.strip()
            if s and not s.startswith(";") and "=" in s:
                k, _, v = s.partition("=")
                current_kv[k.strip()] = v.strip()

        if current_kv == GDSCRIPT_WARNINGS:
            print("      GDScript warnings already up-to-date")
            return

        # 移除旧 [debug] section 中所有 gdscript/warnings/* 行（含其上方注释）
        # 从后往前删以保持索引稳定
        lines_to_delete = set()
        for i in range(debug_start + 1, debug_end):
            s = lines[i].strip()
            if s.startswith("gdscript/warnings/"):
                lines_to_delete.add(i)

        # 也删除紧邻这些行的上方注释行（以 ; 开头，且与下一个非注释行之间无空行）
        for i in range(debug_start + 1, debug_end):
            if i in lines_to_delete:
                continue
            s = lines[i].strip()
            if s.startswith(";"):
                # 检查下方是否紧接一个被删的 key 行
                j = i + 1
                while j < debug_end and lines[j].strip() == "":
                    j += 1
                if j < debug_end and j in lines_to_delete:
                    lines_to_delete.add(i)

        # 执行删除（逆序）
        for i in sorted(lines_to_delete, reverse=True):
            del lines[i]
            if has_debug_section and i < debug_end:
                debug_end -= 1

        # 在 [debug] section 尾部（调整后的 debug_end）插入新内容
        # 重新定位 debug_end（删除行后位置可能变了）
        new_debug_end = debug_end
        for i in range(debug_start + 1, len(lines)):
            s = lines[i].strip()
            if s.startswith("[") and s.endswith("]"):
                new_debug_end = i
                break
        else:
            new_debug_end = len(lines)

        # 确保插入前有空行分隔
        insert_lines = list(desired_lines)
        if new_debug_end > debug_start + 1 and lines[new_debug_end - 1].strip():
            insert_lines.insert(0, "\n")

        for j, nl in enumerate(insert_lines):
            lines.insert(new_debug_end + j, nl)
    else:
        # 没有 [debug] section，追加到文件末尾
        lines.append("\n[debug]")
        lines.extend(desired_lines)

    godot_file.write_text("".join(lines), encoding="utf-8")
    print(f"      OK wrote {len(GDSCRIPT_WARNINGS)} GDScript warnings")


# ─── 步骤 2: 添加 Gopeak MCP 到 opencode.json ────────────────────────────────

def setup_opencode_mcp(project_dir: Path) -> None:
    """创建或更新 opencode.json，添加 Gopeak MCP 配置。"""
    opencode_file = project_dir / "opencode.json"

    if opencode_file.exists():
        with open(opencode_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"[2/3] read {opencode_file}")
    else:
        config = {}
        print(f"[2/3] {opencode_file} not found, will create")

    # 确保 mcp 字段存在
    if "mcp" not in config:
        config["mcp"] = {}

    # 检查 MCP 是否已配置
    mcp_changed = False
    if config["mcp"].get("godot") == GOPEAK_MCP_CONFIG["godot"]:
        print("      Gopeak MCP already configured, skipping")
    else:
        config["mcp"]["godot"] = GOPEAK_MCP_CONFIG["godot"]
        mcp_changed = True
        print("      OK wrote Gopeak MCP config")

    # 确保 lsp 字段存在
    if "lsp" not in config:
        config["lsp"] = {}

    # 检查 LSP 是否已配置
    lsp_changed = False
    if config["lsp"].get("godot") == GODOT_LSP_CONFIG["godot"]:
        print("      Godot LSP already configured, skipping")
    else:
        config["lsp"]["godot"] = GODOT_LSP_CONFIG["godot"]
        lsp_changed = True
        print("      OK wrote Godot LSP config")

    if mcp_changed or lsp_changed:
        with open(opencode_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


# ─── 步骤 3: 安装 Gopeak Godot MCP 插件 ──────────────────────────────────────

def install_gopeak_addon(project_dir: Path) -> bool:
    """通过 PowerShell 安装 Gopeak Godot MCP 编辑器插件。

    Returns:
        True if installation succeeded (or was already done), False otherwise.
    """
    addons_dir = project_dir / "addons"

    # 检查是否已经安装过
    if addons_dir.is_dir() and (addons_dir / "godot_mcp_editor" / "plugin.cfg").exists():
        print("[3/4] Gopeak MCP addon already installed, skipping download")
        return True

    print("[3/4] installing Gopeak Godot MCP addon...")
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", GOPEAK_INSTALL_PS1],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print("      OK plugin installed")
            if result.stdout.strip():
                for line in result.stdout.strip().splitlines():
                    print(f"        {line}")
            return True
        else:
            print(f"      FAIL install failed (exit code {result.returncode})")
            if result.stderr.strip():
                print(f"      error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print("      TIMEOUT (120s)")
        return False
    except FileNotFoundError:
        print("      FAIL PowerShell not found, run manually:")
        print(f"      {GOPEAK_INSTALL_PS1}")
        return False


# ─── 步骤 4: 自动启用插件 ──────────────────────────────────────────────────────

def enable_plugins(project_dir: Path) -> None:
    """扫描 addons/ 目录下的 plugin.cfg，将它们写入 project.godot 的 [editor_plugins]。

    Godot 4 格式：
        [editor_plugins]
        enabled=PackedStringArray("res://addons/foo/plugin.cfg", "res://addons/bar/plugin.cfg")
    """
    addons_dir = project_dir / "addons"
    godot_file = project_dir / "project.godot"

    if not addons_dir.is_dir():
        print("[4/4] SKIP no addons/ directory found")
        return

    # 扫描所有 addon 的 plugin.cfg
    plugin_paths = []
    for plugin_cfg in sorted(addons_dir.glob("*/plugin.cfg")):
        addon_name = plugin_cfg.parent.name
        plugin_paths.append(f"res://addons/{addon_name}/plugin.cfg")

    if not plugin_paths:
        print("[4/4] SKIP no plugin.cfg found in addons/")
        return

    # 构建 Godot PackedStringArray 值
    # 格式: PackedStringArray("res://addons/a/plugin.cfg", "res://addons/b/plugin.cfg")
    packed = "PackedStringArray(" + ", ".join(f'"{p}"' for p in plugin_paths) + ")"
    target_line = f"enabled={packed}\n"

    # 解析 project.godot
    raw = godot_file.read_text(encoding="utf-8") if godot_file.exists() else ""
    lines = raw.splitlines(True)

    # 查找 [editor_plugins] section
    has_section = False
    section_start = -1
    section_end = len(lines)

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower() == "[editor_plugins]":
            has_section = True
            section_start = i
        elif has_section and stripped.startswith("[") and stripped.endswith("]"):
            section_end = i
            break

    if has_section:
        # 检查已有的 enabled= 行
        for i in range(section_start + 1, section_end):
            if lines[i].strip().startswith("enabled="):
                old_value = lines[i].strip()
                if old_value == target_line.strip():
                    print(f"[4/4] plugins already enabled in project.godot")
                    return
                # 更新已有行
                lines[i] = target_line
                godot_file.write_text("".join(lines), encoding="utf-8")
        names = [p.split("/")[3] for p in plugin_paths]
        print(f"[4/4] OK updated plugins in project.godot: {', '.join(names)}")
        return

        # section 存在但没有 enabled= 行，在 section 头之后插入
        lines.insert(section_start + 1, target_line)
        godot_file.write_text("".join(lines), encoding="utf-8")
        names = [p.split("/")[3] for p in plugin_paths]
        print(f"[4/4] OK enabled plugins in project.godot: {', '.join(names)}")
    else:
        # 不存在 [editor_plugins] section，追加到文件末尾
        if lines and lines[-1].strip():
            lines.append("\n")
        lines.append("[editor_plugins]\n")
        lines.append(target_line)
        godot_file.write_text("".join(lines), encoding="utf-8")
        names = [p.split("/")[3] for p in plugin_paths]
        print(f"[4/4] OK enabled plugins in project.godot: {', '.join(names)}")


# ─── 主入口 ─────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Godot project init: GDScript warnings + Gopeak MCP + plugin auto-enable",
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=os.getcwd(),
        help="Godot project directory (default: current working directory)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.is_dir():
        print(f"ERROR: not a directory: {project_dir}")
        sys.exit(1)

    print("Godot project init setup")
    print(f"project dir: {project_dir}")
    print()

    merge_project_godot(project_dir)
    setup_opencode_mcp(project_dir)
    install_ok = install_gopeak_addon(project_dir)

    if install_ok:
        enable_plugins(project_dir)
    else:
        print()
        print("[4/4] SKIP plugin enabling (installation failed or skipped)")

    print()
    print("Done!")
    if install_ok:
        print("  Open project in Godot Editor - plugins are already enabled.")
    else:
        print("  1. Run plugin install manually (see command above)")
        print("  2. Open project in Godot Editor")
        print("  3. Go to Project Settings -> Plugins, enable plugins")


if __name__ == "__main__":
    main()
