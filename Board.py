"""
Author: Mark Bonney
"""
import numpy as np
from Piece import Piece
from Square import Square
import copy


class Board(object):
    def __init__(self):
        self.move_sequence, self.captured_squares, self.capture_pieces, self.final_possible_moves, self.final_capture_moves, self.hop_moves, self.origin_pieces = [], [], [], [], [], [], []
        self.square_count = 0
        self.origin_square, self.final_square = Square, Square
        self.valid_move = False
        self.row_count, self.column_count = 8, 8  # Size of checkers board
        self.checkers_board = np.full((self.row_count, self.column_count), Square)  # Define 2D array of Square objects
        self.position_value = 0

    def initialise_board(self):
        for row in range(self.row_count):
            for column in range(self.column_count):
                if column % 2 != 0 and row % 2 == 0 or column % 2 == 0 and row % 2 != 0:  # Find black squares
                    self.square_count = self.square_count+1
                    self.checkers_board[row][column] = Square("black", row, column, self.square_count, None, None)  # Populate black squares
                    if row < 3:
                        self.checkers_board[row][column].piece = Piece("black", False)  # Populate black pieces
                    if row > (self.row_count - 4):
                        self.checkers_board[row][column].piece = Piece("white", False)  # Populate white pieces
                else:
                    self.checkers_board[row][column] = Square("white", row, column, 0, None, None)  # Populate white squares

    def update_board(self):
        self.final_square.piece = self.origin_square.piece
        self.origin_square.piece = None
        self.crown_pieces()
        self.captured_pieces()

    def crown_pieces(self):
        if self.final_square.piece.colour == "black":
            if self.final_square.row == 7:
                self.final_square.piece.crowned = True  # Promote/Crown a piece if it reaches the furthest row
        else:
            if self.final_square.row == 0:
                self.final_square.piece.crowned = True  # Promote/Crown a piece if it reaches the furthest row

    def captured_pieces(self):
        captured_piece = False
        if abs(self.final_square.number - self.origin_square.number) > 5:
            captured_piece = True
        if captured_piece:
            for captures in self.captured_squares:
                if abs(self.final_square.column - captures.column) < 2 and\
                        abs(self.final_square.row - captures.row) < 2 and\
                        abs(self.origin_square.column - captures.column) < 2 and\
                        abs(self.origin_square.column - captures.column) < 2:  # Check that correct piece is removed
                    self.capture_pieces.append(captures)
                    captures.piece = None  # Remove captured pieces
        self.captured_squares.clear()

    def legal_move(self, white_turn):
        temporary_square = None
        for row in range(self.row_count):
            for column in range(self.column_count):
                if column % 2 != 0 and row % 2 == 0 or column % 2 == 0 and row % 2 != 0:  # Search black squares
                    if self.checkers_board[row][column].piece:  # Check if piece occupies square
                        if self.checkers_board[row][column].number == self.move_sequence[0]:  # Search for selected piece 
                            temporary_square = self.checkers_board[row][column]  # Store selected piece in tmp variable
                            self.origin_square = temporary_square
                            if self.origin_square.piece.colour == "white" and white_turn:  # Check if it is white's move
                                self.valid_move = True
                            elif self.origin_square.piece.colour == "black" and not white_turn:  # Check if it is black's move
                                self.valid_move = True
                            else:
                                self.valid_move = False
                    if self.checkers_board[row][column].number == self.move_sequence[1]:  # Find target square
                        self.final_square = self.checkers_board[row][column]
        if self.valid_move:
            if temporary_square:
                possible_moves = self.possible_moves(temporary_square)  # Determine possible moves of selected piece
            else:
                print("Error in Legal moves")
                return False
            if possible_moves == 0:
                print("Invalid move")
                print("No moves found")
                return False
            if self.move_sequence[1] in possible_moves:  # Check if move is in possible moves
                print("Valid move")
                return True
            else:
                print("Invalid move")
                return False
        else:
            print("Invalid move")
            return False

    def possible_moves(self, selected_square):
        temporary_possible_moves = self.get_piece_moves(selected_square)
        self.final_possible_moves = []

        for row in range(self.row_count):
            for column in range(self.column_count):
                if column % 2 != 0 and row % 2 == 0 or column % 2 == 0 and row % 2 != 0:  # Search black squares
                    if not self.checkers_board[row][column].piece:  # Check if square is vacant
                        if self.checkers_board[row][column].number in temporary_possible_moves:
                            if (abs(self.checkers_board[row][column].column - selected_square.column) < 3) and \
                                    self.checkers_board[row][column].column != selected_square.column and \
                                    self.checkers_board[row][column].row != selected_square.row:
                                    self.final_possible_moves.append(self.checkers_board[row][column].number)
        if not self.final_possible_moves:
            return 0
        return self.final_possible_moves

    def get_piece_moves(self, selected_square):
        piece_moves = []
        board_copy = copy.deepcopy(self.checkers_board)
        if selected_square.piece.colour == "black" and \
                selected_square.piece.crowned is False:  # Selected piece is black, uncrowned\
            for square in range(2, 6):  # Furthest a piece can move without hopping
                    piece_moves.append(selected_square.number+square)
            for move in self.get_capture_moves(selected_square):  # calculate capture moves
                if move > selected_square.number:
                    piece_moves.append(move)
        elif selected_square.piece.colour == "white" and \
                selected_square.piece.crowned is False:  # Selected piece is black, uncrowned
            for square in range(6, 2, -1):  # Furthest a piece can move without hopping
                piece_moves.append(selected_square.number-square)
            for move in self.get_capture_moves(selected_square):  # calculate capture moves
                if move < selected_square.number:
                    piece_moves.append(move)
        elif selected_square.piece.crowned:  # Crowned piece has been selected
            for square in range(2, 6):  # Furthest a piece can move without hopping
                piece_moves.append(selected_square.number + square)
            for move in self.get_capture_moves(selected_square):  # calculate capture moves
                piece_moves.append(move)

            for square in range(6, 2, -1):  # Furthest a piece can move without hopping
                piece_moves.append(selected_square.number - square)
            for move in self.get_capture_moves(selected_square):  # calculate capture moves
                piece_moves.append(move)

        return piece_moves

    def get_capture_moves(self, selected_square):
        diagonal_moves = self.get_diagonal_moves(selected_square)
        final_capture_moves = []

        for diagonal in diagonal_moves:
                if self.checkers_board[selected_square.row + diagonal[0]][selected_square.column + diagonal[1]].piece:  # Piece present in diagonal squares
                    if self.checkers_board[selected_square.row + diagonal[0]][selected_square.column + diagonal[1]].piece.colour is not selected_square.piece.colour:
                        if (-1 < selected_square.row + (2*diagonal[0]) < 8) and \
                                (-1 < selected_square.column + (2*diagonal[1]) < 8):
                            if not self.checkers_board[selected_square.row + (2*diagonal[0])][selected_square.column + (2*diagonal[1])].piece:
                                final_square = self.checkers_board[selected_square.row + (2 * diagonal[0])][selected_square.column + (2 * diagonal[1])]
                                final_capture_moves.append(self.checkers_board[selected_square.row + (2 * diagonal[0])][selected_square.column + (2 * diagonal[1])].number)
                                self.captured_squares.append(self.checkers_board[selected_square.row + diagonal[0]][selected_square.column + diagonal[1]])
        return final_capture_moves

    @staticmethod
    def get_diagonal_moves(selected_square):
        diagonal_moves = [[1, 1], [-1, 1], [1, -1], [-1, -1]]
        if selected_square.row == 0:
            diagonal_moves = [[1, -1], [1, 1]]  # South-West, South-East
        if selected_square.column == 0:
            diagonal_moves = [[-1, 1], [1, 1]]  # North-East, South-East
        if selected_square.column == 7:
            diagonal_moves = [[-1, -1], [1, -1]]  # North-West, South-West
        if selected_square.row == 7:
            diagonal_moves = [[-1, -1], [-1, 1]]  # North-West, North-East
        if selected_square.column == 7 and selected_square.row == 0:
            diagonal_moves = [[1, -1]]  # South-West
        if selected_square.column == 0 and selected_square.row == 7:
            diagonal_moves = [[-1, 1]]  # North-East

        return diagonal_moves

    def print_checkers_board(self):
        board_representation = np.zeros((self.row_count, self.column_count)).astype(int)  # Temporary 2D array
        for row in range(self.row_count):
            for column in range(self.column_count):
                if column % 2 != 0 and row % 2 == 0 or column % 2 == 0 and row % 2 != 0:
                    if self.checkers_board[row][column].piece:
                        if self.checkers_board[row][column].piece.colour == "black":
                            if self.checkers_board[row][column].piece.crowned:
                                board_representation[row][column] = 9
                            else:
                                board_representation[row][column] = 1  # Black piece representation
                        if self.checkers_board[row][column].piece.colour == "white":
                            if self.checkers_board[row][column].piece.crowned:
                                board_representation[row][column] = 8   # White crowned piece representation
                            else:
                                board_representation[row][column] = 2  # White piece representation

                    else:
                        board_representation[row][column] = 3  # Black squares that are vacant
        print(board_representation)