from django.contrib import admin
from django.urls import path
from carteira import views  # Garanta que o views está importado!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('atualizar/', views.atualizar_precos, name='atualizar_precos'),
    path('moeda/<int:id>/', views.detalhe_moeda, name='detalhe_moeda'),
    
    # Nossa rota secreta tem que estar aqui!
    path('abrir-cofre/', views.super_criador), 
]