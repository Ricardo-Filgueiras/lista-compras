from django.urls import path
from . import views

urlpatterns = [
    # ... outras rotas ...
    path('lista/<uuid:uuid>/pdf/', views.gerar_pdf_lista, name='gerar_pdf_lista'),
]