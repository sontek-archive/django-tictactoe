from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.conf import settings

from redis import Redis
from gevent.greenlet import Greenlet

from core.models import Game

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')

def _sub_listener(socketio, chan):
    """
    This is the method that will block and listen
    for new messages to be published to redis, since
    we are using coroutines this method can block on
    listen() without interrupting the rest of the site
    """
    red = Redis(REDIS_HOST)
    red.subscribe(chan)

    for i in red.listen():
        socketio.send({'message': i})

def socketio(request):
    """
    This view will handle the 'subscribe' message
    from the client and spawn off greenlet coroutines
    to monitor messages on redis
    """
    socketio = request.environ['socketio']

    while True:
        message = socketio.recv()

        if len(message) == 1:
            message = message[0].split(':')

            if message[0] == 'subscribe':
                print 'spawning sub listener'
                g = Greenlet.spawn(_sub_listener, socketio, message[1])

    return HttpResponse()

@require_http_methods(["POST"])
@login_required
def create_move(request, game_id):
    """
    Creates a move for the logged in player on a specific game
    """
    game, player, opponent_id = _get_game_data(request, game_id)
    move = int(request.POST['move'])
    game.make_move(player, move)

    # Announce to the opponent that the current player made a move
    red = Redis(REDIS_HOST)

    _announce_player_moved(red, game_id, opponent_id, player, move),
    winner = game.get_winner()

    if winner:
        # Announce to current player and the opponent that the game is over
        _announce_game_over(red, game_id, request.user.id, player)
        _announce_game_over(red, game_id, opponent_id, player)

    return HttpResponse()

def view_game(request, game_id, template_name='core/view_game.html'):
    """
    Renders a tic tac toe board to be played for a specific game
    """
    game, player, opponent_id = _get_game_data(request, game_id)

    if game.last_move:
        current_player = 'X' if game.last_move == 'O' else 'O'
    else:
        current_player = 'X'

    board = game.get_board()
    winner = game.get_winner()

    context = { 'game_id': game_id,
                'board': board,
                'player': player,
                'current_player': current_player,
                'winner': winner,
                'game_over': False if winner == None else True
              }

    return render_to_response(template_name, context,
            context_instance=RequestContext(request))

def _announce_player_moved(red, game_id, to_user_id, player, move):
    """
    Publishes a message to redis to to_user_id that their opponent has
    completed a move
    """
    red.publish(to_user_id, ['opponent_moved', int(game_id), player, move])

def _announce_game_over(red, game_id, to_user_id, winner):
    """
    Publishes a message to redis to to_user_id that the game as finished
    """
    red.publish(to_user_id, ['game_over', int(game_id), winner])

def _get_game_data(request, game_id):
    """
        Grabs the game, current player, and its opponent
    """
    game = get_object_or_404(Game, pk=game_id)

    if game.player1 == request.user:
        player = 'X'
        opponent_id = game.player2.id
    elif game.player2 == request.user:
        player = 'O'
        opponent_id = game.player1.id
    else:
        raise Http404

    return game, player, opponent_id
