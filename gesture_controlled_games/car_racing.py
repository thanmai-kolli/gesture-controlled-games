import pygame
from gesture_controller import detect_gesture

pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture Car Racing")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 22)
big_font = pygame.font.SysFont("arial", 36)

MENU, PLAYING, GAME_OVER = "MENU", "PLAYING", "GAME_OVER"
state = MENU

def reset_game():
    global car_x, speed
    car_x = 275
    speed = 4

reset_game()

running = True
while running:
    screen.fill((40,40,40))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    gesture = detect_gesture()

    # ===== MENU =====
    if state == MENU:
        screen.blit(big_font.render("CAR RACING", True, (255,200,0)), (190,140))
        screen.blit(font.render("OPEN → Start", True, (255,255,255)), (235,200))
        if gesture == "OPEN":
            reset_game()
            state = PLAYING

    # ===== PLAYING =====
    elif state == PLAYING:
        if gesture == "LEFT": car_x -= speed
        elif gesture == "RIGHT": car_x += speed
        elif gesture == "OPEN": speed = min(10, speed + 0.2)

        # Road
        pygame.draw.rect(screen, (60,60,60), (50,0,WIDTH-100,HEIGHT))

        # Collision with road
        if car_x < 50 or car_x > WIDTH-100:
            state = GAME_OVER

        pygame.draw.rect(screen, (0,120,255), (car_x,300,50,80))
        screen.blit(font.render(f"Speed: {int(speed)}", True, (255,255,255)), (10,10))

    # ===== GAME OVER =====
    elif state == GAME_OVER:
        screen.blit(big_font.render("GAME OVER", True, (255,0,0)), (190,140))
        screen.blit(font.render("OPEN → Restart", True, (255,255,255)), (215,220))
        screen.blit(font.render("FIST → Quit", True, (255,255,255)), (235,250))

        if gesture == "OPEN":
            reset_game()
            state = PLAYING
        elif gesture == "FIST":
            running = False

    pygame.display.update()
    clock.tick(30)

pygame.quit()
