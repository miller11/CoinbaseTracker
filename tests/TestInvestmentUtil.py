from trader_bot.InvestmentUtil import InvestmentUtil


class TestInvestmentUtil(InvestmentUtil):
    def __init__(self, currency_pair, interval, short_term_periods, long_term_periods):
        super().__init__(currency_pair, interval, short_term_periods, long_term_periods)
        self._decision = ''
        self._reason = ''
        self._margin = 0
        self._sma = 0
        self._lma = 0

    def set_sma(self, sma):
        self._sma = sma
        return self

    def set_lma(self, lma):
        self._lma = lma
        return self

    def short_term_average(self):
        return self._sma

    def long_term_average(self):
        return self._lma
