from tracemalloc import start
import dash
from dash import html, dcc, dash_table, callback_context
import plotly.graph_objects as go
import dash_trich_components as dtc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import json
import pandas as pd
from pandas_ta import bbands
import pandas_datareader as web
import numpy as np
import datetime
from scipy.stats import pearsonr
'''
# Creating a dictionary with the economic sectors with their respective stocks. Thereafter we'll convert it into
# a json file so we don't need to read the data source page multiple times.

stocks = pd.read_html(
    'https://blog.toroinvestimentos.com.br/empresas-listadas-b3-bovespa', decimal=',')
stocks_sectores = stocks[1]
stocks_sectores.columns = stocks_sectores.iloc[0]
stocks_sectores.drop(index=0, inplace=True)
stocks_sectores_dict = stocks_sectores[[
    'Ticker', 'Setor']].to_dict(orient='list')

# Implementing the economic sector names as the dictionay key and their stocks as values.
d = {}
for stock, sector in zip(stocks_sectores_dict['Ticker'], stocks_sectores_dict['Setor']):
    if sector not in d.keys():
        d[sector] = [stock]
    else:
        d[sector].append(stock)

# Correcting a tiny issue with the resulting dictionary: sometimes, two dictionary keys were
# concerning the very same economic sector! Let's merge them into one.
d['Bens Industriais'].extend(d['Bens industriais'])
d.pop('Bens industriais')
d['Bens Industriais']
d['Energia Elétrica'].extend(d['Energia elétrica'])
d.pop('Energia elétrica')
d['Energia Elétrica']
d['Aluguel de Veículos'].extend(d['Locação de veículos'])
d.pop('Locação de veículos')
d['Construção civil'].extend(d['Construção'])
d.pop('Construção')
d['Shopping Centers'].extend(d['Exploração de imóveis'])
d.pop('Exploração de imóveis')

# Now, we'll translate the economic sectors names to English for better understanding.
translate = {'Alimentos': 'Food & Beverages', 'Varejo': 'Retail', 'Companhia aérea': 'Aerospace',
             'Seguros': 'Insurace', 'Shopping Centers': 'Shopping Malls', 'Financeiro': 'Finance',
             'Mineração': 'Mining', 'Químicos': 'Chemical', 'Educação': 'Education',
             'Energia Elétrica': 'Electrical Energy', 'Viagens e lazer': 'Traveling',
             'Construção civil': 'Real Estate', 'Saúde': 'Health', 'Siderurgia e Metalurgia': 'Steel & Metallurgy',
             'Madeira e papel': 'Wood & Paper', 'Aluguel de Veículos': 'Vehicle Rental',
             'Petróleo e Gás': 'Oil & Gas', 'Saneamento': 'Sanitation', 'Telecomunicações': 'Telecommunication',
             'Tecnologia': 'Technology', 'Comércio': 'Commerce', 'Bens Industriais': 'Industrial Goods'}
for key, value in translate.items():
    d[value] = d.pop(key)
d

# Unfortunately, some of the stocks listed in the dictionary cannot be accessed with yahoo's API. SO we'll need to exclude them.
for sector in list(d.keys()):
    for stock in d[sector]:
        # Trying to read the stock's data and removing it if it's not possible.
        try:
            web.DataReader(f'{stock}.SA', 'yahoo', '01-01-2015', '31-12-2021')
        except:
            d[sector].remove(stock)
    # After the removing process is completed, some economic sectors may not have any stocks at all, so they won't be of use for the
    # the project.
    if d[sector] == []:
        d.pop(sector)

# Converting it into a json file
with open("sector_stocks.json", "w") as outfile:
    json.dump(d, outfile)
'''

