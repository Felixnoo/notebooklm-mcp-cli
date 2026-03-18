"""Export tools - Export artifacts to Google Docs/Sheets."""

from typing import Any

from ._utils import get_client, logged_tool
from ...services import exports as export_service, ServiceError


@logged_tool()
def export_artifact(
    artifact_id: str,
    export_type: str,
    title: str | None = None,
    notebook_id: str | None = None,
) -> dict[str, Any]:
    """Export a NotebookLM artifact to Google Docs or Sheets.

    Supports:
    - Data Tables → Google Sheets
    - Reports (Briefing Doc, Study Guide, Blog Post) → Google Docs

    Args:
        artifact_id: Artifact UUID to export
        export_type: "docs" or "sheets"
        title: Title for exported document (optional)
        notebook_id: Notebook UUID (default: uses saved default notebook ID)

    Returns: URL to the created Google Doc/Sheet
    """
    try:
        client = get_client()
        
        # Use default notebook ID if not provided
        from ._utils import get_default_notebook_id
        if not notebook_id:
            notebook_id = get_default_notebook_id()
            if not notebook_id:
                return {"status": "error", "error": "No notebook ID provided and no default notebook ID configured. Use notebook_list to see available notebooks."}
        
        result = export_service.export_artifact(
            client=client,
            notebook_id=notebook_id,
            artifact_id=artifact_id,
            export_type=export_type,
            title=title,
        )
        return result
    except ServiceError as e:
        return {"status": "error", "error": e.user_message}
    except Exception as e:
        return {"status": "error", "error": str(e)}
