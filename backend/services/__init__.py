from ._guard import *
from backend.services.query_service import QueryService

# Simple in-memory DB mock for demonstration; replace with real DB/session in production
class InMemoryDB:
	def execute(self, sql):
		# Example: return static data for demo
		if "orders" in sql:
			return [
				{"month": "Jan", "value": 50},
				{"month": "Feb", "value": 60},
				{"month": "Mar", "value": 70},
			]
		else:
			return [
				{"month": "Jan", "value": 1000},
				{"month": "Feb", "value": 1200},
				{"month": "Mar", "value": 1400},
			]

query_service = QueryService(InMemoryDB())
