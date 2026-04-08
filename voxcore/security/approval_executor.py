from voxcore.core import VoxCoreEngine

class ApprovalExecutor:
    def __init__(self, engine=None):
        self.engine = engine or VoxCoreEngine()

    def execute_from_approval(self, approval_request):
        context = approval_request.get("context")
        if not context:
            raise ValueError("No context found in approval request")
        return self.engine.execute_query(
            question=context.get("question", ""),
            generated_sql=context.get("sql", ""),
            platform=context.get("platform", "postgres"),
            user_id=approval_request.get("user_id"),
            connection=None
        )
