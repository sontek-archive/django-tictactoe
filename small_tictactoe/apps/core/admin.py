from django.contrib import admin
from core.models import Game

class GameAdmin(admin.ModelAdmin):
    exclude = ('board', 'last_move')

admin.site.register(Game, GameAdmin)
