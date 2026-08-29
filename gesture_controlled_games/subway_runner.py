import pygame
import random
from gesture_controller import detect_gesture

pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture Subway Runner")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 22)
big_font = pygame.font.SysFont("arial", 36)

MENU, PLAYING, GAME_OVER = "MENU", "PLAYING", "GAME_OVER"
state = MENU

LANES = [200, 300, 400]

def reset_game():
    global lane, player_y, vy, obstacles, score
    lane = 1
    player_y = 300
    vy = 0
    obstacles = []
    score = 0

reset_game()

running = True
while running:
    screen.fill((25,25,35))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    gesture = detect_gesture()

    # ===== MENU =====
    if state == MENU:
        screen.blit(big_font.render("SUBWAY RUNNER", True, (0,200,255)), (160,140))
        screen.blit(font.render("OPEN → Start", True, (255,255,255)), (235,200))
        if gesture == "OPEN":
            reset_game()
            state = PLAYING

    # ===== PLAYING =====
    elif state == PLAYING:
        if gesture == "LEFT" and lane > 0: lane -= 1
        elif gesture == "RIGHT" and lane < 2: lane += 1
        elif gesture == "OPEN" and player_y == 300: vy = -15

        vy += 1
        player_y += vy
        if player_y >= 300:
            player_y = 300
            vy = 0

        if random.randint(0,40) == 0:
            obstacles.append([LANES[random.randint(0,2)], 0])

        for obs in obstacles:
            obs[1] += 6
            pygame.draw.rect(screen, (255,80,80), (obs[0], obs[1], 40, 40))

            # Collision check
            if obs[0] == LANES[lane] and abs(obs[1] - player_y) < 30:
                state = GAME_OVER

        pygame.draw.rect(screen, (0,255,150), (LANES[lane], player_y, 40, 40))
        score += 1

        screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10,10))

    # ===== GAME OVER =====
    elif state == GAME_OVER:
        screen.blit(big_font.render("GAME OVER", True, (255,0,0)), (190,140))
        screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (250,190))
        screen.blit(font.render("OPEN → Restart", True, (255,255,255)), (215,230))
        screen.blit(font.render("FIST → Quit", True, (255,255,255)), (235,260))

        if gesture == "OPEN":
            reset_game()
            state = PLAYING
        elif gesture == "FIST":
            running = False

    pygame.display.update()
    clock.tick(30)

pygame.quit()
