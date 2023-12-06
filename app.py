# ! pip install dash
# ! pip install dash_bootstrap_components

from pathlib import Path
import pandas as pd
import numpy as np
import re
import plotly.graph_objects as go
import plotly.express as px
import geopandas as gpd
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, ctx, callback
import dash_bootstrap_components as dbc
from dash import html
from PIL import Image

###############################################################

shared_drive_dataset = 'data/'
static_vars = {'mapbox_token' : '.mapbox_token',
               'gdp' : { 'file' : 'GDP.xlsx',
                           'cleaned_tab' : 'GDP'},
               'findex' : { 'file' : 'Group 4 Preliminary Dataset.xlsx',
                           'cleaned_tab' : 'Findex Cleaned',
                            'raw_tab' : 'Raw Data'},
               'bsp' : { 'file' : 'Group 4 Preliminary Dataset.xlsx',
                           'cleaned_tab' : 'PH FI'},
               'longlat' : 'country_long_lat.xlsx'
                }

dict_findex_grouping = {
    'Mobile money account' : ['Mobile money account (% age 15+)',
                                'Mobile money account, female (% age 15+)',
                              'Mobile money account, male (% age 15+)',
                              'Mobile money account, young (% ages 15-24)',
                              'Mobile money account, older (% age 25+)',
                              'Mobile money account, primary education or less (% ages 15+)',
                              'Mobile money account, secondary education or more (% ages 15+)',
                              'Mobile money account, income, poorest 40% (% ages 15+)',
                              'Mobile money account, income, richest 60% (% ages 15+)',
                              'Mobile money account, out of labor force (% age 15+)',
                              'Mobile money account, in labor force (% age 15+)'],
    'Owns a credit card' : ['Owns a credit card (% age 15+)',
                            'Owns a credit card, female (% age 15+)',
                            'Owns a credit card, male (% age 15+)',
                            'Owns a credit card, young (% ages 15-24)',
                            'Owns a credit card, older (% age 25+)',
                            'Owns a credit card, primary education or less (% ages 15+)',
                            'Owns a credit card, secondary education or more (% ages 15+)',
                            'Owns a credit card, income, poorest 40% (% ages 15+)',
                            'Owns a credit card, income, richest 60% (% ages 15+)',
                            'Owns a credit card, out of labor force (% age 15+)',
                            'Owns a credit card, in labor force (% age 15+)'],
    'Owns a debit card' : ['Owns a debit card (% age 15+)',
                           'Owns a debit card, female (% age 15+)',
                           'Owns a debit card, male (% age 15+)',
                           'Owns a debit card, young (% ages 15-24)',
                           'Owns a debit card, older (% age 25+)',
                           'Owns a debit card, primary education or less (% ages 15+)',
                           'Owns a debit card, secondary education or more (% ages 15+)',
                           'Owns a debit card, income, poorest 40% (% ages 15+)',
                           'Owns a debit card, income, richest 60% (% ages 15+)',
                           'Owns a debit card, out of labor force (% age 15+)',
                           'Owns a debit card, in labor force (% age 15+)'],
    'Made a digital payment' : ['Made a digital payment (% age 15+)',
                                'Made a digital payment, female (% age 15+)',
                                'Made a digital payment, male (% age 15+)',
                                'Made a digital payment, young (% ages 15-24)',
                                'Made a digital payment, older (% age 25+)',
                                'Made a digital payment, primary education or less (% ages 15+)',
                                'Made a digital payment, secondary education or more (% ages 15+)',
                                'Made a digital payment, income, poorest 40% (% ages 15+)',
                                'Made a digital payment, income, richest 60% (% ages 15+)',
                                'Made a digital payment, out of labor force (% age 15+)',
                                'Made a digital payment, in labor force (% age 15+)'],
    'Received digital payments' : ['Received digital payments (% age 15+)',
                                   'Received digital payments, female (% age 15+)',
                                   'Received digital payments, male (% age 15+)',
                                   'Received digital payments, young (% ages 15-24)',
                                   'Received digital payments, older (% age 25+)',
                                   'Received digital payments, primary education or less (% ages 15+)',
                                   'Received digital payments, secondary education or more (% ages 15+)',
                                   'Received digital payments, income, poorest 40% (% ages 15+)',
                                   'Received digital payments, income, richest 60% (% ages 15+)',
                                   'Received digital payments, out of labor force (% age 15+)',
                                   'Received digital payments, in labor force (% age 15+)']
}

