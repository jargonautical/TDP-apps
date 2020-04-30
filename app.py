import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

from plotly.colors import n_colors
import numpy as np
np.random.seed(1)

# define style options
# external stylesheets version
#external_stylesheets = [
#    'http://77.245.66.218/~jargona1/sandbox/reset.css',
#    'http://77.245.66.218/~jargona1/sandbox/header.css',
#    'http://77.245.66.218/~jargona1/sandbox/z-dash-style.css'
#    ]

# Step 1. Launch the application

# local testing version
app = dash.Dash(__name__)

# remote deploy version
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Step 2. Import the dataset

# Population - 5 year bands
pop_data = "https://www.nomisweb.co.uk/api/v01/dataset/NM_2002_1.data.csv?"
pop_url = pop_data + "geography=1820328235...1820328238,1820328230,1820328239,1820328240,1820328233,1820328241,1820328242&date=latest&gender=0&c_age=1,3...18,210&measures=20100"
#Projection
pop_url+='&select=date_name,geography_name,geography_code,c_age_name,measures_name,obs_value,obs_status_name'
pop = pd.read_csv(pop_url)
pop['C_AGE_NAME'] = pop['C_AGE_NAME'].replace(['Aged 5-9'], 'Aged 05-09') # tidies up display order in charts

# number and % of people self-employed
se_data = "https://www.nomisweb.co.uk/api/v01/dataset/NM_17_5.data.csv?"
se_url = se_data + "geography=1811939640...1811939643,1811939634,1811939644,1811939645,1811939638,1811939646,1811939647&date=latestMINUS1&variable=249&measures=21001"
#Projection
se_url += "&select=date_name,geography_name,geography_code,variable_name,measures_name,obs_value"
selfemployed = pd.read_csv(se_url)

# IMD number of LSOAs by deprivation decile
imd_url = "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/845345/File_7_-_All_IoD2019_Scores__Ranks__Deciles_and_Population_Denominators_3.csv"
imd = pd.read_csv(imd_url)
imd.columns = ['lsoa_code','lsoa_name','geography_code','geography_name','imd_score','imd_rank','imd_decile','income_score','income_rank','income_decile','employment_score','employment_rank','employment_decile','skills_score','skills_rank','skills_decile','health_score','health_rank','health_decile','crime_score','crime_rank','crime_decile','housing_score','housing_rank','housing_decile','living_env_score','living_env_rank','living_env_decile','idaci_score','idaci_rank','idaci_decile','idaopi_score','idaopi_rank','idaopi_decile','cyp_score','cyp_rank','cyp_decile','adult_skills_score','adult_skills_rank','adult_skills_decile','geobarriers_score','geobarriers_rank','geobarriers_decile','wider_barriers_score','wider_barriers_rank','wider_barriers_decile','indoors_score','indoors_rank','indoors_decile','outdoors_score','outdoors_rank','outdoors_decile','total_pop','pop0to15','pop16to59','pop60+','working_age']
districts = ['East Devon','Exeter','Mid Devon','North Devon','Plymouth','South Hams','Teignbridge','Torbay','Torridge','West Devon']
imdDevon = imd[imd['geography_name'].isin(districts)]
agg = imdDevon.groupby(['geography_name']).median().reset_index()

# define options for dropdown
features = pop['GEOGRAPHY_NAME'].unique()
opts = [{'label' : i, 'value' : i} for i in features]

# define tickvals
pop_bins = pop['C_AGE_NAME'].unique()

# define colourmap & style options for charts
colors = ['darkslategray','lightseagreen','mediumturquoise','gold','silver','gray']

# add markdown text for different sections

