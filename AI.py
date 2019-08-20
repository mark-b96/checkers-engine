import copy
from anytree import Node, RenderTree

from anytree.exporter import DotExporter


class AI(object):
    def __init__(self):
        self.alpha = -100000
        self.beta = 100000
    # Alpha-beta pruning algorithm

    # Current game position
    # Get possible moves
    # Loop through squares with pieces of certain colour. Determine possible moves for each square containing a piece.
    def get_possible_moves(self, board, white_turn, root, depth):
        children = []
        child = None
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
                                        # board_copy.print_checkers_board()
                                        if depth > 0:
                                            child = Node(board_copy, visited=False, parent=root)
                                            children.append(child)
                                        else:
                                            root.visited = True

                                        board_copy = copy.deepcopy(board)

        return children

    def generate_tree(self, board, white_turn, root, depth):
        children = self.get_possible_moves(board, white_turn, root, depth)
        depth = depth - 1
        # print(children)
        if children is not None:
            for child in children:
                if child.visited == False:
                    white_turn = not white_turn
                    child.name.print_checkers_board()
                    self.generate_tree(child.name, white_turn, child, depth)
