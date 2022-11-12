import copy
import math
import sys
import cv2
import pygame
import numpy as np

from constants import *

# PYGAME SETUP
pygame.init()
screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
pygame.display.set_caption('TIC TAC TOE AI')
screen.fill( BG_COLOR )

class Game:
    def __init__(self):
        self.board = Board()
        self.winner = None
        self.game_over = False
        self.draw_lines()
        self.mode = "pvp"
        self.ai = AI()

    def draw_lines(self):
        # 1 horizontal
        pygame.draw.line(screen, LINE_COLOR, (0, SQSIZE), (WIDTH, SQSIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, 2*SQSIZE), (WIDTH, 2*SQSIZE), LINE_WIDTH)
        # 2 vertical
        pygame.draw.line(screen, LINE_COLOR, (SQSIZE, 0), (SQSIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (2*SQSIZE, 0), (2*SQSIZE, HEIGHT), LINE_WIDTH)

    def display_winner(self):

        #set the font to write with
        font = pygame.font.Font('Montserrat-Black.ttf', 64) 
        #(0, 0, 0) is black, to make black text
        if self.winner == 1:
            text = font.render('You Lost', True, (0, 0, 0))
        elif self.winner == 2:
            text = font.render('You Won', True, (0, 0, 0))
        else:
            text = font.render('Tie', True, (0, 0, 0))
        #get the rect of the text
        textRect = text.get_rect()
        #set the position of the text
        textRect.center = (300, 300)
        #draw a rectangle to cover the old text
        pygame.draw.rect(screen, BG_COLOR, (0, 0, 600, 600))
        #add text to window
        screen.blit(text, textRect)
        #update window
        pygame.display.update()
    
    def reset(self):
        self.board.reset()
        self.winner = None
        self.game_over = False
        screen.fill( BG_COLOR )
        self.draw_lines()
        self.ai.turn = False

class Board:
    def __init__(self):
        self.board = np.zeros( (ROWS, COLS) )

    def final_state(self):
        if(self.check_win(1)):
            return 1
        elif(self.check_win(2)):
            return 2
        elif(self.is_full()):
            return 3
        else:
            return 0
    
    def check_win(self, player):
        # check horizontal
        for i in range(ROWS):
            if(self.board[i][0] == self.board[i][1] == self.board[i][2] == player):
                return True

        # check vertical
        for i in range(COLS):
            if(self.board[0][i] == self.board[1][i] == self.board[2][i] == player):
                return True

        # check diagonal
        if(self.board[0][0] == self.board[1][1] == self.board[2][2] == player):
            return True
        if(self.board[0][2] == self.board[1][1] == self.board[2][0] == player):
            return True

        return False


    def highlight_square(self, x, y):
        row , col = self.get_row_col(x, y)

        # color current square red
        if(row is not None and col is not None and self.is_empty(row, col)):
            pygame.draw.rect(screen, (0,0,0), (col*SQSIZE, row*SQSIZE, SQSIZE, SQSIZE), 8, border_radius=20)

        # reset all other square colors
        for i in range(ROWS):
            for j in range(COLS):
                if((i != row or j != col)):
                    pygame.draw.rect(screen, LINE_COLOR, (j*SQSIZE, i*SQSIZE, SQSIZE, SQSIZE), 8, border_radius=20)

    def get_row_col(self, x, y):
        # check col
        if(x < SQSIZE):
            col = 0
        elif(x < 2*SQSIZE):
            col = 1
        elif(x < 3*SQSIZE):
            col = 2
        else:
            col = None
        
        # check row
        if(y < SQSIZE):
            row = 0
        elif(y < 2*SQSIZE):
            row = 1
        elif(y < 3*SQSIZE):
            row = 2
        else:
            row = None

        return row, col
    
    # check if the given x and y coords are on a playable square
    def is_valid(self, x, y):
        row, col = self.get_row_col(x, y)
        if(row is not None and col is not None):
            if(self.board[row][col] == 0):
                return True
        return False

    # check if the given square at given row and col is empty
    def is_empty(self, row, col):
        return self.board[row][col] == 0
    
    def is_full(self):
        for i in range(ROWS):
            for j in range(COLS):
                if(self.board[i][j] == 0):
                    return False
        return True

    def get_empty_squares(self):
        empty_squares = []
        for i in range(ROWS):
            for j in range(COLS):
                if(self.board[i][j] == 0):
                    empty_squares.append((i, j))
        return empty_squares
    
    # draw the given symbol at the given row and col
    def draw_figures(self, x, y, player):
        row, col = self.get_row_col(x, y)
        if(row is not None and col is not None):
            if(player == 1):
                pygame.draw.circle(screen, CIRC_COLOR, (col*SQSIZE + SQSIZE//2, row*SQSIZE + SQSIZE//2), RADIUS, CIRC_WIDTH)
            elif(player == 2):

                # using opencv to draw two rounded lines
                w = CROSS_WIDTH-7
                p1 = (col*SQSIZE + OFFSET, row*SQSIZE + OFFSET)
                p2 = (col*SQSIZE + SQSIZE - OFFSET, row*SQSIZE + SQSIZE - OFFSET)
                rect = pygame.Rect(*p1, p2[0]-p1[0], p2[1]-p1[1])
                rect.normalize()
                rect.inflate_ip(w, w)
                c = pygame.Color(CROSS_COLOR)
                line_image = np.zeros((rect.height, rect.width, 4), dtype = np.uint8)
                line_image = cv2.line(line_image, (w//2, w//2), (p2[0]-p1[0]+w//2, p2[1]-p1[1]+w//2), (c.r, c.g, c.b, c.a), thickness=w)
                line_surface = pygame.image.frombuffer(line_image.flatten(), rect.size, 'RGBA')
                screen.blit(line_surface, line_surface.get_rect(center = rect.center))

                #rotate the line by 90 degrees
                line_image = np.rot90(line_image, 1)
                line_surface = pygame.image.frombuffer(line_image.flatten(), rect.size, 'RGBA')
                screen.blit(line_surface, line_surface.get_rect(center = rect.center))

            self.board[row][col] = player

    # check if the given player has won
    def check_win(self, player):
        # check horizontal
        for i in range(ROWS):
            if(self.board[i][0] == player and self.board[i][1] == player and self.board[i][2] == player):
                return True
        
        # check vertical
        for j in range(COLS):
            if(self.board[0][j] == player and self.board[1][j] == player and self.board[2][j] == player):
                return True
        
        # check diagonal
        if(self.board[0][0] == player and self.board[1][1] == player and self.board[2][2] == player):
            return True
        if(self.board[0][2] == player and self.board[1][1] == player and self.board[2][0] == player):
            return True

        return False
    
    def reset(self):
        self.board = np.zeros( (ROWS, COLS) )

    def draw(self, row, col, player):
        if(player == 1):
            pygame.draw.circle(screen, CIRC_COLOR, (col*SQSIZE + SQSIZE//2, row*SQSIZE + SQSIZE//2), RADIUS, CIRC_WIDTH)
        elif(player == 2):
            pygame.draw.line(screen, CROSS_COLOR, (col*SQSIZE + OFFSET, row*SQSIZE + OFFSET), (col*SQSIZE + SQSIZE - OFFSET, row*SQSIZE + SQSIZE - OFFSET), CROSS_WIDTH)
            pygame.draw.line(screen, CROSS_COLOR, (col*SQSIZE + OFFSET, row*SQSIZE + SQSIZE - OFFSET), (col*SQSIZE + SQSIZE - OFFSET, row*SQSIZE + OFFSET), CROSS_WIDTH)
        self.board[row][col] = player

    def mark(self, row, col, player):
        self.board[row][col] = player

class AI:
    def __init__(self):
        self.turn = False
        self.player = 2

    def minimax(self, board, maximizing):
        
        #base case
        case = board.final_state()
        if case == 1:
            return -1, None
        elif case == 2:
            return 1, None
        elif case == 3:
            return 0, None
        
        if maximizing:
            max_level = -math.inf
            max_move = None
            empty_squares = board.get_empty_squares()
            for (row,col) in empty_squares:
                temp_board = copy.deepcopy(board)
                temp_board.mark(row, col, self.player)
                score, _ = self.minimax(temp_board, False)
                if score > max_level:
                    max_level = score
                    max_move = (row, col)
            return max_level, max_move
        else:
            min_level = math.inf
            min_move = None
            empty_squares = board.get_empty_squares()
            for (row,col) in empty_squares:
                temp_board = copy.deepcopy(board)
                temp_board.mark(row, col, 1)
                score, _ = self.minimax(temp_board, True)
                if score < min_level:
                    min_level = score
                    min_move = (row, col)
            return min_level, min_move

    
    def eval(self, board):
        eval, move = self.minimax(board, False)
        return move
    



def main():
    # creating a game object
    game = Game()
    mouse_x, mouse_y = 0, 0
    player = 2
    plays = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #reset the board if player presses r
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset()
                    plays = 0
                    player = 2
                    
                if event.key == pygame.K_a:
                    game.mode = 'ai'
                if event.key == pygame.K_p:
                    game.mode = 'pvp'

            if not game.game_over:
                # highlight the square that the mouse is hovering over
                if event.type == pygame.MOUSEMOTION:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    game.board.highlight_square(mouse_x, mouse_y)

                # mark the square that the mouse clicked on
                if player == 2 or not game.mode == 'ai':
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        if game.board.is_valid(mouse_x, mouse_y):
                            game.ai.turn = True
                            game.board.draw_figures(mouse_x, mouse_y, player)
                            plays += 1
                            if(plays >= 3):
                                if(game.board.check_win(player)):
                                    game.game_over = True
                                    game.winner = player
                                    game.display_winner()
                                    plays = 0
                                elif game.board.is_full():
                                    game.game_over = True
                                    game.winner = 0
                                    game.display_winner()
                                    plays = 0
                    
                        # switch player
                        player = 2 if player == 1 else 1
                        print (game.board.board)
                else:
                    if game.mode == 'ai' and game.ai.turn:
                        move = game.ai.eval(game.board)
                        game.board.draw(move[0], move[1], player)
                        plays += 1
                        if(plays >= 3):
                            if(game.board.check_win(player)):
                                game.game_over = True
                                game.winner = player
                                game.display_winner()
                                plays = 0
                            elif game.board.is_full():
                                    game.game_over = True
                                    game.winner = 0
                                    game.display_winner()
                                    plays = 0
                        player = 2 if player == 1 else 1
                        game.ai.turn = False
                        print (game.board.board)
            
        pygame.display.update()

main()