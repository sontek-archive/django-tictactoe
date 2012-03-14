from django.contrib import admin

from core.models import Game
from core.models import GameInvite

class GameAdmin(admin.ModelAdmin):
    pass

class GameInviteAdmin(admin.ModelAdmin):
    pass

admin.site.register(Game, GameAdmin)
admin.site.register(GameInvite, GameInviteAdmin)