# Aiming speed, I had to store the dashboard Carousel's values inside a json file. By doing this, we do not need
# to make multiple requests to Yahoo's API in order to display the object.
'''
# A function that is going to retrieve the stocks' price variation.


def variation(name):
    df = web.DataReader(f'{name}.SA', 'yahoo',
                        start='29-12-2021', end='30-12-2021')
    return 1-(df['Close'].iloc[-1] / df['Close'].iloc[-2])


# Listing the companies to be shown in the Carousel.
carousel_stocks = ['ITUB4', 'BBDC4', 'VALE3', 'PETR4', 'PETR3',
                   'ABEV3', 'BBAS3', 'B3SA3', 'ITSA4', 'CRFB3', 'CIEL3',
                   'EMBR3', 'JBSS3', 'MGLU3', 'PCAR3', 'SANB11', 'SULA11']

carousel_prices = {}
for stock in carousel_stocks:
    # Calculating the stocks' price variation and storing it in the 'carousel_prices' dictionary.
    carousel_prices[stock] = variation(stock)

# Turning 'carousel_prices' into a json file.
with open('carousel_prices.json', 'w') as outfile:
    json.dump(carousel_prices, outfile)'''


# Loading the dashboard's 'sector_stock' and 'carousel_prices'  json files.
sector_stocks = json.load(open('sector_stocks.json', 'r'))
carousel_prices = json.load(open('carousel_prices.json', 'r'))

# The standard stock displayed when the dashboard is initialized will be ABEV3.
ambev = web.DataReader('ABEV3.SA', 'yahoo',
                       start='01-01-2015', end='31-12-2021')

# 'ambev_variation' is stored inside the card that shows the stock's current price.
ambev_variation = 1 - (ambev['Close'].iloc[-1] / ambev['Close'].iloc[-2])

# 'fig' exposes a candlestick chart with the prices of the stock since 2015.
fig = go.Figure()
fig.add_trace(go.Candlestick(x=ambev.index,
                             open=ambev['Open'],
                             close=ambev['Close'],
                             high=ambev['High'],
                             low=ambev['Low'],
                             name='Stock Price'))
fig.update_layout(
    paper_bgcolor='black',
    font_color='grey',
    height=500,
    width=1000,
    margin=dict(l=10, r=10, b=5, t=5),
    autosize=False,
    showlegend=False
)
# Setting the graph to display the 2021 prices in a first moment. Nonetheless,the user can also manually ajust the zoom size
# either by selecting a section of the chart or using one of the time span buttons available.
# The default
min_date = '2021-01-01'
max_date = '2021-12-31'
fig.update_xaxes(range=[min_date, max_date])
fig.update_yaxes(tickprefix='R$')

# The output from this small resample operation feeds the weekly average price chart.
ambev_mean_52 = ambev.resample('W')[
    'Close'].mean().iloc[-52:]
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=ambev_mean_52.index, y=ambev_mean_52.values))
fig2.update_layout(
    title={'text': 'Weekly Average Price', 'y': 0.9},
    font={'size': 8},
    plot_bgcolor='black',
    paper_bgcolor='black',
    font_color='grey',
    height=220,
    width=310,
    margin=dict(l=10, r=10, b=5, t=5),
    autosize=False,
    showlegend=False
)
fig2.update_xaxes(showticklabels=False, showgrid=False)
fig2.update_yaxes(range=[ambev_mean_52.min()-1, ambev_mean_52.max()+1.5],
                  showticklabels=False, gridcolor='darkgrey', showgrid=False)

# Making a speedometer chart which indicates the stock' minimum and maximum closing prices
# reached during the last 52 weeks along its current price.
df_52_weeks_min = ambev.resample('W')['Close'].min()[-52:].min()
df_52_weeks_max = ambev.resample('W')['Close'].max()[-52:].max()
current_price = ambev.iloc[-1]['Close']
fig3 = go.Figure()
fig3.add_trace(go.Indicator(mode='gauge+number', value=current_price,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            gauge={
                                'axis': {'range': [df_52_weeks_min, df_52_weeks_max]},
                                'bar': {'color': '#606bf3'}}))
