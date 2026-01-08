"""
Keyboard input handling.
Blocking input - no timeout flicker.
"""
import sys
import tty
import termios
from dataclasses import dataclass
from typing import Optional
from enum import Enum, auto


class Key(Enum):
    """Recognized key inputs."""
    # Navigation
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    # Numbers
    NUM_1 = auto()
    NUM_2 = auto()
    NUM_3 = auto()
    NUM_4 = auto()
    NUM_5 = auto()
    NUM_6 = auto()
    NUM_7 = auto()
    NUM_8 = auto()
    NUM_9 = auto()
    NUM_0 = auto()

    # Actions
    BACKSPACE = auto()
    DELETE = auto()
    SPACE = auto()
    ENTER = auto()

    # Commands
    UNDO = auto()          # u
    REDO = auto()          # r
    HINT = auto()          # ?
    NOTES_TOGGLE = auto()  # n
    NEW_GAME = auto()      # N (shift+n)
    QUIT = auto()          # q

    # Unknown
    UNKNOWN = auto()


@dataclass
class InputEvent:
    """Represents a keyboard input event."""
    key: Key
    raw: str


def key_to_number(key: Key) -> Optional[int]:
    """Convert a number key to its integer value."""
    mapping = {
        Key.NUM_0: 0,
        Key.NUM_1: 1,
        Key.NUM_2: 2,
        Key.NUM_3: 3,
        Key.NUM_4: 4,
        Key.NUM_5: 5,
        Key.NUM_6: 6,
        Key.NUM_7: 7,
        Key.NUM_8: 8,
        Key.NUM_9: 9,
    }
    return mapping.get(key)


class InputHandler:
    """
    Handles keyboard input in raw terminal mode.
    Context manager for proper terminal restoration.
    """

    def __init__(self):
        self.old_settings = None
        self.fd = sys.stdin.fileno()

    def __enter__(self):
        self.old_settings = termios.tcgetattr(self.fd)
        # Use cbreak mode instead of raw - better escape handling
        tty.setcbreak(self.fd)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_settings:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
        return False

    def read_key(self) -> InputEvent:
        """
        Read a single key (blocking).
        Properly handles escape sequences for arrow keys.
        """
        ch = sys.stdin.read(1)

        # Handle escape sequences (arrow keys, etc.)
        if ch == "\x1b":
            # Read next character
            ch2 = sys.stdin.read(1)
            if ch2 == "[":
                ch3 = sys.stdin.read(1)
                # Arrow keys
                if ch3 == "A":
                    return InputEvent(key=Key.UP, raw="\x1b[A")
                elif ch3 == "B":
                    return InputEvent(key=Key.DOWN, raw="\x1b[B")
                elif ch3 == "C":
                    return InputEvent(key=Key.RIGHT, raw="\x1b[C")
                elif ch3 == "D":
                    return InputEvent(key=Key.LEFT, raw="\x1b[D")
                # Delete key: \x1b[3~
                elif ch3 == "3":
                    ch4 = sys.stdin.read(1)
                    if ch4 == "~":
                        return InputEvent(key=Key.DELETE, raw="\x1b[3~")
            # Pure escape - ignore, not quit
            return InputEvent(key=Key.UNKNOWN, raw=ch + ch2)

        # Single character mappings
        key_map = {
            # Vim-style navigation
            "k": Key.UP,
            "j": Key.DOWN,
            "l": Key.RIGHT,
            "h": Key.LEFT,

            # WASD navigation
            "w": Key.UP,
            "s": Key.DOWN,
            "d": Key.RIGHT,
            "a": Key.LEFT,

            # Numbers
            "1": Key.NUM_1,
            "2": Key.NUM_2,
            "3": Key.NUM_3,
            "4": Key.NUM_4,
            "5": Key.NUM_5,
            "6": Key.NUM_6,
            "7": Key.NUM_7,
            "8": Key.NUM_8,
            "9": Key.NUM_9,
            "0": Key.NUM_0,

            # Actions
            "\x7f": Key.BACKSPACE,
            "\x08": Key.BACKSPACE,
            "x": Key.DELETE,
            " ": Key.SPACE,
            "\r": Key.ENTER,
            "\n": Key.ENTER,

            # Commands
            "u": Key.UNDO,
            "r": Key.REDO,
            "?": Key.HINT,
            "n": Key.NOTES_TOGGLE,
            "N": Key.NEW_GAME,
            "q": Key.QUIT,
            "\x03": Key.QUIT,  # Ctrl+C
        }

        key = key_map.get(ch, Key.UNKNOWN)
        return InputEvent(key=key, raw=ch)
