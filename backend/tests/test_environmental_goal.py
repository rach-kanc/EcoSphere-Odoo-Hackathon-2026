"""Tests for EnvironmentalGoal derived status (issue #3 acceptance criteria)."""
from datetime import date

import pytest

from app.models.environmental_goal import EnvironmentalGoal, GoalStatus, TargetMetric


def make_goal(**kw) -> EnvironmentalGoal:
    defaults = dict(
        title="Reduce emissions",
        target_metric=TargetMetric.TOTAL_CO2E,
        baseline_value=1000.0,
        target_value=800.0,       # reduction goal: lower is better
        current_value=900.0,
        unit="kgCO2e",
        start_date=date(2025, 1, 1),
        deadline=date(2025, 12, 31),
    )
    defaults.update(kw)
    return EnvironmentalGoal(**defaults)


def test_achieved_when_target_met_regardless_of_date():
    g = make_goal(current_value=800.0)  # exactly at target
    assert g.derive_status(as_of=date(2025, 3, 1)) is GoalStatus.ACHIEVED
    # Overshooting the target still counts as achieved.
    g.current_value = 750.0
    assert g.derive_status(as_of=date(2025, 3, 1)) is GoalStatus.ACHIEVED


def test_missed_when_deadline_passed_without_target():
    g = make_goal(current_value=900.0)  # 50% of the way, target not met
    assert g.derive_status(as_of=date(2026, 1, 1)) is GoalStatus.MISSED


def test_on_track_when_progress_keeps_pace_with_timeline():
    # Halfway through the year, halfway to target (1000 -> 900 of a 1000->800 goal).
    g = make_goal(current_value=900.0)  # progress = 50%
    assert g.derive_status(as_of=date(2025, 7, 2)) is GoalStatus.ON_TRACK


def test_at_risk_when_progress_lags_timeline():
    # 90% through the year but only 25% of the reduction done.
    g = make_goal(current_value=950.0)  # progress = 25%
    assert g.derive_status(as_of=date(2025, 11, 25)) is GoalStatus.AT_RISK


def test_org_wide_goal_has_no_department():
    g = make_goal(department_id=None)
    assert g.department_id is None
    assert g.derive_status(as_of=date(2025, 7, 2)) in GoalStatus


def test_growth_goal_direction_inferred_from_baseline():
    # Renewable %: baseline 20 -> target 60, higher is better.
    g = make_goal(
        target_metric=TargetMetric.RENEWABLE_PCT,
        baseline_value=20.0, target_value=60.0, current_value=40.0, unit="%",
    )
    assert g.progress_pct == pytest.approx(50.0)  # (40-20)/(60-20)
    assert g.derive_status(as_of=date(2025, 7, 2)) is GoalStatus.ON_TRACK


def test_status_auto_refreshes_when_progress_updated():
    g = make_goal(current_value=950.0)  # lagging
    # Assigning current_value re-derives status without a manual set.
    g.current_value = 800.0
    assert g.status is GoalStatus.ACHIEVED
    g.current_value = 950.0
    assert g.status in (GoalStatus.ON_TRACK, GoalStatus.AT_RISK, GoalStatus.MISSED)


def test_refresh_status_persists_value():
    g = make_goal(current_value=800.0)
    returned = g.refresh_status(as_of=date(2025, 6, 1))
    assert returned is GoalStatus.ACHIEVED
    assert g.status is GoalStatus.ACHIEVED
