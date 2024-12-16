from django.http import HttpResponse
from django.db import models
from django.core.paginator import Paginator
from django.shortcuts import render,get_object_or_404,redirect
from django.template import loader
from django.utils.timezone import now
from .models import Component, Usage
# Create your views here.

def home(request):
    template = loader.get_template('home.html')
    low=Component.objects.filter(currentStock__lt=models.F('safeStock'))
    context={
        "low":low,
    }
    return HttpResponse(template.render(context,request))

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
