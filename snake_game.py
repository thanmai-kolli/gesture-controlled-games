"""Gesture-controlled Snake: steer with hand position, open palm/fist for up/down."""
import random
from types import SimpleNamespace

import pygame

import config
import ui

WIDTH, HEIGHT = config.WIDTH, config.HEIGHT
CELL = 20
BASE_MOVE_INTERVAL = 0.12  # seconds between grid steps at the start
MIN_MOVE_INTERVAL = 0.06   # fastest the snake will ever move, how ever high the score
GOLDEN_FOOD_CHANCE = 0.2
GOLDEN_FOOD_VALUE = 3
GAME_KEY = "snake"

MENU, PLAYING, PAUSED, GAME_OVER = "MENU", "PLAYING", "PAUSED", "GAME_OVER"

LEGEND = [
    "Hand Left/Right: steer sideways",
    "Open Palm: move up   Fist: move down",
    "P: pause   Esc: back to menu",
]


def _spawn_food():
    pos = (
        random.randrange(40, WIDTH - 40, CELL),
        random.randrange(40, HEIGHT - 40, CELL),
    )
    golden = random.random() < GOLDEN_FOOD_CHANCE
    return pos, golden


def run(screen, clock, gesture_ctrl):
    """Runs Snake until the player backs out ("MENU") or closes the window ("QUIT")."""
    fonts = ui.init_fonts()
    background = ui.make_vertical_gradient((WIDTH, HEIGHT), config.BG_GRADIENT_TOP, config.BG_GRADIENT_BOTTOM)

    state = MENU
    st = SimpleNamespace()

    def reset():
        st.snake_x, st.snake_y = (WIDTH // 2) // CELL * CELL, (HEIGHT // 2) // CELL * CELL
        st.snake = [(st.snake_x, st.snake_y)]
        st.vx, st.vy = 1, 0
        st.food, st.food_golden = _spawn_food()
        st.score = 0
        st.move_timer = 0.0
        st.move_interval = BASE_MOVE_INTERVAL

    reset()

    while True:
        dt = min(clock.tick(config.FPS) / 1000.0, config.MAX_DT)
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                if event.key == pygame.K_p and state in (PLAYING, PAUSED):
                    state = PAUSED if state == PLAYING else PLAYING

        gesture = gesture_ctrl.read()

        if state == MENU:
            best = ui.get_highscore(GAME_KEY)
            ui.draw_center_message(screen, fonts, "GESTURE SNAKE",
                                    [f"Best Score: {best}", "Open Palm to Start"])
            if gesture == "OPEN":
                reset()
                state = PLAYING

        elif state == PLAYING:
            if gesture == "LEFT":
                st.vx, st.vy = -1, 0
            elif gesture == "RIGHT":
                st.vx, st.vy = 1, 0
            elif gesture == "OPEN":
                st.vx, st.vy = 0, -1
            elif gesture == "FIST":
                st.vx, st.vy = 0, 1

            st.move_timer += dt
            if st.move_timer >= st.move_interval:
                st.move_timer -= st.move_interval

                st.snake_x += st.vx * CELL
                st.snake_y += st.vy * CELL
                st.snake.insert(0, (st.snake_x, st.snake_y))

                hit_wall = (st.snake_x < 0 or st.snake_x > WIDTH - CELL
                            or st.snake_y < 0 or st.snake_y > HEIGHT - CELL)
                hit_self = st.snake[0] in st.snake[1:]
                if hit_wall or hit_self:
                    state = GAME_OVER
                    ui.update_highscore(GAME_KEY, st.score)
                elif st.snake[0] == st.food:
                    st.score += GOLDEN_FOOD_VALUE if st.food_golden else 1
                    st.food, st.food_golden = _spawn_food()
                    st.move_interval = max(MIN_MOVE_INTERVAL, BASE_MOVE_INTERVAL - st.score * 0.004)
                else:
                    st.snake.pop()

            for segment in st.snake:
                pygame.draw.rect(screen, config.ACCENT, (*segment, CELL, CELL), border_radius=4)
            food_color = config.WARNING if st.food_golden else config.DANGER
            pygame.draw.rect(screen, food_color, (*st.food, CELL, CELL), border_radius=4)
            ui.draw_text(screen, f"Score: {st.score}", fonts["medium"], config.WHITE, (16, 16))

        elif state == PAUSED:
            for segment in st.snake:
                pygame.draw.rect(screen, config.ACCENT, (*segment, CELL, CELL), border_radius=4)
            food_color = config.WARNING if st.food_golden else config.DANGER
            pygame.draw.rect(screen, food_color, (*st.food, CELL, CELL), border_radius=4)
            ui.draw_center_message(screen, fonts, "PAUSED", ["Press P to resume"])

        elif state == GAME_OVER:
            best = ui.get_highscore(GAME_KEY)
            ui.draw_center_message(screen, fonts, "GAME OVER",
                                    [f"Score: {st.score}   Best: {best}",
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
    pygame.display.set_caption("Gesture Snake")
    _screen = pygame.display.set_mode((WIDTH, HEIGHT))
    _clock = pygame.time.Clock()
    _gesture_ctrl = GestureController()
    try:
        run(_screen, _clock, _gesture_ctrl)
    finally:
        _gesture_ctrl.release()
        pygame.quit()

