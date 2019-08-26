import copy
from anytree import Node, RenderTree



class AI(object):
    def __init__(self):
        self.alpha = -100000
        self.beta = 100000
        self.optimal_position = None
        self.game_terminated = False
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
                            moves = board.possible_moves(board.checkers_board[row][column])
                            print(moves)
                            if moves is not 0:
                                for move in moves:
                                    board_copy.move_sequence = [board_copy.checkers_board[row][column].number, move]
                                    print("Move: ", board_copy.move_sequence)
                                    if board_copy.legal_move(white_turn):
                                        captured_squares = copy.deepcopy(board_copy.captured_squares)
                                        board_copy.update_board()
                                        if depth > 0:
                                            child = Node(board_copy, visited=False, parent=root)
                                            children.append(child)
                                        else:
                                            root.visited = True
                                            self.heuristic_function(captured_squares, board_copy, white_turn)
                                            # if board_copy.position_value == 1000:
                                            self.optimal_position = root
                                            return None

                                        board_copy = copy.deepcopy(board)

        return children

    def generate_tree(self, board, white_turn, root, depth):
        children = self.get_possible_moves(board, white_turn, root, depth)
        depth = depth - 1
        # # print(children)

        if children:
            white_turn = not white_turn
            self.generate_tree(children[0].name, white_turn, children[0], depth)

        # if children:
        #     for child in children:
        #         if child.visited is False:
        #             white_turn = not white_turn
        #             self.generate_tree(child.name, white_turn, child, depth)

    def heuristic_function(self, captured_squares, board, white_turn):
        for square in captured_squares:
            if (square.piece.colour == "white" and white_turn is False) or\
                    (square.piece.colour == "black" and white_turn):
                print(square)
                board.position_value = 1000
            # if (square.piece.colour == "black" and white_turn is False) or\
            #         (square.piece.colour == "white" and white_turn):
            #     print(square)
            #     board.position_value = -1000

