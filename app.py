import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

GSS_string = """
[Center for American Progress](https://americanprogress.org/article/quick-facts-gender-wage-gap/)

The Center for American Progress seeks to explain the gender wage gap by breaking down the wage gap into four major factors:
- Women dominate lower paid industries
- Differences in years of experience (women are first to leave the workforce for family care duties)
- Difference in hours worked (again, family care responsibilities)
- Illegal discrimination

Generally because of these factors, women earn 82 cents for ever dollar earned by a man. This gap is much larger when comparing ethnic and racial groups other than white women to white men. The solutions the Center for American Progress recommends are to further combat illegal discrimination and strengthen support for family care responsibilities as a society.

[AAUW](https://www.aauw.org/resources/research/simple-truth/)

The AAUW states that women earn 83 cents for every dollar a man earns. This site emphasises that this wage gap follows women throughout their lives, resulting in lower social security benefits and pensions. Women only have 70% of what men hold in retirement.

**GSS**

The General Social Survey is a long-term, nationally representative survey conducted to explain changes in thinking ("opinions, attitudes and behaviors") over the populations that make up the adults of the United States. Data collection began in 1972 and questions have been modernized to allow tracking of the same trends since the begining. Topics range from religion, racism, sexism and other topics. Demographic information is also captured to enable easy segmentation of the population and analysis of change in attitudes between groups.
"""

gss_2 = gss_clean.groupby('sex').mean()[['income','job_prestige','socioeconomic_index','education']]\
    .reset_index()\
    .round(2)
gss_2 = gss_2.rename({'sex':'Gender',
                      'income':'Income',
                      'job_prestige': 'Job Prestige',
                      'socioeconomic_index': 'Socioeconomic Index',
                      'education': 'Education'
                     }, axis=1)


table = ff.create_table(gss_2)

gss_clean.male_breadwinner = gss_clean.male_breadwinner.astype('category').cat.reorder_categories(["strongly disagree", "disagree", "agree", "strongly agree"])
gss_bar = gss_clean.groupby(['male_breadwinner','sex']).size().rename('count').reset_index()

fig_bar = px.bar(gss_bar, x='male_breadwinner', y='count', color='sex',
            labels={'male_breadwinner':'Level of Agreement', 'count':'Number of Responses'},
            hover_data = ['sex','male_breadwinner','count'],
            text='count',
            barmode = 'group')

fig_scat = px.scatter(gss_clean, x='job_prestige', y='income', color='sex',
                 height=600, width=600,
                 trendline='ols',
                 labels={'job_prestige':'Job Prestige Rating', 
                        'income':'Income Level'},
                 hover_data=['education', 'socioeconomic_index'])


fig_box_inc = px.box(gss_clean, y='income', color='sex',
                    labels={'income':'Income'})
fig_box_inc.update_layout(showlegend=False)

fig_box_jp = px.box(gss_clean, y='job_prestige', color='sex',
                   labels={'job_prestige': 'Job Prestige Ranking'})
fig_box_jp.update_layout(showlegend=False)


gss_lim = gss_clean[['income','sex','job_prestige']]

jp_binned = pd.cut(gss_lim.job_prestige,bins=6,labels = ['very low','low','somewhat low','somewhat high','high','very high'])

gss_lim['jp_cat'] = jp_binned
gss_lim = gss_lim.dropna()

fig_jp_cat = px.box(gss_lim, y='income', color='sex', facet_col='jp_cat', facet_col_wrap=2,
      color_discrete_map = {'male':'blue', 'female':'red'})
fig_jp_cat.for_each_annotation(lambda a: a.update(text=a.text.replace("jp_cat=", "")))

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(
    [
        html.H1("GSS Survey Analysis"),
        
        dcc.Markdown(children = GSS_string),
        
        html.H2("Breakdown By Gender"),
        
        dcc.Graph(figure=table),
        
        html.H2("Male Breadwinner Question"),
        
        dcc.Graph(figure=fig_bar),
        
        html.H2('Job Prestige vs Income'),
        
        dcc.Graph(figure=fig_scat),
        
        html.Div([
            html.H3('Income by Gender'),
            dcc.Graph(figure=fig_box_inc)
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            html.H3('Job Prestige by Gender'),
            dcc.Graph(figure=fig_box_jp)
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H2('Job Prestige Level by Gender'),
        
        dcc.Graph(figure=fig_jp_cat)
        
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8051, host='0.0.0.0')
