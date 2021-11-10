import pytest
from .TestInvestmentUtil import TestInvestmentUtil
from trader_bot.TraderBot import TraderBotConfig
from trader_bot.TestingTraderBot import TestingTraderBot

CURRENCY_PAIR = 'BTC-USD'
INTERVAL = '30m'
SHORT_TERM_PERIODS = 5
LONG_TERM_PERIODS = 20


def _get_invest_util():
    return TestInvestmentUtil(CURRENCY_PAIR, INTERVAL, SHORT_TERM_PERIODS, LONG_TERM_PERIODS)


def _get_bot_config():
    json_body = "{\n  \"account_id\": \"980ee1ea-75ac-5c33-b80f-14427a26cf5c\",\n  " \
                "\"currency\": \"SOL1\",\n  " \
                "\"default_buy\": 100,\n  " \
                "\"interval\": \"30m\",\n  " \
                "\"short_term_periods\": 5,\n  " \
                "\"long_term_periods\": 20\n}"

    return TraderBotConfig(json_body)


# Test should hold SMA > LMA
def test_no_transact_hold():
    investment_util = _get_invest_util().set_sma(11).set_lma(10)
    bot = TestingTraderBot(_get_bot_config(), investment_util)
    bot.setup().execute_actions()

    assert bot.get_decision()['decision'] == 'HOLD'


# Test should BUY SMA < LMA
def test_no_transact_buy():
    investment_util = _get_invest_util().set_sma(10).set_lma(12)
    bot = TestingTraderBot(_get_bot_config(), investment_util)
    bot.setup().execute_actions()

    assert bot.get_decision()['decision'] == 'BUY'


# should sell, enough margin and sma < lma
def test_transact_buy_sell():
    last_transaction = {"operation": "BUY", "amount": 98.51, "currency_value": 150}
    investment_util = _get_invest_util().set_sma(150).set_lma(152)

    bot = TestingTraderBot(_get_bot_config(), investment_util)
    bot.set_last_transaction(last_transaction)
    bot.setup().execute_actions()

    assert bot.get_decision()['decision'] == 'SELL'


# Should hold, not enough margin
def test_transact_buy_hold_margin():
    last_transaction = {"operation": "BUY", "amount": 158, "currency_value": 242}
    investment_util = _get_invest_util().set_sma(240).set_lma(242)

    bot = TestingTraderBot(_get_bot_config(), investment_util)
    bot.set_last_transaction(last_transaction)
    bot.setup().execute_actions()

    assert bot.get_decision()['decision'] == 'HOLD'


# Should hold, sma > lma
def test_transact_buy_hold_ma():
    last_transaction = {"operation": "BUY", "amount": 158, "currency_value": 200}
    investment_util = _get_invest_util().set_sma(242).set_lma(240)

    bot = TestingTraderBot(_get_bot_config(), investment_util)
    bot.set_last_transaction(last_transaction)
    bot.setup().execute_actions()

    assert bot.get_decision()['decision'] == 'HOLD'


# Should hold, sma < lma
def test_transact_sell_hold_ma():
    last_transaction = {"operation": "SELL", "amount": 158, "currency_value": 200}
    investment_util = _get_invest_util().set_sma(240).set_lma(242)

    bot = TestingTraderBot(_get_bot_config(), investment_util)
    bot.set_last_transaction(last_transaction)
    bot.setup().execute_actions()

    assert bot.get_decision()['decision'] == 'HOLD'


# Should buy, sma < lma
def test_transact_sell_sell_ma():
    last_transaction = {"operation": "SELL", "amount": 158, "currency_value": 200}
    investment_util = _get_invest_util().set_sma(242).set_lma(240)

    bot = TestingTraderBot(_get_bot_config(), investment_util)
    bot.set_last_transaction(last_transaction)
    bot.setup().execute_actions()

    assert bot.get_decision()['decision'] == 'BUY'
