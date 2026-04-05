from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from snapshot import build_snapshot, build_journal
from ai_recommendations import build_ai_recommendations
import pandas as pd


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def df_to_records(df: pd.DataFrame):
    df = df.copy()
    df = df.astype(object)
    df = df.where(pd.notna(df), None)
    return df.to_dict(orient="records")


def validate_date(date: str):
    if not date or not isinstance(date, str):
        raise HTTPException(status_code=400, detail="Date is required in format YYYY-MM-DD")

    try:
        pd.Timestamp(date)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")


@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.get("/snapshot")
def get_snapshot(date: str):
    validate_date(date)

    result = build_snapshot(date)

    return {
        "student_snapshot": df_to_records(result["student_snapshot"]),
        "low_performance_students": df_to_records(result["low_performance_students"]),
        "declining_performance_students": df_to_records(result["declining_performance_students"]),
        "low_submission_students": df_to_records(result["low_submission_students"]),
        "top_students": df_to_records(result["top_students"]),
    }


@app.get("/journal")
def get_journal(date: str):
    validate_date(date)
    return build_journal(date)


@app.get("/recommendations_ai")
def get_recommendations_ai(date: str, use_llm: bool = False):
    validate_date(date)

    recommendations = build_ai_recommendations(
        snapshot_date_str=date,
        use_llm=use_llm,
    )

    safe_recommendations = []
    for rec in recommendations:
        clean_rec = {}
        for key, value in rec.items():
            if pd.isna(value) if not isinstance(value, (list, dict, str, bool, type(None))) else False:
                clean_rec[key] = None
            else:
                clean_rec[key] = value
        safe_recommendations.append(clean_rec)

    return {
        "snapshot_date": date,
        "use_llm": use_llm,
        "count": len(safe_recommendations),
        "recommendations": safe_recommendations,
    }