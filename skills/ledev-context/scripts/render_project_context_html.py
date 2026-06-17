#!/usr/bin/env python3
"""Render ledev-context project HTML from a fixed template and JSON data."""

from __future__ import annotations

import argparse
import shutil
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PLACEHOLDER_RE = re.compile(r"{{([A-Z0-9_]+)}}")
HTML_BACKUP_RE = re.compile(r"^project-context\.[0-9]{8}-[0-9]{6}(?:-[0-9]+)?\.html$")
MAX_HTML_BACKUPS = 5
TRUSTED_HTML_PLACEHOLDERS = {
    "BUSINESS_FLOWS_HTML",
    "CONFIGURATION_HTML",
    "DEPENDENCIES_HTML",
    "MODEL_HTML",
    "ONBOARDING_HTML",
    "PROJECT_CONVENTIONS_HTML",
    "PROJECT_SPECIFICS_HTML",
    "RECOVERY_HTML",
    "SECURITY_HTML",
}

REQUIRED_SECTIONS = [
    "overview",
    "architecture",
    "business",
    "models",
    "security",
    "dependencies",
    "configuration",
    "onboarding",
    "recovery",
    "conventions",
    "specifics",
]

REQUIRED_DESIGN_MARKERS = [
    ("头部依赖标签", 'class="hero-tags"'),
    ("依赖标签", 'class="hero-tag"'),
    ("核心能力卡", 'class="capability-grid"'),
    ("核心业务流程组", 'class="business-flows"'),
    ("核心业务流程卡", 'class="business-flow"'),
    ("数据模型块", 'class="model-blocks"'),
    ("数据模型图", 'class="diagram model-er-diagram"'),
    ("状态机图", 'class="diagram state-machine-diagram"'),
    ("图表无障碍摘要", 'class="sr-only diagram-summary"'),
    ("Mermaid 失败提示", 'class="mermaid-fallback"'),
    ("安全结构块", 'class="security-blocks"'),
    ("业务安全表", "security-controls"),
    ("加密场景表", "crypto-scenarios"),
    ("依赖链路图", 'class="diagram dependency-diagram"'),
    ("配置项表", "configuration-controls"),
    ("新人快速上手", "onboarding-tasks"),
    ("故障恢复表", "recovery-scenarios"),
    ("恢复设计原则", "recovery-principles"),
    ("项目约定列表", "project-conventions"),
    ("项目特化矩阵", "project-specifics"),
    ("事实拓扑", 'class="arch-html"'),
    ("架构中段", 'class="arch-mid"'),
    ("架构中心", 'class="arch-engine"'),
    ("架构中心头部", 'class="arch-engine-head"'),
    ("架构能力格", 'class="arch-engine-grid"'),
    ("架构节点", 'class="arch-node"'),
    ("架构底部服务行", 'class="arch-svc-row"'),
    ("confirmed 状态样式", ".badge.confirmed"),
    ("inferred 状态样式", ".badge.inferred"),
    ("risk 状态样式", ".badge.risk"),
    ("open 状态样式", ".badge.open"),
    ("快速动效 token", "--motion-fast"),
    ("中速动效 token", "--motion-med"),
    ("动效曲线 token", "--ease-standard"),
    ("章节节奏 token", "--section-gap"),
    ("减少动态偏好", "@media (prefers-reduced-motion: reduce)"),
]

FORBIDDEN_MOTION_MARKERS = [
    "scroll-reveal",
    "reveal-on-scroll",
    "parallax",
    "infinite",
    "marquee",
]

FORBIDDEN_INTERNAL_HTML_LABELS = [
    "事实层状态",
    "上下文类型",
    "阶段性上下文来源",
    "证据",
    "evidence-index",
    "Evidence",
]

ARCHITECTURE_TEXT_LIMITS = {
    "LEFT_TIER_TITLE": 12,
    "LEFT_TIER_ITEM_1": 28,
    "LEFT_TIER_ITEM_1_NOTE": 16,
    "LEFT_TIER_FLOW": 12,
    "LEFT_TIER_ITEM_2": 28,
    "LEFT_TIER_ITEM_2_NOTE": 16,
    "ENGINE_NAME": 32,
    "ENGINE_RUNTIME_SHAPE": 16,
    "ENGINE_CAPABILITY_1": 16,
    "ENGINE_CAPABILITY_2": 16,
    "ENGINE_CAPABILITY_3": 16,
    "ENGINE_CAPABILITY_4": 16,
    "RIGHT_TIER_TITLE": 12,
    "RIGHT_TIER_ITEM_1": 28,
    "RIGHT_TIER_ITEM_1_NOTE": 16,
    "RIGHT_TIER_FLOW": 12,
    "RIGHT_TIER_ITEM_2": 28,
    "RIGHT_TIER_ITEM_2_NOTE": 16,
    "BOTTOM_TIER_TITLE": 12,
    "BOTTOM_TIER_ITEM_1": 24,
    "BOTTOM_TIER_ITEM_1_NOTE": 16,
    "BOTTOM_TIER_ITEM_2": 24,
    "BOTTOM_TIER_ITEM_2_NOTE": 16,
    "BOTTOM_TIER_ITEM_3": 24,
    "BOTTOM_TIER_ITEM_3_NOTE": 16,
    "BOTTOM_TIER_ITEM_4": 24,
    "BOTTOM_TIER_ITEM_4_NOTE": 16,
}

ARCHITECTURE_FORBIDDEN_PATTERNS = [
    re.compile(r"\.ai/|\.md\b|:[0-9]+|QA-[0-9]+", re.IGNORECASE),
    re.compile(r"go\.mod|Makefile|\.gitlab-ci|CI\b|lint|test|测试|dev/example|dev scripts", re.IGNORECASE),
    re.compile(r"generated|third[-_ ]party|vendor", re.IGNORECASE),
]

ARCHITECTURE_FLOW_KEYS = {
    "LEFT_TIER_FLOW",
    "RIGHT_TIER_FLOW",
}

ARCHITECTURE_NOTE_KEYS = {
    key for key in ARCHITECTURE_TEXT_LIMITS if key.endswith("_NOTE")
}

ARCHITECTURE_BOTTOM_KEYS = {
    key for key in ARCHITECTURE_TEXT_LIMITS if key.startswith("BOTTOM_TIER_ITEM_")
}

BUSINESS_PARTICIPANT_TYPES = {
    "external_trigger",
    "system",
    "downstream",
    "business_middleware",
}

BUSINESS_PARTICIPANT_TYPE_LABELS = {
    "external_trigger": "外部触发源",
    "system": "本系统",
    "downstream": "直接下游",
    "business_middleware": "业务中间件",
}

BUSINESS_FORBIDDEN_PARTICIPANT_PATTERNS = [
    re.compile(r"(Controller|Service|Svc|Task|Cache|Util|Manager|Interceptor|Filter|Helper|Notify)$", re.IGNORECASE),
    re.compile(r"DB|MySQL|PostgreSQL|Apollo|Nacos|Consul|ZooKeeper|Eureka|Prometheus|Grafana|SkyWalking|Sentinel", re.IGNORECASE),
]

MERMAID_KEYWORDS = {
    "alt",
    "and",
    "autonumber",
    "activate",
    "actor",
    "box",
    "break",
    "critical",
    "deactivate",
    "end",
    "loop",
    "note",
    "opt",
    "par",
    "participant",
    "rect",
    "title",
}

MODEL_FORBIDDEN_PATTERNS = [
    re.compile(r"\.ai/|\.md\b|:[0-9]+|QA-[0-9]+", re.IGNORECASE),
    re.compile(r"证据|evidence|file:|line:", re.IGNORECASE),
]

SECURITY_FORBIDDEN_PATTERNS = [
    re.compile(r"\.ai/|\.md\b|:[0-9]+|QA-[0-9]+", re.IGNORECASE),
    re.compile(r"证据|evidence|file:|line:", re.IGNORECASE),
    re.compile(r"(APP|API|ACCESS|SECRET|TOKEN|KEY|PWD|PASSWORD|AK|SK)[A-Z0-9_]{2,}", re.IGNORECASE),
    re.compile(r"\b(AES|RSA|ECDSA|Ed25519|SHA-?256|SHA-?512|HMAC|CBC|GCM|PKCS|padding|IV|密钥长度|迭代次数)\b", re.IGNORECASE),
]

CONFIG_FORBIDDEN_PATTERNS = [
    re.compile(r"MAX_WITHDRAW_AMOUNT|COMPOSITE_AMOUNT|TX_CONFIRM_UPBOUND", re.IGNORECASE),
    re.compile(r"阈值|上限|下限|批大小|金额|数量|纯业务调参"),
    re.compile(r"(APP|API|ACCESS|SECRET|TOKEN|KEY|PWD|PASSWORD|AK|SK)[A-Z0-9_]{2,}", re.IGNORECASE),
]

