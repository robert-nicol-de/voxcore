from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

router = APIRouter()

class GoogleSheetRequest(BaseModel):
    spreadsheet_id: str
    worksheet_name: str = None  # Optional, default to first sheet
    credentials_json: str  # JSON string of Google service account credentials

@router.post("/api/data/google-sheets")
def fetch_google_sheet(req: GoogleSheetRequest):
    # Save credentials to a temp file
    creds_path = "google_creds.json"
    with open(creds_path, "w") as f:
        f.write(req.credentials_json)
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(req.spreadsheet_id)
        ws = sheet.worksheet(req.worksheet_name) if req.worksheet_name else sheet.get_worksheet(0)
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        # Optionally: run schema/insight/chart logic here
        return JSONResponse({
            "columns": list(df.columns),
            "rows": df.to_dict(orient="records")
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    finally:
        if os.path.exists(creds_path):
            os.remove(creds_path)
