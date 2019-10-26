"""
Author: Mark Bonney
"""
from Board import Board
from GUI import GUI
# from CaptureBoard import CaptureBoard
from AI import AI
# from ServoControl import ServoControl
from anytree import Node, RenderTree
import time


class Game(object):
    def __init__(self):
        self.white_turn = False
        self.valid_move = True
        self.board = Board()
        self.board.initialise_board()
        self.interface = GUI()
        self.interface.draw_board(self.board)
        self.interface.update_gui(self.board)
        self.interface.get_square_coordinates(self.board)
        self.selected_piece = None
        self.target_square = None
        # self.capture = CaptureBoard()
        # self.cap = self.capture.initialise_camera()
        # time.sleep(0.1)
        # self.capture.pin_setup()
        # self.capture.start_game(self.cap)
##        self.capture.calibrate_board(self.cap)
        self.ai = AI()
        # self.servos = ServoControl()
        # self.servos.pin_setup()
        # self.servos.serial_setup()
        # time.sleep(1)
        # self.servos.initialise_servos()
        self.depth = 3  # Single move lookahead
        self.game_termination = False

    def ai_move(self):
        root = Node(self.board, alpha=0, beta=0)
        self.ai.terminal_state = False
        self.ai.alpha_beta(root, self.depth, -100000, 100000, True)
        target_1, target_2, capture_target = None, None, None
        # print(RenderTree(root))
        if root.children:
            for child in root.children:
                if child.beta == root.alpha:
                    self.board.move_sequence = child.name.move_sequence
                    print("AI move: ", self.board.move_sequence)
                    target_1 = [child.name.origin_square.row, child.name.origin_square.column]
                    target_2 = [child.name.final_square.row, child.name.final_square.column]
                    break
            self.make_move()
            del root
                    # if abs(child.name.final_square.number - child.name.origin_square.number) > 5:
                    #     if child.name.final_square.row - child.name.origin_square.row > 0:
                    #         capture_target_row = child.name.origin_square.row + 1
                    #     else:
                    #         capture_target_row = child.name.origin_square.row - 1
                    #     if child.name.final_square.column - child.name.origin_square.column > 0:
                    #         capture_target_column = child.name.origin_square.column + 1
                    #     else:
                    #         capture_target_column = child.name.origin_square.column - 1
                    #     capture_target = [capture_target_row, capture_target_column]

        else:
            print("Game over human wins")
            # self.servos.terminate_serial()
            exit(0)
        print(self.board.move_sequence)
        print("Capture target", capture_target)
        # self.servos.actuate_robot_arm(target_1, target_2, capture_target)
        # self.capture.capture_image(self.cap, self.valid_move, True)
        # circle_coordinates = self.capture.process_image()
        # if circle_coordinates is None:
        #     self.valid_move = False
        #     self.ai_move()
        # move_sequence = self.capture.calculate_coordinates(circle_coordinates)
        # if self.validate_move(move_sequence):
        #     robot_move = [self.selected_piece.number, self.target_square.number]
        #     print("Robot move", robot_move)
        #     if self.board.move_sequence == robot_move:
        #         self.make_move()
        #         del root
        #     else:
        #         print("Robot unable to correctly actuate move")
        #         self.valid_move = False
        #         self.ai_move()
        # else:
        #     print("Robot unable to correctly actuate move")
        #     self.valid_move = False
        #     self.ai_move()

    def human_move(self):
        # self.capture.capture_image(self.cap, self.valid_move, False)
        # circle_coordinates = self.capture.process_image()
        # if circle_coordinates is None:
        #     self.valid_move = False
        #     self.human_move()
        # move_sequence = self.capture.calculate_coordinates(circle_coordinates)
        r1 = input()
        c1 = input()
        r2 = input()
        c2 = input()
        m1 = int(r1)
        m2 = int(c1)
        m3 = int(r2)
        m4 = int(c2)
        print(m1, m2)
        move_sequence = [[m1, m2], [m3, m4]]
        print(move_sequence)
        if self.validate_move(move_sequence):
            self.board.move_sequence = [self.selected_piece.number, self.target_square.number]
            self.make_move()
        else:
            self.human_move()
            # print("Game over AI wins")
            # # self.servos.terminate_serial()
            # exit(0)

    def validate_move(self, move_sequence):
        for move in move_sequence:
            selected_square = self.board.checkers_board[move[0]][move[1]]
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
            print("Start AI move")
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
            self.white_turn = not self.white_turn
        else:
            self.valid_move = False
            print("Invalid move made")
            self.human_move()