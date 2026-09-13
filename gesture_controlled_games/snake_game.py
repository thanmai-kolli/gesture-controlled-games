import pygame
import random
from gesture_controller import detect_gesture

pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture Snake")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 40)

MENU, PLAYING, PAUSED, GAME_OVER = "MENU", "PLAYING", "PAUSED", "GAME_OVER"
state = MENU

def reset_game():
    global snake, snake_x, snake_y, vx, vy, food, score
    snake = [(300, 200)]
    snake_x, snake_y = 300, 200
    vx, vy = 4, 0
    food = (random.randrange(40, WIDTH-40, 20), random.randrange(40, HEIGHT-40, 20))
    score = 0

reset_game()

def draw_text(txt, f, c, x, y):
    screen.blit(f.render(txt, True, c), (x, y))

running = True
while running:
    screen.fill((30, 30, 40))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    gesture = detect_gesture()

    # ===== MENU =====
    if state == MENU:
        draw_text("GESTURE SNAKE", big_font, (0,255,0), 160, 130)
        draw_text("OPEN → Start", font, (255,255,255), 220, 200)
        if gesture == "OPEN":
            reset_game()
            state = PLAYING

    # ===== PLAYING =====
    elif state == PLAYING:
        if gesture == "LEFT":   vx, vy = -4, 0
        elif gesture == "RIGHT":vx, vy = 4, 0
        elif gesture == "OPEN": vx, vy = 0, -4
        elif gesture == "FIST": vx, vy = 0, 4

        snake_x += vx
        snake_y += vy
        snake.insert(0, (snake_x, snake_y))

        # Wall collision
        if snake_x < 0 or snake_x > WIDTH-20 or snake_y < 0 or snake_y > HEIGHT-20:
            state = GAME_OVER

        # Self collision
        if snake[0] in snake[1:]:
            state = GAME_OVER

        if abs(snake_x - food[0]) < 15 and abs(snake_y - food[1]) < 15:
            food = (random.randrange(40, WIDTH-40, 20), random.randrange(40, HEIGHT-40, 20))
            score += 1
        else:
            snake.pop()

        for s in snake:
            pygame.draw.rect(screen, (0,200,0), (*s,20,20))
        pygame.draw.rect(screen, (200,50,50), (*food,20,20))

        draw_text(f"Score: {score}", font, (255,255,255), 10, 10)

    # ===== GAME OVER =====
    elif state == GAME_OVER:
        draw_text("GAME OVER", big_font, (255,0,0), 200, 140)
        draw_text(f"Score: {score}", font, (255,255,255), 240, 190)
        draw_text("OPEN → Restart", font, (255,255,255), 210, 230)
        draw_text("FIST → Quit", font, (255,255,255), 230, 260)

        if gesture == "OPEN":
            reset_game()
            state = PLAYING
        elif gesture == "FIST":
            running = False

    pygame.display.update()
    clock.tick(300)

pygame.quit()
