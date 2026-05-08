# DFS Maze Generator & Solver

A Python program that builds a random, proper maze using a stack‑based DFS (“mouse eating walls”) and then solves it with backtracking (red dot, blue dead ends, final red path).  
Made for a Computer Graphics assignment.

## Features

- **Maze generation** – DFS with stack, walls disappear as the mouse moves.
- **Maze solving** – DFS backtracking, shows the current path (yellow), explored path (orange), dead ends (blue), and final solution (red).
- **Interactive UI** –
  - `⟳ NEW MAZE` button
  - `▶ SOLVE MAZE` button
  - **Speed slider** (click and drag like a volume control, range 1–15)
  - Colour legend
- **Proper maze** – every cell is connected by a unique path (a spanning tree).
- **Bonus** – extra walls are randomly eaten (~1/20) to create cycles.

## Requirements

- **Python 3.7+**
- **Pygame** – install with `pip install pygame`

## How to Run

1. Save the code as `maze_generator_solver.py`
2. Open a terminal in that folder
3. Run:  
   `python maze_generator_solver.py`

The maze will generate automatically. Press the **SOLVE MAZE** button to watch the solver.

## How It Works

### Data Structures

- `northWall[r][c]` = `True` → wall above cell (r,c)
- `eastWall[r][c]` = `True` → wall to the right of cell (r,c)

### Generation (Stack‑based DFS)

1. Start at a random cell, push onto stack.
2. While stack not empty:
   - Look at current cell.
   - If there is an unvisited neighbour, choose one randomly, **eat the wall** between them, push neighbour onto stack.
   - Else (dead end) – pop from stack (backtrack).
3. Repeat until all cells visited → perfect maze.

### Solving (Backtracking)

- Use a stack to remember the current path.
- At each step, look for an unvisited neighbour with no wall.
- If found → move there, push onto stack.
- If dead end → pop, mark cell as **blue** (dead end).
- When the end is reached, reconstruct the path using a parent dictionary and draw it in red.

## Controls

| Control          | Action                                                          |
| ---------------- | --------------------------------------------------------------- |
| **Mouse click**  | Press buttons, drag the speed slider                            |
| **Speed slider** | Drag left/right to change animation speed (1 = slow, 15 = fast) |
| **⟳ NEW MAZE**   | Generate a completely new maze                                  |
| **▶ SOLVE MAZE** | Run the solver on the current maze                              |

## Demo

[Click here to watch the full demo (Loom recording)](https://www.loom.com/share/fb79a6cba8fb40258c57d7f8d61a8a11)

## Author

Anatoli chala UGR/4369/16 – Computer Graphics Assignment 1  
GitHub: [anatoliugr-4369-16-bot](https://github.com/anatoliugr-4369-16-bot)