fig3.update_layout(
    title={'text': 'Min-Max Prices', 'y': 0.9},
    font={'size': 8},
    paper_bgcolor='black',
    font_color='grey',
    height=220,
    width=280,
    margin=dict(l=35, r=0, b=5, t=5),
    autosize=False,
    showlegend=False
)


app = dash.Dash(external_stylesheets=[dbc.themes.CYBORG])
app.layout = html.Div([
    # In this row, a carousel showing the prices of some the main stocks from IBOVESPA is placed.
    dbc.Row([
            dtc.Carousel([

                html.Div([
                    # This span shows the name of the stock.
                    html.Span(stock, style={
                              'margin-right': '10px'}),

                    # This other one shows its variation.
                    html.Span('{}{:.2%}'.format('+' if carousel_prices[stock] > 0 else '', carousel_prices[stock]), style={
                              'color': 'green' if carousel_prices[stock] > 0 else 'red'})
                ]) for stock in sorted(carousel_prices.keys())
            ], id='main-carousel', autoplay=True, slides_to_show=4),

            # The column below will occupy 75% of the width available in the dashboard.
            dbc.Col([

                # This row holds the dropdowns responsible to the selection of the stock which informations are going
                # to be displayed.
                dbc.Row([

                    # As I've decided in the beginning of the script, AMBEV's is the default company of the dashboard.
                    dbc.Col([
                        html.Label('Select the desired sector',
                                   style={'margin-left': '40px'}),
                        dcc.Dropdown(options=[{'label': sector, 'value': sector}
                                              for sector in sorted(list(sector_stocks.keys()))],
                                     value='Food & Beverages',
                                     id='sectors-dropdown', style={'margin-left': '20px', 'width': '400px'}, searchable=False)
                    ], width=6),
                    dbc.Col([

                        html.Label('Select the stock to be displayed'),
                        dcc.Dropdown(
                            id='stocks-dropdown',
                            value='ABEV3',
                            className="disabled",
                            style={'margin-right': '20px'},
                            searchable=False
                        )
                    ], width=6)
                ]),

                # Here the candlestick chart is placed. Note that it is contained inside a dcc.Loading object
                # to give it a loading animation while its data is being imported.
                dbc.Row([
                    dbc.Col([
                        dcc.Loading(
                            [dcc.Graph(id='price-chart', figure=fig)], id='loading-price-chart',
                            type='dot', color='#1F51FF'),

                    ]),
                    dbc.Row([
                        dbc.Col([

                            # This Div contains the time span buttons for adjustment of the x-axis' length.
                            html.Div([
                                     html.Button('1W', id='1W-button',
                                                 n_clicks=0, className='btn-secondary'),
                                     html.Button('1M', id='1M-button',
                                                 n_clicks=0, className='btn-secondary'),
                                     html.Button('3M', id='3M-button',
                                                 n_clicks=0, className='btn-secondary'),
                                     html.Button('6M', id='6M-button',
                                                 n_clicks=0, className='btn-secondary'),
                                     html.Button('1Y', id='1Y-button',
                                                 n_clicks=0, className='btn-secondary'),
                                     html.Button('3Y', id='3Y-button',
                                                 n_clicks=0, className='btn-secondary'),

                                     ], style={'padding': '15px', 'margin-left': '35px'})
                        ], width=4),

                        # The following checklist mentions the indicators available for use in the dashboard.
                        dbc.Col([
                            dcc.Checklist(
                                ['Rolling Mean',
                                 'Exponential Rolling Mean',
                                 'Bollinger Bands'],
                                inputStyle={'margin-left': '15px',
                                            'margin-right': '5px'},
                                id='complements-checklist',
                                style={'margin-top': '20px'})
                        ], width=8)
                    ]),
                ]),
            ], width=9),

            # This other column occupies 25% of the dashboard's width.
            dbc.Col([

                dbc.Row([

                    # This DataTable stores the prices from the companies that pertain to the same economic sector
                    # as the one chosen in the dropdowns.
                    dcc.Loading([

                        dash_table.DataTable(
                            id='stocks-table', style_cell={'font_size': '12px',  'textAlign': 'center'},
                            style_header={'backgroundColor': 'black',
                                          'padding-right': '62px', 'border': 'none'},
                            style_data={'height': '12px', 'backgroundColor': 'black', 'border': 'none'}, style_table={
                                'height': '90px', 'overflowY': 'auto'})
                    ], id='loading-table', type='circle', color='#1F51FF')

                ], style={'margin-top': '28px'}),

                # This Div will hold a card displaying the selected stock's current price and some of its 52-week informations.
                html.Div([

                         dbc.Card([

                             # The card below presents the selected stock's current price.
                             dbc.CardBody([
                                 html.H1('ABEV3', id='stock-name',
                                         style={'font-size': '13px', 'text-align': 'center'}),
                                 dbc.Row([
                                     dbc.Col([
                                         # Placing the current price.
                                         html.P('R$ {:.2f}'.format(ambev['Close'].iloc[-1]), id='stock-price', style={
                                             'font-size': '40px', 'margin-left': '5px'})
                                     ], width=8),
                                     dbc.Col([

                                         # This another paragraph shows the price variation.
                                         html.P(
                                             '{}{:.2%}'.format(
                                                 '+' if ambev_variation > 0 else '-', ambev_variation),
                                             id='stock-variation', style={'font-size': '14px', 'margin-top': '25px', 'color': 'green' if ambev_variation > 0 else 'red'})
                                     ], width=4)

                                 ])

                             ])
                         ], id='stock-data', style={'height': '105px'}, color='black'),

                         # In the section below, some informations about the stock's performance in the last 52 weeks are going to be
                         # exposed.
                         html.Hr(),
                         html.H1(
                             '52-Week Data', style={'font-size': '25px', 'text-align': 'center', 'color': 'grey', 'margin-top': '5px',
                                                    'margin-bottom': '0px'}),
                         # Creating a Carousel showing the stock's weekly average price and a Speedoemeter
                         # displaying how far its current price is from its minimum and maximum values achieved.
                         dtc.Carousel([

                             dcc.Graph(id='52-avg-week-price', figure=fig2),
                             dcc.Graph(id='52-week-min-max', figure=fig3)
                         ], slides_to_show=1, autoplay=True, speed=2000, style={'height': '220px', 'width': '310px', 'margin-bottom': '0px'}),



                         # In this row, the stock's correlation with the BOVESPA index (IBOVESPA), and its sector's daily average price.
                         dbc.Row([

                             html.H2('Correlations', style={
                                     'font-size': '12px', 'color': 'grey', 'text-align': 'center'}),
                             dbc.Col([

                                 # IBOVESPA correlation.
                                 html.Div([
                                     html.H1('IBOVESPA',
                                             style={'font-size': '10px'}),
                                     html.P(id='ibovespa-correlation',
                                               style={'font-size': '20px', 'margin-top': '5px'})
                                 ], style={'text-align': 'center'})


                             ], width=6),

                             dbc.Col([

                                 # Sector correlation.
                                 html.Div([
                                     html.H1('Sector',
                                             style={'font-size': '10px'}),
                                     html.P(id='sector-correlation',
                                            style={'font-size': '20px', 'margin-top': '5px'})
                                 ], style={'text-align': 'center'})

                             ], width=6)
                         ], style={'margin-top': '2px'})
                         ], style={'backgroundColor': 'black', 'margin-top': '20px', 'padding': '5px'})

            ], width=3)
            ])


])
# Interactivity section

