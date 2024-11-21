from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.template import loader
from .models import Component
# Create your views here.

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
                    'c':Component.objects.all(),
                    'error':f"Insufficient stock for {c.name}",
                })
            c.currentStock-=usage_update
            c.save()

            return redirect('components:list')
        except (ValueError,KeyError):
            return render(request,'compList.html',{
                'c':Component.objects.all(),
                'error':"Invalid input",
            })
    else:
        return redirect('components:list')

def usage(request):
    template=loader.get_template('usage.html')
    context={
        "name":""
    }
    return HttpResponse(template.render(context,request))
