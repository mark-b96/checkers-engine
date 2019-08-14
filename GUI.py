import pygame
WHITE_SQUARES = (255, 255, 255)
BLACK_SQUARES = (0, 0, 0)
GREEN_SQUARES = (0, 255, 0)
RED_PIECES = (255, 0, 0)
MAGENTA_PIECES = (255, 0, 255)
BLUE_PIECES = (0, 0, 255)
CYAN_PIECES = (0, 255, 255)


class GUI(object):
    def __init__(self):
        self.screen_width = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_width))
        self.square_size = int(self.screen_width / 8)
        self.piece_size = int(self.square_size/4)
        self.square_coordinates = []

    def draw_board(self, board):
        for row in range(board.row_count):
            for column in range(board.column_count):
                if board.checkers_board[row][column].colour == "white":
                    colour = WHITE_SQUARES
                else:
                    colour = BLACK_SQUARES
                    if board.checkers_board[column][row].number in board.final_possible_moves:
                        colour = GREEN_SQUARES
                pygame.draw.rect(self.screen, colour,
                                 [row * self.square_size, column * self.square_size, self.square_size, self.square_size])
                board.checkers_board[row][column].coordinates = (column * self.square_size) + 50, (
                            row * self.square_size) + 50

    def update_GUI(self, board):
        for row in range(board.row_count):
            for column in range(board.column_count):
                if board.checkers_board[row][column].piece:
                    if board.checkers_board[row][column].piece.colour == "white":
                        colour1 = RED_PIECES
                        if board.checkers_board[row][column].piece.crowned:
                            colour1 = MAGENTA_PIECES
                    else:
                        colour1 = BLUE_PIECES
                        if board.checkers_board[row][column].piece.crowned:
                            colour1 = CYAN_PIECES
                    if board.checkers_board[row][column].piece:
                        coordinates = ((column * self.square_size) + 50, (row*self.square_size) + 50)
                        pygame.draw.circle(self.screen, colour1, coordinates, self.piece_size)
        pygame.display.update()

    def get_square_coordinates(self, board):
        for row in range(board.row_count):
            for column in range(board.column_count):
                self.square_coordinates.append(board.checkers_board[row][column])

    def event_listener(self):
        while 1:
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()

                    for square in self.square_coordinates:
                        if square.colour == "black":
                            if (square.coordinates[0] - self.square_size/2 < x < square.coordinates[0] + self.square_size/2) and \
                                    (square.coordinates[1] - self.square_size/2 < y < square.coordinates[1] + self.square_size/2):
                                return square