# Allowing the stock dropdown to display the stocks that are pertained to the sector chosen in the economic sector dropdown


@ app.callback(
    Output('stocks-dropdown', 'options'),
    Input('sectors-dropdown', 'value')
)
def modify_stocks_dropdown(sector):
    stocks = sector_stocks[sector]
    return stocks


# A function that will change the data being displayed in the candlestick chart in accordance to the stock selected in the dropdown.
# Also, we'll enable the user to adjust the x-axis length and to insert some indicators.
@ app.callback(
    Output('price-chart', 'figure'),
    Input('stocks-dropdown', 'value'),
    Input('complements-checklist', 'value'),
    Input('1W-button', 'n_clicks'),
    Input('1M-button', 'n_clicks'),
    Input('3M-button', 'n_clicks'),
    Input('6M-button', 'n_clicks'),
    Input('1Y-button', 'n_clicks'),
    Input('3Y-button', 'n_clicks'),
)
def change_price_chart(stock, checklist_values, button_1w, button_1m, button_3m, button_6m, button_1y, button_3y):
    # Retrieving the stock's data.
    df = web.DataReader(f'{stock}.SA', 'yahoo',
                        start='01-01-2015', end='31-12-2021')

    # Applying some indicators to its closing prices.
    df_bbands = bbands(df['Close'], length=20, std=2)
    # Measuring the Rolling Mean and Exponential Rolling means
    df['Rolling Mean'] = df['Close'].rolling(window=9).mean()
    df['Exponential Rolling Mean'] = df['Close'].ewm(
        span=9, adjust=False).mean()

    # Each metric will have its own color in the chart.
    colors = {'Rolling Mean': '#6fa8dc',
              'Exponential Rolling Mean': '#03396c', 'Bollinger Bands Low': 'darkorange',
              'Bollinger Bands AVG': 'brown',
              'Bollinger Bands High': 'darkorange'}

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], close=df['Close'],
                                 high=df['High'], low=df['Low'], name='Stock Price'))

    # If the user has selected any of the indicators in the checklist, we'll represent it in the chart.
    if checklist_values != None:
        for metric in checklist_values:

            # Adding the Bollinger Bands' typical three lines.
            if metric == 'Bollinger Bands':
                fig.add_trace(go.Scatter(
                    x=df.index, y=df_bbands.iloc[:, 0],
                    mode='lines', name=metric, line={'color': colors['Bollinger Bands Low'], 'width': 1}))

                fig.add_trace(go.Scatter(
                    x=df.index, y=df_bbands.iloc[:, 1],
                    mode='lines', name=metric, line={'color': colors['Bollinger Bands AVG'], 'width': 1}))

                fig.add_trace(go.Scatter(
                    x=df.index, y=df_bbands.iloc[:, 2],
                    mode='lines', name=metric, line={'color': colors['Bollinger Bands High'], 'width': 1}))

            # Plotting any of the other metrics remained, if they are chosen.
            else:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df[metric], mode='lines', name=metric, line={'color': colors[metric], 'width': 1}))
    fig.update_layout(
        paper_bgcolor='black',
        font_color='grey',
        height=500,
        width=1000,
        margin=dict(l=10, r=10, b=5, t=5),
        autosize=False,
        showlegend=False
    )
    # Defining the chart's x-axis length according to the button clicked.
    # To do this, we'll alter the 'min_date' and 'max_date' global variables that were defined in the beginning of the script.
    global min_date, max_date
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if '1W-button' in changed_id:
        min_date = df.iloc[-1].name - datetime.timedelta(7)
        max_date = df.iloc[-1].name
    elif '1M-button' in changed_id:
        min_date = df.iloc[-1].name - datetime.timedelta(30)
        max_date = df.iloc[-1].name
    elif '3M-button' in changed_id:
        min_date = df.iloc[-1].name - datetime.timedelta(90)
        max_date = df.iloc[-1].name
    elif '6M-button' in changed_id:
        min_date = df.iloc[-1].name - datetime.timedelta(180)
        max_date = df.iloc[-1].name
    elif '1Y-button' in changed_id:
        min_date = df.iloc[-1].name - datetime.timedelta(365)
        max_date = df.iloc[-1].name
    elif '3Y-button' in changed_id:
        min_date = df.iloc[-1].name - datetime.timedelta(1095)
        max_date = df.iloc[-1].name
    else:
        min_date = min_date
        max_date = max_date
        fig.update_xaxes(range=[min_date, max_date])
        fig.update_yaxes(tickprefix='R$')
        return fig
    # Updating the x-axis length.
    fig.update_xaxes(range=[min_date, max_date])
    fig.update_yaxes(tickprefix='R$')
    # fig.update_yaxes(color='white')
    return fig


