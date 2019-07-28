import pygame


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
                board.checkers_board[row][column].coordinates = (column * self.square_size) + 50, (
                            row * self.square_size) + 50
        pygame.display.update()

    def update_board(self, board):
        for row in range(board.row_count):
            for column in range(board.column_count):
                if board.checkers_board[row][column].piece:
                    if board.checkers_board[row][column].piece.colour == "white":
                        colour1 = (255, 0, 0)
                        if board.checkers_board[row][column].piece.crowned:
                            colour1 = (255, 0, 255)
                    else:
                        colour1 = (0, 0, 255)
                        if board.checkers_board[row][column].piece.crowned:
                            colour1 = (0, 255, 255)
                    if board.checkers_board[row][column].piece:
                        coordinates = ((column * self.square_size) + 50, (row*self.square_size) + 50)
                        pygame.draw.circle(self.screen, colour1, coordinates, self.piece_size)
        pygame.display.update()

    def event_listener(self, board):
        while 1:
            selected_square = None
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    square_coordinates = self.get_square_coordinates(board)
                    print("Here",x,y)
                    for square in square_coordinates:
                        if square.piece:
                            if (x < square.coordinates[0] + self.piece_size and x > square.coordinates[0] - self.piece_size) and\
                                    (y < square.coordinates[1] + self.piece_size and y > square.coordinates[1] - self.piece_size):
                                if abs(x-square.coordinates[0])**2 + abs(y-square.coordinates[1])**2 < self.piece_size**2:
                                    selected_square = square
                                    print(x, y, square.piece.colour, square.row, square.column)
                                    return selected_square
                    for square in square_coordinates:
                        if square.colour == "black":
                            if (x < square.coordinates[0] + self.square_size/2 and x > square.coordinates[0] - self.square_size/2) and \
                                    (y < square.coordinates[1] + self.square_size/2 and y > square.coordinates[1] - self.square_size/2):
                                return square
            pygame.display.update()


    def get_square_coordinates(self, board):
        coordinates = []
        for row in range(board.row_count):
            for column in range(board.column_count):
                coordinates.append(board.checkers_board[row][column])
        return coordinates



