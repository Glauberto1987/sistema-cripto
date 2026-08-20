from django.contrib import admin
from django.urls import path
from carteira import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('atualizar/', views.atualizar_precos, name='atualizar_precos'),
    path('moeda/<int:id>/', views.detalhe_moeda, name='detalhe_moeda'),
    
    # 👇 NOVA ROTA DO DOCUMENTÁRIO AQUI 👇
    path('documentario/', views.documentario, name='documentario'),
]