from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(template_name='shopping/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registrar/', include('shopping.urls_auth')),
    path('compras/', include(('shopping.urls', 'shopping'), namespace='shopping')),
]
