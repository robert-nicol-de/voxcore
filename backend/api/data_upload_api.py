import pandas as pd
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter()

def analyze_schema(df):
    return {
        "columns": list(df.columns),
        "types": {col: str(dtype) for col, dtype in df.dtypes.items()}
    }

def generate_charts(df, schema):
    charts = []
    numeric_cols = df.select_dtypes(include="number").columns
    category_cols = df.select_dtypes(include="object").columns
    # Trend chart
    if "date" in df.columns and len(numeric_cols) > 0:
        charts.append({
            "type": "line",
            "x": "date",
            "y": numeric_cols[0]
        })
    # Category breakdown
    if len(category_cols) > 0 and len(numeric_cols) > 0:
        charts.append({
            "type": "bar",
            "x": category_cols[0],
            "y": numeric_cols[0]
        })
    return charts

def generate_insights(df):
    # Dummy insights for demo
    insights = []
    if "revenue" in df.columns:
        change = df["revenue"].pct_change().mean()
        if change < 0:
            insights.append({"id": "trend", "insight": f"Revenue trend ↓ {abs(int(change*100))}%"})
        else:
            insights.append({"id": "trend", "insight": f"Revenue trend ↑ {int(change*100)}%"})
    if "category" in df.columns:
        top = df["category"].value_counts().idxmax()
        insights.append({"id": "topcat", "insight": f"Top category: {top}"})
    if "region" in df.columns:
        under = df.groupby("region")["revenue"].mean().idxmin()
        insights.append({"id": "region", "insight": f"Region: {under} underperforming"})
    return insights

@router.post("/api/data/upload")
def upload_data(file: UploadFile = File(...)):
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)
    else:
        return JSONResponse({"error": "Unsupported file type"}, status_code=400)
    schema = analyze_schema(df)
    charts = generate_charts(df, schema)
    insights = generate_insights(df)
    return {"charts": charts, "insights": insights}
