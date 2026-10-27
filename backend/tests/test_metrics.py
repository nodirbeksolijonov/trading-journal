from datetime import date

import pytest

from app.metrics import calc_pnl, calc_r_multiple, round2, validate_exit, validate_levels
from app.models import Side


def test_round2_never_returns_negative_zero():
    assert str(round2(-0.001)) == "0.0"
    assert round2(-0.006) == -0.01


def test_long_pnl_and_r():
    assert calc_pnl(Side.LONG, 100, 110, 10) == 100
    assert calc_r_multiple(Side.LONG, 100, 110, 95, 10) == 2


def test_short_pnl_and_r():
    assert calc_pnl(Side.SHORT, 100, 90, 5) == 50
    assert calc_r_multiple(Side.SHORT, 100, 90, 105, 5) == 2


def test_losing_trade_hits_stop_is_minus_one_r():
    assert calc_r_multiple(Side.LONG, 100, 95, 95, 1) == -1
    assert calc_r_multiple(Side.SHORT, 100, 105, 105, 1) == -1


def test_fees_reduce_pnl_and_r():
    # Risk is 5 * 10 = 50, gross +100, fees 10 -> net +90 = 1.8R.
    assert calc_pnl(Side.LONG, 100, 110, 10, fees=10) == 90
    assert calc_r_multiple(Side.LONG, 100, 110, 95, 10, fees=10) == 1.8
    # A losing trade at the stop loses more than 1R once fees are paid.
    assert calc_r_multiple(Side.LONG, 100, 95, 95, 10, fees=10) == -1.2


def test_open_trade_or_missing_stop_has_no_values():
    assert calc_pnl(Side.LONG, 100, None, 10, fees=5) is None
    assert calc_r_multiple(Side.LONG, 100, None, 95, 10) is None
    assert calc_r_multiple(Side.LONG, 100, 110, None, 10) is None


@pytest.mark.parametrize(
    "side, stop, tp",
    [
        (Side.LONG, 105, None),
        (Side.LONG, 100, None),
        (Side.LONG, None, 90),
        (Side.SHORT, 95, None),
        (Side.SHORT, None, 110),
    ],
)
def test_levels_on_wrong_side_rejected(side, stop, tp):
    with pytest.raises(ValueError):
        validate_levels(side, 100, stop, tp)


@pytest.mark.parametrize(
    "exit_price, exit_date, message",
    [
        (110, None, "Exit date is required"),
        (None, date(2026, 10, 2), "needs an exit price"),
        (110, date(2026, 9, 30), "before the entry date"),
    ],
)
def test_invalid_exit_rejected(exit_price, exit_date, message):
    with pytest.raises(ValueError, match=message):
        validate_exit(exit_price, date(2026, 10, 1), exit_date)


def test_valid_exits_accepted():
    validate_exit(None, date(2026, 10, 1), None)  # open
    validate_exit(110, date(2026, 10, 1), date(2026, 10, 1))  # same-day
    validate_exit(110, date(2026, 10, 1), date(2026, 10, 9))  # held over
