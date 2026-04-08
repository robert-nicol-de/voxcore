approval_queue = []

def add_to_queue(query):
    approval_queue.append({
        "id": len(approval_queue) + 1,
        "query": query,
        "status": "pending"
    })

def get_queue():
    return approval_queue

def approve_query(query_id):
    for q in approval_queue:
        if q["id"] == query_id:
            q["status"] = "approved"
            return q
    return None

def reject_query(query_id):
    for q in approval_queue:
        if q["id"] == query_id:
            q["status"] = "rejected"
            return q
    return None