dict_bsp_grouping = {
    'BSP Indicators' : ['Number of Banks with Digital with Digital Onboarding Capacity',
                        'Number of Registered E-Money Accounts (in millions)',
                        'Number of Active E-Money Accounts (in millions)',
                        'Digital Payments Volume PesoNet (in millions)',
                        'Digital Payments Volume InstaPay (in millions)',
                        'Digital Payments Value PesoNet (in billions)',
                        'Digital Payments Value InstaPay (in billions)',
                        'Share of digital payments to total payment transactions (Volume)',
                        'Share of digital payments to total payment transactions (Value)']
    }


###############################################################

dataset_folder = Path(shared_drive_dataset)

# GDP dataset
df_gdp = pd.read_excel(# dataset_folder / static_vars['gdp']['file'],
                       Path(__file__).resolve().parent / "data/GDP.xlsx",
                       sheet_name=static_vars['gdp']['cleaned_tab'], header=1, usecols='A:D')

###############################################################

# Load mapbox token
px.set_mapbox_access_token(open(Path(__file__).resolve().parent / "data/.mapbox_token").read())

###############################################################

# Findex dataset
df_findex = pd.read_excel(# dataset_folder / static_vars['findex']['file'],
                       Path(__file__).resolve().parent / "data/Group 4 Preliminary Dataset.xlsx",
                       sheet_name=static_vars['findex']['raw_tab'])

# Add source column
df_findex['Source'] = 'Global Findex'
df_findex = df_findex[df_findex.columns.tolist()[-1:] + df_findex.columns.tolist()[:-1]]

# PHL as starting point. Check which Region PH is part of
target_region = df_findex[df_findex['Country code'] == 'PHL']['Region'].unique()[0]

# Filter regions same with PHL
df_findex = df_findex[(df_findex['Region']==target_region) &
                      (df_findex['Year'].isin([2011, 2014, 2017, 2021]))]

# Drop columns with too many NaNs
df_findex = df_findex.loc[:, df_findex.isnull().mean() < .5]

keep_cols = df_findex.columns[:8].tolist()
for x in df_findex.columns.values:
  if (# re.search('Financial institution account', x) or
      re.search('Mobile money account', x) or
      re.search('Owns a credit card', x) or
      re.search('Owns a debit card', x) or
      re.search('Made a digital payment', x) or
      re.search('Received digital payments', x)
      ):
    keep_cols.append(x)
df_findex = df_findex[keep_cols]

# Shorten name
df_findex = df_findex.replace('East Asia & Pacific (excluding high income)', 'East Asia & Pacific')

###############################################################

# BSP Quarterly data
df_bsp_quarterly = pd.read_excel(#dataset_folder / static_vars['bsp']['file'], usecols='A:B', skiprows=1, nrows=10,
                           Path(__file__).resolve().parent / "data/Group 4 Preliminary Dataset.xlsx",
                           usecols='A:B', skiprows=1, nrows=10,
                           sheet_name=static_vars['bsp']['cleaned_tab'])

###############################################################

# BSP Annual data
df_bsp_annual = pd.read_excel(# dataset_folder / static_vars['bsp']['file'], usecols='A:I', skiprows=13, nrows=5,
                           Path(__file__).resolve().parent / "data/Group 4 Preliminary Dataset.xlsx",
                           usecols='A:I', skiprows=13, nrows=5,
                           sheet_name=static_vars['bsp']['cleaned_tab'])

###############################################################

# Geometry dataset
# Longlat data can be used as zoom variables
df_longlat = pd.read_excel(# dataset_folder / static_vars['longlat']
                           Path(__file__).resolve().parent / "data/country_long_lat.xlsx")
df_longlat = df_longlat.rename(columns={df_longlat.columns[0]: 'Country name'})

df_geom = pd.DataFrame()
for i in df_findex['Country code'].unique():

  # Remove EAP (this is region code for total East Asia and Pacific values)
  if i not in ['EAP']:
    # file_path = dataset_folder / 'gadm41_{country_code}_shp/gadm41_{country_code}_0.shp'.format(country_code=i)
    file_path = Path(__file__).resolve().parent / 'data/gadm41_{country_code}_shp/gadm41_{country_code}_0.shp'.format(country_code=i)
    df_geom = pd.concat([df_geom, gpd.read_file(file_path)], axis=0, ignore_index=True)

