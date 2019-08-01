from Board import Board
from GUI import GUI
from CaptureBoard import CaptureBoard


class Game(object):
    def __init__(self):
        self.white_turn = False

    def update_game_state(self):
        board = Board()
        board.initialise_board()
        interface = GUI()
        interface.draw_board(board)
        interface.update_board(board)
        interface.get_square_coordinates(board)
        selected_piece = None
        capture = CaptureBoard()
        capture.corner_coordinates = capture.capture_image(capture.initialise_camera())
        circle_coordinates = capture.process_image()
        move_sequence = capture.calculate_coordinates(capture.corner_coordinates[0], circle_coordinates)

        while 1:
            for move in move_sequence:
                selected_square = board.checkers_board[move[0]][move[1]]

                # selected_square = interface.event_listener()

                if selected_square.piece:
                    if selected_square.piece.colour == "black":
                        piece_colour = False
                    else:
                        piece_colour = True
                    if piece_colour == self.white_turn:
                        legal_moves = board.possible_moves(selected_square)
                        # print("Legal Moves", legal_moves)
                        selected_piece = selected_square
                        selected_square = None
                    else:
                        selected_piece = None
                interface.draw_board(board)
                interface.update_board(board)
                if selected_piece and selected_square:
                    board.move_sequence = [selected_piece.number, selected_square.number]
                    if board.legal_move(self.white_turn):
                        board.update_board()
                        board.final_possible_moves = []
                        selected_piece = None
                        interface.draw_board(board)
                        interface.update_board(board)
                        self.white_turn = not self.white_turn
