"""Gesture-controlled endless runner: switch lanes and jump over obstacles."""
import random
from types import SimpleNamespace

import pygame

import config
import ui

WIDTH, HEIGHT = config.WIDTH, config.HEIGHT
GAME_KEY = "subway_runner"

MENU, PLAYING, GAME_OVER = "MENU", "PLAYING", "GAME_OVER"

BLOCK = 40
GROUND_Y = HEIGHT - 150
LANES = [WIDTH // 2 - 160, WIDTH // 2, WIDTH // 2 + 160]
JUMP_VELOCITY = -450                # px/s
GRAVITY = 900                       # px/s^2
OBSTACLE_SPEED = 180                # px/s, ramps up with score
MAX_OBSTACLE_SPEED = 360            # px/s
SPAWN_INTERVAL_RANGE = (0.9, 1.6)   # seconds between obstacle spawns
OBSTACLE_KINDS = ("low", "high")    # low: jump over. high: duck under.

LEGEND = [
    "Hand Left/Right: change lane",
    "Open Palm: jump   Fist: duck",
    "Esc: back to menu",
]


def run(screen, clock, gesture_ctrl):
    """Runs Subway Runner until the player backs out ("MENU") or quits ("QUIT")."""
    fonts = ui.init_fonts()
    background = ui.make_vertical_gradient((WIDTH, HEIGHT), config.BG_GRADIENT_TOP, config.BG_GRADIENT_BOTTOM)

    state = MENU
    st = SimpleNamespace()

    def reset():
        st.lane = 1
        st.player_y = float(GROUND_Y)
        st.vy = 0.0
        st.ducking = False
        st.obstacles = []
        st.score = 0.0
        st.spawn_timer = random.uniform(*SPAWN_INTERVAL_RANGE)
        st.prev_gesture = "NONE"

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
            ui.draw_center_message(screen, fonts, "SUBWAY RUNNER",
                                    [f"Best Score: {best}", "Open Palm to Start"])
            if gesture == "OPEN":
                reset()
                state = PLAYING

        elif state == PLAYING:
            lane_changed = gesture != st.prev_gesture
            if gesture == "LEFT" and lane_changed and st.lane > 0:
                st.lane -= 1
            elif gesture == "RIGHT" and lane_changed and st.lane < len(LANES) - 1:
                st.lane += 1
            elif gesture == "OPEN" and st.player_y == GROUND_Y:
                st.vy = JUMP_VELOCITY
            st.ducking = gesture == "FIST"
            st.prev_gesture = gesture

            st.vy += GRAVITY * dt
            st.player_y += st.vy * dt
            if st.player_y >= GROUND_Y:
                st.player_y = float(GROUND_Y)
                st.vy = 0.0

            st.spawn_timer -= dt
            if st.spawn_timer <= 0:
                kind = random.choice(OBSTACLE_KINDS)
                st.obstacles.append([LANES[random.randint(0, len(LANES) - 1)], 0.0, kind])
                st.spawn_timer = random.uniform(*SPAWN_INTERVAL_RANGE)

            obstacle_speed = min(MAX_OBSTACLE_SPEED, OBSTACLE_SPEED + st.score * 0.15)
            crashed = False
            for obs in st.obstacles:
                obs[1] += obstacle_speed * dt
                lane_x, y, kind = obs
                if kind == "low":
                    pygame.draw.rect(screen, config.DANGER, (lane_x, int(y), BLOCK, BLOCK), border_radius=6)
                else:
                    pygame.draw.rect(screen, config.WARNING, (lane_x, int(y) - BLOCK, BLOCK, BLOCK // 2),
                                      border_radius=6)

                if lane_x == LANES[st.lane] and abs(y - GROUND_Y) < 30:
                    if kind == "low" and st.player_y >= GROUND_Y - 20:
                        crashed = True
                    elif kind == "high" and not st.ducking:
                        crashed = True
            st.obstacles[:] = [o for o in st.obstacles if o[1] < HEIGHT + BLOCK]

            st.score += dt * 30
            player_rect = (pygame.Rect(LANES[st.lane], int(st.player_y) + BLOCK // 3, BLOCK, BLOCK - BLOCK // 3)
                           if st.ducking else pygame.Rect(LANES[st.lane], int(st.player_y), BLOCK, BLOCK))
            pygame.draw.rect(screen, config.ACCENT, player_rect, border_radius=6)
            ui.draw_text(screen, f"Score: {int(st.score)}", fonts["medium"], config.WHITE, (16, 16))

            if crashed:
                state = GAME_OVER
                ui.update_highscore(GAME_KEY, int(st.score))

        elif state == GAME_OVER:
            best = ui.get_highscore(GAME_KEY)
            ui.draw_center_message(screen, fonts, "GAME OVER",
                                    [f"Score: {int(st.score)}   Best: {best}",
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
    pygame.display.set_caption("Gesture Subway Runner")
    _screen = pygame.display.set_mode((WIDTH, HEIGHT))
    _clock = pygame.time.Clock()
    _gesture_ctrl = GestureController()
    try:
        run(_screen, _clock, _gesture_ctrl)
    finally:
        _gesture_ctrl.release()
        pygame.quit()

