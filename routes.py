from flask import render_template, jsonify
from app import app
import sys
sys.path.append('.')
import pandas as pd

from classes.site import Site
import datetime
import json

import plotly.graph_objects as go
import plotly


@app.route("/")
def graphs():
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

    # screen fail
    fig.add_trace(go.Scatter(
        x=data['date_range'], 
        y=data['screen_fail']['lower'],
        mode='lines',
        line_color='darksalmon',
        name='Screen Fail 95% CI'
        ))
    fig.add_trace(go.Scatter(
        x=data['date_range'],
        y=data['screen_fail']['upper'],
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', name='Screen Fail 95% CI', line_color='darksalmon'))
    fig.add_trace(go.Scatter(
        x=data['date_range'],
        y=data['screen_fail']['med'],
        mode='lines', name='Screen Fail Pred', line_color='darksalmon'))


    # complete
    fig.add_trace(go.Scatter(
        x=data['date_range'], 
        y=data['complete']['lower'],
        mode='lines',
        line_color='darkseagreen',
        name='Complete 95% CI'
        ))
    fig.add_trace(go.Scatter(
        x=data['date_range'],
        y=data['complete']['upper'],
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', name='Complete Fail 95% CI', line_color='darkseagreen'))
    fig.add_trace(go.Scatter(
        x=data['date_range'],
        y=data['complete']['med'],
        mode='lines', name='Screen Fail Pred', line_color='darkseagreen'))


    # discontinue
    fig.add_trace(go.Scatter(
        x=data['date_range'], 
        y=data['death']['lower'],
        mode='lines',
        line_color='lightslategray',
        name='Discontinue 95% CI'
        ))
    fig.add_trace(go.Scatter(
        x=data['date_range'],
        y=data['death']['upper'],
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', name='Discontinue Fail 95% CI', line_color='lightslategray'))
    fig.add_trace(go.Scatter(
        x=data['date_range'],
        y=data['death']['med'],
        mode='lines', name='Discontinue Fail Pred', line_color='lightslategray'))

    fig.update_layout(
    title="Subject Enrollment Throughout Clinical Lifecycle",
    width=1000,
    height=500,
    xaxis_title="Date",
    yaxis_title="Subjects",
    legend_title="Legend",
    margin=dict(l=20, r=20, t=100, b=100),
    font=dict(
        family="Helvetica Neue",
        size=18,
        color="black"
        )
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    
    # pre-screen histogram
    x = pd.DataFrame(rwj.sim_output['pre_screen']).iloc[:,-1]
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=x,
        marker_color='indigo'
    ))
    fig.update_layout(
        title="# Pre-Screened Subjects",
        width=500,
        height=500,
        xaxis_title='Number of Subjects'
    )
    pre_screen_hist = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    

    # screen-pass histogram
    x = pd.DataFrame(rwj.sim_output['screen_pass']).iloc[:,-1]
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=x,
        marker_color='steelblue'
    ))
    #fig = go.Figure(data=[go.Histogram(x=x)]) # turn to PDF with histnorm='probability'
    fig.update_layout(
        title="# Screen Pass Subjects",
        width=500,
        height=500,
        xaxis_title='Number of Subjects'
    )
    screen_pass_hist = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    # screen-fail histogram
    x = pd.DataFrame(rwj.sim_output['screen_fail']).iloc[:,-1]
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=x,
        marker_color='darksalmon'
    ))
    #fig = go.Figure(data=[go.Histogram(x=x)]) # turn to PDF with histnorm='probability'
    fig.update_layout(
        title="# Screen Fail Subjects",
        width=500,
        height=500,
        xaxis_title='Number of Subjects'
    )
    screen_fail_hist = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    # complete histogram
    x = pd.DataFrame(rwj.sim_output['complete']).iloc[:,-1]
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=x,
        marker_color='darkseagreen'
    ))
    fig.update_layout(
        title="# Complete Subjects",
        width=500,
        height=500,
        xaxis_title='Number of Subjects'
    )
    complete_hist = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # discontinue histogram
    x = pd.DataFrame(rwj.sim_output['death']).iloc[:,-1]
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=x,
        marker_color='lightslategray'
    ))
    fig.update_layout(
        title="# Discontinued Subjects",
        width=500,
        height=500,
        xaxis_title='Number of Subjects'
    )
    discontinue_hist = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("home.html", graphJSON=graphJSON, pre_screen_hist=pre_screen_hist, 
                           screen_pass_hist=screen_pass_hist, screen_fail_hist=screen_fail_hist,
                           complete_hist=complete_hist, discontinue_hist=discontinue_hist)

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
