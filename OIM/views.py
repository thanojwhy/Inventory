from django.http import HttpResponse
from django.template import loader

def home(request):
    template = loader.get_template('home.html')
    context={
        "name":""
    }
    return HttpResponse(template.render(context,request))