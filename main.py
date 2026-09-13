"""Graphical hub for the Gesture Controlled Game Suite.

Replaces the old text-console menu with a single pygame window: pick a game
with the mouse, arrow keys, or hand gestures, play it, then land back here
instead of the whole program exiting after one round.
"""
import pygame

import car_racing
import config
import snake_game
import subway_runner
import ui
from gesture_controller import GestureController

GAMES = [
    {"key": "snake", "name": "Snake", "subtitle": "Classic snake, steered by hand",
     "module": snake_game, "color": config.ACCENT},
    {"key": "subway_runner", "name": "Subway Runner", "subtitle": "Dodge obstacles, jump lanes",
     "module": subway_runner, "color": config.PRIMARY},
    {"key": "car_racing", "name": "Car Racing", "subtitle": "Stay on the road, speed up",
     "module": car_racing, "color": config.WARNING},
]

MENU_LEGEND = [
    "Hand Left/Right or Arrow Keys: choose a game",
    "Open Palm or Enter: play    Hold Fist or Esc: quit",
    "Mouse click also works",
]

CARD_W, CARD_H = 220, 260
CARD_GAP = 30


def _card_rects():
    total_width = len(GAMES) * CARD_W + (len(GAMES) - 1) * CARD_GAP
    start_x = (config.WIDTH - total_width) // 2
    y = config.HEIGHT // 2 - CARD_H // 2 + 10
    return [pygame.Rect(start_x + i * (CARD_W + CARD_GAP), y, CARD_W, CARD_H) for i in range(len(GAMES))]


def _draw_menu(screen, fonts, background, gesture_ctrl, gesture, selected, card_rects, quit_button, fist_hold):
    screen.blit(background, (0, 0))
    ui.draw_text(screen, "GESTURE GAME SUITE", fonts["large"], config.WHITE,
                 (config.WIDTH // 2, 70), center=True)
    ui.draw_text(screen, "Pick a game to play", fonts["medium"], config.GRAY,
                 (config.WIDTH // 2, 110), center=True, shadow=False)

    mouse_pos = pygame.mouse.get_pos()
    for i, (game, rect) in enumerate(zip(GAMES, card_rects)):
        is_selected = i == selected
        hovered = rect.collidepoint(mouse_pos)
        border = game["color"] if (is_selected or hovered) else config.PANEL_BORDER
        ui.draw_panel(screen, rect, config.BG_PANEL, border, radius=16,
                       border_width=4 if is_selected else 2)

        bar_rect = pygame.Rect(rect.x, rect.y, rect.width, 8)
        pygame.draw.rect(screen, game["color"], bar_rect,
                          border_top_left_radius=16, border_top_right_radius=16)

        ui.draw_text(screen, game["name"], fonts["medium"], config.WHITE,
                     (rect.centerx, rect.y + 50), center=True)
        ui.draw_text(screen, game["subtitle"], fonts["small"], config.GRAY,
                     (rect.centerx, rect.y + 90), center=True, shadow=False)
        best = ui.get_highscore(game["key"])
        ui.draw_text(screen, f"Best: {best}", fonts["small"], game["color"],
                     (rect.centerx, rect.y + 130), center=True, shadow=False)

        if is_selected:
            tip_y = rect.bottom + 14
            pygame.draw.polygon(screen, game["color"], [
                (rect.centerx - 10, tip_y), (rect.centerx + 10, tip_y), (rect.centerx, tip_y - 12),
            ])

    quit_button.draw(screen, fonts["small"])
    badge_rect = ui.draw_hud(screen, fonts, gesture_ctrl, gesture, MENU_LEGEND)

    if fist_hold > 0:
        progress = min(1.0, fist_hold / config.FIST_QUIT_HOLD)
        bar_rect = pygame.Rect(badge_rect.left, badge_rect.bottom + 8, badge_rect.width, 10)
        ui.draw_panel(screen, bar_rect, config.BG_PANEL, config.DANGER, radius=5, border_width=1)
        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * progress), bar_rect.height)
        pygame.draw.rect(screen, config.DANGER, fill_rect, border_radius=5)
        ui.draw_text(screen, "Hold Fist to Quit", fonts["small"], config.DANGER,
                     (bar_rect.centerx, bar_rect.bottom + 14), center=True, shadow=False)

    pygame.display.update()


def show_menu(screen, clock, fonts, background, gesture_ctrl, selected):
    """Runs the hub screen until the player picks a game (-> index) or quits (-> "QUIT")."""
    card_rects = _card_rects()
    quit_button = ui.Button((16, 16, 130, 40), "Quit (Esc)", accent_color=config.DANGER)
    gesture_cooldown = 0.0
    fist_hold = 0.0

    while True:
        dt = min(clock.tick(config.FPS) / 1000.0, config.MAX_DT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "QUIT"
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    selected = (selected - 1) % len(GAMES)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected = (selected + 1) % len(GAMES)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return selected
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if quit_button.clicked(event):
                    return "QUIT"
                for i, rect in enumerate(card_rects):
                    if rect.collidepoint(event.pos):
                        return i

        gesture = gesture_ctrl.read()
        gesture_cooldown = max(0.0, gesture_cooldown - dt)

        fist_hold = fist_hold + dt if gesture == "FIST" else 0.0
        if fist_hold >= config.FIST_QUIT_HOLD:
            return "QUIT"

        if gesture_cooldown > 0:
            pass
        elif gesture == "LEFT":
            selected = (selected - 1) % len(GAMES)
            gesture_cooldown = config.MENU_NAV_COOLDOWN
        elif gesture == "RIGHT":
            selected = (selected + 1) % len(GAMES)
            gesture_cooldown = config.MENU_NAV_COOLDOWN
        elif gesture == "OPEN":
            return selected

        _draw_menu(screen, fonts, background, gesture_ctrl, gesture, selected, card_rects, quit_button, fist_hold)


def main():
    pygame.init()
    pygame.display.set_caption(config.CAPTION)
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    clock = pygame.time.Clock()
    fonts = ui.init_fonts()
    background = ui.make_vertical_gradient((config.WIDTH, config.HEIGHT),
                                            config.BG_GRADIENT_TOP, config.BG_GRADIENT_BOTTOM)

    gesture_ctrl = GestureController()
    if not gesture_ctrl.camera_available:
        print("No webcam detected - arrow keys / space / down work as gesture stand-ins.")

    selected = 0
    try:
        while True:
            choice = show_menu(screen, clock, fonts, background, gesture_ctrl, selected)
            if choice == "QUIT":
                break

            selected = choice
            result = GAMES[selected]["module"].run(screen, clock, gesture_ctrl)
            if result == "QUIT":
                break
    finally:
        gesture_ctrl.release()
        pygame.quit()


if __name__ == "__main__":
    main()
