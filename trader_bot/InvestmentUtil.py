from .MovingAverageUtil import MovingAverageUtil


def calculate_coinbase_fee(amount: float):
    amount = float(amount)

    if amount <= 10.99:
        return .99
    elif amount <= 26.49:
        return 1.49
    elif amount <= 51.99:
        return 1.99
    elif amount <= 78.05:
        return 2.99
    else:
        return float(amount) * 0.0149


class InvestmentUtil:
    MARGIN_PERCENTAGE = .015
    TIME_PERIOD = "14d"

    def __init__(self, currency_pair, interval, short_term_periods, long_term_periods):
        self._decision = ''
        self._reason = ''
        self._margin = 0
        self.currency_pair = currency_pair
        self.interval = interval
        self.short_term_periods = short_term_periods
        self.long_term_periods = long_term_periods

    def should_sell(self, buy_amount: float, sell_amount: float):
        long_term_average = self.long_term_average()
        short_term_average = self.short_term_average()

        if short_term_average <= long_term_average:
            fees = calculate_coinbase_fee(buy_amount) + calculate_coinbase_fee(sell_amount)
            investment = buy_amount + fees + (buy_amount * self.MARGIN_PERCENTAGE)
            if sell_amount >= investment:
                self._decision = 'SELL'
                self._reason = f'Should sell here. Sell amount: ${sell_amount}. Investment + margin: {investment}.'
                self._margin = sell_amount - (buy_amount + fees)

                print(self._reason)

                return True
            else:
                self._decision = 'HOLD'
                self._reason = f'Should NOT sell here, not enough margin. Sell amount: ${sell_amount}. Investment + ' \
                               f'margin: {investment}.'

                print(self._reason)

                return False
        else:
            self._decision = 'HOLD'
            self._reason = f'Should NOT sell here. Long term average (${long_term_average}) is lower than the short ' \
                           f'term average (${short_term_average})'

            print(self._reason)

            return False

    def should_buy(self):
        long_term_average = self.long_term_average()
        short_term_average = self.short_term_average()

        if short_term_average >= long_term_average:
            self._decision = 'BUY'
            self._reason = f'Should buy here. short term average (${short_term_average}) is higher than the short ' \
                           f'term average (${long_term_average}). This indicates a price rally. '

            print(self._reason)

            return True
        else:
            self._decision = 'HOLD'
            self._reason = f'Should NOT buy here. short term average (${short_term_average}) is NOT higher than the ' \
                           f'short term average (${long_term_average}). '

            print(self._reason)

            return False

    def short_term_average(self):
        return MovingAverageUtil(self.currency_pair).get_moving_average(self.TIME_PERIOD, self.interval,
                                                                        self.short_term_periods)

    def long_term_average(self):
        return MovingAverageUtil(self.currency_pair).get_moving_average(self.TIME_PERIOD, self.interval,
                                                                        self.long_term_periods)

    def get_decision(self):
        return self._decision

    def get_reason(self):
        return self._reason

    def get_margin(self):
        return self._margin
