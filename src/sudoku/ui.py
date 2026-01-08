"""
UI rendering using Rich.
Claude Code-inspired: clean, minimal, clear visual hierarchy.
Heavy box borders for 3x3 regions, light lines for cells.
"""
from rich.console import Console, Group
from rich.text import Text
from rich.align import Align

from .theme import COLORS, STYLES, BOX
from .state import GameState, GameMode


class Renderer:
    """Handles all terminal rendering."""

    def __init__(self):
        self.console = Console(
            force_terminal=True,
            color_system="truecolor",
        )

    def clear(self) -> None:
        """Clear the terminal."""
        self.console.clear()

    def render_cell(self, state: GameState, row: int, col: int) -> Text:
        """Render a single cell's content (3 chars wide)."""
        value = state.get_value(row, col)
        notes = state.get_notes(row, col)
        is_cursor = (row == state.cursor_row and col == state.cursor_col)
        is_fixed = state.is_fixed(row, col)

        # Check conflicts
        has_conflict = False
        if state.show_conflicts and value != 0:
            conflicts = state.get_conflicts(row, col)
            has_conflict = len(conflicts) > 0

        # Determine style
        if is_cursor:
            if is_fixed:
                style = STYLES["cursor_fixed"]
            else:
                style = STYLES["cursor"]
        elif has_conflict:
            style = STYLES["error_cell"]
        elif is_fixed:
            style = STYLES["fixed"]
        elif value != 0:
            style = STYLES["user"]
        else:
            style = STYLES["empty"]

        # Content
        if value != 0:
            content = f" {value} "
        elif is_cursor:
            content = " _ "
        elif notes:
            # Show up to 3 notes
            note_str = "".join(str(n) for n in sorted(notes)[:3])
            content = note_str.center(3)
            if not is_cursor:
                style = STYLES["notes"]
        else:
            content = "   "

        return Text(content, style=style)

    def build_grid(self, state: GameState) -> Text:
        """
        Build the complete Sudoku grid.
        Uses heavy lines for 3x3 box borders, light lines for cell borders.
        """
        result = Text()

        # Characters
        h_heavy = BOX["h_heavy"]
        h_light = BOX["h_light"]
        v_heavy = BOX["v_heavy"]
        v_light = BOX["v_light"]

        cell_w = 3

        # Top border (heavy)
        result.append("  ")  # Left margin
        result.append(BOX["tl"], style=STYLES["grid_heavy"])
        for box in range(3):
            for cell in range(3):
                result.append(h_heavy * cell_w, style=STYLES["grid_heavy"])
                if cell < 2:
                    result.append(BOX["t_down_mixed"], style=STYLES["grid_heavy"])
            if box < 2:
                result.append(BOX["t_down_heavy"], style=STYLES["grid_heavy"])
        result.append(BOX["tr"], style=STYLES["grid_heavy"])
        result.append("\n")

        for row in range(9):
            # Row content
            result.append("  ")  # Left margin
            result.append(v_heavy, style=STYLES["grid_heavy"])

            for col in range(9):
                cell = self.render_cell(state, row, col)
                result.append_text(cell)

                # Vertical separator
                if col < 8:
                    if (col + 1) % 3 == 0:
                        result.append(v_heavy, style=STYLES["grid_heavy"])
                    else:
                        result.append(v_light, style=STYLES["grid_light"])

            result.append(v_heavy, style=STYLES["grid_heavy"])
            result.append("\n")

            # Horizontal separator after row
            if row < 8:
                result.append("  ")  # Left margin
                if (row + 1) % 3 == 0:
                    # Heavy separator between boxes
                    result.append(BOX["t_right_heavy"], style=STYLES["grid_heavy"])
                    for box in range(3):
                        for cell in range(3):
                            result.append(h_heavy * cell_w, style=STYLES["grid_heavy"])
                            if cell < 2:
                                result.append(BOX["cross_h_heavy"], style=STYLES["grid_heavy"])
                        if box < 2:
                            result.append(BOX["cross_heavy"], style=STYLES["grid_heavy"])
                    result.append(BOX["t_left_heavy"], style=STYLES["grid_heavy"])
                else:
                    # Light separator within box
                    result.append(BOX["t_right_mixed"], style=STYLES["grid_heavy"])
                    for box in range(3):
                        for cell in range(3):
                            result.append(h_light * cell_w, style=STYLES["grid_light"])
                            if cell < 2:
                                result.append(BOX["cross_light"], style=STYLES["grid_light"])
                        if box < 2:
                            result.append(BOX["cross_h_heavy"], style=STYLES["grid_heavy"])
                    result.append(BOX["t_left_mixed"], style=STYLES["grid_heavy"])
                result.append("\n")

        # Bottom border (heavy)
        result.append("  ")  # Left margin
        result.append(BOX["bl"], style=STYLES["grid_heavy"])
        for box in range(3):
            for cell in range(3):
                result.append(h_heavy * cell_w, style=STYLES["grid_heavy"])
                if cell < 2:
                    result.append(BOX["t_up_mixed"], style=STYLES["grid_heavy"])
            if box < 2:
                result.append(BOX["t_up_heavy"], style=STYLES["grid_heavy"])
        result.append(BOX["br"], style=STYLES["grid_heavy"])

        return result

    def build_status(self, state: GameState) -> Text:
        """Build the status line."""
        result = Text()

        # Difficulty
        result.append(state.difficulty.upper(), style=STYLES["header"])

        result.append("    ", style=STYLES["grid_light"])

        # Remaining
        remaining = state.remaining_count()
        result.append(f"{remaining} ", style=STYLES["status"])
        result.append("remaining", style=STYLES["hint"])

        # Notes mode
        if state.notes_mode:
            result.append("    ", style=STYLES["grid_light"])
            result.append("NOTES", style=STYLES["mode_indicator"])

        # Win state
        if state.mode == GameMode.WON:
            result.append("    ", style=STYLES["grid_light"])
            result.append("COMPLETE", style=STYLES["success"])

        return result

    def build_help(self) -> Text:
        """Build help line."""
        result = Text()
        hints = [
            ("hjkl", "move"),
            ("1-9", "set"),
            ("0/x", "clear"),
            ("n", "notes"),
            ("u/r", "undo"),
            ("?", "hint"),
            ("q", "quit"),
        ]

        for i, (key, desc) in enumerate(hints):
            if i > 0:
                result.append("   ")
            result.append(key, style=STYLES["header"])
            result.append(" ", style=STYLES["grid_light"])
            result.append(desc, style=STYLES["hint"])

        return result

    def build_message(self, state: GameState) -> Text:
        """Build message line."""
        if not state.message:
            return Text("")

        style = STYLES.get(state.message_style, STYLES["status"])
        return Text(state.message, style=style)

    def render(self, state: GameState) -> None:
        """Render the complete UI."""
        self.console.clear()

        elements = []

        # Title
        elements.append(Align.center(Text("")))
        elements.append(Align.center(Text("SUDOKU", style=STYLES["title"])))
        elements.append(Align.center(Text("")))

        # Status
        elements.append(Align.center(self.build_status(state)))
        elements.append(Align.center(Text("")))

        # Grid
        elements.append(Align.center(self.build_grid(state)))
        elements.append(Align.center(Text("")))

        # Message
        msg = self.build_message(state)
        if msg.plain:
            elements.append(Align.center(msg))
        else:
            elements.append(Align.center(Text(" ")))

        # Help
        elements.append(Align.center(Text("")))
        elements.append(Align.center(self.build_help()))

        ui = Group(*elements)
        self.console.print(ui)
