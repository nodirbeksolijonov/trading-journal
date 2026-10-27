import pytest

from app.metrics import calc_pnl, calc_r_multiple, validate_levels
from app.models import Side


def test_long_pnl_and_r():
    assert calc_pnl(Side.LONG, 100, 110, 10) == 100
    assert calc_r_multiple(Side.LONG, 100, 110, 95) == 2


def test_short_pnl_and_r():
    assert calc_pnl(Side.SHORT, 100, 90, 5) == 50
    assert calc_r_multiple(Side.SHORT, 100, 90, 105) == 2


def test_losing_trade_hits_stop_is_minus_one_r():
    assert calc_r_multiple(Side.LONG, 100, 95, 95) == -1
    assert calc_r_multiple(Side.SHORT, 100, 105, 105) == -1


def test_open_trade_or_missing_stop_has_no_values():
    assert calc_pnl(Side.LONG, 100, None, 10) is None
    assert calc_r_multiple(Side.LONG, 100, None, 95) is None
    assert calc_r_multiple(Side.LONG, 100, 110, None) is None


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
