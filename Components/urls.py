from django.urls import path
from . import views

app_name="components"

urlpatterns = [
    path('list/',views.component,name='list'),
    path('usage/',views.usage,name="usage"),
]