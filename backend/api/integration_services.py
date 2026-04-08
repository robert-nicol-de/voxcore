import os
import requests
import smtplib
from email.mime.text import MIMEText
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

SLACK_TOKEN = os.environ.get("SLACK_TOKEN", "xoxb-your-token")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "#alerts")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "localhost")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 25))
SMTP_FROM = os.environ.get("SMTP_FROM", "voxcore@system.ai")

router = APIRouter()

def send_slack_message(channel, text, blocks=None):
    resp = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
        json={
            "channel": channel,
            "text": text,
            "blocks": blocks
        }
    )
    return resp.json()

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.sendmail(SMTP_FROM, [to], msg.as_string())

@router.post("/api/slack/actions")
async def handle_slack_action(request: Request):
    payload = await request.json()
    action_id = payload.get("actions", [{}])[0].get("value")
    # TODO: Implement execute_action_from_slack(action_id)
    # For now, just acknowledge
    return JSONResponse({"status": "ok", "action_id": action_id})

# Example trigger endpoint for testing
@router.post("/api/trigger/slack-alert")
def trigger_slack_alert():
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Revenue dropped 18%*"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": "🧠 Impact Story: Revenue declined significantly in the South region. A promotion was launched, resulting in a +12% recovery."}},
        {"type": "section", "text": {"type": "mrkdwn", "text": "⚡ Suggested Action: Launch promotion campaign (78% success rate)"}},
        {"type": "actions", "elements": [
            {"type": "button", "text": {"type": "plain_text", "text": "Approve Action"}, "value": "approve_action_123"},
            {"type": "button", "text": {"type": "plain_text", "text": "View Insight"}, "url": "https://app.voxcore.ai/insight/123"}
        ]}
    ]
    send_slack_message(SLACK_CHANNEL, "Revenue dropped 18%", blocks)
    return {"status": "sent"}

@router.post("/api/trigger/email-daily")
def trigger_email_daily():
    subject = "📊 VoxCore Daily Report"
    body = """
• 3 Insights detected
• 2 Actions executed
• +18% total impact
• 1 Auto-action triggered
🧠 Highlight: Revenue decline recovered within 4 days after promotion.
"""
    send_email("executive@company.com", subject, body)
    return {"status": "sent"}