RECOVERY_FORBIDDEN_PATTERNS = [
    re.compile(r"Bug|TODO|FIXME|缺陷|待修复|代码问题|实现缺陷", re.IGNORECASE),
    re.compile(r"@Transactional|NullPointerException|panic|stack trace", re.IGNORECASE),
]

DEPENDENCY_DIRECTIONS = {
    "upstream",
    "downstream",
    "third-party",
    "internal",
    "runtime",
    "data-store",
    "internal-business",
    "未确认",
}

DEPENDENCY_FORBIDDEN_PATTERNS = [
    re.compile(r"go\.mod|Makefile|\.gitlab-ci|CI\b|lint|test|测试|dev/example|dev scripts", re.IGNORECASE),
    re.compile(r"generated|third[-_ ]party\s*目录|vendor\s*目录", re.IGNORECASE),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render .ai/project-context.html from project-context-html-template.html and JSON placeholders.",
    )
    parser.add_argument("--template", required=True, type=Path, help="HTML template path.")
    parser.add_argument("--data", type=Path, help="JSON data path.")
    parser.add_argument("--out", type=Path, help="Output HTML path.")
    parser.add_argument(
        "--print-placeholders",
        action="store_true",
        help="Print placeholders required by the HTML template and exit.",
    )
    parser.add_argument(
        "--fill-missing",
        default=None,
        help="Fill missing placeholders with this text instead of failing.",
    )
    parser.add_argument(
        "--no-escape",
        action="store_true",
        help="Do not HTML-escape placeholder values. Use only for trusted HTML snippets.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON 格式错误：{path}:{exc.lineno}:{exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"JSON 顶层必须是对象：{path}")
    return data


def normalize_placeholders(data: dict[str, Any]) -> dict[str, str]:
    raw = data.get("placeholders", data)
    if not isinstance(raw, dict):
        raise SystemExit("JSON 中的 placeholders 必须是对象。")

    placeholders: dict[str, str] = {}
    for key, value in raw.items():
        normalized_key = str(key).upper()
        if isinstance(value, (dict, list)):
            placeholders[normalized_key] = json.dumps(value, ensure_ascii=False, indent=2)
        elif value is None:
            placeholders[normalized_key] = ""
        else:
            placeholders[normalized_key] = str(value)
    return placeholders


def render_template(
    template: str,
    placeholders: dict[str, str],
    *,
    fill_missing: str | None,
    escape_values: bool,
    trusted_html_placeholders: set[str] | None = None,
) -> tuple[str, list[str]]:
    trusted_html_placeholders = trusted_html_placeholders or set()
    required = sorted(set(PLACEHOLDER_RE.findall(template)))
    missing = [name for name in required if name not in placeholders]
    if missing and fill_missing is None:
        preview = ", ".join(missing[:20])
        suffix = "" if len(missing) <= 20 else f" ... 共 {len(missing)} 个"
        raise SystemExit(f"缺少模板占位符：{preview}{suffix}")

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        value = placeholders.get(name, fill_missing or "")
        if name in trusted_html_placeholders:
            return value
        if escape_values:
            return html.escape(value, quote=True)
        return value

    return PLACEHOLDER_RE.sub(replace, template), missing


def as_text(value: Any, fallback: str = "未确认") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def escape_text(value: Any, fallback: str = "未确认") -> str:
    return html.escape(as_text(value, fallback), quote=True)


def status_badge_class(value: Any, fallback: str = "open") -> str:
    text = as_text(value, fallback).lower()
    if any(token in text for token in ("confirmed", "已确认", "事实", "明确")):
        return "confirmed"
    if any(token in text for token in ("risk", "风险", "warning", "warn")):
        return "risk"
    if any(token in text for token in ("inferred", "推断", "assumption", "假设")):
        return "inferred"
    if any(token in text for token in ("open", "question", "未确认", "待确认", "未发现")):
        return "open"
    return fallback


def as_text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [as_text(item, "") for item in value if as_text(item, "")]
    text = as_text(value, "")
    if not text:
        return []
    return [part.strip() for part in re.split(r"[，,、/]\s*", text) if part.strip()]


def validate_model_text(label: str, value: Any, problems: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            validate_model_text(f"{label}.{key}", item, problems)
        return
    if isinstance(value, list):
        for index, item in enumerate(value, start=1):
            validate_model_text(f"{label}[{index}]", item, problems)
        return
    text = as_text(value, "")
    for pattern in MODEL_FORBIDDEN_PATTERNS:
        if pattern.search(text):
            problems.append(f"{label} 不应包含证据、路径或内部索引：{text[:40]}")
            break


def validate_security_text(label: str, value: Any, problems: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            validate_security_text(f"{label}.{key}", item, problems)
        return
    if isinstance(value, list):
        for index, item in enumerate(value, start=1):
            validate_security_text(f"{label}[{index}]", item, problems)
        return
    text = as_text(value, "")
    for pattern in SECURITY_FORBIDDEN_PATTERNS:
        if pattern.search(text):
            problems.append(f"{label} 不应包含证据、路径、具体凭据名或算法参数明细：{text[:40]}")
            break


def validate_dependency_text(label: str, value: Any, problems: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            validate_dependency_text(f"{label}.{key}", item, problems)
        return
    if isinstance(value, list):
        for index, item in enumerate(value, start=1):
            validate_dependency_text(f"{label}[{index}]", item, problems)
        return
    text = as_text(value, "")
    for pattern in DEPENDENCY_FORBIDDEN_PATTERNS:
        if pattern.search(text):
            problems.append(f"{label} 不应包含工程支撑或代码边界依赖：{text[:50]}")
            break


def validate_config_text(label: str, value: Any, problems: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            validate_config_text(f"{label}.{key}", item, problems)
        return
    if isinstance(value, list):
        for index, item in enumerate(value, start=1):
            validate_config_text(f"{label}[{index}]", item, problems)
        return
    text = as_text(value, "")
    for pattern in CONFIG_FORBIDDEN_PATTERNS:
        if pattern.search(text):
            problems.append(f"{label} 不应进入 HTML 配置项：{text[:50]}")
            break


def validate_recovery_text(label: str, value: Any, problems: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            validate_recovery_text(f"{label}.{key}", item, problems)
        return
    if isinstance(value, list):
        for index, item in enumerate(value, start=1):
            validate_recovery_text(f"{label}[{index}]", item, problems)
        return
    text = as_text(value, "")
    for pattern in RECOVERY_FORBIDDEN_PATTERNS:
        if pattern.search(text):
            problems.append(f"{label} 不应把实现缺陷或 Bug 写入 HTML 故障恢复：{text[:50]}")
            break


def build_configuration_html(data: dict[str, Any], *, skip_validation: bool = False) -> str:
    controls = data.get("configuration_controls", [])
    if skip_validation and (not isinstance(controls, list) or not controls):
        controls = [
            {
                "name": "安全开关",
                "purpose": "控制外部调用安全校验是否启用。",
                "source": "配置中心或环境配置。",
                "scope": "外部调用入口。",
                "security_impact": "关闭后请求来源或内容完整性无法确认。",
                "failure": "拒绝请求或进入安全异常处理。",
            }
        ]

    problems: list[str] = []
    if not isinstance(controls, list):
        controls = []
        problems.append("configuration_controls 必须是数组。")

    validate_config_text("configuration_controls", controls, problems)

    rows: list[str] = []
    for index, raw_control in enumerate(controls, start=1):
        if not isinstance(raw_control, dict):
            problems.append(f"configuration_controls[{index}] 必须是对象。")
            continue
        rows.append(
            "<tr>"
            f"<td><code>{escape_text(raw_control.get('name'), '未确认：配置项')}</code></td>"
            f"<td>{escape_text(raw_control.get('purpose'), '未确认：作用')}</td>"
            f"<td>{escape_text(raw_control.get('source'), '未确认：来源')}</td>"
            f"<td>{escape_text(raw_control.get('scope'), '未确认：影响范围')}</td>"
            f"<td>{escape_text(raw_control.get('security_impact'), '未确认：安全影响')}</td>"
            f"<td>{escape_text(raw_control.get('failure'), '未确认：错误配置后果')}</td>"
            "</tr>"
        )
    if not rows:
        rows.append("<tr><td>未发现：安全相关配置项</td><td>未确认</td><td>未确认</td><td>未确认</td><td>未确认</td><td>未确认</td></tr>")

    if problems:
        preview = "\n".join(f"- {item}" for item in problems[:12])
        suffix = "" if len(problems) <= 12 else f"\n... 共 {len(problems)} 个问题"
        raise SystemExit(f"HTML 配置项自检失败：\n{preview}{suffix}")

    return (
        '<div class="table-wrap configuration-controls">'
        "<table><thead><tr>"
        "<th>配置项</th><th>作用</th><th>来源</th><th>影响范围</th><th>安全影响</th><th>错误配置后果</th>"
        "</tr></thead><tbody>"
        f'{"".join(rows)}'
        "</tbody></table></div>"
    )


def build_onboarding_html(data: dict[str, Any], *, skip_validation: bool = False) -> str:
    tasks = data.get("onboarding_tasks", [])
    reading_path = data.get("onboarding_reading_path", [])
    if skip_validation and (not isinstance(tasks, list) or not tasks):
        tasks = [
            {
                "task": "理解系统做什么",
                "entry": "项目概述",
                "scenario": "第一次阅读项目。",
                "note": "先建立业务边界，再看流程。",
            },
            {
                "task": "查运行问题",
                "entry": "故障与恢复",
                "scenario": "线上或本地运行异常。",
                "note": "先看观测信号和恢复方式。",
            },
        ]
    if skip_validation and (not isinstance(reading_path, list) or not reading_path):
        reading_path = ["项目定位", "架构", "核心业务", "配置项", "故障与恢复"]

    problems: list[str] = []
    if not isinstance(tasks, list):
        tasks = []
        problems.append("onboarding_tasks 必须是数组。")
    if not isinstance(reading_path, list):
        reading_path = []
        problems.append("onboarding_reading_path 必须是数组。")

    task_cards: list[str] = []
    for index, raw_task in enumerate(tasks, start=1):
        if not isinstance(raw_task, dict):
            problems.append(f"onboarding_tasks[{index}] 必须是对象。")
            continue
        task_cards.append(
            '<article class="panel">'
            f"<h3>{escape_text(raw_task.get('task'), '未确认：上手任务')}</h3>"
            f"<p>{escape_text(raw_task.get('entry'), '未确认：推荐入口')}</p>"
            '<dl class="model-meta">'
            f"<div><dt>场景</dt><dd>{escape_text(raw_task.get('scenario'), '未确认：适用场景')}</dd></div>"
            f"<div><dt>注意</dt><dd>{escape_text(raw_task.get('note'), '未确认：注意事项')}</dd></div>"
            "</dl>"
            "</article>"
        )
    if not task_cards:
        task_cards.append('<article class="panel"><h3>未确认：上手任务</h3><p>未确认：推荐入口</p></article>')

    path_items = "".join(f"<li>{escape_text(item)}</li>" for item in reading_path) or "<li>未确认：阅读路径</li>"

    if problems:
        preview = "\n".join(f"- {item}" for item in problems[:12])
        suffix = "" if len(problems) <= 12 else f"\n... 共 {len(problems)} 个问题"
        raise SystemExit(f"HTML 新人快速上手自检失败：\n{preview}{suffix}")

    return (
        '<div class="grid-2 onboarding-tasks">'
        f'{"".join(task_cards)}'
        "</div>"
        '<div class="callout info onboarding-path">'
        "<strong>建议阅读路径</strong>"
        f"<ol>{path_items}</ol>"
        "</div>"
    )


def build_recovery_html(data: dict[str, Any], *, skip_validation: bool = False) -> str:
    scenarios = data.get("recovery_scenarios", [])
    principles = data.get("recovery_principles", [])
    if skip_validation and (not isinstance(scenarios, list) or not scenarios):
        scenarios = [
            {
                "scenario": "外部依赖不可用",
                "trigger": "下游服务超时或返回失败。",
                "handling": "记录失败并停止当前步骤。",
                "recovery": "等待依赖恢复后重试或人工介入。",
                "signal": "错误日志或失败状态。",
                "impact": "业务结果无法提交到下游。",
            }
        ]
    if skip_validation and (not isinstance(principles, list) or not principles):
        principles = [
            {
                "principle": "超时",
                "scenario": "外部调用。",
                "practice": "限制等待时间，避免请求长期占用资源。",
            },
            {
                "principle": "人工介入",
                "scenario": "自动恢复无法完成。",
                "practice": "保留观测信号，便于人工确认后处理。",
            },
        ]

    problems: list[str] = []
    if not isinstance(scenarios, list):
        scenarios = []
        problems.append("recovery_scenarios 必须是数组。")
    if not isinstance(principles, list):
        principles = []
        problems.append("recovery_principles 必须是数组。")

    validate_recovery_text("recovery_scenarios", scenarios, problems)
    validate_recovery_text("recovery_principles", principles, problems)

    rows: list[str] = []
    for index, raw_scenario in enumerate(scenarios, start=1):
        if not isinstance(raw_scenario, dict):
            problems.append(f"recovery_scenarios[{index}] 必须是对象。")
            continue
        rows.append(
            "<tr>"
            f"<td>{escape_text(raw_scenario.get('scenario'), '未确认：失败场景')}</td>"
            f"<td>{escape_text(raw_scenario.get('trigger'), '未确认：触发条件')}</td>"
            f"<td>{escape_text(raw_scenario.get('handling'), '未确认：当前处理')}</td>"
            f"<td>{escape_text(raw_scenario.get('recovery'), '未确认：恢复方式')}</td>"
            f"<td>{escape_text(raw_scenario.get('signal'), '未确认：观测信号')}</td>"
            f"<td>{escape_text(raw_scenario.get('impact'), '未确认：失败影响')}</td>"
            "</tr>"
        )
    if not rows:
        rows.append("<tr><td>未确认</td><td>未确认</td><td>未确认</td><td>未确认</td><td>未确认</td><td>未确认</td></tr>")

    principle_items: list[str] = []
    for index, raw_principle in enumerate(principles, start=1):
        if not isinstance(raw_principle, dict):
            problems.append(f"recovery_principles[{index}] 必须是对象。")
            continue
        principle_items.append(
            "<li>"
            f"<strong>{escape_text(raw_principle.get('principle'), '未确认：原则')}</strong>"
            f"<span>{escape_text(raw_principle.get('scenario'), '未确认：适用场景')}</span>"
            f"<em>{escape_text(raw_principle.get('practice'), '未确认：具体做法')}</em>"
            "</li>"
        )

    if problems:
        preview = "\n".join(f"- {item}" for item in problems[:12])
        suffix = "" if len(problems) <= 12 else f"\n... 共 {len(problems)} 个问题"
        raise SystemExit(f"HTML 故障与恢复自检失败：\n{preview}{suffix}")

    principle_html = "".join(principle_items) or "<li><strong>未确认：恢复原则</strong><span>未确认：适用场景</span><em>未确认：具体做法</em></li>"
    return (
        '<div class="table-wrap recovery-scenarios">'
        "<table><thead><tr>"
        "<th>失败场景</th><th>触发条件</th><th>当前处理</th><th>恢复方式</th><th>观测信号</th><th>失败影响</th>"
        "</tr></thead><tbody>"
        f'{"".join(rows)}'
        "</tbody></table></div>"
        '<div class="callout info recovery-principles">'
        "<strong>设计原则</strong>"
        f'<ul class="security-concern-list">{principle_html}</ul>'
        "</div>"
    )


def build_project_conventions_html(data: dict[str, Any], *, skip_validation: bool = False) -> str:
    conventions = data.get("project_conventions", [])
    if skip_validation and (not isinstance(conventions, list) or not conventions):
        conventions = [
            {
                "phrase": "目录边界",
                "summary": "按模块职责阅读和修改文件，避免跨边界混写。",
            },
            {
                "phrase": "验证命令",
                "summary": "提交前运行项目约定的测试或检查命令。",
            },
            {
                "phrase": "不要修改",
                "summary": "generated、vendor 或第三方目录只作为边界参考。",
            },
        ]

    problems: list[str] = []
    if not isinstance(conventions, list):
        conventions = []
        problems.append("project_conventions 必须是数组。")

    items: list[str] = []
    for index, raw_convention in enumerate(conventions, start=1):
        if not isinstance(raw_convention, dict):
            problems.append(f"project_conventions[{index}] 必须是对象。")
            continue
        phrase = as_text(raw_convention.get("phrase"), "未确认：约定")
        summary = as_text(raw_convention.get("summary"), "未确认：一句话说明")
        if len(phrase) > 24:
            problems.append(f"project_conventions[{index}].phrase 过长，应是短语：{phrase[:40]}")
        items.append(
            "<li>"
            f"<strong>{escape_text(phrase)}</strong>"
            f"<span>{escape_text(summary)}</span>"
            "</li>"
        )
    if not items:
        items.append("<li><strong>未确认：项目约定</strong><span>未确认：一句话说明</span></li>")

    if problems:
        preview = "\n".join(f"- {item}" for item in problems[:12])
        suffix = "" if len(problems) <= 12 else f"\n... 共 {len(problems)} 个问题"
        raise SystemExit(f"HTML 项目约定自检失败：\n{preview}{suffix}")

    return f'<ul class="index-list project-conventions">{"".join(items)}</ul>'


def build_project_specifics_html(data: dict[str, Any], *, skip_validation: bool = False) -> str:
    matrix = data.get("project_specific_matrix", [])
    notes = data.get("project_specific_notes", [])
    if skip_validation and (not isinstance(matrix, list) or not matrix):
        matrix = [
            {
                "scenario": "默认场景",
                "condition": "常规运行方式。",
                "entry": "主入口。",
                "difference": "未确认：多实现差异。",
                "dependency": "未确认：依赖。",
                "risk": "未确认：风险。",
            }
        ]
    if skip_validation and (not isinstance(notes, list) or not notes):
        notes = ["未确认：项目特化补充。"]

    problems: list[str] = []
    if not isinstance(matrix, list):
        matrix = []
        problems.append("project_specific_matrix 必须是数组。")
    if not isinstance(notes, list):
        notes = []
        problems.append("project_specific_notes 必须是数组。")

    rows: list[str] = []
    for index, raw_item in enumerate(matrix, start=1):
        if not isinstance(raw_item, dict):
            problems.append(f"project_specific_matrix[{index}] 必须是对象。")
            continue
        rows.append(
            "<tr>"
            f"<td>{escape_text(raw_item.get('scenario'), '未确认：场景/实现')}</td>"
            f"<td>{escape_text(raw_item.get('condition'), '未确认：适用条件')}</td>"
            f"<td>{escape_text(raw_item.get('entry'), '未确认：入口')}</td>"
            f"<td>{escape_text(raw_item.get('difference'), '未确认：关键差异')}</td>"
            f"<td>{escape_text(raw_item.get('dependency'), '未确认：依赖')}</td>"
            f"<td>{escape_text(raw_item.get('risk'), '未确认：风险')}</td>"
            "</tr>"
        )
    if not rows:
        rows.append("<tr><td>不适用：未确认多场景差异</td><td>不适用</td><td>不适用</td><td>不适用</td><td>不适用</td><td>不适用</td></tr>")

    note_items = "".join(f"<li>{escape_text(note)}</li>" for note in notes if as_text(note, "")) or "<li>未确认：项目特化补充</li>"

    if problems:
        preview = "\n".join(f"- {item}" for item in problems[:12])
        suffix = "" if len(problems) <= 12 else f"\n... 共 {len(problems)} 个问题"
        raise SystemExit(f"HTML 项目特化自检失败：\n{preview}{suffix}")

    return (
        '<div class="table-wrap project-specifics">'
        "<table><thead><tr>"
        "<th>场景/实现</th><th>适用条件</th><th>入口</th><th>关键差异</th><th>依赖</th><th>风险</th>"
        "</tr></thead><tbody>"
        f'{"".join(rows)}'
        "</tbody></table></div>"
        '<div class="callout info project-specific-notes">'
        "<strong>补充说明</strong>"
        f"<ul>{note_items}</ul>"
        "</div>"
    )


def mermaid_id(value: Any, used: set[str], *, prefix: str = "N") -> str:
    raw = as_text(value, "")
    ascii_part = re.sub(r"[^A-Za-z0-9_]", "_", raw)
    ascii_part = re.sub(r"_+", "_", ascii_part).strip("_")
    if not ascii_part or ascii_part[0].isdigit() or ascii_part.lower() in MERMAID_KEYWORDS:
        ascii_part = prefix
    candidate = ascii_part[:24] or prefix
    if candidate.lower() in MERMAID_KEYWORDS:
        candidate = f"{prefix}_{candidate}"
    suffix = 1
    while candidate in used:
        suffix += 1
        candidate = f"{ascii_part[:20] or prefix}_{suffix}"
    used.add(candidate)
    return candidate


def mermaid_label(value: Any) -> str:
    text = as_text(value, "未确认")
    text = re.sub(r"[\[\]{}<>|;]", " ", text)
    text = text.replace('"', "'").replace("\n", " ").replace("\r", " ")
    return re.sub(r"\s+", " ", text).strip() or "未确认"


def mermaid_sequence_message(value: Any) -> str:
    text = mermaid_label(value)
    text = text.replace("->", "到").replace("--", "到")
    text = re.sub(r"[()+={}]", " ", text)
    return re.sub(r"\s+", " ", text).strip() or "未确认"


def mermaid_edge_label(protocol: Any, auth: Any, relation: Any) -> str:
    parts = [as_text(relation, ""), as_text(protocol, ""), as_text(auth, "")]
    label = " / ".join(part for part in parts if part)
    label = re.sub(r"[\[\]{}<>|;]", " ", label)
    return label or "未确认"


def build_dependencies_html(data: dict[str, Any], *, skip_validation: bool = False) -> str:
    dependencies = data.get("external_dependencies", [])
    links = data.get("dependency_links", [])
    raw_placeholders = data.get("placeholders", {})
    if not isinstance(raw_placeholders, dict):
        raw_placeholders = {}

    if skip_validation and (not isinstance(dependencies, list) or not dependencies):
        dependencies = [
            {
                "name": "上游系统",
                "category": "upstream",
                "direction": "upstream",
                "why_needed": "触发本系统处理业务请求。",
                "protocol": "HTTP",
                "auth": "未确认",
                "failure_impact": "业务请求无法进入本系统。",
                "failure_handling": "返回错误或等待重试。",
            },
            {
                "name": "下游服务",
                "category": "downstream",
                "direction": "downstream",
                "why_needed": "接收本系统输出的处理结果。",
                "protocol": "RPC",
                "auth": "未确认",
                "failure_impact": "业务结果无法提交到下游。",
                "failure_handling": "记录失败并按策略重试。",
            },
        ]
    if skip_validation and (not isinstance(links, list) or not links):
        links = [
            {
                "from": "上游系统",
                "relation": "调用",
                "to": "本系统",
                "protocol": "HTTP",
                "auth": "未确认",
                "failure_handling": "返回错误或等待重试。",
            },
            {
                "from": "本系统",
                "relation": "调用",
                "to": "下游服务",
                "protocol": "RPC",
                "auth": "未确认",
                "failure_handling": "记录失败并按策略重试。",
            },
        ]

    problems: list[str] = []
    if not isinstance(dependencies, list):
        dependencies = []
        problems.append("external_dependencies 必须是数组。")
    if not isinstance(links, list):
        links = []
        problems.append("dependency_links 必须是数组。")

    validate_dependency_text("external_dependencies", dependencies, problems)
    validate_dependency_text("dependency_links", links, problems)

    if not skip_validation and not dependencies:
        problems.append("缺少 external_dependencies，无法渲染外部系统清单。")
    if not skip_validation and not links:
        problems.append("缺少 dependency_links，无法渲染上下游链路图。")

    known_names = {
        as_text(item.get("name"), "")
        for item in dependencies
        if isinstance(item, dict) and as_text(item.get("name"), "")
    }
    system_names = {
        "本系统",
        "本项目",
        as_text(raw_placeholders.get("ENGINE_NAME"), ""),
        as_text(raw_placeholders.get("PROJECT_NAME"), ""),
    }
    system_names = {name for name in system_names if name}

    node_ids: dict[str, str] = {}
    used_ids: set[str] = set()
    edges: list[str] = ["flowchart TB"]
    for index, raw_link in enumerate(links, start=1):
        if not isinstance(raw_link, dict):
            problems.append(f"dependency_links[{index}] 必须是对象。")
            continue
        source = as_text(raw_link.get("from"), "未确认：源")
        target = as_text(raw_link.get("to"), "未确认：目标")
        for node in (source, target):
            if node not in node_ids:
                node_ids[node] = mermaid_id(node, used_ids)
        if known_names and source not in known_names and source not in system_names:
            problems.append(f"链路源未出现在 external_dependencies 中：{source}")
        if known_names and target not in known_names and target not in system_names:
            problems.append(f"链路目标未出现在 external_dependencies 中：{target}")
        edge_label = mermaid_edge_label(raw_link.get("protocol"), raw_link.get("auth"), raw_link.get("relation"))
        edges.append(f'  {node_ids[source]}["{mermaid_label(source)}"] -->|"{mermaid_label(edge_label)}"| {node_ids[target]}["{mermaid_label(target)}"]')

    if len(edges) == 1:
        edges.append('  Unknown["未确认：依赖链路"]')

    for index, raw_dep in enumerate(dependencies, start=1):
        if not isinstance(raw_dep, dict):
            problems.append(f"external_dependencies[{index}] 必须是对象。")
            continue
        direction = as_text(raw_dep.get("direction"), "未确认")
        if direction not in DEPENDENCY_DIRECTIONS:
            problems.append(f"{raw_dep.get('name', f'external_dependencies[{index}]')} 的 direction 无效：{direction}")

    if problems:
        preview = "\n".join(f"- {item}" for item in problems[:12])
        suffix = "" if len(problems) <= 12 else f"\n... 共 {len(problems)} 个问题"
        raise SystemExit(f"HTML 上下游和服务依赖自检失败：\n{preview}{suffix}")

    return mermaid_diagram_html(
        "上下游链路图",
        "dependency-diagram",
        "\n".join(edges),
        summary=f"上下游链路图包含 {len(node_ids)} 个节点和 {max(len(edges) - 1, 0)} 条链路",
    )


def build_security_html(data: dict[str, Any], *, skip_validation: bool = False) -> str:
    controls = data.get("security_controls", [])
    crypto_scenarios = data.get("crypto_scenarios", [])
    concerns = data.get("security_concerns", [])

    if skip_validation and (not isinstance(controls, list) or not controls):
        controls = [
            {
                "point": "身份认证",
                "protects_against": "防止未授权调用进入核心流程。",
                "mechanism": "通过入口认证或调用方校验识别请求来源。",
                "failure": "拒绝请求或记录安全风险。",
            }
        ]
    if skip_validation and (not isinstance(crypto_scenarios, list) or not crypto_scenarios):
        crypto_scenarios = [
            {
                "scenario": "外部调用签名",
                "asset": "外部请求或回调内容",
                "method": "签名校验，避免请求被篡改。",
                "credential_location": "外部托管或配置中心。",
                "failure": "调用失败或进入安全异常处理。",
            }
        ]
    if skip_validation and (not isinstance(concerns, list) or not concerns):
        concerns = [
            {
                "concern": "安全机制未确认",
                "impact": "无法判断关键路径是否覆盖安全控制。",
                "trigger": "事实层缺少明确安全入口或配置。",
                "action": "补充事实扫描或写入 QA 继续确认。",
            }
        ]

    problems: list[str] = []
    if not isinstance(controls, list):
        controls = []
        problems.append("security_controls 必须是数组。")
    if not isinstance(crypto_scenarios, list):
        crypto_scenarios = []
        problems.append("crypto_scenarios 必须是数组。")
    if not isinstance(concerns, list):
        concerns = []
        problems.append("security_concerns 必须是数组。")

    validate_security_text("security_controls", controls, problems)
    validate_security_text("crypto_scenarios", crypto_scenarios, problems)
    validate_security_text("security_concerns", concerns, problems)

    if not skip_validation and not controls:
        problems.append("缺少 security_controls，无法渲染业务安全表。")
    if not skip_validation and not crypto_scenarios:
        problems.append("缺少 crypto_scenarios，无法渲染加密相关表。")

    control_rows: list[str] = []
    for index, raw_control in enumerate(controls, start=1):
        if not isinstance(raw_control, dict):
            problems.append(f"security_controls[{index}] 必须是对象。")
            continue
        control_rows.append(
            "<tr>"
            f"<td>{escape_text(raw_control.get('point'), '未确认：防控点')}</td>"
            f"<td>{escape_text(raw_control.get('protects_against'), '未确认：防什么')}</td>"
            f"<td>{escape_text(raw_control.get('mechanism'), '未确认：怎么防')}</td>"
            f"<td>{escape_text(raw_control.get('failure'), '未确认：失败结果')}</td>"
            "</tr>"
        )
    if not control_rows:
        control_rows.append("<tr><td>未确认</td><td>未确认</td><td>未确认</td><td>未确认</td></tr>")

    crypto_rows: list[str] = []
    for index, raw_scenario in enumerate(crypto_scenarios, start=1):
        if not isinstance(raw_scenario, dict):
            problems.append(f"crypto_scenarios[{index}] 必须是对象。")
            continue
        crypto_rows.append(
            "<tr>"
            f"<td>{escape_text(raw_scenario.get('scenario'), '未确认：场景')}</td>"
            f"<td>{escape_text(raw_scenario.get('asset'), '未确认：保护对象')}</td>"
            f"<td>{escape_text(raw_scenario.get('method'), '未确认：加密/签名/脱敏手段')}</td>"
            f"<td>{escape_text(raw_scenario.get('credential_location'), '未确认：托管位置')}</td>"
            f"<td>{escape_text(raw_scenario.get('failure'), '未确认：失败结果')}</td>"
            "</tr>"
        )
    if not crypto_rows:
        crypto_rows.append("<tr><td>未确认</td><td>未确认</td><td>未确认</td><td>未确认</td><td>未确认</td></tr>")

    concern_items: list[str] = []
    for index, raw_concern in enumerate(concerns, start=1):
        if not isinstance(raw_concern, dict):
            problems.append(f"security_concerns[{index}] 必须是对象。")
            continue
        concern_items.append(
            "<li>"
            f"<strong>{escape_text(raw_concern.get('concern'), '未确认：关注点')}</strong>"
            f"<span>{escape_text(raw_concern.get('impact'), '未确认：影响')}</span>"
            f"<em>{escape_text(raw_concern.get('trigger'), '未确认：触发条件')} / {escape_text(raw_concern.get('action'), '未确认：处理建议')}</em>"
            "</li>"
        )

    if problems:
        preview = "\n".join(f"- {item}" for item in problems[:12])
        suffix = "" if len(problems) <= 12 else f"\n... 共 {len(problems)} 个问题"
        raise SystemExit(f"HTML 安全相关自检失败：\n{preview}{suffix}")

    concerns_html = "".join(concern_items) or "<li><strong>未确认：安全关注点</strong><span>未确认：影响</span><em>未确认：处理建议</em></li>"
    return (
        '<div class="security-blocks">'
        '<article class="panel security-controls">'
        "<h3>业务安全</h3>"
        '<div class="table-wrap"><table><thead><tr>'
        "<th>防控点</th><th>防什么</th><th>怎么防</th><th>失败结果</th>"
        "</tr></thead><tbody>"
        f'{"".join(control_rows)}'
        "</tbody></table></div>"
        "</article>"
        '<article class="panel crypto-scenarios">'
        "<h3>加密相关</h3>"
        '<div class="table-wrap"><table><thead><tr>'
        "<th>场景</th><th>保护对象</th><th>加密/签名/脱敏手段</th><th>凭据托管</th><th>失败结果</th>"
        "</tr></thead><tbody>"
        f'{"".join(crypto_rows)}'
        "</tbody></table></div>"
        "</article>"
        '<div class="callout warn security-concerns">'
        "<strong>关注点</strong>"
        f'<ul class="security-concern-list">{concerns_html}</ul>'
        "</div>"
        "</div>"
    )


def format_state_name(state: dict[str, Any]) -> str:
    label = as_text(state.get("label"), "未确认")
    enum = as_text(state.get("enum"), "")
    value = as_text(state.get("value"), "")
    if enum and value:
        return f"{label}({enum}={value})"
    if enum:
        return f"{label}({enum})"
    if value:
        return f"{label}({value})"
    return label


def mermaid_diagram_html(label: str, diagram_class: str, source: str, *, summary: str | None = None) -> str:
    summary_text = as_text(summary, label)
    summary = f"{summary_text}。如果图表未渲染，请查看下方 Mermaid 源文本。"
    return (
        f'<div class="diagram {diagram_class}" role="img" aria-label="{html.escape(summary, quote=True)}">'
        f'<div class="diagram-label">{html.escape(label, quote=True)}</div>'
        f'<p class="sr-only diagram-summary">{html.escape(summary)}</p>'
        '<div class="diagram-body">'
        f'<pre class="mermaid">{html.escape(source, quote=False)}</pre>'
        '<p class="mermaid-fallback">图表依赖 Mermaid 渲染；如果当前环境无法加载脚本，上方会保留 Mermaid 源文本。</p>'
        "</div>"
        "</div>"
    )


def build_model_er_mermaid(domains: list[Any], entities: list[Any], relations: list[Any]) -> str:
    used: set[str] = set()
    node_ids: dict[str, str] = {}
    lines = ["flowchart TB"]

    entities_by_domain: dict[str, list[str]] = {}
    for raw_entity in entities:
        if not isinstance(raw_entity, dict):
            continue
        name = as_text(raw_entity.get("name"), "")
        if not name:
            continue
        domain = as_text(raw_entity.get("domain"), "未确认数据域")
        entities_by_domain.setdefault(domain, []).append(name)
        node_ids[name] = mermaid_id(name, used, prefix="E")

    for index, raw_domain in enumerate(domains, start=1):
        if not isinstance(raw_domain, dict):
            continue
        domain_name = as_text(raw_domain.get("name"), f"数据域{index}")
        domain_id = mermaid_id(domain_name, used, prefix="D")
        lines.append(f'  subgraph {domain_id}["{mermaid_label(domain_name)}"]')
        for entity_name in entities_by_domain.get(domain_name, []):
            lines.append(f'    {node_ids[entity_name]}["{mermaid_label(entity_name)}"]')
        lines.append("  end")

    for entity_name, entity_id in node_ids.items():
        if not any(f"{entity_id}[" in line for line in lines):
            lines.append(f'  {entity_id}["{mermaid_label(entity_name)}"]')

    for raw_relation in relations:
        if not isinstance(raw_relation, dict):
            continue
        source = as_text(raw_relation.get("from"), "")
        target = as_text(raw_relation.get("to"), "")
        if not source or not target:
            continue
        if source not in node_ids:
            node_ids[source] = mermaid_id(source, used, prefix="E")
            lines.append(f'  {node_ids[source]}["{mermaid_label(source)}"]')
        if target not in node_ids:
            node_ids[target] = mermaid_id(target, used, prefix="E")
            lines.append(f'  {node_ids[target]}["{mermaid_label(target)}"]')
        relation = mermaid_label(raw_relation.get("relation") or raw_relation.get("meaning") or "关联")
        lines.append(f'  {node_ids[source]} -->|"{relation}"| {node_ids[target]}')

    if len(lines) == 1:
        lines.append('  Unknown["未确认：数据模型"]')
    return "\n".join(lines)


def build_state_machine_mermaid(states: list[Any], transitions: list[Any]) -> str:
    used: set[str] = set()
    state_ids: dict[str, str] = {}
    lines = ["stateDiagram-v2"]

    for raw_state in states:
        if not isinstance(raw_state, dict):
            continue
        display = format_state_name(raw_state)
        state_id = mermaid_id(display, used, prefix="S")
        state_ids[display] = state_id
        for candidate in (raw_state.get("label"), raw_state.get("enum")):
            candidate_text = as_text(candidate, "")
            if candidate_text:
                state_ids[candidate_text] = state_id
        lines.append(f'  state "{mermaid_label(display)}" as {state_id}')

    for raw_transition in transitions:
        if not isinstance(raw_transition, dict):
            continue
        start = as_text(raw_transition.get("from"), "")
        target = as_text(raw_transition.get("to"), "")
        if not start or not target:
            continue
        start_id = state_ids.get(start)
        target_id = state_ids.get(target)
        if not start_id:
            start_id = mermaid_id(start, used, prefix="S")
            state_ids[start] = start_id
            lines.append(f'  state "{mermaid_label(start)}" as {start_id}')
        if not target_id:
            target_id = mermaid_id(target, used, prefix="S")
            state_ids[target] = target_id
            lines.append(f'  state "{mermaid_label(target)}" as {target_id}')
        event = mermaid_label(raw_transition.get("event") or "流转")
        lines.append(f"  {start_id} --> {target_id}: {event}")

    if len(lines) == 1:
        lines.append('  state "未确认：状态机" as Unknown')
    return "\n".join(lines)


def build_sequence_mermaid(
    participants: list[Any],
    steps: list[Any],
    *,
    fallback_system_name: str = "本系统",
) -> str:
    used: set[str] = set()
    participant_aliases: dict[str, str] = {}
    participant_order: list[str] = []
    participant_types: dict[str, str] = {}
    lines = ["sequenceDiagram"]

    for index, raw_participant in enumerate(participants, start=1):
        if not isinstance(raw_participant, dict):
            continue
        name = as_text(raw_participant.get("name"), f"参与方{index}")
        alias = mermaid_id(name, used, prefix="P")
        participant_aliases[name] = alias
        participant_order.append(name)
        participant_types[name] = as_text(raw_participant.get("type"), "")
        lines.append(f'  participant {alias} as {mermaid_label(name)}')

    if not participant_order:
        participant_aliases[fallback_system_name] = "Sys"
        participant_order.append(fallback_system_name)
        participant_types[fallback_system_name] = "system"
        lines.append(f"  participant Sys as {mermaid_label(fallback_system_name)}")

    system_name = next((name for name in participant_order if participant_types.get(name) == "system"), participant_order[0])
    external_name = next((name for name in participant_order if participant_types.get(name) == "external_trigger"), system_name)
    downstream_name = next((name for name in participant_order if participant_types.get(name) == "downstream"), system_name)

    def alias_for(name: str) -> str:
        if name not in participant_aliases:
            participant_aliases[name] = mermaid_id(name, used, prefix="P")
            lines.insert(1, f'  participant {participant_aliases[name]} as {mermaid_label(name)}')
        return participant_aliases[name]

    for index, raw_step in enumerate(steps, start=1):
        if isinstance(raw_step, dict):
            source = as_text(raw_step.get("from"), "")
            target = as_text(raw_step.get("to"), "")
            message = as_text(raw_step.get("message") or raw_step.get("step"), f"步骤 {index}")
        else:
            message = as_text(raw_step, f"步骤 {index}")
            if index == 1:
                source, target = external_name, system_name
            elif index == len(steps) and downstream_name != system_name:
                source, target = system_name, downstream_name
            else:
                source, target = system_name, system_name
        lines.append(f"  {alias_for(source)}->>{alias_for(target)}: {mermaid_sequence_message(message)}")

    if len(lines) == 1:
        lines.append("  Sys->>Sys: 未确认")
    return "\n".join(lines)


def build_model_html(data: dict[str, Any], *, skip_validation: bool = False) -> str:
    domains = data.get("data_domains", [])
    entities = data.get("data_entities", [])
    relations = data.get("data_relations", [])
    state_machine = data.get("state_machine", {})

    if skip_validation and (not isinstance(domains, list) or not domains):
        domains = [
            {
                "name": "示例数据域",
                "summary": "承载核心业务数据。",
                "objects": ["核心对象 A", "核心对象 B"],
                "producer": "本系统",
                "consumer": "下游消费方",
            }
        ]
    if skip_validation and (not isinstance(entities, list) or not entities):
        entities = [
            {
                "name": "核心对象 A",
                "domain": "示例数据域",
                "meaning": "代表核心业务记录。",
                "key_fields": ["id", "status"],
                "created_by": "入口流程",
                "consumed_by": "核心流程",
            }
        ]
    if skip_validation and (not isinstance(relations, list) or not relations):
        relations = [
            {
                "from": "核心对象 A",
                "relation": "关联",
                "to": "核心对象 B",
                "meaning": "表达对象间业务关系。",
            }
        ]
    if skip_validation and not isinstance(state_machine, dict):
        state_machine = {}
    if skip_validation and not state_machine:
        state_machine = {
            "name": "示例状态机",
            "status": "confirmed",
            "states": [
                {"label": "待处理", "enum": "PENDING", "value": "0", "meaning": "等待处理", "entry": "创建后", "exit": "开始处理", "failure": "进入异常"},
                {"label": "处理中", "enum": "PROCESSING", "value": "1", "meaning": "正在处理", "entry": "任务启动", "exit": "处理完成", "failure": "进入异常"},
            ],
            "transitions": [
                {"from": "待处理", "event": "开始处理", "to": "处理中", "actor": "本系统", "failure": "记录失败"},
            ],
        }

    problems: list[str] = []
    if not isinstance(domains, list):
        domains = []
        problems.append("data_domains 必须是数组。")
    if not isinstance(entities, list):
        entities = []
        problems.append("data_entities 必须是数组。")
    if not isinstance(relations, list):
        relations = []
        problems.append("data_relations 必须是数组。")
    if not isinstance(state_machine, dict):
        state_machine = {}
        problems.append("state_machine 必须是对象。")

    validate_model_text("data_domains", domains, problems)
    validate_model_text("data_entities", entities, problems)
    validate_model_text("data_relations", relations, problems)
    validate_model_text("state_machine", state_machine, problems)

    if not skip_validation and not domains:
        problems.append("缺少 data_domains，无法渲染数据域模型。")
    if not skip_validation and not entities:
        problems.append("缺少 data_entities，无法渲染核心数据对象。")

    for index, raw_domain in enumerate(domains, start=1):
        if not isinstance(raw_domain, dict):
            problems.append(f"data_domains[{index}] 必须是对象。")
    entity_names: set[str] = set()
    for index, raw_entity in enumerate(entities, start=1):
        if not isinstance(raw_entity, dict):
            problems.append(f"data_entities[{index}] 必须是对象。")
            continue
        name = as_text(raw_entity.get("name"), "")
        if name:
            entity_names.add(name)

    for index, raw_relation in enumerate(relations, start=1):
        if not isinstance(raw_relation, dict):
            problems.append(f"data_relations[{index}] 必须是对象。")
            continue
        source = as_text(raw_relation.get("from"), "")
        target = as_text(raw_relation.get("to"), "")
        if not skip_validation and entity_names:
            if source and source not in entity_names:
                problems.append(f"数据关系源对象未在 data_entities 中定义：{source}")
            if target and target not in entity_names:
                problems.append(f"数据关系目标对象未在 data_entities 中定义：{target}")

    state_status = as_text(state_machine.get("status"), "未确认：状态机")
    state_name = as_text(state_machine.get("name"), "状态机")
    states = state_machine.get("states", [])
    transitions = state_machine.get("transitions", [])
    if not isinstance(states, list):
        states = []
        problems.append("state_machine.states 必须是数组。")
    if not isinstance(transitions, list):
        transitions = []
        problems.append("state_machine.transitions 必须是数组。")
    if not skip_validation and state_status == "confirmed" and not states:
        problems.append("state_machine.status 为 confirmed 时必须提供 states。")

    state_aliases: set[str] = set()
    for index, raw_state in enumerate(states, start=1):
        if not isinstance(raw_state, dict):
            problems.append(f"state_machine.states[{index}] 必须是对象。")
            continue
        display = format_state_name(raw_state)
        for candidate in (raw_state.get("label"), raw_state.get("enum"), display):
            candidate_text = as_text(candidate, "")
            if candidate_text:
                state_aliases.add(candidate_text)
        if not skip_validation and state_status == "confirmed" and not as_text(raw_state.get("enum"), "") and not as_text(raw_state.get("value"), ""):
            problems.append(f"{display} 缺少枚举名或数值，无法保留状态代码语义。")

    for index, raw_transition in enumerate(transitions, start=1):
        if not isinstance(raw_transition, dict):
            problems.append(f"state_machine.transitions[{index}] 必须是对象。")
            continue
        start = as_text(raw_transition.get("from"), "未确认：起始状态")
        target = as_text(raw_transition.get("to"), "未确认：目标状态")
        if not skip_validation and states:
            if start not in state_aliases:
                problems.append(f"状态流转起点未在 states 中定义：{start}")
            if target not in state_aliases:
                problems.append(f"状态流转终点未在 states 中定义：{target}")

    if problems:
        preview = "\n".join(f"- {item}" for item in problems[:12])
        suffix = "" if len(problems) <= 12 else f"\n... 共 {len(problems)} 个问题"
        raise SystemExit(f"HTML 数据模型自检失败：\n{preview}{suffix}")

    er_html = mermaid_diagram_html(
        "核心数据 ER 图",
        "model-er-diagram",
        build_model_er_mermaid(domains, entities, relations),
        summary=f"核心数据 ER 图包含 {len(entities)} 个核心对象和 {len(relations)} 条对象关系",
    )
    if state_status.startswith("未发现") or (not states and not transitions):
        state_html = (
            '<article class="panel model-state-machine">'
            f"<h3>{escape_text(state_name)}</h3>"
            f'<p class="summary">{escape_text(state_status, "未发现：状态机")}</p>'
            "</article>"
        )
    else:
        state_html = mermaid_diagram_html(
            f"{state_name}",
            "state-machine-diagram",
            build_state_machine_mermaid(states, transitions),
            summary=f"{state_name}包含 {len(states)} 个状态和 {len(transitions)} 条流转",
        )

    return (
        '<div class="model-blocks">'
        f"{er_html}{state_html}"
        "</div>"
    )


def build_business_flows_html(data: dict[str, Any], *, skip_validation: bool = False) -> str:
    flows = data.get("business_flows", [])
    if not isinstance(flows, list) or not flows:
        if skip_validation:
            flows = [
                {
                    "name": "示例业务流程",
                    "intent": "说明该流程解决的业务问题。",
                    "participants": [
                        {"name": "外部触发源", "type": "external_trigger"},
                        {"name": "本系统", "type": "system"},
                        {"name": "直接下游", "type": "downstream"},
                    ],
                    "sequence_steps": [
                        "外部触发源发起请求或任务",
                        "本系统执行校验和核心处理",
                        "本系统向直接下游提交请求或输出结果",
                    ],
                    "stages": [
                        {"name": "入口处理", "action": "接收并校验输入", "reason": "避免无效请求进入核心流程", "failure": "拒绝请求或记录失败"},
                        {"name": "核心处理", "action": "执行业务规则", "reason": "产出本流程的业务结果", "failure": "返回错误或进入补偿"},
                    ],
                }
            ]
        else:
            raise SystemExit("HTML 核心业务自检失败：缺少 business_flows，无法渲染逐条业务流程。")

    problems: list[str] = []
    sections: list[str] = ['<div class="business-flows">']

    for index, raw_flow in enumerate(flows, start=1):
        if not isinstance(raw_flow, dict):
            problems.append(f"business_flows[{index}] 必须是对象。")
            continue

        name = as_text(raw_flow.get("name"), f"未确认：流程 {index}")
        intent = as_text(raw_flow.get("intent"), "未确认：业务意图")
        participants = raw_flow.get("participants", [])
        steps = raw_flow.get("sequence_steps", [])
        stages = raw_flow.get("stages", [])

        if not isinstance(participants, list):
            participants = []
            problems.append(f"{name} 的 participants 必须是数组。")
        if not isinstance(steps, list):
            steps = []
            problems.append(f"{name} 的 sequence_steps 必须是数组。")
        if not isinstance(stages, list):
            stages = []
            problems.append(f"{name} 的 stages 必须是数组。")

        participant_types: set[str] = set()
        for p_index, participant in enumerate(participants, start=1):
            if not isinstance(participant, dict):
                problems.append(f"{name} 的 participant {p_index} 必须是对象。")
                continue
            p_name = as_text(participant.get("name"))
            p_type = as_text(participant.get("type"), "未确认")
            participant_types.add(p_type)
            if p_type not in BUSINESS_PARTICIPANT_TYPES:
                problems.append(f"{name} 的参与方 `{p_name}` 类型无效：{p_type}")
            for pattern in BUSINESS_FORBIDDEN_PARTICIPANT_PATTERNS:
                if pattern.search(p_name):
                    problems.append(f"{name} 的参与方 `{p_name}` 应折叠为本系统动作，不应进入 HTML 时序。")
                    break

        if not skip_validation:
            if "system" not in participant_types:
                problems.append(f"{name} 缺少 system 类型参与方。")
            if len(steps) < 2:
                problems.append(f"{name} 至少需要 2 条时序步骤。")
            if not stages:
                problems.append(f"{name} 缺少阶段拆解。")

        sequence_html = mermaid_diagram_html(
            "业务时序图",
            "business-sequence-diagram",
            build_sequence_mermaid(participants, steps),
            summary=f"{name}的业务时序图包含 {len(participants)} 个参与方和 {len(steps)} 个步骤",
        )

        stage_cards: list[str] = []
        for stage in stages:
            if not isinstance(stage, dict):
                problems.append(f"{name} 的阶段必须是对象。")
                continue
            stage_cards.append(
                '<article class="stage-card">'
                f"<h4>{escape_text(stage.get('name'), '未确认：阶段')}</h4>"
                '<dl class="stage-meta">'
                f"<div><dt>动作</dt><dd>{escape_text(stage.get('action'), '未确认：做什么')}</dd></div>"
                f"<div><dt>目的</dt><dd>{escape_text(stage.get('reason'), '未确认：为什么需要')}</dd></div>"
                f"<div><dt>失败</dt><dd>{escape_text(stage.get('failure'), '未确认：失败处理')}</dd></div>"
                "</dl>"
                "</article>"
            )
        if not stage_cards:
            stage_cards.append(
                '<article class="stage-card"><h4>未确认：阶段</h4>'
                '<dl class="stage-meta"><div><dt>动作</dt><dd>未确认</dd></div>'
                '<div><dt>目的</dt><dd>未确认</dd></div><div><dt>失败</dt><dd>未确认</dd></div></dl></article>'
            )

        sections.append(
            '<article class="business-flow">'
            f"<h3>{escape_text(name)}</h3>"
            f'<p class="business-flow-intent">{escape_text(intent)}</p>'
            f"{sequence_html}"
            '<div class="stage-grid" aria-label="阶段拆解">'
            f'{"".join(stage_cards)}'
            "</div>"
            "</article>"
        )

    sections.append("</div>")

    if problems:
        preview = "\n".join(f"- {item}" for item in problems[:12])
        suffix = "" if len(problems) <= 12 else f"\n... 共 {len(problems)} 个问题"
        raise SystemExit(f"HTML 核心业务自检失败：\n{preview}{suffix}")

    return "\n".join(sections)


def validate_architecture_placeholders(placeholders: dict[str, str], *, skip: bool = False) -> None:
    if skip:
        return

    problems: list[str] = []
    for key, limit in ARCHITECTURE_TEXT_LIMITS.items():
        value = placeholders.get(key, "").strip()
        if len(value) > limit:
            problems.append(f"{key} 过长（{len(value)}>{limit}）：{value[:40]}")

    for key in ARCHITECTURE_FLOW_KEYS:
        value = placeholders.get(key, "").strip()
        if any(mark in value for mark in ("，", "。", "；", ",", ".", ";")):
            problems.append(f"{key} 应为 1-3 个动词，不应写完整句子：{value[:40]}")

    for key in ARCHITECTURE_NOTE_KEYS:
        value = placeholders.get(key, "").strip()
        for pattern in ARCHITECTURE_FORBIDDEN_PATTERNS:
            if pattern.search(value):
                problems.append(f"{key} 不应包含证据、路径、QA 或工程支撑内容：{value[:40]}")
                break

    for key in ARCHITECTURE_BOTTOM_KEYS:
        value = placeholders.get(key, "").strip()
        for pattern in ARCHITECTURE_FORBIDDEN_PATTERNS:
            if pattern.search(value):
                problems.append(f"{key} 只能放运行时依赖组件，不应放工程支撑或代码边界：{value[:40]}")
                break

    if problems:
        preview = "\n".join(f"- {item}" for item in problems[:12])
        suffix = "" if len(problems) <= 12 else f"\n... 共 {len(problems)} 个问题"
        raise SystemExit(f"HTML 架构图字段自检失败：\n{preview}{suffix}")


def assert_contains(rendered: str, needle: str, label: str) -> None:
    if needle not in rendered:
        raise SystemExit(f"HTML 自检失败：缺少 {label} `{needle}`。")


def assert_not_contains(rendered: str, needle: str, label: str) -> None:
    if needle in rendered:
        raise SystemExit(f"HTML 自检失败：不应包含 {label} `{needle}`。")


def validate_rendered(rendered: str) -> None:
    unresolved = sorted(set(PLACEHOLDER_RE.findall(rendered)))
    if unresolved:
        raise SystemExit(f"HTML 自检失败：仍有未替换占位符：{', '.join(unresolved[:20])}")

    for section_id in REQUIRED_SECTIONS:
        assert_contains(rendered, f'id="{section_id}"', "固定章节")

    for num in range(1, 12):
        assert_contains(rendered, f'<span class="nav-num">{num:02d}</span>', "两位编号导航")
        assert_contains(rendered, f'<span class="section-num">{num:02d}</span>', "两位章节编号")

    assert_contains(rendered, "@media", "响应式或打印样式")
    assert_contains(rendered, "@media print", "打印样式")

    for label, marker in REQUIRED_DESIGN_MARKERS:
        assert_contains(rendered, marker, label)

    for marker in FORBIDDEN_MOTION_MARKERS:
        assert_not_contains(rendered.lower(), marker, "装饰性动效标记")

    for label in FORBIDDEN_INTERNAL_HTML_LABELS:
        assert_not_contains(rendered, label, "HTML 首屏内部流程标签")


def validate_output_path(path: Path) -> None:
    parts = path.parts
    if path.name == "project-context.tmp.html" and len(parts) >= 2 and parts[-2] == ".ai":
        raise SystemExit("不要生成临时 HTML；请直接输出 .ai/project-context.html，脚本会自动备份旧版。")
    if path.name == "project-context.tmp.html" and len(parts) >= 3 and parts[-3:] == (".ai", "drafts", "project-context.tmp.html"):
        raise SystemExit("不要生成临时 HTML；请直接输出 .ai/project-context.html，脚本会自动备份旧版。")


def html_backup_dir(path: Path) -> Path:
    return path.parent / "drafts"


def list_html_backups(path: Path) -> list[Path]:
    drafts_dir = html_backup_dir(path)
    if not drafts_dir.exists():
        return []
    backups = [
        item
        for item in drafts_dir.iterdir()
        if item.is_file() and HTML_BACKUP_RE.match(item.name)
    ]
    return sorted(backups, key=lambda item: item.name, reverse=True)


def backup_existing_html(path: Path) -> tuple[Path | None, list[Path], list[Path]]:
    if not path.exists() or path.name != "project-context.html":
        return None, [], list_html_backups(path)

    drafts_dir = html_backup_dir(path)
    drafts_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = drafts_dir / f"project-context.{timestamp}.html"

    counter = 1
    while backup_path.exists():
        backup_path = drafts_dir / f"project-context.{timestamp}-{counter}.html"
        counter += 1

    shutil.copy2(path, backup_path)

    backups = list_html_backups(path)
    pruned: list[Path] = []
    for old_backup in backups[MAX_HTML_BACKUPS:]:
        old_backup.unlink()
        pruned.append(old_backup)

    return backup_path, pruned, list_html_backups(path)


def format_backup_list(backups: list[Path]) -> str:
    if not backups:
        return ""
    lines = ["可用 rollback 回退到以下版本（时间倒序）："]
    for index, backup in enumerate(backups, start=1):
        lines.append(f"{index}. {backup}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    template = args.template.read_text(encoding="utf-8")

    if args.print_placeholders:
        for name in sorted(set(PLACEHOLDER_RE.findall(template))):
            print(name)
        return 0

    if args.data is None or args.out is None:
        raise SystemExit("渲染 HTML 时必须同时提供 --data 和 --out；仅查看占位符时使用 --print-placeholders。")

    validate_output_path(args.out)
    data = load_json(args.data)
    placeholders = normalize_placeholders(data)
    placeholders["BUSINESS_CONFIDENCE_CLASS"] = status_badge_class(placeholders.get("BUSINESS_CONFIDENCE"), "inferred")
    placeholders["STATE_MACHINE_STATUS_CLASS"] = status_badge_class(placeholders.get("STATE_MACHINE_STATUS"), "open")
    placeholders["SECURITY_STATUS_CLASS"] = status_badge_class(placeholders.get("SECURITY_STATUS"), "risk")
    placeholders["BUSINESS_FLOWS_HTML"] = build_business_flows_html(
        data,
        skip_validation=args.data.name == "project-context-html-data-template.json",
    )
    placeholders["CONFIGURATION_HTML"] = build_configuration_html(
        data,
        skip_validation=args.data.name == "project-context-html-data-template.json",
    )
    placeholders["MODEL_HTML"] = build_model_html(
        data,
        skip_validation=args.data.name == "project-context-html-data-template.json",
    )
    placeholders["SECURITY_HTML"] = build_security_html(
        data,
        skip_validation=args.data.name == "project-context-html-data-template.json",
    )
    placeholders["DEPENDENCIES_HTML"] = build_dependencies_html(
        data,
        skip_validation=args.data.name == "project-context-html-data-template.json",
    )
    placeholders["ONBOARDING_HTML"] = build_onboarding_html(
        data,
        skip_validation=args.data.name == "project-context-html-data-template.json",
    )
    placeholders["PROJECT_CONVENTIONS_HTML"] = build_project_conventions_html(
        data,
        skip_validation=args.data.name == "project-context-html-data-template.json",
    )
    placeholders["PROJECT_SPECIFICS_HTML"] = build_project_specifics_html(
        data,
        skip_validation=args.data.name == "project-context-html-data-template.json",
    )
    placeholders["RECOVERY_HTML"] = build_recovery_html(
        data,
        skip_validation=args.data.name == "project-context-html-data-template.json",
    )
    validate_architecture_placeholders(
        placeholders,
        skip=args.data.name == "project-context-html-data-template.json",
    )
    rendered, missing = render_template(
        template,
        placeholders,
        fill_missing=args.fill_missing,
        escape_values=not args.no_escape,
        trusted_html_placeholders=TRUSTED_HTML_PLACEHOLDERS,
    )
    validate_rendered(rendered)
    backup_path, pruned_backups, backups = backup_existing_html(args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")

    missing_note = f"，使用默认值填充 {len(missing)} 个缺失占位符" if missing else ""
    print(f"已生成 {args.out}{missing_note}")
    if backup_path:
        print(f"已自动备份旧版本：{backup_path}")
        if pruned_backups:
            print(f"已删除超过 {MAX_HTML_BACKUPS} 个限制的旧备份：{len(pruned_backups)} 个")
        print("如需回退到上个版本，执行 rollback。")
        backup_list = format_backup_list(backups)
        if backup_list:
            print(backup_list)
    return 0


if __name__ == "__main__":
    sys.exit(main())
