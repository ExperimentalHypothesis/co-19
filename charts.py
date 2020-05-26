import requests, json
import pandas as pd
import heapq

import plotly, json, requests   
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash, dash_table
import dash_core_components as dcc 
import dash_html_components as html 

############## DATA FROM JSON FOR TESTING ###############

# get the global data
# daily_states_df = pd.read_json(r"C:\Users\nirvikalpa\source\repos\Python\demos\dash-demo-coronavirus\data\state-daily.json")
# daily_us_df = pd.read_json(r"C:\Users\nirvikalpa\source\repos\Python\demos\dash-demo-coronavirus\data\us-daily.json")
# current_state_df = pd.read_json(r"C:\Users\nirvikalpa\source\repos\Python\demos\dash-demo-coronavirus\data\state-current.json")
# current_us_df = pd.read_json(r"C:\Users\nirvikalpa\source\repos\Python\demos\dash-demo-coronavirus\data\us-current.json")
# pop_df = pd.read_json(r"C:\Users\nirvikalpa\source\repos\Python\demos\dash-demo-coronavirus\data\us-pop.json")


############## DATA FROM API ###############
def get_api_data(source:str):
    ''' get data from api, return dateframe '''
    data = requests.get(source)
    return pd.read_json(data.text)

# get the global data
daily_states_df = get_api_data("https://covidtracking.com/api/v1/states/daily.json")
daily_us_df = get_api_data("https://covidtracking.com/api/v1/us/daily.json")
current_state_df = get_api_data("https://covidtracking.com/api/v1/states/current.json")
current_us_df = get_api_data("https://covidtracking.com/api/v1/us/current.json")
pop_df = pd.read_json(r"C:\Users\nirvikalpa\source\repos\Python\demos\dash-demo-coronavirus\data\us-pop.json")

population = pd.read_csv(r"C:\Users\nirvikalpa\source\repos\Python\demos\dash-demo-coronavirus\data\us_population.csv")



def cumulative_linechart_us():
    """ create linechart showing the cummulative progression in time """

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_us_df["dateChecked"], y=daily_us_df["totalTestResults"], mode='lines', name='Tested', visible='legendonly'))
    fig.add_trace(go.Scatter(x=daily_us_df["dateChecked"], y=daily_us_df["negative"], mode='lines', name='Negative', visible='legendonly'))
    fig.add_trace(go.Scatter(x=daily_us_df["dateChecked"], y=daily_us_df["positive"], mode='lines', name='Positive'))
    fig.add_trace(go.Scatter(x=daily_us_df["dateChecked"], y=daily_us_df["hospitalized"], mode='lines', name='Hospitalized'))
    fig.add_trace(go.Scatter(x=daily_us_df["dateChecked"], y=daily_us_df["recovered"], mode='lines', name='Recovered'))
    fig.add_trace(go.Scatter(x=daily_us_df["dateChecked"], y=daily_us_df["death"], mode='lines', name='Fatal'))
    fig.update_layout( plot_bgcolor = 'rgba(0,0,0,0)', title="Cumulative Progression in Time")

    fig.update_layout(
        legend=dict(
            x=0.01,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        # margin = dict(t=50, l=0, r=0, b=0)
    )
    return fig


def cumulative_barchart_us():
    """ create barchart for USA cumulative data """

    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Positive"], y=current_us_df["positive"], name='Positive'))
    fig.add_trace(go.Bar(x=["Hospitalized"], y=current_us_df["hospitalizedCumulative"],  name='Hospitalized'))
    fig.add_trace(go.Bar(x=["Recovered"], y=current_us_df["recovered"],  name='Recovered'))
    fig.add_trace(go.Bar(x=["Fatal"], y=current_us_df["death"],  name='Fatal'))

    fig.update_layout(title_text='Cumulative Barmode', plot_bgcolor = 'rgba(0,0,0,0)')
    return fig


def total_tests_pie():
    """ create piechart for total test """

    fig = px.pie(current_us_df, 
                values=[current_us_df["positive"][0], current_us_df["negative"][0], current_us_df["pending"][0]], 
                names=['Positive', 'Negative', 'Pending'], 
                title='Tests Total')
    fig.update_layout(legend_orientation="h", margin = dict(l=20, r=20))

    return fig


def hosp_death_daily_increase():
    """ create line chart for daily increase"""

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=daily_us_df["dateChecked"], y=daily_us_df["deathIncrease"], name="Fatal Cases", mode='lines'),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=daily_us_df["dateChecked"], y=daily_us_df["positiveIncrease"], name="Positive Cases", mode='lines'),
        secondary_y=True,
    )
    fig.update_layout(
        title_text="Positive & Fatal Cases: Daily Increase",
		plot_bgcolor = 'rgba(0,0,0,0)',
        legend=dict(
            x=0.01,
            y=1.0,
            # bgcolor='rgba(255, 255, 255, 0)',
            # bordercolor='rgba(255, 255, 255, 0)'
        ),
        margin = dict(l=20, r=20)
    )
    fig.update_yaxes(title_text="<b>Fatal</b> Daily Increase", secondary_y=False)
    fig.update_yaxes(title_text="<b>Positive</b> Daily Increase", secondary_y=True)

    return fig



