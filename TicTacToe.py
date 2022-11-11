import copy
import sys
import pygame
import random
import numpy as np

from constants import *

# --- PYGAME SETUP ---

pygame.init()
screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
pygame.display.set_caption('TIC TAC TOE AI')
screen.fill( BG_COLOR )