"""Report generation API routes (issue #13)."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.carbon_transaction import SourceType
from app.services.environmental_report_service import EnvironmentalReportService

router = APIRouter(prefix="/reports", tags=["reports"])

_CONTENT = {
    "csv": ("text/csv", "csv"),
    "excel": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xlsx",
    ),
    "pdf": ("application/pdf", "pdf"),
}


@router.get("/environmental")
def generate_environmental_report(
    format: str = Query(..., pattern="^(csv|excel|pdf)$"),
    department_id: Optional[int] = None,
    source_type: Optional[SourceType] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """Export Carbon Transactions filtered by department/date range/module."""
    service = EnvironmentalReportService(db)
    filters = dict(
        department_id=department_id,
        source_type=source_type,
        date_from=date_from,
        date_to=date_to,
    )
    if format == "csv":
        content = service.to_csv(**filters)
    elif format == "excel":
        content = service.to_excel(**filters)
    elif format == "pdf":
        content = service.to_pdf(**filters)
    else:  # unreachable given the Query pattern, kept for clarity
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported format")

    media_type, ext = _CONTENT[format]
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="environmental_report.{ext}"'},
    )
