"""
Author: Mark Bonney
"""
from Board import Board
##from GUI import GUI
from CaptureBoard import CaptureBoard
from AI import AI
from ServoControl import ServoControl
from anytree import Node
import time
import ASUS.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(35, GPIO.OUT)  # Red LED output
GPIO.setup(33, GPIO.OUT)  # Green LED output
GPIO.setmode(GPIO.BOARD)
import os
GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Push-button pin with pull-up resistor

class Game(object):
    def __init__(self):
        self.white_turn = False
        self.valid_move = True
        self.board = Board()
        self.board.initialise_board()
        self.start_time = 0
##        self.interface = GUI()
##        self.interface.draw_board(self.board)
##        self.interface.update_gui(self.board)
##        self.interface.get_square_coordinates(self.board)
        self.selected_piece = None
        self.target_square = None
        self.capture_status = False
        self.capture = CaptureBoard()
        self.cap = self.capture.initialise_camera()
        time.sleep(0.1)
        self.capture.pin_setup()
        self.capture.start_game(self.cap)
##        self.capture.calibrate_board(self.cap)
        self.ai = AI()
        self.servos = ServoControl()
        self.servos.pin_setup()
        self.servos.serial_setup()
        time.sleep(1)
        self.servos.initialise_servos()
        self.depth = 3  # Three move lookahead
        self.game_termination = False

    def ai_move(self):
        while GPIO.input(31):
            self.start_time = time.time()
            GPIO.output(35, GPIO.HIGH)
            GPIO.output(33, GPIO.HIGH)
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
            ai_time = time.time() - self.start_time
            GPIO.output(35, GPIO.LOW)
            print("AI time: ", ai_time)
            print(self.board.move_sequence)
            print("Capture target", capture_target)
            self.start_time = time.time()
            target_1 = [target_1.row, target_1.column]
            target_2 = [target_2.row, target_2.column]
            self.servos.actuate_robot_arm(target_1, target_2, capture_target)
    #        time.sleep(5)
            actuation_time = time.time() - self.start_time
            print("Actuation time: ", actuation_time)
            self.start_time = time.time()
            self.capture.capture_image(self.cap, self.valid_move, True)
            circle_coordinates = self.capture.process_image()
            if circle_coordinates is None:
                self.valid_move = False
                self.ai_move()
            else:
                move_sequence = self.capture.calculate_coordinates(circle_coordinates)
                if self.validate_move(move_sequence):
                    robot_move = [self.selected_piece.number, self.target_square.number]
                    print("Robot move", robot_move)
                    if self.board.move_sequence == robot_move:
                        self.make_move()
                        cv_time = time.time() - self.start_time
                        print("Validation time: ", cv_time)
                        del root
                    else:
                        print("Robot unable to correctly actuate move")
                        self.valid_move = False
                        self.ai_move()
                else:
                    print("Robot unable to correctly actuate move")
                    self.valid_move = False
                    self.ai_move()
            break

    def human_move(self):
        while GPIO.input(31):
            self.capture.capture_image(self.cap, self.valid_move, False)
            circle_coordinates = self.capture.process_image()
            if circle_coordinates is None:
                self.valid_move = False
                self.human_move()
            else:
                print("Circle coordinates: ", circle_coordinates)
                move_sequence = self.capture.calculate_coordinates(circle_coordinates)
                if self.validate_move(move_sequence):
                    self.board.move_sequence = [self.selected_piece.number, self.target_square.number]
                    if abs(self.selected_piece.number - self.target_square.number) > 5:
                        self.capture_status = True
                    else:
                        self.capture_status = False

                    self.make_move()
                else:
                    print("Game over AI wins")
                    self.valid_move = False
                    self.human_move()
            break

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
        while GPIO.input(31):
            self.ai_move()
            if self.capture_status:
                self.ai_move()
            self.human_move()
            if self.capture_status:
                self.human_move()
        print("Not Running")
        os.system("sudo poweroff")

    def make_move(self):
        if self.board.legal_move(self.white_turn):
            self.board.update_board()
            self.board.final_possible_moves = []
            self.selected_piece = None
##            self.interface.draw_board(self.board)
##            self.interface.update_gui(self.board)
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
