from django.contrib import admin
from .models import Moeda, Transacao

admin.site.register(Moeda)
admin.site.register(Transacao)