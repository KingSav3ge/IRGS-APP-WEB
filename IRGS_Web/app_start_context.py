"""Actor-received Engine start context for read-only App presentation."""
from core_world import CoreWorld
from start_readiness import actor_view


def received_start_context(record, actor):
    # This display snapshot is not an execution/recovery token. Actual command
    # acceptance continues to use the host's private branch/restore CAS scope.
    return actor_view(CoreWorld(state=record['state']), actor,
                      branch_id=record['id'], restore_id='app-read-only-presentation')
