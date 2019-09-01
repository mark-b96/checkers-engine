from Board import Board
from GUI import GUI
from CaptureBoard import CaptureBoard
from AI import AI
from anytree import Node, RenderTree
import time


class Game(object):
    def __init__(self):
        self.white_turn = False
        self.board = Board()
        self.board.initialise_board()
        self.interface = GUI()
        self.interface.draw_board(self.board)
        self.interface.update_gui(self.board)
        self.interface.get_square_coordinates(self.board)
        self.selected_piece = None
        self.target_square = None
        self.capture = CaptureBoard()
        self.cap = self.capture.initialise_camera()
        self.ai = AI()
        self.depth = 1  # Single move lookahead
        self.game_termination = False

    def ai_move(self):
        root = Node(self.board, value=0)
        self.board.print_checkers_board()
        self.ai.terminal_state = False
        max_value = self.ai.alpha_beta(root, self.depth, -10000, 10000, True)
        for child in root.children:
            if child.value == max_value:
                self.board.move_sequence = child.name.move_sequence
        print(self.board.move_sequence)
        self.make_move()
        del root

    def update_game_state(self):
        while 1:
            self.ai_move()
            self.capture.capture_image(self.cap, self.white_turn)
            circle_coordinates = self.capture.process_image()
            move_sequence = self.capture.calculate_coordinates(circle_coordinates)
            print(move_sequence)
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
                        legal_moves = self.board.possible_moves(selected_square)
                        # print("Legal Moves", legal_moves)
                        self.selected_piece = selected_square
                        selected_square = None
                    else:
                        self.selected_piece = None
                else:
                    self.target_square = selected_square

            if self.selected_piece and self.target_square:
                self.board.move_sequence = [self.selected_piece.number, self.target_square.number]
                self.make_move()

    def make_move(self):
        if self.board.legal_move(self.white_turn):
            self.board.update_board()
            self.board.final_possible_moves = []
            self.selected_piece = None
            self.interface.draw_board(self.board)
            self.interface.update_gui(self.board)
            self.white_turn = not self.white_turn
