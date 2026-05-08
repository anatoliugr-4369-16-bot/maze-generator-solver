import pygame
import random
import sys
"""
DFS MAZE GENERATOR AND SOLVER
This program generates a perfect maze using Depth-First Search (DFS)
backtracking and then solves it using another DFS traversal.
"""
#          MAZE GENERATOR & SOLVER
ROWS = 12
COLS = 16
CELL_SIZE = 40
PADDING = 40
WIDTH = COLS * CELL_SIZE + PADDING * 2
GRID_HEIGHT = ROWS * CELL_SIZE
INFO_HEIGHT = 150
WINDOW_HEIGHT = GRID_HEIGHT + INFO_HEIGHT + PADDING * 2
GRID_TOP = INFO_HEIGHT + PADDING

# Colors
LIGHT_GRAY = (248, 248, 250)
PANEL_BG = (35, 40, 48)
BUTTON_BASE = (55, 65, 80)
BUTTON_HOVER = (85, 100, 125)
TEXT_LIGHT = (235, 245, 255)
WALL_COLOR = (25, 25, 30)
CELL_FILL = (255, 255, 255)

# Generation Colors
COLOR_GEN_VISITED = (80, 200, 180)
COLOR_GEN_MOUSE = (50, 255, 140)

COLOR_MOUSE = (255, 210, 90)
COLOR_PATH = (255, 160, 60)
COLOR_DEAD = (130, 180, 230)
COLOR_SOLUTION = (220, 80, 70)
COLOR_START_GOAL = (80, 180, 120)

#                      MAZE DATA STRUCTURES
# northWall[r][c] = True  means the north (top) wall of cell (r,c) is present
# northWall[r][c] = False means the north wall has been removed (passage exists)
# eastWall[r][c]  = True  means the east (right) wall of cell (r,c) is present
# eastWall[r][c]  = False means the east wall has been removed (passage exists)
northWall = [[True for _ in range(COLS)] for _ in range(ROWS)]
eastWall = [[True for _ in range(COLS)] for _ in range(ROWS)]
visited = [[False for _ in range(COLS)] for _ in range(ROWS)]

current_solution = None
dead_ends = set()
maze_solved = False


def draw_cell(screen, r, c, fill_color):
    x = c * CELL_SIZE + PADDING
    y = r * CELL_SIZE + GRID_TOP

    pygame.draw.rect(screen, fill_color, (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2))

    if northWall[r][c]:
        pygame.draw.line(screen, WALL_COLOR, (x, y), (x + CELL_SIZE, y), 2)

    if eastWall[r][c]:
        pygame.draw.line(screen, WALL_COLOR, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)

    if c == 0:
        if eastWall[r][0]:
            pygame.draw.line(screen, WALL_COLOR, (x, y), (x, y + CELL_SIZE), 2)
    elif eastWall[r][c - 1]:
        pygame.draw.line(screen, WALL_COLOR, (x, y), (x, y + CELL_SIZE), 2)

    if r + 1 < ROWS and northWall[r + 1][c]:
        pygame.draw.line(screen, WALL_COLOR, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)

    # Draw bottom border of the entire maze (only for the last row)
    if r == ROWS - 1:
        pygame.draw.line(screen, WALL_COLOR, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)


