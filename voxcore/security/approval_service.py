from datetime import datetime
import psycopg2

import json
from datetime import datetime, timedelta

class ApprovalService:
    def __init__(self, conn):
        self.conn = conn

    def create_request(self, query, user_id, risk_score, reason, context=None, expires_at=None):
        cur = self.conn.cursor()
        context_json = json.dumps(context) if context else None
        if not expires_at:
            expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        cur.execute("""
            INSERT INTO approval_requests (query, user_id, risk_score, reason, context, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (query, user_id, risk_score, reason, context_json, expires_at))
        self.conn.commit()
        return cur.fetchone()[0]

    def get_by_id(self, request_id):
        cur = self.conn.cursor()
        cur.execute("SELECT id, query, user_id, status, risk_score, reason, context, expires_at FROM approval_requests WHERE id = %s", (request_id,))
        row = cur.fetchone()
        if not row:
            return None
        context = None
        try:
            context = json.loads(row[6]) if row[6] else None
        except Exception:
            context = None
        return {
            "id": row[0],
            "query": row[1],
            "user_id": row[2],
            "status": row[3],
            "risk_score": row[4],
            "reason": row[5],
            "context": context,
            "expires_at": row[7]
        }

    def list_pending(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT * FROM approval_requests
            WHERE status = 'pending'
            ORDER BY created_at DESC
        """)
        return cur.fetchall()

    def review(self, request_id, decision, reviewer):
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE approval_requests
            SET status = %s,
                reviewed_by = %s,
                reviewed_at = %s
            WHERE id = %s
        """, (decision, reviewer, datetime.utcnow(), request_id))
        self.conn.commit()
