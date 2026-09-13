"""Shared constants and visual theme for the Gesture Controlled Game Suite.

Every module (hub + games + UI kit) imports from here so the whole suite
shares one window size, one color palette and one set of gesture/camera
settings instead of redefining them per file.
"""

# --- Display -----------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
CAPTION = "Gesture Controlled Game Suite"

# --- Camera / gesture recognition --------------------------------------
CAMERA_INDEX = 0
LEFT_THRESHOLD = 0.40
RIGHT_THRESHOLD = 0.60
GESTURE_SMOOTHING = 8           # frames averaged (majority vote) to de-jitter
PREVIEW_SIZE = (160, 120)       # camera thumbnail drawn in the HUD

# --- Shared timing (seconds) --------------------------------------------
MENU_NAV_COOLDOWN = 0.3         # min time between gesture-driven menu moves
FIST_QUIT_HOLD = 1.0            # continuous seconds of FIST needed to quit the hub
MAX_DT = 0.05                   # clamp so a slow frame (model load, OS hiccup) can't spike physics/timers

# --- Palette -------------------------------------------------------------
BG_DARK = (18, 18, 24)
BG_GRADIENT_TOP = (26, 27, 38)
BG_GRADIENT_BOTTOM = (12, 12, 18)
BG_PANEL = (32, 32, 42)
PANEL_BORDER = (70, 70, 85)
PRIMARY = (0, 200, 255)
ACCENT = (0, 230, 120)
DANGER = (255, 70, 70)
WARNING = (255, 200, 0)
WHITE = (235, 235, 240)
GRAY = (150, 150, 160)
BLACK = (0, 0, 0)

GESTURE_COLORS = {
    "NONE": GRAY,
    "LEFT": PRIMARY,
    "RIGHT": PRIMARY,
    "OPEN": ACCENT,
    "FIST": DANGER,
}

# --- Fonts ---------------------------------------------------------------
FONT_NAME = "arial"

# --- Persistence ---------------------------------------------------------
SCORES_FILE = "highscores.json"
