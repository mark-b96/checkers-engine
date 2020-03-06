"""
Author: Mark Bonney
"""
from Board import Board
from GUI import GUI
from AI import AI
from anytree import Node
import time


class Game(object):
    def __init__(self):
        self.white_turn = False
        self.valid_move = True
        self.board = Board()
        self.board.initialise_board()
        self.start_time = 0
        self.interface = GUI()
        self.interface.draw_board(self.board)
        self.interface.update_gui(self.board)
        self.interface.get_square_coordinates(self.board)
        self.selected_piece = None
        self.target_square = None
        self.capture_status = False
        self.ai = AI()
        self.depth = 3  # Three move lookahead
        self.game_termination = False
        self.selected = False
        self.s1 = None

    def ai_move(self):
        root = Node(self.board, value=0)
        self.ai.terminal_state = False
        self.ai.alpha_beta(root, self.depth, -10000, 10000, True)
        target_1, target_2, capture_target = None, None, None
        if root.children:
            for child in root.children:
                if child.beta == root.alpha:
                    self.board.move_sequence = child.name.move_sequence
                    print("AI move: ", self.board.move_sequence)
                    target_1 = child.name.origin_square
                    target_2 = child.name.final_square
                    break
            if abs(target_1.number - target_2.number) > 5:
                print("CAPTURE")
                if target_2.row - target_1.row > 0:
                    capture_target_row = target_1.row + 1
                else:
                    capture_target_row = target_1.row - 1
                if target_2.column - target_1.column > 0:
                    capture_target_column = target_1.column + 1
                else:
                    capture_target_column = target_1.column - 1
                capture_target = [capture_target_row, capture_target_column]
                self.capture_status = True
            else:
                self.capture_status = False
        else:
            print("Game over human wins")
            self.valid_move = False
            self.ai_move()
        print(self.board.move_sequence)
        print("Capture target", capture_target)
        self.start_time = time.time()
        target_1 = [target_1.row, target_1.column]
        target_2 = [target_2.row, target_2.column]
        self.make_move()

    def human_move(self):
        if self.selected is False:
            self.s1 = self.interface.event_listener()
        x = self.board.possible_moves(self.s1)
        if x is not 0:
            self.interface.draw_board(self.board)
            self.interface.update_gui(self.board)
            s2 = self.interface.event_listener()
            move_sequence = [[self.s1.row, self.s1.column], [s2.row, s2.column]]
            print("Move Seq: ", move_sequence)
            if self.validate_move(move_sequence):
                self.board.move_sequence = [self.s1.number, s2.number]
                print("Move: ", self.board.move_sequence)
                self.make_move()
            else:
                self.selected = True
                self.human_move()
        else:
            self.human_move()

    def validate_move(self, move_sequence):
        for move in move_sequence:
            selected_square = self.board.checkers_board[move[0]][move[1]]
            # selected_square = self.interface.event_listener()
            print(self.board.checkers_board[move[0]][move[1]].number)
            if selected_square.piece:
                if selected_square.piece.colour == "black":
                    piece_colour = False
                else:
                    piece_colour = True
                if piece_colour == self.white_turn:
                    print("Getting legal moves")
                    self.board.possible_moves(selected_square)
                    self.selected_piece = selected_square
                    selected_square = None
                else:
                    self.selected_piece = None
            else:
                self.target_square = selected_square

        if self.selected_piece and self.target_square:
            print("Move validated")
            return True
        else:
            return False

    def update_game_state(self):
        while 1:
            self.ai_move()
            self.human_move()

    def make_move(self):
        if self.board.legal_move(self.white_turn):
            self.board.update_board()
            self.board.final_possible_moves = []
            self.selected_piece = None
            self.interface.draw_board(self.board)
            self.interface.update_gui(self.board)
            self.valid_move = True
            if self.capture_status:
                moves = self.board.get_capture_moves(self.target_square)
                if self.target_square.piece.colour == "white" and self.target_square.piece.crowned is False:
                    for move in moves:
                        if move > self.target_square.number:
                            moves.remove(move)
                elif self.target_square.piece.colour == "black" and self.target_square.piece.crowned is False:
                    for move in moves:
                        if move < self.target_square.number:
                            moves.remove(move)
                if moves:
                    self.board.captured_squares.clear()

                else:
                    self.board.captured_squares.clear()
                    self.white_turn = not self.white_turn
                    self.capture_status = False
            else:
                self.white_turn = not self.white_turn
        else:
            self.valid_move = False
            print("Invalid move made")
            self.human_move()
