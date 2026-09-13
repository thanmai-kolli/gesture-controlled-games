"""Reusable UI toolkit shared by the hub and every game.

Keeping all drawing primitives (fonts, panels, buttons, HUD, overlays,
high-score persistence) in one place means the menu and the three games
all look and behave consistently instead of re-implementing their own
text/box drawing code.
"""
import json
import os

import pygame

import config


def init_fonts():
    """Creates the shared font set. Must be called after pygame.init()."""
    return {
        "small": pygame.font.SysFont(config.FONT_NAME, 18),
        "medium": pygame.font.SysFont(config.FONT_NAME, 24),
        "large": pygame.font.SysFont(config.FONT_NAME, 36),
        "huge": pygame.font.SysFont(config.FONT_NAME, 56),
    }


def make_vertical_gradient(size, top_color, bottom_color):
    """Pre-renders a vertical gradient once so it can be cheaply blit'd every frame."""
    surface = pygame.Surface(size)
    height = max(size[1] - 1, 1)
    for y in range(size[1]):
        t = y / height
        color = tuple(int(top_color[i] + (bottom_color[i] - top_color[i]) * t) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (size[0], y))
    return surface


# --------------------------------------------------------------------------
# Primitives
# --------------------------------------------------------------------------

def draw_text(surface, text, font, color, pos, center=False, shadow=True):
    """Renders text with an optional drop shadow for readability over gameplay."""
    if shadow:
        shadow_surf = font.render(text, True, config.BLACK)
        shadow_rect = shadow_surf.get_rect()
        if center:
            shadow_rect.center = (pos[0] + 2, pos[1] + 2)
        else:
            shadow_rect.topleft = (pos[0] + 2, pos[1] + 2)
        surface.blit(shadow_surf, shadow_rect)

    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    if center:
        text_rect.center = pos
    else:
        text_rect.topleft = pos
    surface.blit(text_surf, text_rect)
    return text_rect


def draw_panel(surface, rect, color=config.BG_PANEL, border_color=config.PANEL_BORDER,
               radius=14, border_width=2):
    """Rounded card/panel background used by menus, HUD widgets and buttons."""
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_color and border_width:
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=radius)
    return rect


class Button:
    """A clickable/hoverable rounded rect with a label."""

    def __init__(self, rect, text, base_color=config.BG_PANEL, accent_color=config.PRIMARY,
                 text_color=config.WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.base_color = base_color
        self.accent_color = accent_color
        self.text_color = text_color

    def draw(self, surface, font, hovered=None):
        if hovered is None:
            hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        draw_panel(surface, self.rect, self.base_color,
                   self.accent_color if hovered else config.PANEL_BORDER,
                   radius=10, border_width=3 if hovered else 2)
        draw_text(surface, self.text, font, self.text_color, self.rect.center, center=True)
        return hovered

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# --------------------------------------------------------------------------
# Gesture / camera HUD
# --------------------------------------------------------------------------

def draw_camera_preview(surface, fonts, gesture_ctrl, topright):
    """Small bordered thumbnail of the live webcam feed (or a fallback notice)."""
    w, h = config.PREVIEW_SIZE
    rect = pygame.Rect(0, 0, w + 8, h + 8)
    rect.topright = topright
    draw_panel(surface, rect, config.BG_PANEL, config.PANEL_BORDER, radius=8)

    preview = gesture_ctrl.get_preview_surface(config.PREVIEW_SIZE)
    inner = pygame.Rect(rect.x + 4, rect.y + 4, w, h)
    if preview is not None:
        surface.blit(preview, inner.topleft)
    else:
        pygame.draw.rect(surface, config.BLACK, inner)
        msg = "No Camera" if not gesture_ctrl.camera_available else "..."
        draw_text(surface, msg, fonts["small"], config.GRAY, inner.center, center=True, shadow=False)
        draw_text(surface, "(keyboard active)", fonts["small"], config.GRAY,
                   (inner.centerx, inner.centery + 18), center=True, shadow=False)
    return rect


def draw_gesture_badge(surface, fonts, gesture, topright):
    """Colour-coded label showing the gesture currently recognised."""
    color = config.GESTURE_COLORS.get(gesture, config.GRAY)
    label = f"Gesture: {gesture}"
    text_surf = fonts["medium"].render(label, True, color)
    text_rect = text_surf.get_rect()
    padding_x, padding_y = 12, 6
    badge_rect = pygame.Rect(0, 0, text_rect.width + padding_x * 2, text_rect.height + padding_y * 2)
    badge_rect.topright = topright
    draw_panel(surface, badge_rect, config.BG_PANEL, color, radius=8, border_width=2)
    text_rect.center = badge_rect.center
    surface.blit(text_surf, text_rect)
    return badge_rect


def draw_legend(surface, fonts, lines, bottomleft):
    """Small always-visible reminder of what each gesture/key does."""
    padding = 10
    line_height = fonts["small"].get_height() + 4
    width = max(fonts["small"].size(line)[0] for line in lines) + padding * 2
    height = line_height * len(lines) + padding
    rect = pygame.Rect(0, 0, width, height)
    rect.bottomleft = bottomleft
    draw_panel(surface, rect, config.BG_PANEL, config.PANEL_BORDER, radius=8)
    for i, line in enumerate(lines):
        draw_text(surface, line, fonts["small"], config.GRAY,
                   (rect.x + padding, rect.y + padding // 2 + i * line_height), shadow=False)
    return rect


def draw_hud(surface, fonts, gesture_ctrl, gesture, legend_lines=None):
    """Standard top-right camera+gesture HUD, plus an optional bottom-left legend."""
    margin = 16
    preview_rect = draw_camera_preview(surface, fonts, gesture_ctrl, (config.WIDTH - margin, margin))
    badge_rect = draw_gesture_badge(surface, fonts, gesture, (config.WIDTH - margin, preview_rect.bottom + 8))
    if legend_lines:
        draw_legend(surface, fonts, legend_lines, (margin, config.HEIGHT - margin))
    return badge_rect


# --------------------------------------------------------------------------
# Modal overlays (menu / paused / game over share this look)
# --------------------------------------------------------------------------

def draw_overlay(surface, alpha=170):
    """Dims the frame behind a modal message."""
    overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    surface.blit(overlay, (0, 0))


def draw_center_message(surface, fonts, title, lines=(), title_color=config.WHITE, dim=True):
    """Centered modal title + supporting lines, used for menu/pause/game-over screens."""
    if dim:
        draw_overlay(surface)
    center_x = config.WIDTH // 2
    draw_text(surface, title, fonts["huge"], title_color, (center_x, config.HEIGHT // 2 - 90), center=True)
    for i, line in enumerate(lines):
        draw_text(surface, line, fonts["medium"], config.WHITE,
                   (center_x, config.HEIGHT // 2 - 10 + i * 34), center=True)


# --------------------------------------------------------------------------
# High-score persistence (small local JSON file, best-effort)
# --------------------------------------------------------------------------

def _scores_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), config.SCORES_FILE)


def load_highscores():
    path = _scores_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def get_highscore(game_key):
    return load_highscores().get(game_key, 0)


def update_highscore(game_key, score):
    """Persists `score` if it beats the stored best. Returns (best_score, is_new_record)."""
    scores = load_highscores()
    best = scores.get(game_key, 0)
    if score > best:
        scores[game_key] = score
        try:
            with open(_scores_path(), "w", encoding="utf-8") as f:
                json.dump(scores, f, indent=2)
        except OSError:
            pass
        return score, True
    return best, False
