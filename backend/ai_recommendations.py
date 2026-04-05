import json
import re
from typing import Any, Dict, List

import pandas as pd

from snapshot import build_snapshot

try:
    from llm_client import llm_call
except Exception:
    llm_call = None


PRIORITY_ORDER = {
    "high": 3,
    "medium": 2,
    "low": 1,
}


def _safe_float(value):
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except Exception:
        return None


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _student_payload(student_row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "student_id": int(student_row["student_id"]),
        "first_name": _clean_text(student_row.get("FirstName")),
        "last_name": _clean_text(student_row.get("LastName")),
        "email": _clean_text(student_row.get("Email")),
        "average_grade": _safe_float(student_row.get("average_grade")),
        "recent_average_grade": _safe_float(student_row.get("recent_average_grade")),
        "submission_rate": _safe_float(student_row.get("submission_rate")),
        "late_submissions": _safe_float(student_row.get("late_submissions")),
        "submitted_assignments": _safe_float(student_row.get("submitted_assignments")),
        "total_assignments_available": _safe_float(student_row.get("total_assignments_available")),
        "days_since_last_submission": _safe_float(student_row.get("days_since_last_submission")),
        "grade_drop": _safe_float(student_row.get("grade_drop")),
    }


def _merge_signal(student_map: Dict[int, Dict[str, Any]], student_row: Dict[str, Any], signal: str):
    student_id = int(student_row["student_id"])
    payload = _student_payload(student_row)

    if student_id not in student_map:
        student_map[student_id] = {
            **payload,
            "signals": [],
        }

    if signal not in student_map[student_id]["signals"]:
        student_map[student_id]["signals"].append(signal)

    # keep freshest non-null metrics
    for key, value in payload.items():
        if key in {"student_id", "first_name", "last_name", "email"}:
            if value:
                student_map[student_id][key] = value
        else:
            if value is not None:
                student_map[student_id][key] = value


def _infer_rule_based_action(student: Dict[str, Any]) -> Dict[str, Any]:
    signals = set(student.get("signals", []))
    avg = student.get("average_grade")
    recent_avg = student.get("recent_average_grade")
    submission_rate = student.get("submission_rate")
    grade_drop = student.get("grade_drop")
    days_since_last_submission = student.get("days_since_last_submission")
    late_submissions = student.get("late_submissions")

    if "low_performance" in signals and "low_submission" in signals:
        return {
            "primary_signal": "combined_risk",
            "label": "critical_academic_risk",
            "recommended_action": "contact_student_and_schedule_follow_up",
            "priority": "high",
            "short_reason": (
                f"Low grades and weak submission pattern were detected"
                f"{'' if avg is None else f' (average grade {avg:.1f})'}"
                f"{'' if submission_rate is None else f' with submission rate {submission_rate:.0%}'}."
            ),
        }

    if "low_performance" in signals:
        if avg is not None and avg < 35:
            return {
                "primary_signal": "low_performance",
                "label": "severe_low_performance",
                "recommended_action": "contact_student_and_schedule_follow_up",
                "priority": "high",
                "short_reason": f"Average grade is critically low at {avg:.1f}.",
            }
        return {
            "primary_signal": "low_performance",
            "label": "low_performance",
            "recommended_action": "check_in_with_student",
            "priority": "high",
            "short_reason": (
                "Average grade is below the expected level"
                f"{'' if avg is None else f' ({avg:.1f})'}."
            ),
        }

    if "declining" in signals:
        return {
            "primary_signal": "declining",
            "label": "performance_drop",
            "recommended_action": "investigate_recent_drop",
            "priority": "medium" if (grade_drop is not None and grade_drop < 20) else "high",
            "short_reason": (
                "Recent performance fell compared with the overall record"
                f"{'' if grade_drop is None else f' (drop of {grade_drop:.1f} points)'}."
            ),
        }

    if "low_submission" in signals:
        if submission_rate is not None and submission_rate < 0.5:
            return {
                "primary_signal": "low_submission",
                "label": "serious_low_engagement",
                "recommended_action": "send_reminder_and_monitor_next_assignment",
                "priority": "high",
                "short_reason": f"Submission rate is very low at {submission_rate:.0%}.",
            }
        return {
            "primary_signal": "low_submission",
            "label": "low_submission",
            "recommended_action": "monitor_next_assignment",
            "priority": "medium",
            "short_reason": (
                "Submission activity is below target"
                f"{'' if submission_rate is None else f' ({submission_rate:.0%})'}."
            ),
        }

    if "top_student" in signals:
        extra = ""
        if avg is not None:
            extra = f" Average grade is {avg:.1f}."
        return {
            "primary_signal": "top_student",
            "label": "positive_performance",
            "recommended_action": "praise_student",
            "priority": "low",
            "short_reason": "Strong and consistent performance detected." + extra,
        }

    # fallback
    reason_bits = []
    if avg is not None:
        reason_bits.append(f"average grade {avg:.1f}")
    if recent_avg is not None:
        reason_bits.append(f"recent average {recent_avg:.1f}")
    if submission_rate is not None:
        reason_bits.append(f"submission rate {submission_rate:.0%}")
    if days_since_last_submission is not None:
        reason_bits.append(f"{int(days_since_last_submission)} days since last submission")
    if late_submissions is not None and late_submissions > 0:
        reason_bits.append(f"{int(late_submissions)} late submissions")

    return {
        "primary_signal": "monitor",
        "label": "general_monitoring",
        "recommended_action": "monitor_next_assignment",
        "priority": "low",
        "short_reason": "; ".join(reason_bits) if reason_bits else "General monitoring suggested.",
    }


