from django.contrib import admin

from .models import Bem, Localizacao, Movimentacao, Setor, TipoBem


admin.site.register(Bem)
admin.site.register(TipoBem)
admin.site.register(Setor)
admin.site.register(Localizacao)
admin.site.register(Movimentacao)
