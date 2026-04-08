from voxcore.connectors.base import BaseConnector
from voxcore.connectors.registry import register_connector

@register_connector("sheets")
class SheetsConnector(BaseConnector):
    def connect(self):
        import gspread  # lazy import
        return gspread.service_account(filename=self.config["credentials_json"])

    def test_connection(self):
        try:
            client = self.connect()
            spreadsheet = client.open(self.config["spreadsheet_name"])
            return spreadsheet is not None
        except:
            return False

    def get_schema(self):
        client = self.connect()
        spreadsheet = client.open(self.config["spreadsheet_name"])
        worksheet = spreadsheet.sheet1
        columns = worksheet.row_values(1)
        return {"columns": columns}

    def execute_query(self, query: str):
        # For demo: just return all rows as dicts
        client = self.connect()
        spreadsheet = client.open(self.config["spreadsheet_name"])
        worksheet = spreadsheet.sheet1
        rows = worksheet.get_all_records()
        return rows
