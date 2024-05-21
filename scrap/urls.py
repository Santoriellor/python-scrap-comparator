from django.urls import path
from . import views

urlpatterns = [ 
    path('products/', views.index, name='index'),
    path('fetch-coop-data/', views.fetch_coop_data, name='fetch_coop_data'),
    path('fetch-migros-data/', views.fetch_migros_data, name='fetch_migros_data'),
    path('fetch-aldi-data/', views.fetch_aldi_data, name='fetch_aldi_data'),
    path('view-history-result/', views.view_history_result, name='view_history_result'),
    path('get-query-by-search-id/', views.get_query_by_search_id, name='get_query_by_search_id'),
    path('get-search-history/', views.get_search_history, name='get_search_history'),
    path('delete-history-result/', views.delete_history_result, name='delete_history_result'),
] 