def hospitalized():
    """ create horizontal barchart for hospitalized cases """
    
    fig = go.Figure(data=[
    go.Bar( name='Cumulative', 
            orientation='h',
            y=["Hospitalized", "In ICU", "On Ventilator"], 
            x=[current_us_df["hospitalizedCumulative"][0], current_us_df["inIcuCurrently"][0], current_us_df["onVentilatorCurrently"][0]],
            showlegend=False),

    go.Bar( name='Current',
            orientation='h', 
            y=["Hospitalized", "In ICU", "On Ventilator"], 
            x=[current_us_df["hospitalizedCurrently"][0], current_us_df["inIcuCumulative"][0], current_us_df["onVentilatorCumulative"][0]],
            showlegend=False)
            ])
    fig.update_layout(barmode='group', plot_bgcolor = 'rgba(0,0,0,0)', title='Hospitalization')
    return fig


def corelation_positive_population():
    pop_df = pd.read_json(r"C:\Users\nirvikalpa\source\repos\Python\demos\dash-demo-coronavirus\data\us-pop.json")
    state_df = pd.read_json(r"C:\Users\nirvikalpa\source\repos\Python\demos\dash-demo-coronavirus\data\state-current.json")
    df = pd.merge(state_df, pop_df, on="state")    
    

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["pop"], y=df["positive"], mode='markers', text=df['state name']))

    # styling
    fig.update_layout(  plot_bgcolor = 'rgba(0,0,0,0)', 
                        title='Corelation between population and positive', 
                        autosize=False,
                        width=400,
                        height=600,
                        margin=dict(
                            l=10,
                            r=10,
                            # b=30,
                            # t=30,
                            # pad=4
                        ),)
    
    return fig


import plotly.graph_objects as go

# function for mortality barchart 
def create_mortality_barchart():
    grouped_df = daily_states_df.groupby("state", as_index=False)[["totalTestResults", "positive", "hospitalized", "recovered", "death"]].sum()
    grouped_df["mortality"] = grouped_df["death"]/grouped_df["positive"] * 100

    fig = px.bar(grouped_df, y='mortality', x='state', text='mortality')
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')

    fig.update_layout(uniformtext_minsize=8, 
                    uniformtext_mode='hide',
                    # title={
                    #     'text': 'Mortality Rate by State',
                    #     'y':0.9,
                    #     'x':0.5,
                    #     # 'xanchor': 'center',
                    #     'yanchor': 'top'
                    #     },
                        font=dict(
                            size=10,
                            color="#7f7f7f"
                        ),
                    # title='Mortality Rate by State',
                    xaxis_tickfont_size=14,
					plot_bgcolor = 'rgba(0,0,0,0)',
                    yaxis=dict(
                        title='Mortality Rate in %',
                        titlefont_size=15,
                        tickfont_size=13
                        ),
                    height=350,
                    xaxis=dict(title='',),
                    margin = dict(t=50, l=0, r=0, b=50),
                    )
    return fig

