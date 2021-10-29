import plotly.graph_objs as go


class GraphUtil:
    def __init__(self, data):
        self.short_term_samplings = 5
        self.long_term_samplings = 20
        self.data = data

        self.fig = go.Figure()  # declare figure
        self._graph_ticker_info()

    def show_figure(self):
        self.fig.show()

    def get_html(self):
        return self.fig.to_html(include_plotlyjs=False, full_html=False)

    def get_json(self):
        return self.fig.to_json()

    def add_account_buy(self, datetime):
        self.fig.add_vline(x=datetime, line_dash="dash")

    def add_account_sell(self, datetime):
        self.fig.add_vline(x=datetime, line_color='darkgrey', line_dash="dot")

    def _graph_ticker_info(self):
        # Adding Moving average calculated field
        self.data['MA5'] = self.data['Close'].rolling(5).mean()
        self.data['MA20'] = self.data['Close'].rolling(20).mean()

        # Candlestick
        self.fig.add_trace(go.Candlestick(x=self.data.index,
                                          open=self.data['Open'],
                                          high=self.data['High'],
                                          low=self.data['Low'],
                                          close=self.data['Close'], name='market data'))

        # Add Moving average on the graph
        self.fig.add_trace(
            go.Scatter(x=self.data.index, y=self.data['MA20'], line=dict(color='blue', width=1.5), name='Long Term MA'))
        self.fig.add_trace(
            go.Scatter(x=self.data.index, y=self.data['MA5'], line=dict(color='orange', width=1.5),
                       name='Short Term MA'))

        # Updating X axis and graph
        self.fig.update_xaxes(rangeslider_visible=True)
