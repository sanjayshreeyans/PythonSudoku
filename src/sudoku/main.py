#!/usr/bin/env python3
"""
Terminal Sudoku - Claude Code inspired UI
Entry point and main game loop.
"""
import sys
import signal

from .state import GameState, GameMode
from .ui import Renderer
from .input import InputHandler, Key, key_to_number


def handle_input(state: GameState, key: Key) -> None:
    """Process a key input."""
    state.clear_message()

    # Navigation
    if key == Key.UP:
        state.move_cursor(-1, 0)
    elif key == Key.DOWN:
        state.move_cursor(1, 0)
    elif key == Key.LEFT:
        state.move_cursor(0, -1)
    elif key == Key.RIGHT:
        state.move_cursor(0, 1)

    # Number input
    elif key in (Key.NUM_1, Key.NUM_2, Key.NUM_3, Key.NUM_4,
                 Key.NUM_5, Key.NUM_6, Key.NUM_7, Key.NUM_8, Key.NUM_9):
        num = key_to_number(key)
        if num is not None:
            row, col = state.cursor_row, state.cursor_col
            if state.is_fixed(row, col):
                state.set_message("Fixed cell", "warning")
            elif state.notes_mode:
                state.toggle_note(row, col, num)
            else:
                state.set_value(row, col, num)

    # Clear cell
    elif key in (Key.NUM_0, Key.BACKSPACE, Key.DELETE):
        row, col = state.cursor_row, state.cursor_col
        if state.is_fixed(row, col):
            state.set_message("Fixed cell", "warning")
        else:
            state.clear_cell(row, col)

    # Toggle notes mode
    elif key == Key.NOTES_TOGGLE:
        state.notes_mode = not state.notes_mode
        mode_str = "on" if state.notes_mode else "off"
        state.set_message(f"Notes {mode_str}", "status")

    # Undo
    elif key == Key.UNDO:
        if state.undo():
            state.set_message("Undo", "status")
        else:
            state.set_message("Nothing to undo", "hint")

    # Redo
    elif key == Key.REDO:
        if state.redo():
            state.set_message("Redo", "status")
        else:
            state.set_message("Nothing to redo", "hint")

    # Hint
    elif key == Key.HINT:
        if state.apply_hint():
            state.set_message("Hint applied", "success")
        else:
            state.set_message("Move to empty cell", "hint")


def game_loop(state: GameState, renderer: Renderer) -> str:
    """Main game loop. Returns: 'quit', 'new_game', or 'won'."""
    with InputHandler() as input_handler:
        renderer.render(state)

        while True:
            event = input_handler.read_key()

            if event.key == Key.QUIT:
                return "quit"

            if event.key == Key.NEW_GAME:
                return "new_game"

            handle_input(state, event.key)

            if state.mode == GameMode.WON:
                renderer.render(state)
                input_handler.read_key()
                return "won"

            renderer.render(state)


def cleanup_terminal() -> None:
    """Restore terminal state."""
    sys.stdout.write("\033[?25h")   # Show cursor
    sys.stdout.write("\033[0m")     # Reset colors
    sys.stdout.write("\033[2J")     # Clear screen
    sys.stdout.write("\033[H")      # Home cursor
    sys.stdout.flush()


def main() -> None:
    """Entry point."""
    def signal_handler(sig, frame):
        cleanup_terminal()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    renderer = Renderer()
    difficulty = "medium"

    try:
        while True:
            state = GameState.new_game(difficulty)
            result = game_loop(state, renderer)

            if result == "quit":
                break
            elif result in ("new_game", "won"):
                continue
    finally:
        cleanup_terminal()
        print("Thanks for playing.")


if __name__ == "__main__":
    main()
