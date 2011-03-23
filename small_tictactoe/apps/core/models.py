from django.db import models
from django.contrib.auth.models import User
import pickle

class Game(models.Model):
    player1 = models.ForeignKey(User, related_name='player1_set')
    player2 = models.ForeignKey(User, related_name='player2_set')
    last_move = models.CharField(max_length=1, null=True, blank=True)
    board = models.CharField(max_length=100,
            default=pickle.dumps([''] * 9))

    def __unicode__(self):
        board = self.get_board()
        return '%s vs %s (%s)' % (self.player1.username,
                self.player2.username, board)

    def get_board(self):
        return pickle.loads(str(self.board))
    def make_move(self, player, move):
        """
        player is X or O and move is a number 0-9
        """
        board = self.get_board() 
        board[move] = player
        self.board = pickle.dumps(board)
        self.last_move = player
        self.save()

    def get_valid_moves(self):
        """
        Returns a list of valid moves. A move can be passed to get_move_name to
        retrieve a human-readable name or to make_move/undo_move to play it.
        """
        board = self.get_board()
        return [pos for pos in range(9) if board[pos] == '']

    def all_equal(self, list):
            """
            Returns True if all the elements in a list are equal, or if
            the list is empty. 
            """
            return not list or list == [list[0]] * len(list)

    def get_winner(self):
        """
        Determine if one player has won the game. Returns X, O, '' for Tie,
        or None
        """
        board = self.get_board()

        winning_rows = [[0,1,2], [3,4,5], [6,7,8], # horizontal
                        [0,3,6], [1,4,7], [2,5,8], # vertical
                        [0,4,8], [2,4,6]]          # diagonal

        for row in winning_rows:
            if board[row[0]] != '' and self.all_equal([board[i] for i in row]):
                return board[row[0]]

        # No winner found, check for a tie
        if not self.get_valid_moves():
            return ''

        return None
