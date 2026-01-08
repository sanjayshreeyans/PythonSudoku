"""
Centralized color and style definitions.
Claude Code-inspired: muted, professional, dark theme with clear visual hierarchy.
"""
from rich.style import Style

# Base palette - Claude Code inspired
COLORS = {
    # Backgrounds
    "bg_primary": "#0d1117",
    "bg_cell": "#161b22",
    "bg_cursor": "#1f6feb",
    "bg_cursor_dim": "#21262d",
    "bg_box_alt": "#0d1117",

    # Text
    "text_fixed": "#58a6ff",       # Blue - given numbers (prominent)
    "text_user": "#e6edf3",        # Bright white - user input
    "text_notes": "#484f58",       # Dim - pencil marks
    "text_muted": "#30363d",
    "text_secondary": "#8b949e",

    # Accents
    "cursor_ring": "#58a6ff",
    "error": "#f85149",
    "error_bg": "#3d1f20",
    "success": "#3fb950",
    "warning": "#d29922",

    # Grid
    "grid_light": "#21262d",
    "grid_heavy": "#8b949e",
    "border": "#30363d",
}

# Pre-built styles
STYLES = {
    # Cell content
    "fixed": Style(color=COLORS["text_fixed"], bold=True),
    "user": Style(color=COLORS["text_user"]),
    "notes": Style(color=COLORS["text_notes"]),
    "empty": Style(color=COLORS["text_muted"]),

    # Cursor states
    "cursor": Style(
        color="#ffffff",
        bgcolor=COLORS["bg_cursor"],
        bold=True
    ),
    "cursor_fixed": Style(
        color=COLORS["text_fixed"],
        bgcolor=COLORS["bg_cursor_dim"],
        bold=True
    ),

    # Feedback
    "error": Style(color=COLORS["error"], bold=True),
    "error_cell": Style(color=COLORS["error"], bgcolor=COLORS["error_bg"]),
    "success": Style(color=COLORS["success"], bold=True),
    "warning": Style(color=COLORS["warning"]),

    # Grid lines
    "grid_light": Style(color=COLORS["grid_light"]),
    "grid_heavy": Style(color=COLORS["grid_heavy"]),

    # UI chrome
    "title": Style(color=COLORS["text_fixed"], bold=True),
    "header": Style(color=COLORS["text_secondary"]),
    "hint": Style(color=COLORS["text_muted"], italic=True),
    "status": Style(color=COLORS["text_secondary"]),
    "mode_indicator": Style(color=COLORS["warning"], bold=True),
}

# Box drawing - heavy lines for 3x3 borders, light for cells
BOX = {
    # Light (inner cell borders)
    "h_light": "─",
    "v_light": "│",

    # Heavy (3x3 box borders)
    "h_heavy": "━",
    "v_heavy": "┃",

    # Corners - heavy outer
    "tl": "┏",
    "tr": "┓",
    "bl": "┗",
    "br": "┛",

    # T-junctions
    "t_down_heavy": "┳",
    "t_up_heavy": "┻",
    "t_right_heavy": "┣",
    "t_left_heavy": "┫",

    # Cross - heavy
    "cross_heavy": "╋",

    # Mixed junctions (heavy outer, light inner)
    "t_down_mixed": "┯",
    "t_up_mixed": "┷",
    "t_right_mixed": "┠",
    "t_left_mixed": "┨",
    "cross_light": "┼",

    # Heavy-light junctions
    "cross_h_heavy": "╂",  # horizontal heavy
}

# Layout
LAYOUT = {
    "cell_width": 3,
}