# This dash_table displays the value from the stocks that are part of the economic sector chosen in the dropdowns.
@ app.callback(
    Output('stocks-table', 'data'),
    Output('stocks-table', 'columns'),
    Input('sectors-dropdown', 'value')
)
def update_stocks_table(sector):
    global sector_stocks
    # This DataFrame will be the base for the table.
    df = pd.DataFrame({'Stock': [stock for stock in sector_stocks[sector]], 'Close': [np.nan for i in range(len(sector_stocks[sector]))]},
                      index=[stock for stock in sector_stocks[sector]])
    # Each one of the stock names and their respective prices are going to be stored in the 'df'  DataFrame
    for stock in sector_stocks[sector]:
        stock_value = web.DataReader(
            f'{stock}.SA', 'yahoo', start='30-12-2021', end='31-12-2021')['Close'].iloc[-1]
        df.loc[stock, 'Close'] = f'R$ {stock_value :.2f}'
    # Finally, the DataFrame will be converted into a dictionary.
    return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns]

# The following function will edit the values being displayed in the 'stock-data' card.


@app.callback(
    Output('stock-name', 'children'),
    Output('stock-price', 'children'),
    Output('stock-variation', 'children'),
    Output('stock-variation', 'style'),
    Input('stocks-dropdown', 'value')
)
def update_stock_data_card(stock):

    # Retrieving data from the Yahoo Finance API.
    df = web.DataReader(f'{stock}.SA', 'yahoo',
                        start='2021-12-29', end='2021-12-31')['Close']
    # Getting the chosen stock's current price and its variation in comparison to its previous value.
    stock_current_price = df.iloc[-1]
    stock_variation = 1 - (df.iloc[-1] / df.iloc[-2])

    # Note that as in the Carousel, the varitation value will be painted in red or green depending if it is a negative or positive number.
    return stock, 'R$ {:.2f}'.format(stock_current_price), '{}{:.2%}'.format('+' if stock_variation > 0 else'-', stock_variation), \
        {'font-size': '14px', 'margin-top': '25px',
            'color': 'green' if stock_variation > 0 else 'red'}

