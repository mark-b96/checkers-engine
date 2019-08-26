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
        # self.capture = CaptureBoard()
        # self.cap = self.capture.initialise_camera()
        self.ai = AI()
        self.depth = 4 # Single move lookahead
        self.game_termination = False

    def update_game_state(self):
        while 1:
            root = Node(self.board)
            self.ai.generate_tree(self.board, self.white_turn, root, self.depth)
            print(RenderTree(root))
            self.board.move_sequence = self.ai.optimal_position.path[1].name.move_sequence
            # print("AI MOVE: ", self.ai.optimal_position.path[1].name.move_sequence)
            if self.board.move_sequence and self.game_termination:
                # time.sleep(1)
                self.make_move()
            else:
                if self.white_turn:
                    print("Black wins!")
                    exit(0)
                else:
                    print("White wins")
                    exit(0)

            # print(len(root.leaves))
            print(RenderTree(root))
            # self.capture.capture_image(self.cap, self.white_turn)
            # circle_coordinates = self.capture.process_image()
            # move_sequence = self.capture.calculate_coordinates(circle_coordinates)
            # print(move_sequence)
            # for move in move_sequence:
            #     selected_square = self.board.checkers_board[move[0]][move[1]]
            #     # selected_square = self.interface.event_listener()
            #     print(self.board.checkers_board[move[0]][move[1]].number)
            #     if selected_square.piece:
            #         if selected_square.piece.colour == "black":
            #             piece_colour = False
            #         else:
            #             piece_colour = True
            #         if piece_colour == self.white_turn:
            #             print("Getting legal moves")
            #             legal_moves = self.board.possible_moves(selected_square)
            #             # print("Legal Moves", legal_moves)
            #             self.selected_piece = selected_square
            #             selected_square = None
            #         else:
            #             self.selected_piece = None
            #     else:
            #         self.target_square = selected_square
            #
            # if self.selected_piece and self.target_square:
            #     self.board.move_sequence = [self.selected_piece.number, self.target_square.number]
            #     self.make_move()

    def make_move(self):
        if self.board.legal_move(self.white_turn):
            self.board.update_board()
            self.board.final_possible_moves = []
            self.selected_piece = None
            self.interface.draw_board(self.board)
            self.interface.update_gui(self.board)
            self.white_turn = not self.white_turn
        else:
            self.game_termination = True
