from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.models import User
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.contrib import messages

import simplejson
import random

from core.models import Game, GameMove, GameInvite
from lib import Player_X, Player_O
from core.forms import EmailForm

from redis import Redis
from django.conf import settings
from gevent.greenlet import Greenlet

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')

def sub_listener(socketio, chan):
        print 'in sublistener...'
        red = Redis(REDIS_HOST)
        red.subscribe(chan)

        while True:
            for i in red.listen():
                print 'sending message'
                socketio.send({'message': i})

def socketio(request):
    socketio = request.environ['socketio']

    if socketio.on_connect():
        print 'connecting'

    while True:
        message = socketio.recv()

        if len(message) == 1:
            message = message[0].split(':')

            if message[0] == 'subscribe':
                print 'spawning sub listener'
                g = Greenlet.spawn(sub_listener, socketio, message[1])

    return HttpResponse()

@login_required
def create_move(request, game_id):
    game = _get_game(request.user, game_id)
    if request.POST:
        move = int(request.POST['move'])
        player = Player_X if game.player1 == request.user else Player_O

        GameMove(game=game, player=request.user, move=move).save()

        board = game.get_board()
        board.make_move(move, player)

        red = Redis(REDIS_HOST)
        red.publish('#%d' % game.id, [player, move])

        # Are we playing against a bot?
        computer = User.objects.get(username='bot')

        if computer in [game.player1, game.player2]:
            if board.is_game_over():
                return JsonResponse(['', "Over"])

            move, board = _create_computer_move(game, board)

            if board.is_game_over():
                return JsonResponse(_game_over(board, move=move))

            return JsonResponse([move, ''])
        else:
            if board.is_game_over():
                data = _game_over(board, move)
                # have to revserse the data because I'm handling it differently
                # on the redis calls, didn't want to rewrite
                red.publish('#%d' % game.id, ['', data[0], board.get_winner()])

    return HttpResponse()

def _create_computer_move(game, board):
    computer = User.objects.get(username='bot')
    cpu = Player_X if game.player1 == computer else Player_O

    move = board.get_best_move(cpu)
    GameMove(game=game, player=computer, move=move).save()
    board.make_move(move, cpu)

    return move, board

def _game_over(board, move=None):
    winner = board.get_winner()

    if move:
        data = [move]
    else:
        data = ['']

    if winner:
        data.append(winner)
        return data

    if len(board.get_valid_moves()) == 0:
        data.append('Over');
        return data

def JsonResponse(data):
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

def _get_bot():
    try:
        bot = User.objects.get(username='bot')
    except User.DoesNotExist:
        bot = User(username='bot')
        bot.save()
    finally:
        return bot

@login_required
def create_computer_game(request):
    bot = _get_bot()

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
    bot = _get_bot()

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