# This function is responsible for updating the average weekly price chart.


@app.callback(
    Output('52-avg-week-price', 'figure'),
    Input('stocks-dropdown', 'value')
)
def update_average_weekly_price(stock):
    # Receiving the stock's prices and measuring the its average weekly price in the last 52 weeks.
    df = web.DataReader(f'{stock}.SA', 'yahoo',
                        start='2021-01-01', end='2021-12-31')['Close']
    df_avg_52 = df.resample('W').mean().iloc[-52:]

    # Plotting the data in a line chart.
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_avg_52.index, y=df_avg_52.values))
    fig2.update_layout(
        title={'text': 'Weekly Average Price', 'y': 0.9},
        font={'size': 8},
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='grey',
        height=220,
        width=310,
        margin=dict(l=10, r=10, b=5, t=5),
        autosize=False,
        showlegend=False
    )
    fig2.update_xaxes(tickformat='%m-%y', showticklabels=False,
                      gridcolor='darkgrey', showgrid=False)
    fig2.update_yaxes(range=[df_avg_52.min()-1, df_avg_52.max()+1.5],
                      showticklabels=False, gridcolor='darkgrey', showgrid=False)

    return fig2

# This function will update the speedometer chart located in the '52-Week Data' section.


@app.callback(
    Output('52-week-min-max', 'figure'),
    Input('stocks-dropdown', 'value')
)
def update_min_max(stock):
    # The same logic as 'update_average_weekly_price', but instead we are getting the minimum and maximum prices
    # reached in the last 52 weeks and comparing them with the stock's current price.
    df = web.DataReader(f'{stock}.SA', 'yahoo',
                        start='2021-01-01', end='2021-12-31')['Close']
    df_avg_52 = df.resample('W').mean().iloc[-52:]
    df_52_weeks_min = df_avg_52.resample('W').min()[-52:].min()
    df_52_weeks_max = df_avg_52.resample('W').max()[-52:].max()
    current_price = df.iloc[-1]
    fig3 = go.Figure()
    fig3.add_trace(go.Indicator(mode='gauge+number', value=current_price,
                                domain={'x': [0, 1], 'y': [0, 1]},
                                gauge={
                                    'axis': {'range': [df_52_weeks_min, df_52_weeks_max]},
                                    'bar': {'color': '#606bf3'}}))
    fig3.update_layout(
        title={'text': 'Min-Max Prices', 'y': 0.9},
        font={'size': 8},
        paper_bgcolor='black',
        font_color='grey',
        height=220,
        width=280,
        margin=dict(l=35, r=0, b=5, t=5),
        autosize=False,
        showlegend=False
    )

    return fig3

