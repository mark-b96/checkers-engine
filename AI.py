import copy
from anytree import Node, RenderTree


class AI(object):
    def __init__(self):
        self.terminal_state = True

    def get_possible_moves(self, root, max_player):
        """
        Function that returns the possible moves for a given node
        :param board:
        :param white_turn:
        :param root:
        :param depth:
        :return:
        """
        board = root.name
        board_copy = copy.deepcopy(board)

        for row in range(board.row_count):
            for column in range(board.column_count):
                if board.checkers_board[row][column].colour == "black":  # Find all the black squares containing pieces
                    if board.checkers_board[row][column].piece:
                        if board.checkers_board[row][column].piece.colour == "black":  # Determine piece colour
                            piece_colour = True
                        else:
                            piece_colour = False
                        if piece_colour == max_player:  # If a valid piece is found, determine its possible moves
                            moves = board.possible_moves(board.checkers_board[row][column])
                            if moves is not 0:  # Confirm that the piece can move
                                for move in moves:
                                    board_copy.move_sequence = [board_copy.checkers_board[row][column].number, move]
                                    print("Move: ", board_copy.move_sequence)
                                    if board_copy.legal_move(not max_player):
                                        self.terminal_state = False  # The agent can make a move
                                        board_copy.update_board()
                                        board_copy.print_checkers_board()
                                        Node(board_copy, parent=root, value=0)
                                        board_copy = copy.deepcopy(board)  # Restore board position

    def alpha_beta(self, node, depth, alpha, beta, max_player):
        if depth == 0 or self.terminal_state:
            return self.heuristic_function(node, max_player)
        self.get_possible_moves(node, max_player)
        print(RenderTree(node))

        if max_player:
            for child in node.children:
                alpha = max(alpha, self.alpha_beta(child, depth-1, alpha, beta, False))
                if alpha >= beta:
                    break
            return alpha
        else:
            for child in node.children:
                beta = min(beta, self.alpha_beta(child, depth-1, alpha, beta, True))
                if alpha >= beta:
                    break
            return beta

    @staticmethod
    def heuristic_function(node, max_player):
        black_piece_count = 0
        white_piece_count = 0
        position_value = 0
        board = node.name
        for row in range(board.row_count):
            for column in range(board.column_count):
                if board.checkers_board[row][column].colour == "black":
                    if board.checkers_board[row][column].piece:
                        if board.checkers_board[row][column].piece.colour == "black":
                            black_piece_count = black_piece_count + 1
                            if column == 0 or column == 7:
                                position_value = position_value + 50
                        else:
                            white_piece_count = white_piece_count + 1
        print("Number of black pieces:", black_piece_count)
        print("Number of white pieces:", white_piece_count)
        if black_piece_count - white_piece_count > 0 and max_player:
            position_value = position_value + 1000
        elif black_piece_count - white_piece_count < 0 and not max_player:
            position_value = position_value - 1000

        node.value = position_value
        print(position_value)
        return position_value




