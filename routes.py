from flask import render_template, jsonify
from app import app
import sys
sys.path.append('.')

from classes.site import Site
import datetime
import json

import plotly.graph_objects as go
import plotly


@app.route("/")
def hello_world():
    # return render_template("home.html")
    rwj = Site('RWJ', alpha=0.75, beta=0.1, 
            open_date=datetime.date(2021, 1, 1), close_date=datetime.date(2021, 12, 30),
            screen_pass=0.75, complete=0.9)

    rwj.sim_site()
    data = json.loads(rwj.get_CIs())
    fig = go.Figure()

    # pre-screen
    fig.add_trace(go.Scatter(x=data['date_range'], y=data['pre_screen']['lower'],
        fill=None,
        mode='lines',
        line_color='indigo',
        name='Pre-Screen 95% CI'
        #showlegend=False
        ))
    fig.add_trace(go.Scatter(
        x=data['date_range'],
        y=data['pre_screen']['upper'],
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', name='Pre-Screen 95% CI', line_color='indigo'))
    fig.add_trace(go.Scatter(
        x=data['date_range'],
        y=data['pre_screen']['med'],
        mode='lines', name='Pre-Screen Pred', line_color='indigo'))

    # screen pass
    fig.add_trace(go.Scatter(x=data['date_range'], y=data['screen_pass']['lower'],
        fill=None,
        mode='lines',
        line_color='steelblue',
        name='Screen Pass 95% CI'
        #showlegend=False
        ))
    fig.add_trace(go.Scatter(
        x=data['date_range'],
        y=data['screen_pass']['upper'],
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', name='Screen Pass 95% CI', line_color='steelblue'))
    fig.add_trace(go.Scatter(
        x=data['date_range'],
        y=data['screen_pass']['med'],
        mode='lines', name='Screen Pass Pred', line_color='steelblue'))


    fig.update_layout(
    title="Subject Enrollment Throughout Clinical Lifecycle",
    xaxis_title="Date",
    yaxis_title="Subjects",
    legend_title="Legend",
    font=dict(
        family="Helvetica Neue",
        size=18,
        color="black"
    )
)


    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("home.html", graphJSON=graphJSON)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/site_data")
def site_data():
    rwj = Site('RWJ', alpha=1, beta=0.1, 
                open_date=datetime.date(2021, 1, 1), close_date=datetime.date(2021, 12, 30),
                screen_pass=0.75, complete=0.9)

    rwj.sim_site()

    return jsonify(rwj.get_CIs())
