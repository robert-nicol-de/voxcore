from voxcore.api.monitoring_ws import active_connections
import json

async def broadcast_event(event: dict):
    dead_connections = []
    for conn in active_connections:
        try:
            await conn.send_text(json.dumps(event))
        except:
            dead_connections.append(conn)
    for dc in dead_connections:
        active_connections.remove(dc)
