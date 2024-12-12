#prelims
import pandas as pd
import geopandas as gpd
import polars as pl
import plotly.express as px
import datetime as dt
from dateutil.relativedelta import relativedelta
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

#load data
df = pl.read_parquet('../port data/dashboard/main.parquet')
#init handy variables
earliest_date = df['time'].min()
latest_date = df['time'].max()

#define port stats function
def port_stats(df, start_date=earliest_date, end_date=latest_date):
    #create ports stats for most recent 12 months
    portstats_df = (
        #convert main gdf to polars
        df
        #filter to most recent 12 months
        .filter(pl.col('time').is_between(start_date, end_date))
        #ensure sorting
        .sort(['mmsi', 'time'])
        #create row index (for identifying docking events)
        .with_row_index('docking_id')
        .with_columns(
            #create docking event id - NOTE may need to ensure this captures all relevant messages
            docking_id = (
                #keep only docking ids associated with docking messages
                pl.when(pl.col('status')==5)
                .then(pl.col('docking_id'))
                .otherwise(pl.lit(None))
                #backfill over vessel
                .backward_fill().over('mmsi')
            )
        )
        #drop messages not associated with a docking event
        .drop_nulls(subset='docking_id')
        .with_columns(
            #sum anchorage time for each docking event
            time_at_anchor = (
                pl.when(pl.col('status')==1)
                .then(pl.col('status_duration'))
                .otherwise(pl.lit(None))
                .sum().over('docking_id')
            ),
            #get monthly vessels and visits
            vessels = pl.col('mmsi').n_unique().over('port_name', 'month'),
            visits = pl.col('docking_id').n_unique().over('port_name', 'month')
        )
        #aggregate to ports
        .group_by('port_name')
        .agg(
            #keep lat and long
            port_lat = pl.col('port_lat').first(),
            port_lon = pl.col('port_lon').first(),
            #get monthly average of unique vessels seen at each port
            vessels_avg = pl.col('vessels').mean(),
            #get monthly average of vessel visits at each port
            visits_avg = pl.col('visits').mean(),
            #get median time at berth in hours
            time_at_berth_median = (
                pl.when(pl.col('status')==5)
                .then(pl.col('status_duration'))
                .otherwise(pl.lit(None))
            ).median()/60,
            #get median time at anchor in hours
            time_at_anchor_median = pl.col('time_at_anchor').median()/60,
            #get mean time at anchor in hours
            time_at_anchor_mean = pl.col('time_at_anchor').mean()/60
        )
        #convert to pandas to that geopandas is happy
        .to_pandas()
    )
    #convert back to geodataframe
    portstats_gdf = (
        gpd.GeoDataFrame(
            portstats_df, 
            geometry=gpd.points_from_xy(portstats_df.port_lon, 
                                        portstats_df.port_lat),
            crs=3857
        )
    )
    return portstats_gdf

#init app
app = dash.Dash()
#layout
app.layout = (
    html.Div(
        children=[
            #set title of app
            html.H1('Port Performance Dashboard (alpha)'),
            html.H3('Select Date Range'),
            dcc.DatePickerRange(
                id='date_range',
                #set initial 
                initial_visible_month=str(latest_date - relativedelta(months=-12)),
                start_date=latest_date + relativedelta(months=-12),
                end_date=latest_date
            ),
            dcc.Graph(id='map_fig')
        ]
    )
)

#decorate with DatePickerRange component
@app.callback(
    Output('map_fig', 'figure'),
    Input('date_range', 'start_date'),
    Input('date_range', 'end_date')
)
def update_map(start_date, end_date):
    #ensure function doesn't change main df
    data = df.clone()
    if start_date and end_date:
        start_date = dt.datetime.fromisoformat(start_date) #refactor to DRY
        end_date = dt.datetime.fromisoformat(end_date)
        data = port_stats(data, start_date.date(), end_date.date())
    elif start_date:
        start_date = dt.datetime.fromisoformat(start_date)
        data = port_stats(data, start_date.date())
    elif end_date:
        end_date = dt.datetime.fromisoformat(end_date)
        data = port_stats(data, end_date=end_date.date())
    else:
        data = port_stats(data)
    #create map figure
    fig = px.scatter_geo(
        data,
        lon='port_lon',
        lat='port_lat',
        size='visits_avg',
        color='time_at_berth_median',
        range_color=[0,50],
        hover_name='port_name',
        size_max=20,
        title='Average visits per month & Median Hours at Berth',
        color_continuous_scale=px.colors.sequential.Viridis,
        width=1000,
        height=600,
        labels={
            'time_at_berth_median':'Median Hours at Berth'
        }
    )

    # Fit the view to ports
    fig.update_geos(fitbounds="locations")

    # Add footnote using add_annotation
    fig.add_annotation(
        text="Note: Circle size corresponds to average vessel visits per month",  # Footnote text
        xref="paper", yref="paper",  # Position relative to the plot area
        x=0, y=0-0.05,  # Adjust to footnote position
        showarrow=False,  # No arrow, just text
        font=dict(size=14, color="black"),  # Customize the font style
        align="left"
    )
    return fig

#run
if __name__ == '__main__':
    app.run_server(debug=True)