from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from mock import Mock, patch
import pickle
from core.models import Game
from core.views import create_move

class TestTicTacToeBoard(TestCase):
    def setUp(self):
        self.player1 = User.objects.create(username='X')
        self.player2 = User.objects.create(username='O')

        self.player1.save()
        self.player2.save()

    def test_game_unicode_output(self):
        """
        Tests that we are returning a human readable string
        """
        board = pickle.dumps(['X', 'X', 'X', '', '', '', '', '', ''])
        game = Game(player1=self.player1, player2=self.player2,
                board=board)

        self.assertEqual("X vs O (['X', 'X', 'X', '', '', '', '', '', ''])",
                str(game))

    def test_finds_winner(self):
        """
        Tests that getting a winner works properly
        """
        board = pickle.dumps(['X', 'X', 'X', '', '', '', '', '', ''])
        game = Game(player1=self.player1, player2=self.player2,
                board=board)
        winner = game.get_winner()

        self.assertEqual(winner, 'X')

    def test_doesnt_find_winner(self):
        board = pickle.dumps(['', '', '', '', '', '', '', '', ''])
        game = Game(player1=self.player1, player2=self.player2,
                board=board)
        winner = game.get_winner()

        self.assertEqual(winner, None)

    def test_find_tie(self):
        """
        Tests that you get a tie when the board is full
        """
        board = pickle.dumps(['X', 'X', 'O',
                              'O', 'O', 'X',
                              'X', 'O', 'X'])

        game = Game(player1=self.player1, player2=self.player2,
                board=board)
        winner = game.get_winner()

        self.assertEqual(winner, '')

    def test_make_move(self):
        """
        Tests that you can make moves
        """
        board = pickle.dumps(['', '', '', '', '', '', '', '', ''])

        game = Game(player1=self.player1, player2=self.player2,
                board=board)

        game.make_move('X', 0)
        board = pickle.dumps(['X', '', '', '', '', '', '', '', ''])

        self.assertEqual(board, game.board)
        self.assertEqual('X', game.last_move)


    def test_gets_valid_moves(self):
        """
        Tests that getting valid moves works properly
        """
        board = pickle.dumps(['', '', '', '', '', '', '', '', ''])
        game = Game(player1=self.player1, player2=self.player2,
                board=board)
        moves = game.get_valid_moves()

        self.assertEqual(len(moves), 9)

    def test_doesnt_gets_valid_moves(self):
        """
        Tests that getting valid moves works properly
        """
        board = pickle.dumps(['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'])
        game = Game(player1=self.player1, player2=self.player2,
                board=board)
        moves = game.get_valid_moves()

        self.assertEqual(len(moves), 0)

class TestGameViews(TestCase):
    def setUp(self):
        self.player1 = User.objects.create(username='X')
        self.player1.set_password('test')
        self.player2 = User.objects.create(username='O')

        self.player1.save()
        self.player2.save()

        self.game = Game(player1=self.player1, player2=self.player2)
        self.game.save()

        self.client = Client()
        self.client.login(username='X', password='test')


    def test_create_move_publishes_to_redis(self):
        """
        Tests that we are publishing to redis when we create moves
        """
        request = Mock(name='request')
        request.user = self.player1

        redis = Mock(name='redis')
        redis.publish = Mock()

        self.game.board = pickle.dumps(['X', '', '',
                                        '', 'X', '',
                                        '', '', ''])
        self.game.save()

        with patch('core.views.Redis') as mock_redis:
            mock_redis.return_value = redis

            move = 8
            player = 'X'
            response = self.client.post('/create_move/%d/' % self.game.id,
                        {
                            'move': move
                        }
                    )


            redis.publish.assert_called_with(self.player2.id,
                    ['game_over', self.game.id, player])

            _pop_last_call(redis.publish)

            redis.publish.assert_called_with(self.player1.id,
                    ['game_over', self.game.id, player])

            _pop_last_call(redis.publish)

            redis.publish.assert_called_with(self.player2.id,
                    ['opponent_moved', self.game.id, player, move])



    def test_winning_move_publishes_to_redis(self):
        """
        Tests that we are publishing to redis when we create moves
        """
        request = Mock(name='request')
        request.user = self.player1

        redis = Mock(name='redis')
        redis.publish = Mock()

        with patch('core.views.Redis') as mock_redis:
            mock_redis.return_value = redis

            move = 0
            player = 'X'
            response = self.client.post('/create_move/%d/' % self.game.id,
                        {
                            'move': move
                        }
                    )

            redis.publish.assert_called_once_with(self.player2.id,
                    ['opponent_moved', self.game.id, player, move])


    def test_create_move_makes_move(self):
        """
        Tests that we are creating moves in the db when we call create_move
        """
        request = Mock(name='request')
        request.user = self.player1

        redis = Mock(name='redis')
        redis.publish = Mock()

        with patch('core.views.Redis') as mock_redis:
            mock_redis.return_value = redis

            move = 0
            player = 'X'
            response = self.client.post('/create_move/%d/' % self.game.id,
                        {
                            'move': move
                        }
                    )

            game = Game.objects.get(pk=self.game.id)
            board = game.get_board()
            self.assertEqual(board[0], player)

    def test_make_move_wins(self):
        pass

def _pop_last_call(mock):
    if not mock.call_count:
        raise AssertionError('Cannot pop last call: call_count is 0')

    mock.call_args_list.pop()

    try:
        mock.call_args = mock.call_args_list[-1]
    except IndexError:
        mock.call_args = None
        mock.called = False

    mock.call_count -=1
