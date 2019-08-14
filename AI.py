import copy
from anytree import Node, RenderTree

from anytree.exporter import DotExporter


class AI(object):
    def __init__(self):
        self.final_move_sequence = []
        self.all_possible_moves = []
        self.game_states = []
        self.level_states = []
    # Alpha-beta pruning algorithm

    # Current game position
    # Get possible moves
    # Loop through squares with pieces of certain colour. Determine possible moves for each square containing a piece.
    def get_possible_moves(self, board, white_turn, root, depth):
        self.game_states = []
        children = []
        board_copy = copy.deepcopy(board)
        for row in range(board.row_count):
            for column in range(board.column_count):
                if board.checkers_board[row][column].colour == "black":
                    if board.checkers_board[row][column].piece:
                        if board.checkers_board[row][column].piece.colour == "black":
                            piece_colour = False
                        else:
                            piece_colour = True
                        if piece_colour == white_turn:
                            moves = board_copy.possible_moves(board.checkers_board[row][column])
                            print(moves)
                            if moves is not 0:
                                for move in moves:
                                    board_copy.move_sequence = [board_copy.checkers_board[row][column].number, move]
                                    if board_copy.legal_move(white_turn):
                                        board_copy.update_board()
                                        board_copy.print_checkers_board()
                                        children.append(Node(board_copy, parent=root))
                                        self.game_states.append(board_copy)
                                        self.level_states.append(board_copy)
                                        board_copy = copy.deepcopy(board)

        print(self.game_states)
        if depth > 0:
            white_turn = not white_turn
            depth = depth - 1
            for state, child in zip(self.level_states, children):
                self.get_possible_moves(state, white_turn, child, depth)
            self.level_states.clear()
            children.clear()