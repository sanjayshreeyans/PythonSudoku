"""
Game state management: cursor, undo/redo, notes.
"""
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
from enum import Enum

from . import grid as grid_logic


class GameMode(Enum):
    PLAYING = "playing"
    WON = "won"


@dataclass
class Action:
    """Represents an undoable action."""
    row: int
    col: int
    old_value: int
    new_value: int
    old_notes: frozenset[int]
    new_notes: frozenset[int]


@dataclass
class GameState:
    """Complete game state."""

    # Grid state
    initial_grid: np.ndarray
    current_grid: np.ndarray
    solution: np.ndarray

    # Cursor
    cursor_row: int = 4
    cursor_col: int = 4

    # Notes (pencil marks)
    notes: dict[tuple[int, int], set[int]] = field(default_factory=dict)

    # Undo/redo stacks
    undo_stack: list[Action] = field(default_factory=list)
    redo_stack: list[Action] = field(default_factory=list)

    # Game meta
    mode: GameMode = GameMode.PLAYING
    difficulty: str = "medium"

    # UI state
    show_conflicts: bool = True
    notes_mode: bool = False
    message: Optional[str] = None
    message_style: str = "status"

    @classmethod
    def new_game(cls, difficulty: str = "medium") -> "GameState":
        """Create a new game state."""
        puzzle, solution = grid_logic.generate_puzzle(difficulty)
        return cls(
            initial_grid=puzzle.copy(),
            current_grid=puzzle.copy(),
            solution=solution,
            difficulty=difficulty,
        )

    def is_fixed(self, row: int, col: int) -> bool:
        """Check if a cell is part of the initial puzzle."""
        return self.initial_grid[row, col] != 0

    def can_edit(self, row: int, col: int) -> bool:
        """Check if a cell can be edited."""
        return not self.is_fixed(row, col) and self.mode == GameMode.PLAYING

    def get_value(self, row: int, col: int) -> int:
        """Get current value at cell."""
        return int(self.current_grid[row, col])

    def get_notes(self, row: int, col: int) -> set[int]:
        """Get notes for a cell."""
        return self.notes.get((row, col), set())

    def set_value(self, row: int, col: int, value: int) -> bool:
        """Set a cell value. Returns True if successful."""
        if not self.can_edit(row, col):
            return False

        old_value = int(self.current_grid[row, col])
        old_notes = frozenset(self.get_notes(row, col))

        if old_value == value:
            return False

        action = Action(
            row=row, col=col,
            old_value=old_value, new_value=value,
            old_notes=old_notes, new_notes=frozenset(),
        )
        self.undo_stack.append(action)
        self.redo_stack.clear()

        self.current_grid[row, col] = value

        if value != 0:
            self.notes.pop((row, col), None)

        if grid_logic.is_complete(self.current_grid):
            self.mode = GameMode.WON

        return True

    def toggle_note(self, row: int, col: int, num: int) -> bool:
        """Toggle a note/candidate for a cell."""
        if not self.can_edit(row, col):
            return False

        if self.current_grid[row, col] != 0:
            return False

        key = (row, col)
        old_notes = frozenset(self.get_notes(row, col))

        if key not in self.notes:
            self.notes[key] = set()

        if num in self.notes[key]:
            self.notes[key].remove(num)
        else:
            self.notes[key].add(num)

        new_notes = frozenset(self.notes[key])

        action = Action(
            row=row, col=col,
            old_value=0, new_value=0,
            old_notes=old_notes, new_notes=new_notes,
        )
        self.undo_stack.append(action)
        self.redo_stack.clear()

        return True

    def clear_cell(self, row: int, col: int) -> bool:
        """Clear a cell's value and notes."""
        if not self.can_edit(row, col):
            return False

        old_value = int(self.current_grid[row, col])
        old_notes = frozenset(self.get_notes(row, col))

        if old_value == 0 and not old_notes:
            return False

        action = Action(
            row=row, col=col,
            old_value=old_value, new_value=0,
            old_notes=old_notes, new_notes=frozenset(),
        )
        self.undo_stack.append(action)
        self.redo_stack.clear()

        self.current_grid[row, col] = 0
        self.notes.pop((row, col), None)

        return True

    def undo(self) -> bool:
        """Undo the last action."""
        if not self.undo_stack:
            return False

        action = self.undo_stack.pop()
        self.redo_stack.append(action)

        self.current_grid[action.row, action.col] = action.old_value
        if action.old_notes:
            self.notes[(action.row, action.col)] = set(action.old_notes)
        else:
            self.notes.pop((action.row, action.col), None)

        if self.mode == GameMode.WON:
            self.mode = GameMode.PLAYING

        return True

    def redo(self) -> bool:
        """Redo the last undone action."""
        if not self.redo_stack:
            return False

        action = self.redo_stack.pop()
        self.undo_stack.append(action)

        self.current_grid[action.row, action.col] = action.new_value
        if action.new_notes:
            self.notes[(action.row, action.col)] = set(action.new_notes)
        else:
            self.notes.pop((action.row, action.col), None)

        if grid_logic.is_complete(self.current_grid):
            self.mode = GameMode.WON

        return True

    def move_cursor(self, dr: int, dc: int) -> None:
        """Move cursor by delta, wrapping at edges."""
        self.cursor_row = (self.cursor_row + dr) % 9
        self.cursor_col = (self.cursor_col + dc) % 9

    def apply_hint(self) -> bool:
        """Apply a hint to the current cursor position."""
        r, c = self.cursor_row, self.cursor_col
        if self.current_grid[r, c] == 0 and not self.is_fixed(r, c):
            correct_value = int(self.solution[r, c])
            return self.set_value(r, c, correct_value)
        return False

    def get_conflicts(self, row: int, col: int) -> list[tuple[int, int]]:
        """Get cells that conflict with value at (row, col)."""
        return grid_logic.find_conflicts(self.current_grid, row, col)

    def remaining_count(self) -> int:
        """Count remaining empty cells."""
        return grid_logic.count_empty(self.current_grid)

    def set_message(self, msg: str, style: str = "status") -> None:
        """Set an ephemeral status message."""
        self.message = msg
        self.message_style = style

    def clear_message(self) -> None:
        """Clear the status message."""
        self.message = None