df_geom = df_geom.rename(columns={df_geom.columns[0]: 'Country code', df_geom.columns[1]: 'Country name'})
df_geom = df_geom.merge(df_longlat.drop_duplicates(), on='Country name', how='left')

df_findex_geom = (df_geom.drop(columns=['Country name'])).merge(df_findex, on=['Country code'], how='left')
df_findex_geom = df_findex_geom.set_index('Country name')

###############################################################

# Initialize Dash application
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

###############################################################

# set this figures in html
regional_view_layout = html.Div(children=[
    dbc.Container(children=[
        html.Br(),
        dbc.Row(dcc.Link(html.Button('Go to Country View', style={'text-align':'center'}), href='/country-view'), justify="end"),
        dbc.Row(children=[
            dbc.Col(html.H1("Charting A Digital Future", style={'font-weight' : 'bold', 'color': 'darkblue', 'marginTop': 30})),
            dbc.Col(dbc.RadioItems(
                list(dict_findex_grouping.keys()),
                list(dict_findex_grouping.keys())[3],
                id='findex-radio-select1',
                inline=True), align='center')
            ], justify='evenly'),
        dbc.Row(children=[
            dbc.Col(),
            dbc.Col(html.Div(children=[
                dcc.Dropdown(id='findex-dropdown-select1')], style={'width': '85%'}))
            ], justify='end'),
        html.Br(),
        dbc.Row(children=[
            dbc.Col(html.Div(children=[
                dcc.Loading(id='map-loading', type="circle", children=dcc.Graph(id='eap-map-fig')),
                ], style={'width': '95%', 'display': 'inline-block', 'padding': '0px 0px', 'margin':'0% 0% 0% 0%'})),
            dbc.Col(html.Div(children=[
                dcc.Loading(id='fig2-loading', type="circle", children=dcc.Graph(id='hbar-fig'))
                ], style={'width': '80%', 'display': 'inline-block', 'padding': '0px 0px', 'margin':'0% 0% 0% 0%'}))
            ], justify='evenly'),
        html.Br(),
        dbc.Row(children=[
            html.Div(children=[
                dcc.Slider(df_findex['Year'].min(),
                       df_findex['Year'].max(),
                       step=None,
                       value=df_findex['Year'].max(),
                       marks={str(year): str(year) for year in df_findex['Year'].unique()},
                       id='year-slider')
                ], style={'width': '40%', 'display': 'inline-block', 'padding': '0px 0px', 'margin':'0% 2% 10px 0%'})
            ], justify="center"),
        ])
], style={'font-size' : '14px'})

@callback (
    Output('findex-dropdown-select1', 'options'),
    Output('findex-dropdown-select1', 'value'),
    Input('findex-radio-select1', 'value')
)
def set_dropdown_select (findex_radio_value):
    return dict_findex_grouping[findex_radio_value], dict_findex_grouping[findex_radio_value][0]

