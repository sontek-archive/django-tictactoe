from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.contrib import messages

import random

from core.models import Game, GameMove, GameInvite
from lib import Player_X, Player_O
from core.forms import EmailForm

import redis
from django.conf import settings
from gevent.greenlet import Greenlet

from socketio.namespace import BaseNamespace
from socketio import socketio_manage

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')

class GameNamespace(BaseNamespace):
    def listener(self, chan):
            red = redis.StrictRedis(REDIS_HOST)
            red = red.pubsub()
            red.subscribe(chan)

            print 'subscribed on chan ', chan

            while True:
                for i in red.listen():
                    self.send({'message': i}, json=True)

    def recv_message(self, message):
        action, pk = message.split(':')

        if action == 'subscribe':
            Greenlet.spawn(self.listener, pk)

def socketio(request):
    socketio_manage(request.environ,
        {
            '': GameNamespace,
        }, request=request
    )

    return HttpResponse()


@login_required
def create_move(request, game_id):
    game = _get_game(request.user, game_id)
    if request.POST:
        move = int(request.POST['move'])
        red = redis.StrictRedis(REDIS_HOST)

        # get player of move
        tic_player = Player_X if game.player1 == request.user else Player_O

        GameMove(game=game, player=request.user, move=move).save()
        board = game.get_board()
        board.make_move(move, tic_player)

        # get opponent
        opponent_player = Player_O if tic_player == Player_X else Player_X
        opponent_user = game.player1 if tic_player == Player_O else game.player2

        # get computer
        computer_user = _get_computer() 
        playing_computer = computer_user in [game.player1, game.player2]

        # if game over, and not playing against computer,  send notification of move, and of game over
        winner = board.get_winner()

        if board.is_game_over():
            red.publish('%d' % request.user.id, ['game_over', game.id, winner])

            if not playing_computer:
                red.publish('%d' % opponent_user.id, ['opponent_moved', game.id, tic_player, move])
                red.publish('%d' % opponent_user.id, ['game_over', game.id, winner])
        else:
            if playing_computer:
                move, board = _create_computer_move(game, board)
                red.publish('%d' % request.user.id, ['opponent_moved', game.id, opponent_player, move])

                if board.is_game_over():
                    winner = board.get_winner()
                    red.publish('%d' % request.user.id, ['game_over', game.id, winner])
            else:
                red.publish('%d' % opponent_user.id, ['opponent_moved', game.id, tic_player, move])

    return HttpResponse()

def _create_computer_move(game, board):
    computer = User.objects.get(username='bot')
    cpu = Player_X if game.player1 == computer else Player_O

    move = board.get_best_move(cpu)
    GameMove(game=game, player=computer, move=move).save()
    board.make_move(move, cpu)

    return move, board

def _get_computer():
    try:
        bot = User.objects.get(username='bot')
    except User.DoesNotExist:
        bot = User(username='bot')
        bot.save()
    finally:
        return bot

@login_required
def create_computer_game(request):
    bot = _get_computer()

    coin_toss = random.choice([0, 1])

    if coin_toss == 0:
        game = Game(player1=request.user, player2=bot)
    else:
        game = Game(player1=bot, player2=request.user)

    game.save()

    if coin_toss == 1:
        board = game.get_board()
        move, board = _create_computer_move(game, board)

        GameMove(game=game, player=bot, move=move).save()

    return redirect('view_game', game_id=game.id)

@login_required
def view_game(request, game_id, template_name='core/view_game.html'):
    bot = _get_computer()

    game = _get_game(request.user, game_id)

    player = Player_X if game.player1 == request.user else Player_O

    moves = game.gamemove_set.all().order_by('-id')

    if not moves:
        current_player = Player_X
    else:
        current_player = Player_O if moves[0].player == game.player1 else Player_X
    
    playing_computer = bot in [game.player1, game.player2]

    context = { 'game': game, 
                'board': game.get_board(), 
                'player': player, 
                'current_player': current_player,
                'playing_computer': playing_computer
              }

    return render_to_response(template_name, context,
            context_instance=RequestContext(request))

@login_required
def accept_invite(request, key):
    try:
        invite = GameInvite.objects.get(invite_key=key, is_active=True)
    except GameInvite.DoesNotExist:
        raise Http404

    if not request.user == invite.inviter:
        coin_toss = random.choice([0, 1])

        if coin_toss == 0:
            game = Game(player1=invite.inviter, player2=request.user)
        else:
            game = Game(player1=request.user, player2=invite.inviter)

        game.save()

        red = redis.StrictRedis(REDIS_HOST)
        red.publish('%d' % invite.inviter.id, ['game_started', game.id, str(request.user.username)])

        # No reason to keep the invites around
        invite.delete()

        return redirect('view_game', game_id=game.id)

    raise Http404

@login_required
def game_list(request, template_name='core/game_list.html'):
    games = Game.objects.get_by_user(request.user)[:15]

    if request.POST:
        form = EmailForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            if email == request.user.email:
                messages.add_message(request, messages.ERROR, 'You are not allowed to invite yourself.')
                form = EmailForm()
            else:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    user = None

                invite = GameInvite(inviter=request.user, is_active=True)

                if user:
                    invite.invitee = user

                invite.save()


                url = reverse('accept_invite', args=[invite.invite_key])
                current_site = Site.objects.get_current()
                messages.add_message(request, messages.SUCCESS, 'Invite was sent!')

                if invite.invitee:
                    red = redis.StrictRedis(REDIS_HOST)
                    red.publish('%d' % invite.invitee.id, ['new_invite', str(request.user.username), url])

                send_mail('You are invited to play tic tac toe :)', 'Click here! %s%s' % (current_site.domain, url), 'sontek@gmail.com',
                            [email], fail_silently=False)

                form = EmailForm()
    else:
        form = EmailForm()

    context = { 'games': games, 'form': form }

    return render_to_response(template_name, context,
            context_instance=RequestContext(request))

def _get_game(user, game_id):
    game = get_object_or_404(Game, pk=game_id)
    if not game.player1 == user and not game.player2 == user:
        raise Http404 

    return game
