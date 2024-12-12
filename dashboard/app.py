#prelims
import polars as pl
import plotly.express as px
import datetime as dt
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

#load data
df = pl.read_parquet('../port data/dashboard/main.parquet')
print(df.head(2))
#init handy variables
latest_date = df['time'].max()


#init app
app = dash.Dash()
app.layout = (
    html.Div(
        children=[
            #set title of app
            html.H1('Port Performance Dashboard (alpha)'),
            dcc.DatePickerRange(
                id='date_range',
                #initial_visible_month=
            )
        ]
    )
)



#run
#if __name__ == '__main__':
 #   app.run_server(debug=True)