@callback (
    Output('eap-map-fig', 'figure'),
    Output('hbar-fig', 'figure'),
    Input('findex-dropdown-select1', 'value'),
    Input('year-slider', 'value')
)
def get_hbar (findex_dropdown_value, year_slider_value):

    df_tmp4 = df_findex[df_findex['Year']==year_slider_value]
    df_tmp4 = pd.melt(df_tmp4[['Country name', 'Year'] + [findex_dropdown_value]],
                      id_vars=['Country name', 'Year'],
                      value_vars=findex_dropdown_value,
                      var_name='Subgroup', value_name='Share')
    df_tmp4 = df_tmp4.sort_values(by='Share')

    # Horizontal Bar Chart
    # For total East Asia & Pacific
    trace1 = go.Bar(x=df_tmp4[df_tmp4['Country name']=='East Asia & Pacific']['Share'],
                    y=df_tmp4[df_tmp4['Country name']=='East Asia & Pacific']['Country name'],
                    orientation='h',
                    showlegend=False,
                    text=round(df_tmp4[df_tmp4['Country name']=='East Asia & Pacific']['Share']*100, 1),
                    textposition='auto',
                    marker=dict(color='#D3D3D3')
                    )
    # For each country in East Asia & Pacific
    trace2 = go.Bar(x=df_tmp4[df_tmp4['Country name']!='East Asia & Pacific']['Share'],
                    y=df_tmp4[df_tmp4['Country name']!='East Asia & Pacific']['Country name'],
                    orientation='h',
                    showlegend=False,
                    text=round(df_tmp4[df_tmp4['Country name']!='East Asia & Pacific']['Share']*100, 1),
                    textposition='auto',
                    marker=dict(color = df_tmp4[df_tmp4['Country name']!='East Asia & Pacific']['Share'], colorscale='Viridis')
                    )

    hbar_fig = go.Figure([trace2, trace1])
    hbar_fig.update_layout(paper_bgcolor = "rgba(0, 0, 0, 0)",
                           plot_bgcolor = "rgba(0, 0, 0, 0)",
                           xaxis_tickformat = ".0%")


    df_tmp = df_findex_geom[['geometry', 'latitude', 'longitude', 'Year'] + [findex_dropdown_value]]
    df_tmp = df_tmp[df_tmp['Year']==year_slider_value]

    # Use Choropleth for faster rendering
    eap_map = px.choropleth(df_tmp,
                        # geojson=df_tmp.geometry,
                        locations=df_tmp.index,
                        hover_name=df_tmp.index,
                        locationmode='country names',
                        color=findex_dropdown_value,
                        color_continuous_scale='Viridis',
                        scope='asia',
                        fitbounds='locations',
                        center={'lat': df_findex_geom[df_findex_geom['Country code']=='PHL']['latitude'].unique()[0], \
                                'lon': df_findex_geom[df_findex_geom['Country code']=='PHL']['longitude'].unique()[0]},
                        projection='mercator',
                        # template='ggplot2', 'seaborn', 'simple_white', 'plotly','plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
                        template='ggplot2'
                        )
    eap_map.update_coloraxes(
        colorbar={
            'orientation' : 'v',
            'yanchor': 'bottom',
            'y': 0,
            'xanchor': "left",
            'x': -0.2,
            'tickformat' : ".0%",
            'title' : None,
            'thickness' : 20
            }
        )
    eap_map.update_layout(margin={"r":0, "t":0, "l":0, "b":0})

    return eap_map, hbar_fig

###############################################################

def set_layout(fig, ht, fig_title, l=0, r=0, t=0, b=0):
    fig.update_layout(
        showlegend=True,
        legend={
            'orientation': "h",
            'yanchor': "top",
            'y': 0.95,
            'xanchor': "left",
            'x': 0.01,
            "font" : {"color" : "lightgray"}
        },
        margin={'t': t, 'r': r, 'l': l, 'b': b},
        xaxis={'anchor': 'y', 'domain': [0.0, 1.0]},
        yaxis={'anchor': 'x', 'domain': [0.0, 1.0]},
        yaxis_range=[0, ht],
        height=300,
        paper_bgcolor = "rgba(0, 0, 0, 0)",
        plot_bgcolor = "rgba(0, 0, 0, 0)",
        title = {
            "text" : fig_title,
            "font" : {"family" : "Arial, Bold",
                      "size" : 14},
            # "x" : 0.5,
            'xanchor' : 'left',
            'yanchor' : 'top'
            # "pad" : {'t': 50, 'r': 0, 'l': 0, 'b': 20}
            # "automargin" : True,
            # 'yanchor' : 'bottom',
        }
    )
    fig.update_xaxes(type='category')
    fig.update_annotations(font_size=8)

def set_layout2 (fig, fig_title, l=0, r=0, t=0, b=0):
    fig.update_layout(
        showlegend=True,
        legend={
            'orientation': "h",
            'yanchor': "top",
            'y': 0.95,
            'xanchor': "left",
            'x': 0.01,
            "font" : {"color" : "lightgray"}
        },
        margin={'t': t, 'r': r, 'l': l, 'b': b},
        xaxis={'anchor': 'y', 'domain': [0.0, 1.0]},
        yaxis={'anchor': 'x', 'domain': [0.0, 1.0]},
        height=300,
        paper_bgcolor = "rgba(0, 0, 0, 0)",
        plot_bgcolor = "rgba(0, 0, 0, 0)",
        title = {
            "text" : fig_title,
            "font" : {"family" : "Arial, Bold",
                      "size" : 14},
            # "x" : 0.5,
            'xanchor' : 'left',
            'yanchor' : 'top'
            # "pad" : {'t': 50, 'r': 0, 'l': 0, 'b': 20}
            # "automargin" : True,
            # 'yanchor' : 'bottom',
        }
    )
    # fig.update_layout(yaxis_range=[0, ht])
    # fig.update_xaxes(type='category')
    fig.update_annotations(font_size=8)

