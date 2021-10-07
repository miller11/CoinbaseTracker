import yfinance as yf


class MovingAverageUtil:
    def __init__(self, currency):
        self.currency = currency

    def get_moving_average(self, time_period, interval, num_samples):
        data = yf.download(tickers=self.currency, period=time_period, interval=interval)

        return data['Close'].tail(num_samples).mean()
