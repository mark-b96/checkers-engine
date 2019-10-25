"""
Author: Mark Bonney
"""
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
        moves = self.move_ordering(root, max_player)

        if moves is not 0:  # Confirm that the piece can move
            for move in moves:
                board_copy.move_sequence = move
                print("Move: ", board_copy.move_sequence)
                if board_copy.legal_move(not max_player):
                    self.terminal_state = False  # The agent can make a move
                    board_copy.update_board()
                    Node(board_copy, parent=root, alpha=0, beta=0)
                    board_copy = copy.deepcopy(board)  # Restore board position

    def move_ordering(self, root, max_player):
        board = root.name
        all_possible_moves = []

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
                                    move_sequence = [board.checkers_board[row][column].number, move]
                                    if abs(move_sequence[0] - move_sequence[1]) > 5:
                                        all_possible_moves.insert(0, move_sequence)
                                        print("Capture move found")
                                    else:
                                        all_possible_moves.append(move_sequence)
        print("Possible moves: ", all_possible_moves)
        return all_possible_moves

    def alpha_beta(self, node, depth, alpha, beta, max_player):
        if depth == 0 or self.terminal_state:
            return self.heuristic_function(node, max_player)
        self.get_possible_moves(node, max_player)

        # print(RenderTree(node))

        if max_player:
            max_eval = -100000
            for child in node.children:
                evaluation = self.alpha_beta(child, depth-1, alpha, beta, False)
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                node.alpha = alpha
                node.beta = beta
                if alpha >= beta:
                    break
            return max_eval
        else:
            min_eval = 100000
            for child in node.children:
                evaluation = self.alpha_beta(child, depth-1, alpha, beta, True)
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                node.alpha = alpha
                node.beta = beta
                if alpha >= beta:
                    break
            return min_eval

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
                            if board.checkers_board[row][column].piece.crowned:
                                black_piece_count = black_piece_count + 2
                            else:
                                black_piece_count = black_piece_count + 1
                            if column == 0 or column == 7:
                                position_value = position_value + 50
                        else:
                            if board.checkers_board[row][column].piece.crowned:
                                white_piece_count = white_piece_count + 2
                            else:
                                white_piece_count = white_piece_count + 1
        print("Number of black pieces:", black_piece_count)
        print("Number of white pieces:", white_piece_count)
        diff = black_piece_count - white_piece_count
        position_value = position_value + (diff*1000)
        if diff == 0:
            position_value = position_value + 500

        print(position_value)
        node.alpha = position_value
        # node.value = position_value
        return position_value