def get_bsp_bars(df_src, cols, name=None, col_color=dict(color='#3399FF')):

  trace1 = go.Bar(x=df_src['Period'],
                  y=df_src.iloc[:,-1],
                  marker=col_color,
                  name=name,
                  text=df_src.iloc[:,-1],
                  textposition='auto',
                  xperiodalignment="middle")
  return trace1

def get_groupbars(df_src, cols):
  first_level_attr = ['female', 'male', 'young', 'older', 'primary education', 'secondary education',
                      'income, poorest', 'income, richest', 'out of labor force', 'in labor force']

  df = pd.melt(df_src[['Country name', 'Year'] + cols],
                    id_vars=['Country name', 'Year'],
                    value_vars=cols,
                    var_name='Subgroup', value_name='Share')
  # df['Subgroup'] = df['Subgroup'].apply(lambda x: x[re.search('|'.join(first_level_attr).lower(), x.lower()).start():])
  df['Subgroup'] = df['Subgroup'].apply(lambda x: [attr for attr in first_level_attr if re.search(attr, x)][0])

  trace1 = go.Bar(x=df[df['Subgroup']==df['Subgroup'].unique()[0]]['Year'],
                y=df[df['Subgroup']==df['Subgroup'].unique()[0]]['Share']*100,
                marker=dict(color='#FF3333'),
                name=df['Subgroup'].unique()[0],
                hovertext=df['Subgroup'].unique()[0],
                text=np.round(df[df['Subgroup']==df['Subgroup'].unique()[0]]['Share']*100),
                textposition='auto'
                )
  trace2 = go.Bar(x=df[df['Subgroup']==df['Subgroup'].unique()[1]]['Year'],
                y=df[df['Subgroup']==df['Subgroup'].unique()[1]]['Share']*100,
                marker=dict(color='#3399FF'),
                name=df['Subgroup'].unique()[1],
                hovertext=df['Subgroup'].unique()[1],
                text=np.round(df[df['Subgroup']==df['Subgroup'].unique()[1]]['Share']*100),
                textposition='auto'
                )
  return trace1, trace2

country_view_layout = html.Div(children=[
    dbc.Container(children=[
        html.Br(),
        dbc.Row(dcc.Link(html.Button('Go to Regional View', style={'text-align':'center'}), href='/regional-view'), justify="end"),
        dbc.Row(children=[
            dbc.Col(html.H1("Charting A Digital Future",
                            style={'font-weight' : 'bold', 'color': 'darkblue', 'marginTop': 30}), width={"size": 6}),
            dbc.Col(dbc.RadioItems(id='findex-radio-select',
                                   inline=True), align='center', width={"size": 5}),
            dbc.Col(html.Img(id='img1', height=80))
            ], justify='around'),
        dbc.Row(children=[
            dbc.Col(),
            dbc.Col(html.Div(children=[
                dcc.Dropdown(
                    list(df_findex['Country name'].unique()),
                    list(df_findex['Country name'].unique())[-1],
                    id='country-dropdown-select',
                    )], style={'width': '85%'}))
            ], justify='end'),
        html.Br(),
        dbc.Row(children=[
            dbc.Col(html.Div(children=[
                dcc.Loading(id='fig1-loading', type="circle", children=dcc.Graph(id='fig1')),
                ], style={'width': '95%', 'display': 'inline-block', 'padding': '0px 0px', 'margin':'10% 0% 0% 10%'})),
            dbc.Col(html.Div(children=[
                dcc.Loading(id='fig2-loading', type="circle", children=dcc.Graph(id='fig2'))
                ], style={'width': '95%', 'display': 'inline-block', 'padding': '0px 0px', 'margin':'10% 0% 0% 10%'})),
            dbc.Col(html.Div(children=[
                dcc.Loading(id='fig3-loading', type="circle", children=dcc.Graph(id='fig3'))
                ], style={'width': '95%', 'display': 'inline-block', 'padding': '0px 0px', 'margin':'10% 0% 0% 10%'}))
            ]),
        html.Br(),
        dbc.Row(children=[
            dbc.Col(html.Div(children=[
                dcc.Loading(id='fig4-loading', type="circle", children=dcc.Graph(id='fig4')),
                ], style={'width': '95%', 'display': 'inline-block', 'padding': '0px 0px', 'margin':'10% 0% 0% 10%'})),
            dbc.Col(html.Div(children=[
                dcc.Loading(id='fig5-loading', type="circle", children=dcc.Graph(id='fig5'))
                ], style={'width': '95%', 'display': 'inline-block', 'padding': '0px 0px', 'margin':'10% 0% 0% 10%'})),
            dbc.Col(html.Div(children=[
                dcc.Loading(id='fig6-loading', type="circle", children=dcc.Graph(id='fig6'))
                ], style={'width': '95%', 'display': 'inline-block', 'padding': '0px 0px', 'margin':'10% 0% 0% 10%'}))
            ])
        ])
    ], style={'font-size' : '14px'})

