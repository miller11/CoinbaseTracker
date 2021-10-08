import yfinance as yf


class MovingAverageUtil:
    def __init__(self, currency_pair):
        self.currency_pair = currency_pair

    def get_moving_average(self, time_period, interval, num_samples):
        data = yf.download(tickers=self.currency_pair, period=time_period, interval=interval)

        return data['Close'].tail(num_samples).mean()
