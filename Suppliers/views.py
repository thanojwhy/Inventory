from django.http import HttpResponse
from django.template import loader
# Create your views here.
def supplier(request):
    template=loader.get_template('supList.html')
    context={
        "name":""
    }
    return HttpResponse(template.render(context,request))