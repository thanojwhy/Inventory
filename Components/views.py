from django.http import HttpResponse
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

def usage(request):
    template=loader.get_template('usage.html')
    context={
        "name":""
    }
    return HttpResponse(template.render(context,request))
