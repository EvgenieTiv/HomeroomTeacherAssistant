from pathlib import Path
import pandas as pd
import numpy as np


# =========================
# Paths
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"


# =========================
# SNAPSHOT
# =========================
def build_snapshot(snapshot_date_str):
    content = pd.read_csv(DATA_DIR / "Content.csv")
    solutions = pd.read_csv(DATA_DIR / "Solutions.csv")
    users = pd.read_csv(DATA_DIR / "Users.csv")

    content["CreatedDate"] = pd.to_datetime(content["CreatedDate"], utc=True, errors="coerce")
    content["LastAllowedDate"] = pd.to_datetime(content["LastAllowedDate"], utc=True, errors="coerce")
    solutions["CreatedDate"] = pd.to_datetime(solutions["CreatedDate"], utc=True, errors="coerce")

    snapshot_date = pd.Timestamp(snapshot_date_str, tz="UTC")

    students = users[users["UserTypeId"] == 1].copy()
    students = students[["Id", "Email", "FirstName", "LastName"]].copy()
    students = students.rename(columns={"Id": "student_id"})
    students = students.sort_values("student_id").reset_index(drop=True)

    content_snapshot = content[
        (content["CreatedDate"] <= snapshot_date) &
        (content["ContentType"] == 0)
    ].copy()

    solutions_snapshot = solutions[
        solutions["CreatedDate"] <= snapshot_date
    ].copy()

    content_small = content_snapshot[
        ["Id", "CourseId", "CreatedDate", "LastAllowedDate", "Name"]
    ].copy()

    merged = solutions_snapshot.merge(
        content_small,
        left_on="ContentId",
        right_on="Id",
        how="inner",
        suffixes=("_solution", "_content")
    )

    merged = merged[merged["UserId"].isin(students["student_id"])].copy()

    merged = merged.sort_values(["UserId", "ContentId", "CreatedDate_solution"])
    merged_latest = merged.groupby(["UserId", "ContentId"], as_index=False).tail(1)

    merged_latest["Grade"] = pd.to_numeric(merged_latest["Grade"], errors="coerce")

    # ❗ ВАЖНО: считаем валидными только оценки > 0
    valid = merged_latest[merged_latest["Grade"] > 0].copy()

    student_snapshot = students.copy()
    total_assignments_available = content_small["Id"].nunique()
    student_snapshot["total_assignments_available"] = total_assignments_available

    submitted = valid.groupby("UserId")["ContentId"].nunique().reset_index()
    submitted = submitted.rename(columns={"UserId": "student_id", "ContentId": "submitted_assignments"})

    late = valid.copy()
    late["is_late"] = (
        late["LastAllowedDate"].notna() &
        (late["CreatedDate_solution"] > late["LastAllowedDate"])
    )
    late = late.groupby("UserId")["is_late"].sum().reset_index()
    late = late.rename(columns={"UserId": "student_id", "is_late": "late_submissions"})

    avg = valid.groupby("UserId")["Grade"].mean().reset_index()
    avg = avg.rename(columns={"UserId": "student_id", "Grade": "average_grade"})

    recent = valid.sort_values(["UserId", "CreatedDate_solution"], ascending=[True, False])
    recent["rank"] = recent.groupby("UserId").cumcount() + 1
    recent = recent[recent["rank"] <= 3]

    recent_avg = recent.groupby("UserId")["Grade"].mean().reset_index()
    recent_avg = recent_avg.rename(columns={"UserId": "student_id", "Grade": "recent_average_grade"})

    last = valid.groupby("UserId")["CreatedDate_solution"].max().reset_index()
    last = last.rename(columns={"UserId": "student_id", "CreatedDate_solution": "last_submission_date"})
    last["days_since_last_submission"] = (
        snapshot_date - last["last_submission_date"]
    ).dt.days

    for df in [submitted, late, avg, recent_avg, last]:
        student_snapshot = student_snapshot.merge(df, on="student_id", how="left")

    student_snapshot["submitted_assignments"] = student_snapshot["submitted_assignments"].fillna(0)
    student_snapshot["late_submissions"] = student_snapshot["late_submissions"].fillna(0)

    student_snapshot["average_grade"] = student_snapshot["average_grade"].round(2)
    student_snapshot["recent_average_grade"] = student_snapshot["recent_average_grade"].round(2)

    if total_assignments_available > 0:
        student_snapshot["submission_rate"] = (
            student_snapshot["submitted_assignments"] / total_assignments_available
        ).round(3)
    else:
        student_snapshot["submission_rate"] = 0.0

    low_performance = student_snapshot[student_snapshot["average_grade"] < 50]

    declining = student_snapshot[
        (student_snapshot["recent_average_grade"].notna()) &
        ((student_snapshot["average_grade"] - student_snapshot["recent_average_grade"]) >= 15)
    ].copy()

    declining["grade_drop"] = (
        declining["average_grade"] - declining["recent_average_grade"]
    ).round(2)

    low_submission = student_snapshot[student_snapshot["submission_rate"] < 0.8]
    top_students = student_snapshot[student_snapshot["average_grade"] >= 85]

    return {
        "student_snapshot": student_snapshot,
        "low_performance_students": low_performance,
        "declining_performance_students": declining,
        "low_submission_students": low_submission,
        "top_students": top_students,
    }


