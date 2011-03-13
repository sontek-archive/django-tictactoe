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

import simplejson
import random

from tictactoe.core.models import Game, GameMove, GameInvite
from tictactoe.lib import Player_X, Player_O
from tictactoe.core.forms import EmailForm

@login_required
def create_move(request, game_id):
    game = _get_game(request.user, game_id)

    if request.POST:
        move = int(request.POST['move'])
        player = Player_X if game.player1 == request.user else Player_O

        GameMove(game=game, player=request.user, move=move).save()

        board = game.get_board()
        board.make_move(move, player)

        if board.is_game_over():
            return _game_over(board)

        # Are we playing against a bot?
        computer = User.objects.get(username='bot')
        if game.player1 == computer or game.player2 == computer:
            move, board = _create_computer_move(game, board)

            if board.is_game_over():
                return _game_over(board, move=move)

            return HttpResponse(simplejson.dumps([move, '']), mimetype='application/json')

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
        return HttpResponse(simplejson.dumps(data), mimetype='application/json')

    if len(board.get_valid_moves()) == 0:
        data.append('Over');
        return HttpResponse(simplejson.dumps(data), mimetype='application/json')

@login_required
def create_computer_game(request):
    try:
        bot = User.objects.get(username='bot')
    except User.DoesNotExist:
        bot = User(username='bot')
        bot.save()

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
    game = _get_game(request.user, game_id)

    player = Player_X if game.player1 == request.user else Player_O

    moves = game.gamemove_set.all().order_by('-id')

    if not moves:
        current_player = Player_X
    else:
        current_player = Player_O if moves[0].player == game.player1 else Player_X

    context = { 'game': game, 'board': game.get_board(), 'player': player, 
                'current_player': current_player
              }

    return render_to_response(template_name, context,
            context_instance=RequestContext(request))

@login_required
def accept_invite(request, key):
    import pdb;pdb.set_trace()
    try:
        invite = GameInvite.objects.get(invite_key=key, is_active=True)
    except GameInvite.DoesNotExist:
        raise Http404

    game = invite.game

    if invite and not request.user == game.player1:
        game.player2 = request.user
        game.save()

        # No reason to keep the invites around
        invite.delete()

        return redirect('view_game', game_id=game.id)

    raise Http404

@login_required
def game_list(request, template_name='core/game_list.html'):
    games = Game.objects.filter(Q(player1=request.user) | Q(player2=request.user))[:10]

    if request.POST:
        form = EmailForm(request.POST)

        if form.is_valid():
            game = Game(player1=request.user)
            game.save()

            invite = GameInvite(game=game, is_active=True)
            invite.save()

            email = form.cleaned_data["email"]

            url = reverse('accept_invite', args=[invite.invite_key])
            current_site = Site.objects.get_current()
            send_mail('You are invited to play tic tac toe :)', 'Click here! %s%s' % (current_site.domain, url), 'sontek@gmail.com',
                        [email], fail_silently=False)
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

