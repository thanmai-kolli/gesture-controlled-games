"""Gesture-controlled car racing: steer with hand position, open palm to accelerate."""
from types import SimpleNamespace

import pygame

import config
import ui

WIDTH, HEIGHT = config.WIDTH, config.HEIGHT
GAME_KEY = "car_racing"

MENU, PLAYING, GAME_OVER = "MENU", "PLAYING", "GAME_OVER"

CAR_W, CAR_H = 50, 80
CAR_Y = int(HEIGHT * 0.75)
ROAD_MARGIN = 100
ROAD_RECT = pygame.Rect(ROAD_MARGIN, 0, WIDTH - 2 * ROAD_MARGIN, HEIGHT)
BASE_SPEED = 120      # px/s
MAX_SPEED = 300       # px/s
ACCELERATION = 180    # px/s^2

LEGEND = [
    "Hand Left/Right: steer",
    "Open Palm: accelerate",
    "Esc: back to menu",
]


def run(screen, clock, gesture_ctrl):
    """Runs Car Racing until the player backs out ("MENU") or quits ("QUIT")."""
    fonts = ui.init_fonts()
    background = ui.make_vertical_gradient((WIDTH, HEIGHT), config.BG_GRADIENT_TOP, config.BG_GRADIENT_BOTTOM)

    state = MENU
    st = SimpleNamespace()

    def reset():
        st.car_x = float(WIDTH // 2 - CAR_W // 2)
        st.speed = float(BASE_SPEED)
        st.score = 0.0

    reset()

    while True:
        dt = min(clock.tick(config.FPS) / 1000.0, config.MAX_DT)
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "MENU"

        gesture = gesture_ctrl.read()

        if state == MENU:
            best = ui.get_highscore(GAME_KEY)
            ui.draw_center_message(screen, fonts, "CAR RACING",
                                    [f"Best Distance: {best}", "Open Palm to Start"])
            if gesture == "OPEN":
                reset()
                state = PLAYING

        elif state == PLAYING:
            if gesture == "LEFT":
                st.car_x -= st.speed * dt
            elif gesture == "RIGHT":
                st.car_x += st.speed * dt
            elif gesture == "OPEN":
                st.speed = min(MAX_SPEED, st.speed + ACCELERATION * dt)

            pygame.draw.rect(screen, (60, 60, 60), ROAD_RECT)
            for third in (1, 2):
                lane_x = ROAD_RECT.left + ROAD_RECT.width * third // 3
                pygame.draw.line(screen, (90, 90, 90), (lane_x, 0), (lane_x, HEIGHT), 2)

            car_rect = pygame.Rect(int(st.car_x), CAR_Y, CAR_W, CAR_H)

            if car_rect.left < ROAD_RECT.left or car_rect.right > ROAD_RECT.right:
                state = GAME_OVER
                ui.update_highscore(GAME_KEY, int(st.score))
            else:
                st.score += st.speed * dt

            pygame.draw.rect(screen, config.PRIMARY, car_rect, border_radius=6)
            ui.draw_text(screen, f"Speed: {int(st.speed)}", fonts["medium"], config.WHITE, (16, 16))
            ui.draw_text(screen, f"Distance: {int(st.score)}", fonts["medium"], config.WHITE, (16, 46))

        elif state == GAME_OVER:
            best = ui.get_highscore(GAME_KEY)
            ui.draw_center_message(screen, fonts, "GAME OVER",
                                    [f"Distance: {int(st.score)}   Best: {best}",
                                     "Open Palm: Restart    Fist: Menu"])
            if gesture == "OPEN":
                reset()
                state = PLAYING
            elif gesture == "FIST":
                return "MENU"

        ui.draw_hud(screen, fonts, gesture_ctrl, gesture, LEGEND)
        pygame.display.update()


if __name__ == "__main__":
    from gesture_controller import GestureController

    pygame.init()
    pygame.display.set_caption("Gesture Car Racing")
    _screen = pygame.display.set_mode((WIDTH, HEIGHT))
    _clock = pygame.time.Clock()
    _gesture_ctrl = GestureController()
    try:
        run(_screen, _clock, _gesture_ctrl)
    finally:
        _gesture_ctrl.release()
        pygame.quit()

