from django.http import HttpResponse
from django.db import models
from django.core.paginator import Paginator
from django.shortcuts import render,get_object_or_404,redirect
from django.template import loader
from django.utils.timezone import now
from .models import Component, Usage

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
# Create your views here.

def home(request):
    template = loader.get_template('home.html')

    # Low stock notifications
    low_stock = Component.objects.filter(currentStock__lt=models.F('safeStock'))

    # Prediction logic for a selected component
    component_id = request.GET.get('component_id', 2)  # Default to component with id=2
    c = Component.objects.get(id=component_id)
    usage = Usage.objects.filter(component=c).order_by('dateAndTime')

    daily_usage = usage.extra({'date': "date(dateAndTime)"}).values('date').annotate(
        total=models.Sum('quantityUsed')).order_by('date')

    # Prepare data for ML prediction
    df = pd.DataFrame(daily_usage)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['days'] = (df['date'] - df['date'].min()).dt.days

        x = df[['days']]
        y = df[['total']]

        # Train model
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import mean_squared_error
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        from io import BytesIO
        import base64

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(x_train, y_train)

        # Predict future usage
        future_days = max(x['days']) + 30
        future_dates = pd.date_range(start=df['date'].max(), periods=31)[1:]
        predictions = model.predict(np.array(range(max(x['days']) + 1, future_days + 1)).reshape(-1, 1))

        # Plot graph
        sns.set(style='whitegrid')
        plt.figure(figsize=(10, 5))
        sns.lineplot(x=df['date'], y=df['total'], marker='o', label='Actual Usage')
        plt.plot(future_dates, predictions, 'r--', label="Predicted Usage")
        plt.title("Usage Prediction")
        plt.xlabel("Date")
        plt.ylabel("Quantity Used")
        plt.legend()

        # Encode graph to base64
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        rmse = np.sqrt(mean_squared_error(y_test, model.predict(x_test)))
    else:
        image_base64 = None
        predictions = None
        rmse = None

    # Combined context
    context = {
        "low": low_stock,
        "component": c,
        "image": image_base64,
        "predictions": list(zip(future_dates, predictions)) if predictions.any() else [],
        "rmse": rmse,
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
    paginator=Paginator(usage_log,10)

    page_no=request.GET.get('page')
    page_obj=paginator.get_page(page_no)
    
    template=loader.get_template('usage.html')
    context={
        "usage":page_obj
    }
    return HttpResponse(template.render(context,request))
