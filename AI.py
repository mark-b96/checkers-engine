import copy
from anytree import Node, RenderTree

from anytree.exporter import DotExporter


class AI(object):
    def __init__(self):
        self.final_move_sequence = []
        self.all_possible_moves = []
        self.game_states = []
    # Alpha-beta pruning algorithm

    # Current game position
    # Get possible moves
    # Loop through squares with pieces of certain colour. Determine possible moves for each square containing a piece.
    def get_possible_moves(self, board, white_turn):
        self.game_states = []
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
                                        self.game_states.append(board_copy)
                                        board_copy = copy.deepcopy(board)

        print(self.game_states)

    def construct_game_tree(self, board):
        root = Node(board)
        for game_state in self.game_states:
                child = Node(game_state, parent=root)
        for children in root.children:
            self.get_possible_moves(children.name, white_turn=True)




