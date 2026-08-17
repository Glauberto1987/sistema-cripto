from django.contrib import admin
from .models import Moeda, Transacao

admin.site.register(Moeda)
admin.site.register(Transacao)
from .models import HistoricoPatrimonio

@admin.register(HistoricoPatrimonio)
class HistoricoPatrimonioAdmin(admin.ModelAdmin):
    list_display = ('data', 'valor_total')
    ordering = ('-data',)