def build_rule_based_ai_recommendations(snapshot_date_str: str) -> List[Dict[str, Any]]:
    snapshot = build_snapshot(snapshot_date_str)

    student_map: Dict[int, Dict[str, Any]] = {}

    for row in snapshot["low_performance_students"].to_dict(orient="records"):
        _merge_signal(student_map, row, "low_performance")

    for row in snapshot["declining_performance_students"].to_dict(orient="records"):
        _merge_signal(student_map, row, "declining")

    for row in snapshot["low_submission_students"].to_dict(orient="records"):
        _merge_signal(student_map, row, "low_submission")

    for row in snapshot["top_students"].to_dict(orient="records"):
        _merge_signal(student_map, row, "top_student")

    recommendations = []
    for student in student_map.values():
        rule = _infer_rule_based_action(student)
        recommendations.append({
            **student,
            **rule,
        })

    recommendations.sort(
        key=lambda x: (
            -PRIORITY_ORDER.get(x.get("priority", "low"), 0),
            x.get("last_name", ""),
            x.get("first_name", ""),
        )
    )

    return recommendations


def _extract_json_array(text: str):
    if not text:
        return None

    text = text.strip()

    # direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    # fenced block or embedded array
    match = re.search(r"\[.*\]", text, flags=re.DOTALL)
    if not match:
        return None

    try:
        parsed = json.loads(match.group(0))
        if isinstance(parsed, list):
            return parsed
    except Exception:
        return None

    return None


def enrich_recommendations_with_llm(
    recommendations: List[Dict[str, Any]],
    snapshot_date_str: str,
    max_items: int = 12,
) -> List[Dict[str, Any]]:
    if not recommendations or llm_call is None:
        return recommendations

    selected = recommendations[:max_items]

    compact_payload = []
    for rec in selected:
        compact_payload.append({
            "student_id": rec["student_id"],
            "first_name": rec["first_name"],
            "last_name": rec["last_name"],
            "signal": rec["primary_signal"],
            "signals": rec.get("signals", []),
            "average_grade": rec.get("average_grade"),
            "recent_average_grade": rec.get("recent_average_grade"),
            "submission_rate": rec.get("submission_rate"),
            "grade_drop": rec.get("grade_drop"),
            "days_since_last_submission": rec.get("days_since_last_submission"),
            "late_submissions": rec.get("late_submissions"),
            "rule_label": rec.get("label"),
            "rule_action": rec.get("recommended_action"),
            "rule_priority": rec.get("priority"),
            "rule_reason": rec.get("short_reason"),
        })

    prompt = f"""
You are an academic support assistant for a school dashboard.

You will receive a list of student cases for snapshot date {snapshot_date_str}.
Each case already contains rule-based signals.
Your task is NOT to invent new data.
You may only refine the recommendation.

Return ONLY a JSON array.
Each item must contain:
- student_id
- label
- recommended_action
- priority
- short_reason

Allowed recommended_action values:
- contact_student_and_schedule_follow_up
- check_in_with_student
- investigate_recent_drop
- send_reminder_and_monitor_next_assignment
- monitor_next_assignment
- praise_student

Allowed priority values:
- high
- medium
- low

Keep short_reason to one short sentence.
Do not include markdown.
Input:
{json.dumps(compact_payload, ensure_ascii=False, indent=2)}
""".strip()

    messages = [
        {"role": "system", "content": "You return clean JSON only."},
        {"role": "user", "content": prompt},
    ]

    try:
        raw = llm_call(messages, max_new_tokens=1200)
        parsed = _extract_json_array(raw)

        if not isinstance(parsed, list):
            return recommendations

        by_id = {}
        for item in parsed:
            if not isinstance(item, dict):
                continue
            if "student_id" not in item:
                continue
            by_id[item["student_id"]] = item

        enriched = []
        for rec in recommendations:
            patch = by_id.get(rec["student_id"])
            if not patch:
                enriched.append(rec)
                continue

            enriched.append({
                **rec,
                "label": patch.get("label", rec.get("label")),
                "recommended_action": patch.get("recommended_action", rec.get("recommended_action")),
                "priority": patch.get("priority", rec.get("priority")),
                "short_reason": patch.get("short_reason", rec.get("short_reason")),
            })

        enriched.sort(
            key=lambda x: (
                -PRIORITY_ORDER.get(x.get("priority", "low"), 0),
                x.get("last_name", ""),
                x.get("first_name", ""),
            )
        )

        return enriched

    except Exception:
        return recommendations


def build_ai_recommendations(snapshot_date_str: str, use_llm: bool = False) -> List[Dict[str, Any]]:
    recommendations = build_rule_based_ai_recommendations(snapshot_date_str)

    if use_llm:
        recommendations = enrich_recommendations_with_llm(
            recommendations=recommendations,
            snapshot_date_str=snapshot_date_str,
        )

    return recommendations