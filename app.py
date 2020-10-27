import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np
import geojson
import math



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('airbnb_NYC_2019.csv')
fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="neighbourhood_group", zoom=9)
fig.update_layout(mapbox_style="carto-positron")
figSunburst = px.sunburst(df, path=['neighbourhood_group', 'room_type'], values='price')
room_histogram = px.histogram(df, x="room_type", color="neighbourhood_group")
violin_fig = px.violin(df, y="price", x='neighbourhood_group', box=True)
treemap_fig=px.treemap(df, path=[px.Constant('nyc'), 'neighbourhood_group', 'neighbourhood'], values='price',
                  hover_data=['neighbourhood'])

app.layout = html.Div([

    html.H1(children='Airbnb NYC', style={'font-family': 'Helvetica', 'textAlign': 'center'}),
    html.Div([
      html.Label('Select a neighborhood',style={'font-family': 'Helvetica'}),
      dcc.Dropdown(
          id="dropdown-neighbourhood",
          options=[
              {'label': 'Brooklyn', 'value': 'Brooklyn'},
              {'label': 'Manhattan', 'value': 'Manhattan'},
              {'label': 'Bronx', 'value': 'Bronx'},
              {'label': 'Queens', 'value': 'Queens'},
              {'label': 'Staten Island', 'value': 'Staten Island'}
          ],
          placeholder="Select a neighborhoods",
          value=['Brooklyn', 'Manhattan', 'Bronx', 'Queens', 'Staten Island'],
          multi=True
      ),

      dcc.Graph(
          id='map-nyc',
          figure=fig
      )
    ]),
    html.Div([
        html.H3(children='Price, room type and neighborhoods', style={'justify-content': 'center', 'font-family': 'Helvetica','text-align': 'center'}),
         html.H4(children="Price"),
        dcc.Slider(
          id='my-slider',
          min=0,
          max=1200,
          step=50,
          value=100,
          marks={
            0: '$0',
            200: '$200',
            400: '$400',
            600: '$600',
            800: '$800',
            1000: '$1000',
            1200: '$1200+'
          }
        ),
          html.Div(id='slider-output-container'),
      ], style={'width': '100%'}),
    html.Div([
      html.Div([
        dcc.Graph(
          id="sunburst-fig",
          figure=figSunburst
        ),

      ], style={'width': '48%'}),
      html.Div([
        dcc.Graph(
          id="histogram-room",
          figure=room_histogram
        )
      ], style={'width': '48%'})
      ], style={'display': 'flex'}),
    html.Div([
       dcc.Graph(
        id="violin-graph",
        figure=violin_fig
      ),
    ]),
    html.Div([
      html.Div([
        html.P(children="Avg price - Manhattan"),
        html.H4(children="123", id="manhattan-mean", style={'color': '#EF553B', 'text-align': 'center', 'font-size': '40px'})
      ]),
      html.Div([
        html.P(children="Avg price -  Brooklyn"),
        html.H4(children="123", id='brooklyn-mean', style={'color': '#636EFA', 'text-align': 'center', 'font-size': '40px'})
      ]),
      html.Div([
        html.P(children="Avg price -  Queens"),
        html.H4(children="123", id="queens-mean", style={'color': '#02CC96', 'text-align': 'center', 'font-size': '40px'})
      ]),
      html.Div([
        html.P(children="Avg price Bronx"),
        html.H4(children="123", id="bronx-mean", style={'color': '#FFA15A', 'text-align': 'center', 'font-size': '40px'})
      ]),
      html.Div([
        html.P(children="Avg price Staten Island"),
        html.H4(children="123", id="si-island", style={'color': '#AB63FA', 'text-align': 'center', 'font-size': '40px'})
      ]),

    ], style={'display': 'flex', 'justify-content': 'space-around', 'font-family': 'Helvetica'}),
    html.Div([
      html.H3(children='Neighborhoods', style={'justify-content': 'center', 'font-family': 'Helvetica','text-align': 'center'}),
      dcc.Graph(
        id="treemap",
        figure=treemap_fig
      )
    ]),
])

@app.callback(
  [
    dash.dependencies.Output('sunburst-fig', 'figure'),
    dash.dependencies.Output('histogram-room', 'figure'),
    dash.dependencies.Output('violin-graph', 'figure')
  ],
  [dash.dependencies.Input('my-slider', 'value')]
)
def update_sunburst(price):
  if price == 1200:
    df_filter = df
  else:
    df_filter = df[df['price'] <= price]

  sunb = px.sunburst(df_filter, path=['room_type', 'neighbourhood_group'], values='price', hover_data=['neighbourhood'])
  histo = px.histogram(df_filter, x="room_type", color="neighbourhood_group")
  violin = violin_fig = px.violin(df_filter, y="price", x='neighbourhood_group', box=True)
  return sunb, histo, violin


@app.callback(
  dash.dependencies.Output('map-nyc', 'figure'),
  dash.dependencies.Input('dropdown-neighbourhood', 'value')
)

def update_figure(value):
  df_filter = df[
               df['neighbourhood_group'].isin(value)
  ]
  fig = px.scatter_mapbox(df_filter, lat="latitude", lon="longitude", color="neighbourhood_group", zoom=8)
  fig.update_layout(mapbox_style="carto-positron")

  return fig

@app.callback(
  [
    dash.dependencies.Output('manhattan-mean', 'children'),
    dash.dependencies.Output('brooklyn-mean', 'children'),
    dash.dependencies.Output('queens-mean', 'children'),
    dash.dependencies.Output('bronx-mean', 'children'),
    dash.dependencies.Output('si-island', 'children'),
  ],
  [dash.dependencies.Input('my-slider', 'value')]
)

def update_mean(price):
  if price == 1200:
    df_filter = df
  else:
    df_filter = df[df['price'] <= price]

  mh_mean = math.floor(df_filter[df_filter['neighbourhood_group'] == 'Manhattan']['price'].mean())
  br_mean = math.floor(df_filter[df_filter['neighbourhood_group'] == 'Brooklyn']['price'].mean())
  qu_mean = math.floor(df_filter[df_filter['neighbourhood_group'] == 'Queens']['price'].mean())
  bro_mean = math.floor(df_filter[df_filter['neighbourhood_group'] == 'Bronx']['price'].mean())
  si_mean = math.floor(df_filter[df_filter['neighbourhood_group'] == 'Staten Island']['price'].mean())
  
  return mh_mean, br_mean, qu_mean, bro_mean, si_mean

if __name__ == '__main__':
    app.run_server(debug=True)