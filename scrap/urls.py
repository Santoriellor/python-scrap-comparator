from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.index, name='index'),
    path('fetch-data/', views.fetch_data, name='fetch_data'),
    path('get-search/', views.get_search, name='get_search'),
    path('get-search-history/', views.get_search_history, name='get_search_history'),
    path('delete-history-result/', views.delete_history_result, name='delete_history_result'),
] 
