from django.urls import path
from . import views

app_name="suppliers"

urlpatterns = [
    path('details/',views.supplier,name='details'),
]