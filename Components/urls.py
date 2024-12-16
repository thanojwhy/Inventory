from django.urls import path
from . import views

app_name="components"

urlpatterns = [
    path('',views.home,name="homePage"),
    path('update-usage/<int:c_id>',views.update_usage,name="update"),
    path('list/',views.component,name='list'),
    path('usage/',views.usage,name="usage"),
]