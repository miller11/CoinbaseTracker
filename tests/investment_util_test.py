import pytest
from .TestInvestmentUtil import TestInvestmentUtil

CURRENCY_PAIR = 'BTC-USD'
INTERVAL = '30m'
SHORT_TERM_PERIODS = 5
LONG_TERM_PERIODS = 20


# Test should_sell
# Test SMA > LMA. Should HOLD
def test_sell_hold():
    investment_util = TestInvestmentUtil(CURRENCY_PAIR, INTERVAL, SHORT_TERM_PERIODS, LONG_TERM_PERIODS)
    investment_util = investment_util.set_sma(11).set_lma(10)

    assert not investment_util.should_sell(100, 105)
    assert investment_util.get_decision() == 'HOLD'


# Test SMA <= LMA and does not have enough margin. Should HOLD
def test_sell_hold_margin():
    investment_util = TestInvestmentUtil(CURRENCY_PAIR, INTERVAL, SHORT_TERM_PERIODS, LONG_TERM_PERIODS)
    investment_util = investment_util.set_sma(11).set_lma(10)

    assert not investment_util.should_sell(100, 101)
    assert investment_util.get_decision() == 'HOLD'


# Test SMA <= LMA and has enough margin. Should SELL
def test_sell_sell():
    investment_util = TestInvestmentUtil(CURRENCY_PAIR, INTERVAL, SHORT_TERM_PERIODS, LONG_TERM_PERIODS)
    investment_util = investment_util.set_sma(11).set_lma(11)

    assert investment_util.should_sell(100, 105)
    assert investment_util.get_decision() == 'SELL'


# Test SMA >= LMA so buy
def test_buy_buy():
    investment_util = TestInvestmentUtil(CURRENCY_PAIR, INTERVAL, SHORT_TERM_PERIODS, LONG_TERM_PERIODS)
    investment_util = investment_util.set_sma(12).set_lma(11)

    assert investment_util.should_buy()
    assert investment_util.get_decision() == 'BUY'


# Test SMA !>= LMA so HOLD
def test_buy_hold():
    investment_util = TestInvestmentUtil(CURRENCY_PAIR, INTERVAL, SHORT_TERM_PERIODS, LONG_TERM_PERIODS)
    investment_util = investment_util.set_sma(10).set_lma(11)

    assert not investment_util.should_buy()
    assert investment_util.get_decision() == 'HOLD'
