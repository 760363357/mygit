
from django.urls import path
from .views import index, check


urlpatterns = [
    path('', index, name='index'),
    path('articel/', check),
]