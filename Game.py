from Board import Board


class Game(object):
    def __init__(self):
        self.white_turn = False

    def update_game_state(self):
        board = Board()
        board.initialise_board()
        board.print_checkers_board()

        while 1:
            if self.white_turn:
                s = input("White's turn")
            else:
                s = input("Black's turn")

            board.move_sequence = list(map(int, s.split()))

            if board.legal_move(self.white_turn):
                board.update_board()
                board.print_checkers_board()
                self.white_turn = not self.white_turn
            else:
                print("Invalid move. Try again")
