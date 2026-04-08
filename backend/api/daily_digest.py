import datetime
from .integration_services import send_email
from voxcore.engine.insight_memory import InsightMemory
from .action_api import ACTION_EXECUTIONS

from fastapi import APIRouter

router = APIRouter()
insight_memory = InsightMemory()

def collect_daily_metrics():
    today = datetime.date.today().isoformat()
    insights = [i for i in insight_memory.get_all_insights() if i.get("created_at", "").startswith(today)]
    actions = [e for e in ACTION_EXECUTIONS if e.get("created_at", "").startswith(today)]
    auto_actions = [e for e in actions if e.get("user_id") == "auto-system" or e.get("auto")]
    total_impact = sum(e.get("impact", 0) for e in actions if e.get("impact") is not None)
    highlight = ""
    if total_impact > 0:
        highlight = f"Revenue drop recovered in 4 days."
    return {
        "insights": len(insights),
        "actions": len(actions),
        "auto_actions": len(auto_actions),
        "total_impact": total_impact,
        "highlight": highlight
    }


def generate_html_email(data):
    # Impact story (reuse engine)
    from .impact_story_api import generate_impact_story
    impact_story = data.get('impact_story', '')
    if not impact_story and data.get('top_insight'):
        impact_story = generate_impact_story({
            'insight': data['top_insight']['insight'],
            'actions': data['top_insight'].get('actions', []),
            'results': data['top_insight'].get('results', [])
        })
    # Automation metrics
    auto_metrics = data.get('auto_metrics', {})
    # Top 3 insights
    top_insights = data.get('top_insights', [])
    insights_html = ''.join(f'<li>{i+1}. {ins["title"]} ({ins["insight"]})</li>' for i, ins in enumerate(top_insights))
    # Actions
    actions_html = ''.join(f'<li>{a}</li>' for a in data.get('actions_list', []))
    sent_to_slack = 'Yes' if data.get('sent_to_slack') else 'No'
    return f"""
    <html><body style='font-family:sans-serif;'>
    <h2>📊 VoxCore Daily Report</h2>
    <hr>
    <p><b>📈 Total Impact:</b> +{data['total_impact']:.1f}%<br>
    <b>⚡ Auto-Actions:</b> {data['auto_actions']}<br>
    <b>🎯 Success Rate:</b> {auto_metrics.get('success_rate', 0)*100:.0f}%<br>
    <b>🤖 Automation Rate:</b> {auto_metrics.get('automation_rate', 0)*100:.0f}%<br>
    <b>📤 Sent to Slack:</b> {sent_to_slack}</p>
    <hr>
    <h3>🔥 Top Insights</h3>
    <ul>{insights_html}</ul>
    <h3>🧠 Impact Story</h3>
    <p>{impact_story}</p>
    <h3>⚡ Actions Taken</h3>
    <ul>{actions_html}</ul>
    <hr>
    <a href='https://voxcore.app' style='color:#2563eb;font-weight:bold;'>View Full Dashboard →</a>
    </body></html>
    """


import requests
@router.post("/api/trigger/send-daily-digest")
def send_daily_digest():
    data = collect_daily_metrics()
    # Top 3 insights (by confidence/score)
    from .insights import _build_viis_insights
    top_insights = _build_viis_insights()[:3]
    data['top_insights'] = top_insights
    data['top_insight'] = top_insights[0] if top_insights else None
    # Actions taken (titles)
    data['actions_list'] = [e.get('action_id', 'Action') for e in ACTION_EXECUTIONS if e.get('created_at', '').startswith(datetime.date.today().isoformat())]
    # Impact story
    from .impact_story_api import generate_impact_story
    if data['top_insight']:
        data['impact_story'] = generate_impact_story({
            'insight': data['top_insight']['insight'],
            'actions': data['top_insight'].get('actions', []),
            'results': data['top_insight'].get('results', [])
        })
    # Automation metrics
    try:
        r = requests.get('http://127.0.0.1:8000/api/actions/auto-metrics')
        if r.ok:
            data['auto_metrics'] = r.json()
    except Exception:
        data['auto_metrics'] = {}
    # Sent to Slack (if any insight sent today)
    data['sent_to_slack'] = any(getattr(i, 'sentToSlack', False) for i in top_insights)
    html = generate_html_email(data)
    send_email("executive@company.com", "VoxCore Daily Report", html)
    return {"status": "sent", "email": html}
