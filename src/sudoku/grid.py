"""
Sudoku grid logic: generation, validation, solving.
Pure functions operating on numpy arrays.
"""
import numpy as np
from typing import Optional
import random


def create_empty_grid() -> np.ndarray:
    """Create an empty 9x9 grid."""
    return np.zeros((9, 9), dtype=np.int8)


def is_valid_placement(grid: np.ndarray, row: int, col: int, num: int) -> bool:
    """Check if placing num at (row, col) is valid."""
    if num == 0:
        return True

    # Check row
    if num in grid[row, :]:
        if grid[row, col] != num:
            return False

    # Check column
    if num in grid[:, col]:
        if grid[row, col] != num:
            return False

    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    box = grid[box_row:box_row + 3, box_col:box_col + 3]
    if num in box:
        if grid[row, col] != num:
            return False

    return True


def find_conflicts(grid: np.ndarray, row: int, col: int) -> list[tuple[int, int]]:
    """Find all cells that conflict with the value at (row, col)."""
    conflicts = []
    val = grid[row, col]
    if val == 0:
        return conflicts

    # Check row
    for c in range(9):
        if c != col and grid[row, c] == val:
            conflicts.append((row, c))

    # Check column
    for r in range(9):
        if r != row and grid[r, col] == val:
            conflicts.append((r, col))

    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if (r, c) != (row, col) and grid[r, c] == val:
                conflicts.append((r, c))

    return conflicts


def get_candidates(grid: np.ndarray, row: int, col: int) -> set[int]:
    """Get valid candidates for a cell."""
    if grid[row, col] != 0:
        return set()

    candidates = set(range(1, 10))

    # Remove row values
    candidates -= set(grid[row, :])

    # Remove column values
    candidates -= set(grid[:, col])

    # Remove box values
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    candidates -= set(grid[box_row:box_row + 3, box_col:box_col + 3].flatten())

    return candidates


def solve(grid: np.ndarray) -> Optional[np.ndarray]:
    """Solve sudoku using backtracking. Returns solution or None."""
    grid = grid.copy()

    def backtrack() -> bool:
        # Find empty cell
        for r in range(9):
            for c in range(9):
                if grid[r, c] == 0:
                    for num in range(1, 10):
                        if is_valid_placement(grid, r, c, num):
                            grid[r, c] = num
                            if backtrack():
                                return True
                            grid[r, c] = 0
                    return False
        return True

    if backtrack():
        return grid
    return None


def generate_puzzle(difficulty: str = "medium") -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a Sudoku puzzle.
    Returns (puzzle, solution) where puzzle has some cells removed.
    """
    # Difficulty determines how many cells to remove
    remove_count = {
        "easy": 35,
        "medium": 45,
        "hard": 55,
    }.get(difficulty, 45)

    # Start with empty grid and fill diagonally (always valid)
    grid = create_empty_grid()

    # Fill diagonal 3x3 boxes first (they don't affect each other)
    for box in range(3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in range(3):
            for j in range(3):
                grid[box * 3 + i, box * 3 + j] = nums[i * 3 + j]

    # Solve the rest
    solution = solve(grid)
    if solution is None:
        # Fallback: use a known valid puzzle
        solution = np.array([
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ], dtype=np.int8)

    # Create puzzle by removing cells
    puzzle = solution.copy()
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    removed = 0
    for r, c in cells:
        if removed >= remove_count:
            break
        puzzle[r, c] = 0
        removed += 1

    return puzzle, solution


def is_complete(grid: np.ndarray) -> bool:
    """Check if the grid is completely and correctly filled."""
    if 0 in grid:
        return False

    # Check all rows
    for r in range(9):
        if len(set(grid[r, :])) != 9:
            return False

    # Check all columns
    for c in range(9):
        if len(set(grid[:, c])) != 9:
            return False

    # Check all boxes
    for box_r in range(3):
        for box_c in range(3):
            box = grid[box_r*3:(box_r+1)*3, box_c*3:(box_c+1)*3]
            if len(set(box.flatten())) != 9:
                return False

    return True


def count_empty(grid: np.ndarray) -> int:
    """Count empty cells."""
    return int(np.sum(grid == 0))
