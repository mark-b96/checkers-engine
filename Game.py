from Board import Board
from GUI import GUI
from CaptureBoard import CaptureBoard
from AI import AI
from anytree import Node, RenderTree
import copy

class Game(object):
    def __init__(self):
        self.white_turn = False

    def update_game_state(self):
        board = Board()
        board.initialise_board()
        interface = GUI()
        interface.draw_board(board)
        interface.update_gui(board)
        interface.get_square_coordinates(board)
        selected_piece = None
        target_square = None
        # capture = CaptureBoard()
        # cap = capture.initialise_camera()
        ai = AI()
        depth = 2
        root = Node(board)
        ai.generate_tree(board, self.white_turn, root, depth)

        print(len(root.leaves))
        print(RenderTree(root))


        # while 1:
        #     capture.capture_image(cap)
        #     circle_coordinates = capture.process_image()
        #     move_sequence = capture.calculate_coordinates(circle_coordinates)
        #     print(move_sequence)
        #     for move in move_sequence:
        #         selected_square = board.checkers_board[move[0]][move[1]]
        #         # selected_square = interface.event_listener()
        #         print(board.checkers_board[move[0]][move[1]].number)
        #         if selected_square.piece:
        #             if selected_square.piece.colour == "black":
        #                 piece_colour = False
        #             else:
        #                 piece_colour = True
        #             if piece_colour == self.white_turn:
        #                 print("Getting legal moves")
        #                 legal_moves = board.possible_moves(selected_square)
        #                 # print("Legal Moves", legal_moves)
        #                 selected_piece = selected_square
        #                 selected_square = None
        #             else:
        #                 selected_piece = None
        #         else:
        #             target_square = selected_square
        #
        #     if selected_piece and target_square:
        #         board.move_sequence = [selected_piece.number, target_square.number]
        #         if board.legal_move(self.white_turn):
        #             board.update_board()
        #             board.final_possible_moves = []
        #             selected_piece = None
        #             interface.draw_board(board)
        #             interface.update_board(board)
        #             self.white_turn = not self.white_turn