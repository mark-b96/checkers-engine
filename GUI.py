import pygame
import time

class GUI(object):
    def __init__(self):
        self.screen_width = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_width))
        self.square_size = int(self.screen_width / 8)
        self.piece_size = int(self.square_size/4)

    def draw_board(self, board):
        for row in range(board.row_count):
            for column in range(board.column_count):
                if board.checkers_board[row][column].colour == "white":
                    colour = (255, 255, 255)
                else:
                    colour = (0, 0, 0)
                    if board.checkers_board[column][row].number in board.final_possible_moves:
                        colour = (0, 255, 0)
                pygame.draw.rect(self.screen, colour,
                                 [row * self.square_size, column * self.square_size, self.square_size, self.square_size])

        for row in range(board.row_count):
            for column in range(board.column_count):
                if board.checkers_board[row][column].piece:
                    if board.checkers_board[row][column].piece.colour == "white":
                        colour1 = (255, 0, 0)
                    else:
                        colour1 = (0, 0, 255)
                    if board.checkers_board[row][column].piece:
                        coordinates = ((column * self.square_size) + 50, (row*self.square_size) + 50)
                        pygame.draw.circle(self.screen, colour1, coordinates, self.piece_size)

        pygame.display.update()

    def event_listener(self):
        while 1:
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print("HERE")
                    x, y = pygame.mouse.get_pos()
                    print(x, y)
            time.sleep(0.03)
            pygame.display.update()