class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial):
        self.rect = pygame.Rect(x, y, w, h)
        self.min = min_val
        self.max = max_val
        self.val = initial
        self.knob_radius = h // 2 + 2
        self.dragging = False

    def get_knob_x(self):
        return self.rect.x + (self.val - self.min) / (self.max - self.min) * self.rect.w

    def draw(self, screen):
        pygame.draw.rect(screen, (70, 80, 95), self.rect, border_radius=self.knob_radius)
        fill_w = (self.val - self.min) / (self.max - self.min) * self.rect.w
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.h)
            pygame.draw.rect(screen, (180, 210, 250), fill_rect, border_radius=self.knob_radius)
        knob_x = self.get_knob_x()
        pygame.draw.circle(screen, (255, 255, 255), (int(knob_x), self.rect.centery), self.knob_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.dragging = True
            self._set_val_from_x(event.pos[0])
            return self.val
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_val_from_x(event.pos[0])
            return self.val
        return None

    def _set_val_from_x(self, x):
        ratio = max(0, min(1, (x - self.rect.x) / self.rect.w))
        self.val = int(round(self.min + ratio * (self.max - self.min)))


def draw_ui(screen, font, speed_slider, generate_btn, solve_btn, mouse_pos):
    panel = pygame.Surface((WIDTH, INFO_HEIGHT))
    panel.set_alpha(240)
    panel.fill(PANEL_BG)
    screen.blit(panel, (0, 0))

    gen_color = BUTTON_HOVER if generate_btn.collidepoint(mouse_pos) else BUTTON_BASE
    pygame.draw.rect(screen, gen_color, generate_btn, border_radius=12)
    gen_text = font.render("⟳ NEW MAZE", True, TEXT_LIGHT)
    screen.blit(gen_text, (generate_btn.x + 15, generate_btn.y + 10))

    solve_color = BUTTON_HOVER if solve_btn.collidepoint(mouse_pos) else BUTTON_BASE
    pygame.draw.rect(screen, solve_color, solve_btn, border_radius=12)
    solve_text = font.render("▶ SOLVE MAZE", True, TEXT_LIGHT)
    screen.blit(solve_text, (solve_btn.x + 15, solve_btn.y + 10))

    speed_label = font.render("SPEED", True, TEXT_LIGHT)
    screen.blit(speed_label, (solve_btn.right + 25, solve_btn.y + 8))
    speed_slider.draw(screen)
    val_text = font.render(str(speed_slider.val), True, TEXT_LIGHT)
    screen.blit(val_text, (speed_slider.rect.right + 12, speed_slider.rect.centery - 8))

    legend = [("Current Mouse", COLOR_MOUSE), ("Explored Path", COLOR_PATH),
              ("Dead End", COLOR_DEAD), ("Solution Path", COLOR_SOLUTION),
              ("Start / Goal", COLOR_START_GOAL)]
    start_x = 20
    y_top = solve_btn.y + 48
    item_width = 135
    for i, (label, color) in enumerate(legend):
        row = i // 3
        col = i % 3
        x = start_x + col * item_width
        y = y_top + row * 22
        pygame.draw.circle(screen, color, (x + 8, y + 8), 7)
        text = font.render(label, True, TEXT_LIGHT)
        screen.blit(text, (x + 22, y + 1))


def reset_maze_data():
    global current_solution, dead_ends, maze_solved
    northWall[:] = [[True] * COLS for _ in range(ROWS)]
    eastWall[:] = [[True] * COLS for _ in range(ROWS)]
    visited[:] = [[False] * COLS for _ in range(ROWS)]
    current_solution = None
    dead_ends = set()
    maze_solved = False


# Time Complexity: O(ROWS * COLS)
# Each cell is visited once during DFS maze generation.
def generate_maze(screen, clock, font, speed_slider, generate_btn, solve_btn):
    """Generates a perfect maze using DFS backtracking."""
    reset_maze_data()
    start_r = random.randint(0, ROWS-1)
    start_c = random.randint(0, COLS-1)
    stack = [(start_r, start_c)]
    visited[start_r][start_c] = True

    while stack:
        r, c = stack[-1]
        neighbours = []
        for dr, dc, dname in [(-1,0,'up'),(1,0,'down'),(0,-1,'left'),(0,1,'right')]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and not visited[nr][nc]:
                neighbours.append((dname, nr, nc))

        if neighbours:
            direction, nr, nc = random.choice(neighbours)

            # Remove the wall between current cell and chosen neighbor
            if direction == 'up': northWall[r][c] = False
            elif direction == 'down': northWall[nr][nc] = False
            elif direction == 'left': eastWall[nr][nc] = False
            elif direction == 'right': eastWall[r][c] = False

            visited[nr][nc] = True
            stack.append((nr, nc))
        else:
            stack.pop()

        screen.fill(LIGHT_GRAY)
        draw_ui(screen, font, speed_slider, generate_btn, solve_btn, pygame.mouse.get_pos())

        for i in range(ROWS):
            for j in range(COLS):
                if stack and (i, j) == stack[-1]:
                    color = COLOR_GEN_MOUSE
                elif visited[i][j]:
                    color = COLOR_GEN_VISITED
                else:
                    color = CELL_FILL
                draw_cell(screen, i, j, color)

        pygame.display.flip()
        clock.tick(10 + speed_slider.val * 6)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


# Time Complexity: O(ROWS * COLS)
# DFS may visit every cell once while searching for the exit.
def solve_maze(screen, clock, font, speed_slider, start, end, generate_btn, solve_btn):
    """Solves the maze using DFS backtracking and shows dead ends."""
    global current_solution, dead_ends, maze_solved
    stack = [start]
    solve_visited = [[False] * COLS for _ in range(ROWS)]
    solve_visited[start[0]][start[1]] = True
    parent = {}           # Used to reconstruct the final solution path
    dead_ends = set()

    directions = [(-1, 0, 'up'), (1, 0, 'down'), (0, -1, 'left'), (0, 1, 'right')]

    while stack:
        r, c = stack[-1]

        if (r, c) == end:
            # Reconstruct solution path using parent dictionary
            on_solution = [[False] * COLS for _ in range(ROWS)]
            cur = end
            while cur != start:
                on_solution[cur[0]][cur[1]] = True
                cur = parent.get(cur)
            on_solution[start[0]][start[1]] = True
            current_solution = on_solution
            maze_solved = True
            return True

        random.shuffle(directions)
        moved = False
        for dr, dc, wall_check in directions:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < ROWS and 0 <= nc < COLS) or solve_visited[nr][nc]:
                continue
            wall_blocked = False
            if wall_check == 'up' and northWall[r][c]: wall_blocked = True
            elif wall_check == 'down' and northWall[nr][nc]: wall_blocked = True
            elif wall_check == 'left' and eastWall[nr][nc]: wall_blocked = True
            elif wall_check == 'right' and eastWall[r][c]: wall_blocked = True

            if not wall_blocked:
                solve_visited[nr][nc] = True
                parent[(nr, nc)] = (r, c)      # Record parent for path reconstruction
                stack.append((nr, nc))
                moved = True
                break

        if not moved:
            dead_ends.add((r, c))              # Mark this cell as a dead end (will be blue)
            stack.pop()

        screen.fill(LIGHT_GRAY)
        draw_ui(screen, font, speed_slider, generate_btn, solve_btn, pygame.mouse.get_pos())

        for i in range(ROWS):
            for j in range(COLS):
                if stack and (i, j) == stack[-1]:
                    color = COLOR_MOUSE
                elif stack and (i, j) in stack[:-1]:
                    color = COLOR_PATH
                elif (i, j) in dead_ends:
                    color = COLOR_DEAD
                else:
                    color = CELL_FILL
                draw_cell(screen, i, j, color)

        if stack:
            cr, cc = stack[-1]
            cx = cc * CELL_SIZE + PADDING + CELL_SIZE//2
            cy = cr * CELL_SIZE + GRID_TOP + CELL_SIZE//2
            pygame.draw.circle(screen, COLOR_MOUSE, (cx, cy), 13)
            pygame.draw.circle(screen, (255, 255, 200), (cx, cy), 7)

        sr, sc = start
        er, ec = end
        pygame.draw.circle(screen, COLOR_START_GOAL,
                         (sc*CELL_SIZE + PADDING + CELL_SIZE//2, sr*CELL_SIZE + GRID_TOP + CELL_SIZE//2), 11)
        pygame.draw.circle(screen, COLOR_START_GOAL,
                         (ec*CELL_SIZE + PADDING + CELL_SIZE//2, er*CELL_SIZE + GRID_TOP + CELL_SIZE//2), 11)

        pygame.display.flip()
        clock.tick(8 + speed_slider.val * 5)

    return False


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("DFS Maze Generator and Solver")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("segoeui", 13)

    speed_slider = Slider(380, 30, 140, 10, 1, 15, 3)
    generate_btn = pygame.Rect(20, 25, 140, 38)
    solve_btn = pygame.Rect(175, 25, 140, 38)

    generate_maze(screen, clock, font, speed_slider, generate_btn, solve_btn)

    start = (random.randint(0, ROWS-1), 0)
    end = (random.randint(0, ROWS-1), COLS-1)
    eastWall[start[0]][0] = False      # Open left entrance
    eastWall[end[0]][end[1]] = False   # Open right exit

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            slider_val = speed_slider.handle_event(event)
            if slider_val is not None:
                speed_slider.val = slider_val

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if generate_btn.collidepoint(event.pos):
                    generate_maze(screen, clock, font, speed_slider, generate_btn, solve_btn)
                    start = (random.randint(0, ROWS-1), 0)
                    end = (random.randint(0, ROWS-1), COLS-1)
                    eastWall[start[0]][0] = False
                    eastWall[end[0]][end[1]] = False
                    global current_solution, dead_ends, maze_solved
                    current_solution = None
                    dead_ends = set()
                    maze_solved = False

                elif solve_btn.collidepoint(event.pos) and not maze_solved:
                    solve_maze(screen, clock, font, speed_slider, start, end, generate_btn, solve_btn)

        screen.fill(LIGHT_GRAY)
        for i in range(ROWS):
            for j in range(COLS):
                if current_solution and current_solution[i][j]:
                    fill = COLOR_SOLUTION
                elif dead_ends and (i, j) in dead_ends:
                    fill = COLOR_DEAD
                else:
                    fill = CELL_FILL
                draw_cell(screen, i, j, fill)

        if start and end:
            sr, sc = start
            er, ec = end
            pygame.draw.circle(screen, COLOR_START_GOAL,
                             (sc*CELL_SIZE + PADDING + CELL_SIZE//2, sr*CELL_SIZE + GRID_TOP + CELL_SIZE//2), 12)
            pygame.draw.circle(screen, COLOR_START_GOAL,
                             (ec*CELL_SIZE + PADDING + CELL_SIZE//2, er*CELL_SIZE + GRID_TOP + CELL_SIZE//2), 12)

        draw_ui(screen, font, speed_slider, generate_btn, solve_btn, mouse_pos)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()