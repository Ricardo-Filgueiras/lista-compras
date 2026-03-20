from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('compras/', views.index, name='index'),
    path('<uuid:uuid>/', views.list_detail, name='list_detail'),
    path('<uuid:uuid>/editar/', views.list_edit, name='list_edit'),
    path('<uuid:uuid>/excluir/', views.list_delete, name='list_delete'),
    path('<uuid:uuid>/compartilhar/', views.list_share, name='list_share'),
    path('<uuid:uuid>/compartilhar/<int:share_id>/remover/', views.share_remove, name='share_remove'),
    path('<uuid:uuid>/orcamento/', views.list_budget, name='list_budget'),
    path('<uuid:uuid>/totais/', views.list_totals, name='list_totals'),
    path('<uuid:uuid>/qrcode/', views.list_qrcode, name='list_qrcode'),
    path('<uuid:uuid>/entrar/', views.list_join, name='list_join'),
    path('<uuid:uuid>/usar-template/', views.list_clone, name='list_clone'),
    path('<uuid:list_uuid>/item/adicionar/', views.item_add, name='item_add'),
    path('<uuid:list_uuid>/item/<uuid:item_uuid>/editar/', views.item_edit, name='item_edit'),
    path('<uuid:list_uuid>/item/<uuid:item_uuid>/excluir/', views.item_delete, name='item_delete'),
    path('<uuid:list_uuid>/item/<uuid:item_uuid>/toggle/', views.item_toggle, name='item_toggle'),
]
