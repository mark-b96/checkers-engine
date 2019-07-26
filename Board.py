import numpy as np
from Piece import Piece
from Square import Square


class Board(object):
    def __init__(self):
        self.move_sequence = []
        self.square_count = 0
        self.origin_square, self.final_square, self.captured_square = Square, Square, Square
        self.valid_move = False
        self.row_count, self.column_count = 8, 8  # Size of checkers board
        self.checkers_board = np.full((self.row_count, self.column_count), Square)  # Define 2D array of Square objects

    def initialise_board(self):
        for row in range(self.row_count):
            for column in range(self.column_count):
                if column % 2 != 0 and row % 2 == 0 or column % 2 == 0 and row % 2 != 0:  # Find black squares
                    self.square_count = self.square_count+1
                    self.checkers_board[row][column] = Square("black", row, column, self.square_count, None)  # Populate black squares
                    if row < 3:
                        self.checkers_board[row][column].piece = Piece("black", False)  # Populate black pieces
                    if row > (self.row_count - 4):
                        self.checkers_board[row][column].piece = Piece("white", False)  # Populate white pieces
                else:
                    self.checkers_board[row][column] = Square("white", row, column, 0, None)  # Populate white squares

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
        if self.captured_square:
            self.captured_square.piece = None  # Remove captured piece

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
            possible_moves = self.possible_moves(temporary_square)  # Determine possible moves of selected piece
            if possible_moves == 0:
                if white_turn:
                    print("Game Over. Black wins")
                    exit(0)
                else:
                    print("Game over. Black wins")
                    exit(0)
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
        print("Valid Piece", selected_square.piece.colour)
        temporary_possible_moves = self.get_piece_moves(selected_square)
        final_possible_moves = []

        for row in range(self.row_count):
            for column in range(self.column_count):
                if column % 2 != 0 and row % 2 == 0 or column % 2 == 0 and row % 2 != 0:  # Search black squares
                    if not self.checkers_board[row][column].piece:  # Check if square is vacant
                        if self.checkers_board[row][column].number in temporary_possible_moves:
                            if (abs(self.checkers_board[row][column].column - selected_square.column) < 3) and \
                                    self.checkers_board[row][column].column != selected_square.column:
                                    final_possible_moves.append(self.checkers_board[row][column].number)

                                # Recursive loop required for multiple hops here
        if not final_possible_moves:
            return 0
        print(final_possible_moves)
        return final_possible_moves

    def get_piece_moves(self, selected_square):
        piece_moves = []
        diagonal_moves = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
        if selected_square.piece.colour == "black" and \
                selected_square.piece.crowned is False:  # Selected piece is black, uncrowned\
            for square in range(3, 10):  # Furthest a piece can hop alters square number by 9
                if square > 5:  # Move with a hop/capture
                    for diagonal in diagonal_moves:
                        if self.checkers_board[selected_square.row+diagonal[0]][selected_square.column+diagonal[1]].piece:
                            if self.checkers_board[selected_square.row+diagonal[0]][selected_square.column+diagonal[1]].piece.colour\
                                    is not selected_square.piece.colour:
                                self.captured_square = self.checkers_board[selected_square.row + diagonal[0]][selected_square.column + diagonal[1]]
                                piece_moves.append(selected_square.number+square)
                else:
                    piece_moves.append(selected_square.number+square)

        if selected_square.piece.colour == "white" and \
                selected_square.piece.crowned is False:  # Selected piece is black, uncrowned
            for square in range(10, 3, -1):
                if square > 5:  # Move with a hop/capture
                    for diagonal in diagonal_moves:
                        if self.checkers_board[selected_square.row+diagonal[0]][selected_square.column+diagonal[1]].piece:
                            if self.checkers_board[selected_square.row+diagonal[0]][selected_square.column+diagonal[1]].piece.colour\
                                    is not selected_square.piece.colour:
                                self.captured_square = self.checkers_board[selected_square.row + diagonal[0]][selected_square.column + diagonal[1]]
                                piece_moves.append(selected_square.number-square)
                else:
                    piece_moves.append(selected_square.number - square)
        if selected_square.piece.crowned:  # Crowned piece has been selected
            for square in range(3, 10):
                if square > 5:  # Move with a hop/capture
                    for diagonal in diagonal_moves:
                        if self.checkers_board[selected_square.row+diagonal[0]][selected_square.column+diagonal[1]].piece:
                            if self.checkers_board[selected_square.row+diagonal[0]][selected_square.column+diagonal[1]].piece.colour\
                                    is not selected_square.piece.colour:
                                self.captured_square = self.checkers_board[selected_square.row + diagonal[0]][selected_square.column + diagonal[1]]
                                piece_moves.append(selected_square.number+square)
                else:
                    piece_moves.append(selected_square.number + square)
            for square in range(10, 3, -1):
                if square > 5:  # Move with a hop/capture
                    for diagonal in diagonal_moves:
                        if self.checkers_board[selected_square.row+diagonal[0]][selected_square.column+diagonal[1]].piece:
                            if self.checkers_board[selected_square.row+diagonal[0]][selected_square.column+diagonal[1]].piece.colour\
                                    is not selected_square.piece.colour:
                                self.captured_square = self.checkers_board[selected_square.row + diagonal[0]][selected_square.column + diagonal[1]]
                                piece_moves.append(selected_square.number-square)
                else:
                    piece_moves.append(selected_square.number - square)
        return piece_moves

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
