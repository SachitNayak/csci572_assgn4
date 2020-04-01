from django.urls import path

from . import views

app_name = 'search'
urlpatterns = [
    path('', views.index, name='search_index'),
    path('results/', views.process, name='process_query'),
]