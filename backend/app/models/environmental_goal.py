"""Environmental Goal ORM model — sustainability targets with progress tracking.

Status (on-track / at-risk / achieved / missed) is **derived** from progress
against the target relative to how much of the goal's timeline has elapsed, so
it can't drift out of sync with reality. The value is still stored on the row
(for fast querying and reporting) but is refreshed automatically whenever
progress changes; call :meth:`refresh_status` from a scheduled job to also catch
purely time-based transitions (e.g. a deadline passing).
"""
from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.core.database import Base


class GoalStatus(str, enum.Enum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    ACHIEVED = "achieved"
    MISSED = "missed"


class TargetMetric(str, enum.Enum):
    """What the goal measures. Determines how progress is interpreted."""

    TOTAL_CO2E = "total_co2e"          # absolute emissions (lower is better)
    REDUCTION_PCT = "reduction_pct"    # % reduction vs baseline (higher is better)
    ENERGY = "energy"                  # energy consumption (lower is better)
    WATER = "water"                    # water consumption (lower is better)
    WASTE = "waste"                    # waste generated (lower is better)
    RENEWABLE_PCT = "renewable_pct"    # % renewable (higher is better)
    OTHER = "other"


# Fraction of remaining-progress-vs-remaining-time below which a goal is "at risk".
_AT_RISK_TOLERANCE = 0.9


class EnvironmentalGoal(Base):
    """A time-bound sustainability target for an organisation or department.

    Examples: 'Reduce emissions by 20%', 'Achieve Net Zero by 2030'.
    Progress is tracked via ``current_value`` against ``baseline_value`` and
    ``target_value``; direction (lower- vs higher-is-better) is inferred from
    whether the target sits below or above the baseline.
    """

    __tablename__ = "environmental_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ``None`` department == organisation-wide scope.
    department_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )

    target_metric: Mapped[TargetMetric] = mapped_column(
        Enum(TargetMetric, name="target_metric"),
        nullable=False,
        default=TargetMetric.TOTAL_CO2E,
    )
    # Numeric values — e.g. 500 (kgCO2e), 20 (%), 1000 (kWh)
    baseline_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    current_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)  # e.g. "kgCO2e", "%", "kWh"

    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline: Mapped[date] = mapped_column(Date, nullable=False)

    # Derived from progress vs timeline; kept in sync by ``refresh_status``.
    status: Mapped[GoalStatus] = mapped_column(
        Enum(GoalStatus, name="goal_status"), nullable=False, default=GoalStatus.ON_TRACK
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    department: Mapped["Department | None"] = relationship("Department")  # type: ignore[name-defined]  # noqa: F821

    # ── Progress ──────────────────────────────────────────────────────────

    @property
    def _lower_is_better(self) -> bool:
        """Reduction-style goals want the value to go *down* from baseline."""
        if self.baseline_value is None:
            # No baseline: treat REDUCTION/RENEWABLE percentages as higher-better.
            return self.target_metric not in (
                TargetMetric.REDUCTION_PCT,
                TargetMetric.RENEWABLE_PCT,
            )
        return self.target_value < self.baseline_value

    def _progress_fraction_for(self, current: float) -> float:
        """Progress toward the target for a given ``current`` value.

        Uses the baseline when available so reduction goals measure how far the
        value has moved from baseline toward target, not a raw current/target
        ratio. Values can exceed 1.0 when the target is overshot.
        """
        base, cur, tgt = self.baseline_value, current, self.target_value
        if base is not None and base != tgt:
            return (base - cur) / (base - tgt) if self._lower_is_better else (
                (cur - base) / (tgt - base)
            )
        # Fall back to a simple ratio when no usable baseline is set.
        if tgt == 0:
            return 1.0 if cur == 0 else 0.0
        return cur / tgt

    @property
    def progress_fraction(self) -> float:
        """Progress toward the target in [0, ∞), where 1.0 means target reached."""
        return self._progress_fraction_for(self.current_value)

    @property
    def progress_pct(self) -> float:
        """Percentage progress toward the target, clamped to [0, 100]."""
        return round(max(0.0, min(self.progress_fraction, 1.0)) * 100, 1)

    @property
    def is_target_met(self) -> bool:
        return self.progress_fraction >= 1.0

    # ── Derived status ────────────────────────────────────────────────────

    def _derive_status(self, current: float, as_of: date | None = None) -> GoalStatus:
        """Compute status from a given ``current`` value vs. the elapsed timeline.

        * ``ACHIEVED`` — the target has been met (regardless of date).
        * ``MISSED``   — the deadline has passed without meeting the target.
        * ``ON_TRACK`` — progress keeps pace with the fraction of time elapsed.
        * ``AT_RISK``  — progress lags meaningfully behind the timeline.
        """
        as_of = as_of or date.today()
        progress = self._progress_fraction_for(current)

        if progress >= 1.0:
            return GoalStatus.ACHIEVED
        if as_of >= self.deadline:
            return GoalStatus.MISSED

        # How far through the timeline are we?
        start = self.start_date
        if start is None or start >= self.deadline:
            time_fraction = 0.0
        else:
            elapsed = (as_of - start).days
            total = (self.deadline - start).days
            time_fraction = max(0.0, min(elapsed / total, 1.0))

        if time_fraction == 0.0:
            return GoalStatus.ON_TRACK
        return (
            GoalStatus.ON_TRACK
            if max(0.0, progress) >= time_fraction * _AT_RISK_TOLERANCE
            else GoalStatus.AT_RISK
        )

    def derive_status(self, as_of: date | None = None) -> GoalStatus:
        """Compute the status from current progress vs. elapsed timeline."""
        return self._derive_status(self.current_value, as_of)

    def refresh_status(self, as_of: date | None = None) -> GoalStatus:
        """Recompute and persist :attr:`status`. Returns the new value."""
        self.status = self.derive_status(as_of)
        return self.status

    @validates("current_value")
    def _refresh_on_progress(self, key, value):
        """Auto-derive status whenever progress is updated (no manual override)."""
        # Only recompute once enough fields exist to make it meaningful.
        if self.target_value is not None and self.deadline is not None:
            self.status = self._derive_status(value)
        return value

    def __repr__(self) -> str:  # pragma: no cover
        return f"<EnvironmentalGoal '{self.title}' {self.progress_pct}% — {self.status.value}>"