@callback (
    Output('findex-radio-select', 'options'),
    Output('findex-radio-select', 'value'),
    Input('country-dropdown-select', 'value')
)
def set_radio_select (country_dropdown_value):
    if country_dropdown_value == 'Philippines':
      return list(dict_findex_grouping.keys()) + list(dict_bsp_grouping.keys()), list(dict_findex_grouping.keys())[3]
    return list(dict_findex_grouping.keys()), list(dict_findex_grouping.keys())[3]

@callback(
    Output('img1', 'src'),
    Input('country-dropdown-select', 'value')
)
def get_static_img(country_dropdown_value):
  if country_dropdown_value == 'Philippines':
    # return Image.open(dataset_folder / 'country_img/PHL.png')
    return Image.open(Path(__file__).resolve().parent / 'data/country_img/PHL.png')
  # Add other country link option
  return None

@callback(
    Output('fig1', 'figure'),
    Output('fig2', 'figure'),
    Output('fig3', 'figure'),
    Output('fig4', 'figure'),
    Output('fig5', 'figure'),
    Output('fig6', 'figure'),
    Input('country-dropdown-select', 'value'),
    Input('findex-radio-select', 'value')
)
def update_graph(country_dropdown_value, findex_radio_value):

  if ((country_dropdown_value == 'Philippines') & (findex_radio_value == 'BSP Indicators')):

    trace1 = get_bsp_bars(df_bsp_quarterly, df_bsp_quarterly.iloc[:,-1], col_color=dict(color='#3399FF'))
    fig1 = go.Figure([trace1])
    set_layout2(fig1, fig_title=str(df_bsp_quarterly.columns[-1]))
    fig1.update_layout(showlegend=False)
    fig1.update_xaxes(
        dtick="M3",
        tick0=df_bsp_quarterly['Period'].min(),
        tickformat="%b %Y",
        tickangle=-20,
        ticklabelmode="period")

    # So bars will still be visible, determine max yaxes height relative to max value for selected country
    ht = df_bsp_annual.iloc[:,0:2].iloc[:,-1].max()
    ht = (ht if ht % 10 == 0 else ht + 10 - ht % 10)

    trace2 = get_bsp_bars(df_bsp_annual.iloc[:, [0, 1]], df_bsp_annual.iloc[:, [0, 1]], col_color=dict(color='#3399FF'))
    fig2 = go.Figure([trace2])
    set_layout2(fig2, fig_title=str(df_bsp_annual.iloc[:, [0, 1]].columns[-1]))
    fig2.update_xaxes(type='category')
    fig2.update_layout(showlegend=False)

    trace3 = get_bsp_bars(df_bsp_annual.iloc[:, [0, 2]], df_bsp_annual.iloc[:, [0, 2]], col_color=dict(color='#3399FF'))
    fig3 = go.Figure([trace3])
    set_layout2(fig3, fig_title=str(df_bsp_annual.iloc[:, [0, 2]].columns[-1]))
    fig3.update_xaxes(type='category')
    fig3.update_layout(showlegend=False)

    trace4 = get_bsp_bars(df_bsp_annual.iloc[:, [0, 3]], df_bsp_annual.iloc[:, [0, 3]], col_color=dict(color='#FF3333'), name="Pesonet")
    trace5 = get_bsp_bars(df_bsp_annual.iloc[:, [0, 4]], df_bsp_annual.iloc[:, [0, 4]], col_color=dict(color='#3399FF'), name="Instapay")
    fig4 = go.Figure([trace4, trace5])
    fig4.update_layout(barmode='stack')
    fig4.update_xaxes(type='category')
    set_layout2(fig4, fig_title="Digital Payments Volume (in millions)")

    trace6 = get_bsp_bars(df_bsp_annual.iloc[:, [0, 5]], df_bsp_annual.iloc[:, [0, 5]], col_color=dict(color='#3399FF'), name="Pesonet")
    trace7 = get_bsp_bars(df_bsp_annual.iloc[:, [0, 6]], df_bsp_annual.iloc[:, [0, 6]], col_color=dict(color='#FF3333'), name="Instapay")
    fig5 = go.Figure([trace6, trace7])
    fig5.update_layout(barmode='stack')
    fig5.update_xaxes(type='category')
    set_layout2(fig5, fig_title="Digital Payments Value (in billions)")

    trace8 = get_bsp_bars(df_bsp_annual.iloc[:, [0, 7]], df_bsp_annual.iloc[:, [0, 7]], col_color=dict(color='#3399FF'), name="Volume")
    trace9 = get_bsp_bars(df_bsp_annual.iloc[:, [0, 8]], df_bsp_annual.iloc[:, [0, 8]], col_color=dict(color='#FF3333'), name="Value")
    fig6 = go.Figure([trace8, trace9])
    fig6.update_xaxes(type='category')
    set_layout2(fig6, fig_title="Share of Digital Payments to Total Payment Transactions")

  else:
    df_tmp2 = df_findex[(df_findex['Country name']==country_dropdown_value)][['Country name', 'Year'] + dict_findex_grouping[findex_radio_value]]
    df_tmp3 = df_gdp[df_gdp['Country name']==country_dropdown_value].drop(columns=['GDP in Billions'])

    # So bars will still be visible, determine max yaxes height relative to max value for selected country
    ht = (df_tmp2.drop(columns=['Country name', 'Year']).dropna().to_numpy().max()*100)
    ht = (ht if ht % 10 == 0 else ht + 10 - ht % 10)

    trace1 = go.Scatter(x=df_tmp3['Year'],
                        y=df_tmp3['GDP Growth %']*100,
                        showlegend=True,
                        text=round(df_tmp3['GDP Growth %']*100, 1),
                        name='GDP Growth %',
                        line_color='#FF3333'
                        )
    trace2 = go.Bar(x=df_tmp2.iloc[:,:3].iloc[:,-2],
                    y=(df_tmp2.iloc[:,:3].iloc[:,-1])*100,
                    marker=dict(color='#3399FF'),
                    name=df_tmp2.iloc[:,:3].columns[-1],
                    hovertext=df_tmp2.iloc[:,:3].columns[-1],
                    text=np.round((df_tmp2.iloc[:,:3].iloc[:,-1])*100),
                    textposition='auto')
    fig1 = go.Figure([trace1, trace2])
    set_layout(fig1, ht, fig_title="% w/ " + str(findex_radio_value) + " & YoY GDP Growth")

    trace3, trace4 = get_groupbars(df_tmp2, cols=df_tmp2.columns[3:5].tolist())
    fig2 = go.Figure([trace3, trace4])
    set_layout(fig2, ht, fig_title=str(findex_radio_value) + " by Sex")

    trace5, trace6 = get_groupbars(df_tmp2, cols=df_tmp2.columns[5:7].tolist())
    fig3 = go.Figure([trace5, trace6])
    set_layout(fig3, ht, fig_title=str(findex_radio_value) + " by Age")

    trace7, trace8 = get_groupbars(df_tmp2, cols=df_tmp2.columns[7:9].tolist())
    fig4 = go.Figure([trace7, trace8])
    set_layout(fig4, ht, fig_title=str(findex_radio_value) + " by Education")

    trace9, trace10 = get_groupbars(df_tmp2, cols=df_tmp2.columns[9:11].tolist())
    fig5 = go.Figure([trace9, trace10])
    set_layout(fig5, ht, fig_title=str(findex_radio_value) + " by Income")

    trace11, trace12 = get_groupbars(df_tmp2, cols=df_tmp2.columns[11:13].tolist())
    fig6 = go.Figure([trace11, trace12])
    set_layout(fig6, ht, fig_title=str(findex_radio_value) + " by Employment")

  return fig1, fig2, fig3, fig4, fig5, fig6

###############################################################

# Update the index page
@callback(Output('page-content', 'children'),
          Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/country-view':
        return country_view_layout
    else:
        return regional_view_layout

###############################################################

if __name__ == '__main__':
    # app.run_server(host='127.0.0.1', port='8050')
    # app.run(debug=True)
    app.run()