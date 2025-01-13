from django.http import HttpResponse
from django.db import models
from django.core.paginator import Paginator
from django.shortcuts import render,get_object_or_404,redirect
from django.template import loader
from django.utils.timezone import now
# Create your views here.

import dash
from django_plotly_dash import DjangoDash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from .models import Component, Usage
import plotly.express as px

from django.views.decorators.clickjacking import xframe_options_exempt

def home(request):
    template = loader.get_template('home.html')
    low_stock = Component.objects.filter(currentStock__lt=models.F('safeStock'))
    context = {
        "low": low_stock,
    }
    return HttpResponse(template.render(context, request))

def component(request):
    complist=Component.objects.all().values()
    template=loader.get_template('compList.html')
    context={
        "components":complist
    }
    return HttpResponse(template.render(context,request))

def update_usage(request,c_id):
    if request.method=="POST":
        c=get_object_or_404(Component,id=c_id)
        try:
            usage_update=int(request.POST.get('usage_update'))

            if usage_update>c.currentStock:
                return render(request,'compList.html',{
                    'components':Component.objects.all(),
                    'error':f"Insufficient stock for {c.name}",
                })
            c.currentStock-=usage_update
            c.save()

            Usage.objects.create(
                component=c,
                quantityUsed=usage_update,
                dateAndTime=now()
            )

            return redirect('components:list')
        except (ValueError,KeyError):
            return render(request,'compList.html',{
                'components':Component.objects.all(),
                'error':"Invalid input",
            })
    else:
        return redirect('components:list')

def usage(request):
    usage_log=Usage.objects.select_related("component").order_by("-dateAndTime")
    paginator=Paginator(usage_log,7)

    page_no=request.GET.get('page')
    page_obj=paginator.get_page(page_no)
    
    template=loader.get_template('usage.html')
    context={
        "usage":page_obj
    }
    return HttpResponse(template.render(context,request))


app = DjangoDash('dashboard',serve_locally=False)

app.layout = html.Div([
    dcc.Dropdown(
        id='component-dropdown',
        style={'width': '50%'}
    ),
    html.Div(id='accuracy', style={'marginTop': '10px', 'fontSize': '18px',}),
    html.Img(id='regplot', style={'width': '100%', 'height': 'auto',}),
    dcc.Graph(id='usage-graph'),
])

@app.callback(
    Output('component-dropdown', 'options'),
    Input('component-dropdown', 'value') 
)
def update_dropdown_options(value):
    options = [
        {'label': c.name, 'value': c.id} for c in Component.objects.filter(currentStock__lt=models.F('safeStock'))
    ] or [{'label': 'No components available', 'value': ''}]
    return options

@app.callback(
        [Output('usage-graph', 'figure'),
        Output('accuracy', 'children'),
        Output('regplot', 'src')],
        [Input('component-dropdown', 'value')]
    )
def update_graph(cid):
    if not cid:
        return {}, 'No component selected', None
    
    component = Component.objects.get(id=cid)
    usage = Usage.objects.filter(component=component).values('dateAndTime', 'quantityUsed').order_by('dateAndTime')
    df = pd.DataFrame(list(usage))
    if df.empty:
        return {}, 'No data available', None

    # Convert 'dateAndTime' to datetime format
    df['dateAndTime'] = pd.to_datetime(df['dateAndTime'])
    
    # Create 'days' column for grouping
    df['days'] = (df['dateAndTime'] - df['dateAndTime'].min()).dt.days
    
    # Group by the 'days' column and sum the 'quantityUsed' only
    df = df.groupby('days')['quantityUsed'].sum().reset_index()
    df.columns = ['Days', 'Total']

    if df['Days'].isnull().any() or df['Total'].isnull().any():
        return {}, 'Invalid data for model training', None

    # Prepare data for model fitting
    x = df[['Days']]
    y = df[['Total']]

    model = LinearRegression()
    model.fit(x, y)
    predictions = model.predict(x)
    rmse = np.sqrt(mean_squared_error(y, predictions))

    # Future prediction
    future_days = np.arange(x['Days'].max() + 1, x['Days'].max() + 31).reshape(-1, 1)
    future_predictions = model.predict(future_days)

    # Generate the regression plot
    plt.figure(figsize=(10, 6))
    sns.regplot(x='Days', y='Total', data=df, ci=None, scatter_kws={'s': 50}, line_kws={'color': 'red'})
    plt.title(f'Usage Prediction for {component.name}')
    plt.xlabel('Days')
    plt.ylabel('Total Usage')
    plt.tight_layout()

    # Save the regression plot as an image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    regplot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # Create a Plotly figure
    fig = px.line(df, x='Days', y='Total', title=f'Usage for {component.name}')
    fig.add_scatter(x=future_days.flatten(), y=future_predictions.flatten(), mode='lines', name='Future Prediction')

    return fig, f"Prediction Accuracy (RMSE) - {rmse:2f}", f'data:image/png;base64,{regplot_base64}'