mince_text = '''
### Collating the datasets we always need for demographic context

#### Why 'data mince'? Lucy explains:
"A long time ago, my brother went off to university and started learning to shop,
cook and stay alive on a student's budget. He found out that pretty quickly
he fell into a pattern; after a long day of lectures and coursework and
assignments he would realise it was time to cook dinner. He'd chop an onion
and start frying it, add some cheap beef mince to the pan ... and then realise
he hadn't decided what he was actually going to cook. Chilli? Spag bol? Maybe go all
out and make cottage pie? His basic fried-mince-and-onion was just the
starting point.

What we found when we started working on projects for different clients, no
matter how sophisticated the toolset or how complex the problem, was that we
almost always needed to start with the same initial collection of demographic
data; population, income, deprivation, working patterns and so on. This is
what we call our 'data mince'."

Working in the data science field in the middle of a global pandemic, there
are many opportunties to start building tracking dashboards and viral
infection models. But there are enough of those already, so we're focusing on
how we can provide something useful to anyone trying to manage service demand or
community responses to the current crisis.

We'll update this periodically as we find new and useful things to add to it,
but for now here are the basics:
- population,
- deprivation
- economic activity.
'''

pop_text = '''
### Looking at population variation
We always find it useful to look at the distribution of ages
rather than the absolute values; the shape of a place's age
profile tells you a lot when you compare it to the wider
area. For example, Exeter and Plymouth stand out in this chart
because of the much higher numbers of resident young people
due to the universities. Torbay on the other hand has a profile skewed
towards the older age ranges, as many people retire to the area.

If we were looking at something like vulnerability profiles, then both groups
would be of interest. Outbreaks like the coronavirus are particularly concerning
for the elderly and anyone with an underlying health condition, but young people
are by no means immune. In fact a university environment can carry extra risks,
e.g. dorms, house shares, group tutorials and lectures in spaces that see a
lot of use.
'''

se_text = '''
##### Economic vulnerability
Health isn't the only vulnerability factor; for many people self-employment,
freelance and contracting work and zero-hours contracts have become a standard
part of their income generation. To take a look at the potential numbers of
people affected we can use the ONS Annual Labour Survey data - latest is for
the year from October 2018 to September 2019.
'''

imd_text = '''
But income isn't the only measure of wellbeing, although it certainly makes a
difference. The Indices of Multiple Deprivation (IMD) are updated every few
years and cover a wider range of measures including environment, barriers to
opportunity, health and crime.

In the chart below we look at the overall rank, score and decile across the
top-level domain. The lower the median, the more of that area is relatively
deprived compared to the country as a whole.
'''

# Step 3. Create a plotly figure

# make the population chart
trace_1 = go.Bar(x = pop['C_AGE_NAME'], y = pop['OBS_VALUE'],
                    name = 'num',
                    marker=dict(
                        #color='rgba(26, 192, 184, 0.9)',
                        color=colors[1],
                        #line=dict(color='rgba(26, 192, 184, 1)',width=3)
                        line=dict(color=colors[0],width=2)
                    )
                )

layout = go.Layout(title = 'Population in 5 year age bands',
                   hovermode = 'closest',
                   plot_bgcolor='#fcfcfc',
                   font = dict(
                       family = 'Chivo',
                       size =  14,
                       color = 'black'),
                   xaxis = dict(
                       tickmode = 'array',
                       tickvals = pop_bins,
                       ticktext = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29','30-34','35-39','40-44','45-49','50-54','55-59','60-64','65-69','70-74','75-79','80-84','85+']
                       ),
                   hoverlabel = dict(
                       bgcolor = '#fff',
                       bordercolor = '#000'
                       )
                )

fig1 = go.Figure(data = [trace_1],
                layout = layout
                )

# make the employment profile chart
trace_2 = go.Bar(x = selfemployed['GEOGRAPHY_NAME'], y = selfemployed['OBS_VALUE'],
                    name = 'num',
                    marker=dict(
                        color=colors[2],
                        line=dict(color=colors[1],
                        width=2)
                    )
                )