# =========================
# JOURNAL
# =========================
def build_journal(snapshot_date_str):
    content = pd.read_csv(DATA_DIR / "Content.csv")
    solutions = pd.read_csv(DATA_DIR / "Solutions.csv")
    users = pd.read_csv(DATA_DIR / "Users.csv")

    content["CreatedDate"] = pd.to_datetime(content["CreatedDate"], utc=True, errors="coerce")
    content["LastAllowedDate"] = pd.to_datetime(content["LastAllowedDate"], utc=True, errors="coerce")
    solutions["CreatedDate"] = pd.to_datetime(solutions["CreatedDate"], utc=True, errors="coerce")

    snapshot_date = pd.Timestamp(snapshot_date_str, tz="UTC")

    # students only
    students = users[users["UserTypeId"] == 1].copy()
    students = students[["Id", "Email", "FirstName", "LastName"]].copy()
    students = students.rename(columns={"Id": "student_id"})
    students = students.sort_values(["LastName", "FirstName", "student_id"]).reset_index(drop=True)

    # assignments available by snapshot date
    assignments = content[
        (content["CreatedDate"] <= snapshot_date) &
        (content["ContentType"] == 0)
    ].copy()

    assignments = assignments.sort_values(["CreatedDate", "Id"]).reset_index(drop=True)
    assignments = assignments[
        ["Id", "Name", "CreatedDate", "LastAllowedDate", "CourseId"]
    ].copy()
    assignments = assignments.rename(
        columns={
            "Id": "assignment_id",
            "CreatedDate": "assignment_created_date",
            "LastAllowedDate": "assignment_last_allowed_date",
        }
    )

    # only solutions up to snapshot date
    solutions = solutions[solutions["CreatedDate"] <= snapshot_date].copy()
    solutions["Grade"] = pd.to_numeric(solutions["Grade"], errors="coerce")
    solutions = solutions.rename(columns={"CreatedDate": "submitted_at"})

    # merge with explicit names
    merged = solutions.merge(
        assignments,
        left_on="ContentId",
        right_on="assignment_id",
        how="inner"
    )

    # keep students only
    merged = merged[merged["UserId"].isin(students["student_id"])].copy()

    # keep latest solution per student per assignment
    merged = merged.sort_values(["UserId", "ContentId", "submitted_at"])
    latest = merged.groupby(["UserId", "ContentId"], as_index=False).tail(1).copy()

    # late flag only for valid submissions (>0)
    latest["is_late"] = (
        latest["assignment_last_allowed_date"].notna() &
        (latest["submitted_at"] > latest["assignment_last_allowed_date"])
    )

    # assignment columns for frontend
    assignment_columns = []
    for _, row in assignments.iterrows():
        assignment_columns.append({
            "assignment_id": int(row["assignment_id"]),
            "title": row["Name"],
            "created_date": None if pd.isna(row["assignment_created_date"]) else row["assignment_created_date"].isoformat(),
            "last_allowed_date": None if pd.isna(row["assignment_last_allowed_date"]) else row["assignment_last_allowed_date"].isoformat(),
        })

    # lookup: 0 or NaN => missing
    latest_lookup = {}
    for _, row in latest.iterrows():
        key = (int(row["UserId"]), int(row["assignment_id"]))

        grade = None if pd.isna(row["Grade"]) else float(row["Grade"])
        submitted_at = None if pd.isna(row["submitted_at"]) else row["submitted_at"].isoformat()

        if grade is None or grade <= 0:
            latest_lookup[key] = {
                "status": "missing",
                "grade": None,
                "submitted_at": None,
                "is_late": False,
            }
        else:
            latest_lookup[key] = {
                "status": "submitted",
                "grade": grade,
                "submitted_at": submitted_at,
                "is_late": bool(row["is_late"]),
            }

    # build rows
    rows = []
    for _, student in students.iterrows():
        student_id = int(student["student_id"])

        cells = []
        for _, assignment in assignments.iterrows():
            assignment_id = int(assignment["assignment_id"])
            key = (student_id, assignment_id)

            if key not in latest_lookup:
                cells.append({
                    "assignment_id": assignment_id,
                    "status": "missing",
                    "grade": None,
                    "submitted_at": None,
                    "is_late": False,
                })
            else:
                cell = latest_lookup[key]
                cells.append({
                    "assignment_id": assignment_id,
                    "status": cell["status"],
                    "grade": cell["grade"],
                    "submitted_at": cell["submitted_at"],
                    "is_late": cell["is_late"],
                })

        rows.append({
            "student_id": student_id,
            "Email": student["Email"],
            "FirstName": student["FirstName"],
            "LastName": student["LastName"],
            "cells": cells,
        })

    return {
        "snapshot_date": snapshot_date_str,
        "assignments": assignment_columns,
        "rows": rows,
    }