def reported_cases_by_state():
    grouped_df = daily_states_df.groupby("state", as_index=False)[["totalTestResults", "positive", "hospitalized", "recovered", "death"]].sum()

    fig = go.Figure()
    # fig.add_trace(go.Bar(x= grouped_df["state"],
    #                 y=grouped_df["totalTestResults"],
    #                 name="Total Tests"
    #                 ))
    fig.add_trace(go.Bar(x= grouped_df["state"],
                    y=grouped_df["positive"],
                    name="Positive",
                    ))
    fig.add_trace(go.Bar(x= grouped_df["state"],
                    y=grouped_df["hospitalized"],
                    name="Hospitalized"
                    ))
    fig.add_trace(go.Bar(x= grouped_df["state"],
                    y=grouped_df["recovered"],
                    name="Recovered",
                    ))
    fig.add_trace(go.Bar(x= grouped_df["state"],
                    y=grouped_df["death"],
                    name="Death"
                    ))

    fig.update_layout(
        title='Reported Cases by State',
        # xaxis_tickfont_size=8,
        yaxis=dict(
            # title='Reported Cases',
            # titlefont_size=10,
            # tickfont_size=8,
        ),
        legend=dict(
            x=0.01,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        height=350,
        margin = dict(t=250, l=0, r=0, b=250),
        barmode='group',
        bargap=0.15, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1, # gap between bars of the same location coordinate.
        plot_bgcolor = 'rgba(0,0,0,0)'
    )
    return fig


def test_sun():
    
    fig =go.Figure(go.Sunburst(
        labels=["Eve", "Cain", "Seth", "Enos", "Noam", "Abel", "Awan", "Enoch", "Azura"],
        parents=["", "Eve", "Eve", "Seth", "Seth", "Eve", "Eve", "Awan", "Eve" ],
        values=[10, 14, 12, 10, 2, 6, 6, 4, 4],
    ))
    fig.update_layout(margin = dict(t=0, l=40, r=0, b=0), title_text='Sunplot Test')

    return fig




def scatter_bar_population_positive():

    pop_df = pd.read_json(r"C:\Users\nirvikalpa\source\repos\Python\demos\dash-demo-coronavirus\data\us-pop.json")
    df = pd.merge(current_state_df, pop_df, on="state")    
    popul = df["pop"]
    pint = [int(i.replace(",",""))for i in df["pop"]]

    y_positive_df = df["positive"]
    y_population_df = pint
    x_state_df = current_state_df["state"]

    fig = make_subplots(rows=2, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.02)

    fig.add_trace(go.Scatter(x=x_state_df, 
                            y=y_positive_df,
                            name='Positive Cases in Thousands',
                            mode='lines+markers',
                            line_color="rgba(0,0,0,0.7)",
                            line_width=1),
                row=2, col=1)

    fig.add_trace(go.Bar(x=x_state_df, 
                        y=y_population_df,
                        name='State Population in Millions',
                        marker=dict(
                            color="rgba(50,171,96,0.6)",
                            line=dict(
                                color="rgba(50,171,96,1)",
                                width=1,
                            )
                        ),
                        ),
                row=1, col=1)

    fig.update_layout(
                    # margin = dict(t=0, l=0, r=0, b=00),

                    height=600, 
                    # width=1300, 

                    plot_bgcolor='rgba(0, 0, 0, 0)',
                    title_text="Positive Cases & Population by State",
                    xaxis=dict(
                        showgrid=False,
                        showline=False,
                        showticklabels=True,
                        linecolor='rgba(102, 102, 102, 0.8)',
                        linewidth=2,
                        #domain=[0, 0.7],
                    ),

                    xaxis2=dict(
                        showgrid=True,
                        showline=True,
                        linecolor='rgba(102, 102, 102, 0.8)',
                        linewidth=2,
                        showticklabels=False,
                        #domain=[0, .7],
                    ),
                    
                    yaxis=dict(
                        zeroline=False,
                        showline=False,
                        showticklabels=True,
                        showgrid=True,
                        domain=[0, 0.42],
                    ),

                    yaxis2=dict(
                        zeroline=False,
                        showline=False,
                        showticklabels=True,
                        showgrid=True,
                        domain=[0.47, 1],
                        side='top',
                        dtick=100000,
                    ),

                    legend=dict(
                        x=0.029, 
                        y=1.038, 
                        font_size=10
                    ),

                    # margin=dict(
                    #     l=100, 
                    #     r=20, 
                    #     t=70, 
                    #     b=70
                    # ),   
            )

    # anotation
    largest_positive = heapq.nlargest(5, y_positive_df)
    for xa, ya in zip(x_state_df, y_positive_df):
        if ya in largest_positive:
            fig.add_annotation(
                xref='x2',
                yref='y2',
                x=xa,
                y=ya + 13000,
                text="{:,}".format(ya),
                showarrow=False)

    return fig

def sunburst():
    df = pd.read_json(r"C:\Users\nirvikalpa\source\repos\Python\demos\dash-demo-coronavirus\data\sunburst.json")
    fig = px.sunburst(df,
                    path=["total for usa", "region", "division", "state"], 
                    values='positive', 
                    color="death", 
                    color_continuous_scale="Rdbu",
)
    fig.update_layout(
        height=600, 
        title="Positive Cases by Region - Click To Expand",
        margin=dict(
                    l=1,
                    r=1,
                    b=70,
                    t=100,
        )
        )
    return fig


# divisions = 
# [{"New England" : ['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 'Rhode Island', 'Vermont']},
# {"Mid-Atlantic": ['New Jersey', 'New York', 'Pennsylvania']},
# {"East North Central": ['Illinois', 'Indiana', 'Michigan', 'Ohio','Wisconsin']},
# {"West North Central": ["Iowa, Kansas", "Minnesota", "Missouri", "Nebraska", "North Dakota", "South Dakota"]},
# {'South Atlantic': ('Delaware', 'Florida', 'Georgia', 'Maryland', 'North Carolina', 'South Carolina', 'Virginia', 'District of Columbia','West Virginia')},
# {'East South Central': ('Alabama', 'Kentucky', 'Mississippi', 'Tennessee')},
# {'West South Central': ('Arkansas', 'Louisiana', 'Oklahoma', 'Texas')},
# {'Mountain': ('Arizona', 'Colorado', 'Idaho', 'Montana', 'Nevada', 'New Mexico', 'Utah', 'Wyoming')},
# {'Pacific': ('Alaska', 'California', 'Hawaii', 'Oregon', 'Washington')}]


# regions= [
#     { "Northeast":
#         [
#             {"New England" : ['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 'Rhode Island', 'Vermont']},
#             {"Mid-Atlantic": ['New Jersey', 'New York', 'Pennsylvania']}
#         ]
#     },

# { "Midwest":
#     [
#         {"East North Central": ['Illinois', 'Indiana', 'Michigan', 'Ohio','Wisconsin']},
#         {"West North Central": ["Iowa, Kansas", "Minnesota", "Missouri", "Nebraska", "North Dakota", "South Dakota"]},
#     ]
# },

# {
#     "South":
#     [
#         {'South Atlantic': ('Delaware', 'Florida', 'Georgia', 'Maryland', 'North Carolina', 'South Carolina', 'Virginia', 'District of Columbia','West                  Virginia')},
#         {'East South Central': ('Alabama', 'Kentucky', 'Mississippi', 'Tennessee')},
#         {'West South Central': ('Arkansas', 'Louisiana', 'Oklahoma', 'Texas')},
#     ]
# },

# {
#     "West":
#     [
#         {'Mountain': ('Arizona', 'Colorado', 'Idaho', 'Montana', 'Nevada', 'New Mexico', 'Utah', 'Wyoming')},
#         {'Pacific': ('Alaska', 'California', 'Hawaii', 'Oregon', 'Washington')}
#     ]
# },

# ]


# for region in regions:
#     for region_name, region_list in region.items():
#         for division in region_list:
#             for division_name, states in division.items():
#                 for state in states:
#                     df.loc[(df["state name"] == state),"division"]=division_name
#                     df.loc[(df["state name"] == state),"region"]=region_name