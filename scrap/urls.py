from django.urls import path
from . import views

urlpatterns = [ 
    path('products/', views.index, name='index'),
    path('search/', views.search_products, name='search_products'),
    path('view-history-result/', views.view_history_result, name='view_history_result'),
    path('update-history-result/', views.update_history_result, name='update_history_result'),
    path('delete-history-result/', views.delete_history_result, name='delete_history_result'),
] 