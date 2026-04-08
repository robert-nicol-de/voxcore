from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
import requests
import os

router = APIRouter()

# Dummy: Replace with real user/session token retrieval
ACCESS_TOKEN = os.environ.get("GOOGLE_ACCESS_TOKEN", "demo_token")

@router.get("/api/google/sheets")
def list_sheets():
    drive_url = "https://www.googleapis.com/drive/v3/files"
    res = requests.get(
        drive_url,
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        params={
            "q": "mimeType='application/vnd.google-apps.spreadsheet'",
            "fields": "files(id,name)"
        }
    )
    return res.json()

@router.get("/api/google/sheet-preview")
def preview_sheet(sheet_id: str):
    # For demo: fetch first 5 rows using Sheets API
    sheets_url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/A1:Z6"
    res = requests.get(
        sheets_url,
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    values = res.json().get("values", [])
    if not values:
        return JSONResponse({"error": "No data found"}, status_code=404)
    columns = values[0]
    rows = values[1:]
    return {"columns": columns, "rows": rows}
