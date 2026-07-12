"""Environmental Report generation (issue #13).

Filters: Department, Date Range, Module (source type) — the criteria that map
onto real Environmental data. Employee/Challenge/ESG Category from the
Business Workflow's Section 7 filter set are Social/Governance/Gamification
concepts with no relationship to CarbonTransaction and are out of scope here;
they belong to the shared Custom Report Builder once those modules expose
their own report rows.

Exports the filtered Carbon Transactions as CSV, Excel (.xlsx), or PDF.
"""
from __future__ import annotations

import csv
import io
from datetime import date
from typing import Optional

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from sqlalchemy.orm import Session

from app.models.carbon_transaction import SourceType
from app.repositories.carbon_transaction_repository import CarbonTransactionRepository

_COLUMNS = ["Date", "Department", "Module", "Emission Factor", "Quantity", "Unit", "CO2e (kg)", "Created By", "Status"]


class EnvironmentalReportService:
    def __init__(self, db: Session):
        self.repo = CarbonTransactionRepository(db)

    def _rows(
        self,
        *,
        department_id: Optional[int],
        source_type: Optional[SourceType],
        date_from: Optional[date],
        date_to: Optional[date],
    ) -> list[list]:
        transactions = self.repo.list(
            department_id=department_id,
            source_type=source_type,
            date_from=date_from,
            date_to=date_to,
        )
        return [
            [
                t.transaction_date.isoformat(),
                t.department.name if t.department else "Unassigned",
                t.source_type.value,
                t.emission_factor.name,
                t.quantity,
                t.emission_factor.unit,
                t.co2e,
                t.created_by.value,
                t.status.value,
            ]
            for t in transactions
        ]

    def to_csv(self, **filters) -> bytes:
        rows = self._rows(**filters)
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(_COLUMNS)
        writer.writerows(rows)
        return buf.getvalue().encode("utf-8")

    def to_excel(self, **filters) -> bytes:
        rows = self._rows(**filters)
        wb = Workbook()
        ws = wb.active
        ws.title = "Environmental Report"
        ws.append(_COLUMNS)
        for row in rows:
            ws.append(row)
        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    def to_pdf(self, **filters) -> bytes:
        rows = self._rows(**filters)
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(letter))
        table_data = [_COLUMNS] + [[str(cell) for cell in row] for row in rows]
        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ]
            )
        )
        doc.build([table])
        return buf.getvalue()