layout2 = go.Layout(title = 'Number of economically active people aged 16-64 who are self-employed',
                   hovermode = 'closest',
                   plot_bgcolor='#fcfcfc',
                   font = dict(
                       family = 'Chivo',
                       size = 14,
                       color = 'black'
                   ),
                   hoverlabel = dict(
                       bgcolor = '#fff',
                       bordercolor = '#000',
                       font = dict(
                           family = 'Chivo',
                           size =  12,
                           color = 'black')
                       )
                )

fig2 = go.Figure(data = [trace_2],
                layout = layout2
                )

trace_3 = go.Bar(x = agg['geography_name'], y = agg['imd_decile'],
                    name = 'num',
                    marker=dict(
                        color=colors[5],
                        line=dict(color=colors[5],
                        width=2)
                    )
                )

layout3 = go.Layout(title = 'Indices of Multiple Deprivation - median IMD decile by area',
                   hovermode = 'closest',
                   plot_bgcolor='#fcfcfc',
                   font = dict(
                       family = 'Chivo',
                       size = 14,
                       color = 'black'
                   ),
                   hoverlabel = dict(
                       bgcolor = '#fff',
                       bordercolor = '#000',
                       font = dict(
                           family = 'Chivo',
                           size =  12,
                           color = 'black')
                       )
                )

fig3 = go.Figure(data = [trace_3],
                layout = layout3
                )



# Step 4. Create a Dash layout
app.layout = html.Div([

                  html.Div([
                      html.Div(
                      className='hero-image',
                      children=[
                        html.Div(
                        className='hero-text',
                        children='TDP sandbox')
                      ])
                      ]),

                # adding a header and a paragraph
                html.Div(
                children=[
                    html.Nav(children=[
                      html.A('Tutorial - how to use an API', href='/link here'),
                      html.A('Data Mince - our open data starter', href='/link here'),
                      html.A('Footfall data in Plymouth parks', href='/link here'),
                      html.A('Coming soon', href='/link here')
                    ])
                    ]),

                html.Div([
                    html.H2('Data Mince - our open data starter kit')
                    ]
                    ),

                html.Div([
                    dcc.Markdown(children=mince_text)
                    ],
                style = {'padding' : '10px' ,
                         'backgroundColor' : '#fff'}),

                html.Div([
                    dcc.Markdown(children=pop_text)
                        ],
                    style = {'padding' : '10px' ,
                             'backgroundColor' : '#fff'}),

                # dropdown
                html.P([
                    html.Label("Choose an area"),
                    dcc.Dropdown(id = 'opt',
                                 options = opts,
                                 value = 'East Devon')
                        ], style = {'width': '400px',
                                    'fontSize' : '16px',
                                    'padding-left' : '50px',
                                    'display': 'inline-block'}),

                # adding the first plot
                dcc.Graph(id = 'population', figure = fig1),

                # adding the second plot and text

                html.Div([
                    dcc.Markdown(children=se_text)
                        ],
                    style = {'padding' : '10px',
                             'backgroundColor' : ';fff'}),

                dcc.Graph(id = 'self-employment',
                          figure = fig2),

                html.Div([
                    dcc.Markdown(children=imd_text)
                        ],
                    style = {'padding' : '10px' ,
                             'backgroundColor' : '#fff'}),

                # adding the third plot
                dcc.Graph(id = 'imd',
                          figure = fig3)

                ])






# Step 5. Add callback functions
@app.callback(Output('population', 'figure'),
             [Input('opt', 'value')])
def update_figure(input1):
    # filtering the data
    dff = pop[(pop['GEOGRAPHY_NAME'] == input1)]

    # updating the plot
    trace_1 = go.Bar(x = dff['C_AGE_NAME'], y = dff['OBS_VALUE'],
                        name = input1,
                        marker=dict(
                            color=colors[1],
                            line=dict(color=colors[0],
                            width=1)
                            )
                        )

    fig = go.Figure(data = [trace_1],
                    layout = layout
                    )
    return fig

# Step 6. Add the server clause
if __name__ == '__main__':
    app.run_server(debug = True)
