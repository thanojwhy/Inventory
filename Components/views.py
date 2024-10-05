from django.http import HttpResponse
from django.template import loader
# Create your views here.

def component(request):
    template=loader.get_template('compList.html')
    context={
        "name":""
    }
    return HttpResponse(template.render(context,request))