# This function will measure the correlation coefficient between the stock's closing values and the BOVESPA index.


@ app.callback(
    Output('ibovespa-correlation', 'children'),
    Input('stocks-dropdown', 'value')
)
def ibovespa_correlation(stock):
    start = datetime.datetime(2021, 12, 31).date() - \
        datetime.timedelta(days=7 * 52)
    end = datetime.datetime(2021, 12, 31).date()

    # Retrieving the IBOVESPA values in the last 52 weeks.
    ibovespa = web.DataReader('^BVSP', 'yahoo', start=start, end=end)['Close']

    # Now, doing the same with the chosen stock's prices.
    stock_close = web.DataReader(
        f'{stock}.SA', 'yahoo', start=start, end=end)['Close']

    # Returning the correlation coefficient value between.
    return f'{pearsonr(ibovespa, stock_close)[0] :.2%}'

# Now, this other function will measure the same stat, but now between the stock's value
# and the average closing price from its respective sector in the last 52 weeks.


@ app.callback(
    Output('sector-correlation', 'children'),
    Input('sectors-dropdown', 'value'),
    Input('stocks-dropdown', 'value')
)
def sector_correlation(sector, stock):
    start = datetime.datetime(2021, 12, 31).date() - \
        datetime.timedelta(days=7 * 52)
    end = datetime.datetime(2021, 12, 31).date()

    # Retrieving the daily closing prices from the selected stocks in the last 52 weeks.
    stock_close = web.DataReader(
        f'{stock}.SA', 'yahoo', start=start, end=end)['Close']

    # Creating a DataFrame that will store the prices from all the stocks
    # that pertain to the economic sector selected in the last 52 weeks.
    sector_df = pd.DataFrame()

    # Retrieving the price for each of the stocks present in 'sector_stocks'
    global sector_stocks
    stocks_from_sector = [stock_ for stock_ in sector_stocks[sector]]
    for stock_ in stocks_from_sector:
        sector_df[stock_] = web.DataReader(
            f'{stock_}.SA', 'yahoo', start=start, end=end)['Close']

    # With all the prices obtained, let's measure the sector's daily average value.
    sector_daily_average = sector_df.mean(axis=1)

    # Now, returning the correlation coefficient.
    return f'{pearsonr(sector_daily_average, stock_close)[0] :.2%}'


# Running the Dash app.
if __name__ == '__main__':
    app.run_server(debug=True)
