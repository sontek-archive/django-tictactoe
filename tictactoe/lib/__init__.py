import random

Player_X = 'X' 
Player_O = 'O'
Empty = '' 


class Board(object):
    """ Tic Tac Toe Board """
    def __init__(self):
        """ Initialize all members. """
        self.pieces = [Empty] * 9

    def all_equal(self, list):
        """ Returns True if all the elements in a list are equal, or if the list is empty. """
        return not list or list == [list[0]] * len(list)

    def get_opponent(self, player):
        """ Gets the opponent of the specific player """
        return Player_X if player == Player_O else Player_O

    def get_winner(self):
        """ Determine if one player has won the game. Returns Player_X, Player_O or None """
        winning_rows = [[0,1,2], [3,4,5], [6,7,8], # horizontal
                        [0,3,6], [1,4,7], [2,5,8], # vertical
                        [0,4,8], [2,4,6]]          # diagonal

        for row in winning_rows:
            if self.pieces[row[0]] != Empty and self.all_equal([self.pieces[i] for i in row]):
                return self.pieces[row[0]]

        return ''

    def get_valid_moves(self, moves_to_check=range(9)):
        """ Returns a list of valid moves. A move can be passed to get_move_name to
        retrieve a human-readable name or to make_move/undo_move to play it."""
        return [pos for pos in moves_to_check if self.pieces[pos] == Empty]

    def is_game_over(self):
        """ Returns True if one player has won or if there are no valid moves left. """
        return self.get_winner() or not self.get_valid_moves()

    def make_move(self, move, player):
        """ Plays a move. Note: this doesn't check if the move is legal! """
        self.pieces[move] = player

    def undo_move(self, move):
        """ Undoes a move/removes a piece of the board. """
        self.make_move(move, Empty)

    def get_random_move(self, moves):
        """ Gets a random valid move from the list, returns None if there is no valid moves """
        possible_moves = self.get_valid_moves(moves_to_check=moves)

        if len(possible_moves) != 0:
            return random.choice(possible_moves)
        else:
            return None

    def get_best_move(self, player):
        """ Gets the best move for a specific player """
        opponent = self.get_opponent(player)

        valid_moves = self.get_valid_moves() 
        # First, check if we can win in the next move
        for i in valid_moves:
            self.make_move(i, player)

            if self.get_winner() == player:
                self.undo_move(i)
                return i

            self.undo_move(i)

        # Check if the player could win on his next move, and block them.
        for i in valid_moves:
            self.make_move(i, opponent)

            if self.get_winner() == opponent:
                self.undo_move(i)
                return i

            self.undo_move(i)

        # Try to take the center, if it is free.
        if 4 in valid_moves:
            return 4

        # Force a move into the side if we are in the center
        sides = [1, 3, 5, 7]
        if self.pieces[4] == player:
            for side, replacement in zip(sides, sides[::-1]):
                if side in valid_moves and replacement in valid_moves:
                    return side

        # Play opposite of opponent's corner
        corners = [0, 2, 6, 8]
        for corner, replacement in zip(corners, corners[::-1]):
            if self.pieces[corner] == opponent:
                if self.pieces[replacement] == Empty:
                    return replacement

        # Try to take one of the corners, if they are free.
        move = self.get_random_move(corners)

        if move != None:
            return move

        # Move on one of the sides.
        return self.get_random_move(valid_moves)
