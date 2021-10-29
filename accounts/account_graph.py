from TimeseriesUtil import TimeseriesUtil
import plotly.graph_objs as go
import pandas as pd


if __name__ == '__main__':
    query_string = """  SELECT time, measure_value::double as {}
                        FROM "realized-gains"."ross-gains" 
                        WHERE time between ago(14d) and now() 
                        AND type = 'account'
                        and measure_name = '{}'
                        ORDER BY time DESC """

    b_df = pd.DataFrame(TimeseriesUtil().run_query(query_string.format('balance', 'balance')))
    g_df = pd.DataFrame(TimeseriesUtil().run_query(query_string.format('gain', 'gain')))
    i_df = pd.DataFrame(TimeseriesUtil().run_query(query_string.format('investment', 'investment')))

    df = pd.concat([b_df.set_index('time'), g_df.set_index('time'),  i_df.set_index('time')], axis=1, join='inner')

    df['balance'] = df['balance'].apply(lambda x: "${0:,.2f}".format(float(x)))
    df['gain'] = df['gain'].apply(lambda x: "${0:,.2f}".format(float(x)))
    df['investment'] = df['investment'].apply(lambda x: "${0:,.2f}".format(float(x)))

    fig = go.Figure()  # declare figure

    fig.add_trace(go.Scatter(x=df.index, y=df['balance'], line=dict(color='blue', width=1.5), name='balance'))
    fig.add_trace(go.Scatter(x=df.index, y=df['gain'], line=dict(color='green', width=1.5), name='gain'))
    fig.add_trace(go.Scatter(x=df.index, y=df['investment'], line=dict(color='orange', width=1.5), name='investment'))

    fig.update_yaxes(autorange="reversed")

    fig.show()

