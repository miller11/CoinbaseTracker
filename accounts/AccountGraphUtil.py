import plotly.graph_objs as go


class AccountGraphUtil:
    def __init__(self):
        self.fig = go.Figure()  # declare figure
        self._graph_account_data()

    def show_figure(self):
        self.fig.show()

    def get_html(self):
        return self.fig.to_html(include_plotlyjs=False, full_html=False)

    def get_json(self):
        return self.fig.to_json()

    def _graph_account_data(self):
        self.fig.add_trace(
            go.Scatter(x=self.data.index, y=self.data['MA20'], line=dict(color='blue', width=1.5), name='Long Term MA'))
        self.fig.add_trace(
            go.Scatter(x=self.data.index, y=self.data['MA5'], line=dict(color='orange', width=1.5),
                       name='Short Term MA'))