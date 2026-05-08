import pygame
import random
import sys

ROWS = 12
COLS = 16
CELL_SIZE = 40
PADDING = 40
WIDTH = COLS * CELL_SIZE + PADDING * 2
GRID_HEIGHT = ROWS * CELL_SIZE
INFO_HEIGHT = 150
WINDOW_HEIGHT = GRID_HEIGHT + INFO_HEIGHT + PADDING * 2
GRID_TOP = INFO_HEIGHT + PADDING

LIGHT_GRAY = (248, 248, 250)
PANEL_BG = (35, 40, 48)
BUTTON_BASE = (55, 65, 80)
BUTTON_HOVER = (85, 100, 125)
TEXT_LIGHT = (235, 245, 255)
WALL_COLOR = (25, 25, 30)
CELL_FILL = (255, 255, 255)
COLOR_GEN_VISITED = (80, 200, 180)
COLOR_GEN_MOUSE = (50, 255, 140)

northWall = [[True for _ in range(COLS)] for _ in range(ROWS)]
eastWall  = [[True for _ in range(COLS)] for _ in range(ROWS)]
visited = [[False for _ in range(COLS)] for _ in range(ROWS)]

def draw_cell(screen, r, c, fill_color):
    x = c * CELL_SIZE + PADDING
    y = r * CELL_SIZE + GRID_TOP
    pygame.draw.rect(screen, fill_color, (x+1, y+1, CELL_SIZE-2, CELL_SIZE-2))
    if northWall[r][c]:
        pygame.draw.line(screen, WALL_COLOR, (x, y), (x+CELL_SIZE, y), 2)
    if eastWall[r][c]:
        pygame.draw.line(screen, WALL_COLOR, (x+CELL_SIZE, y), (x+CELL_SIZE, y+CELL_SIZE), 2)
    if c == 0:
        if eastWall[r][0]:
            pygame.draw.line(screen, WALL_COLOR, (x, y), (x, y+CELL_SIZE), 2)
    elif eastWall[r][c-1]:
        pygame.draw.line(screen, WALL_COLOR, (x, y), (x, y+CELL_SIZE), 2)
    if r+1 < ROWS and northWall[r+1][c]:
        pygame.draw.line(screen, WALL_COLOR, (x, y+CELL_SIZE), (x+CELL_SIZE, y+CELL_SIZE), 2)
    if r == ROWS-1:
        pygame.draw.line(screen, WALL_COLOR, (x, y+CELL_SIZE), (x+CELL_SIZE, y+CELL_SIZE), 2)

def generate_maze(screen, clock):
    start_r = random.randint(0, ROWS-1)
    start_c = random.randint(0, COLS-1)
    stack = [(start_r, start_c)]
    visited[start_r][start_c] = True

    while stack:
        r, c = stack[-1]
        neighbours = []
        for dr, dc, dname in [(-1,0,'up'),(1,0,'down'),(0,-1,'left'),(0,1,'right')]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and not visited[nr][nc]:
                neighbours.append((dname, nr, nc))

        if neighbours:
            direction, nr, nc = random.choice(neighbours)
            if direction == 'up': northWall[r][c] = False
            elif direction == 'down': northWall[nr][nc] = False
            elif direction == 'left': eastWall[nr][nc] = False
            elif direction == 'right': eastWall[r][c] = False
            visited[nr][nc] = True
            stack.append((nr, nc))
        else:
            stack.pop()

        screen.fill(LIGHT_GRAY)
        for i in range(ROWS):
            for j in range(COLS):
                if stack and (i,j) == stack[-1]:
                    color = COLOR_GEN_MOUSE
                elif visited[i][j]:
                    color = COLOR_GEN_VISITED
                else:
                    color = CELL_FILL
                draw_cell(screen, i, j, color)
        pygame.display.flip()
        clock.tick(30)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Maze Generator - DFS")
    clock = pygame.time.Clock()
    generate_maze(screen, clock)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main()