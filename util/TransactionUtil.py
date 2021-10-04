from MovingAverageUtil import MovingAverageUtil


def calculate_coinbase_fee(amount):
    if amount <= 10.99:
        return .99
    elif amount <= 26.49:
        return 1.49
    elif amount <= 51.99:
        return 1.99
    elif amount <= 78.05:
        return 2.99
    else:
        return amount * .0149


class TransactionUtil:
    MARGIN_PERCENTAGE = .015
    TIME_PERIOD = "14d"

    def __init__(self, currency_type, interval, short_term_periods, long_term_periods):
        self.currency_type = currency_type
        self.interval = interval
        self.short_term_periods = short_term_periods
        self.long_term_periods = long_term_periods

    def should_sell(self, buy_amount, sell_amount):
        long_term_average = self.long_term_average()
        short_term_average = self.short_term_average()

        if short_term_average <= long_term_average:
            fees = calculate_coinbase_fee(buy_amount) + calculate_coinbase_fee(sell_amount)
            investment = buy_amount + fees + (buy_amount * self.MARGIN_PERCENTAGE)
            if sell_amount >= investment:
                print(f'Should sell here. Sell amount: ${sell_amount}. Investment + margin: {investment}.')
                return True
            else:
                print(f'Should NOT sell here, not enough margin. Sell amount: ${sell_amount}. Investment + margin: {investment}.')
                return False
        else:
            print(f'Should NOT sell here. Long term average (${long_term_average}) is higher than the short term '
                  f'average (${short_term_average})')
            return False

    def should_buy(self):
        long_term_average = self.long_term_average()
        short_term_average = self.short_term_average()

        if short_term_average >= long_term_average:
            print(f'Should buy here. short term average (${short_term_average}) is higher than the short term '
                  f'average (${long_term_average}). This indicates a price rally.')
            return True
        else:
            print(f'Should NOT buy here. short term average (${short_term_average}) is NOT higher than the short term '
                  f'average (${long_term_average}).')
            return False

    def short_term_average(self):
        return MovingAverageUtil(self.currency_type).get_moving_average(self.TIME_PERIOD, self.interval,
                                                                        self.short_term_periods)

    def long_term_average(self):
        return MovingAverageUtil(self.currency_type).get_moving_average(self.TIME_PERIOD, self.interval,
                                                                        self.long_term_periods)
