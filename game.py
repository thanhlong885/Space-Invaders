import pygame
from pygame import mixer
import random
import math

pygame.init()
screen = pygame.display.set_mode((800, 800))

# Change title
pygame.display.set_caption("Space Invaders")

# Change icon
icon = pygame.image.load("spaceship.png")
pygame.display.set_icon(icon)

# Background
background = pygame.image.load("galaxy_background.jpg")
mixer.music.load("background.wav")
mixer.music.play(-1)  # play forever mode

# Player
playerImg = pygame.image.load("spaceship.png")
player_x = 370
player_y = 480
player_x_change = 0
player_y_change = 0

# Enemy
enemyImg = []
enemy_x = []
enemy_y = []
enemy_x_change = []
enemy_y_change = []
num_enemies = 6

for i in range(num_enemies):
    enemyImg.append(pygame.image.load("alien.png"))
    enemy_x.append(random.randint(0, 735))
    enemy_y.append(random.randint(50, 150))
    enemy_x_change.append(0.2)
    enemy_y_change.append(40)

# Bullet
bulletImg = pygame.image.load("bullet.png")
bullet_x = 0
bullet_y = player_y
bullet_x_change = 0
bullet_y_change = 1
bullet_state = "ready"  # can fire

# Score and Lives
score_value = 0
lives = 5

# Font
font = pygame.font.Font("freesansbold.ttf", 32)
text_x = 10
text_y = 10

over_font = pygame.font.Font("freesansbold.ttf", 128)


def show_score(x, y):
    score = font.render(f"Score: {score_value}", True, (255, 255, 255))
    screen.blit(score, (x, y))

    lives_label = font.render(f"Lives: {lives}", True, (255, 255, 255))
    screen.blit(lives_label, (800 - lives_label.get_width() - 10, 10))


def game_over():
    over_text = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(over_text, (300, 350))


def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def fire_bullet(x, y):
    global bullet_x, bullet_y, bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))


def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    distance = math.sqrt(
        math.pow(enemy_x - bullet_x, 2) + math.pow(enemy_y - bullet_y, 2)
    )
    return distance < 27


def move_bullet(bullet_y, bullet_state):
    """Di chuyển đạn và cập nhật trạng thái nếu đạn ra khỏi màn hình"""
    if bullet_y <= 0:
        bullet_y = player_y
        bullet_state = "ready"

    if bullet_state == "fire":
        fire_bullet(bullet_x, bullet_y)
        bullet_y -= bullet_y_change

    return bullet_y, bullet_state


def move_player(player_x, player_y, player_x_change, player_y_change):
    player_x += player_x_change
    if player_x <= 0:
        player_x = 0
    elif player_x >= 736:
        player_x = 736

    player_y += player_y_change
    if player_y <= 0:
        player_y = 0
    elif player_y >= 736:
        player_y = 736

    return player_x, player_y


def main():
    global player_x, player_y, score_value, bullet_state, bullet_y, bullet_x, player_x_change, player_y_change, lives
    running = True
    while running:
        # change background
        screen.fill((0, 0, 0))
        # Background
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # check keystroke
            if event.type == pygame.KEYDOWN:  # when pressed
                if event.key == pygame.K_LEFT:
                    player_x_change -= 0.5
                if event.key == pygame.K_RIGHT:
                    player_x_change += 0.5
                if event.key == pygame.K_UP:
                    player_y_change -= 0.5
                if event.key == pygame.K_DOWN:
                    player_y_change += 0.5
                if event.key == pygame.K_SPACE:
                    if bullet_state == "ready":
                        # can oly fire when state is ready
                        bullet_sound = mixer.Sound("laser.wav")
                        bullet_sound.play()
                        bullet_x = player_x
                        bullet_y = player_y
                        fire_bullet(bullet_x, bullet_y)
            
            if event.type == pygame.KEYUP:  # when remove
                if (
                    event.key == pygame.K_LEFT
                    or event.key == pygame.K_RIGHT
                    or event.key == pygame.K_UP
                    or event.key == pygame.K_DOWN
                ):
                    player_x_change = 0
                    player_y_change = 0
        
        # Player movement
        player_x, player_y = move_player(
            player_x, player_y, player_x_change, player_y_change
        )

        # Enemy movement
        lives_decremented = False  # Track lives decrementation per frame

        for i in range(num_enemies):
            if enemy_y[i] > 800:
                if not lives_decremented:
                    lives -= 1
                    lives_decremented = True

                # Respawn enemy
                enemy_x[i] = random.randint(0, 735)
                enemy_y[i] = random.randint(50, 150)

                if lives <= 0:
                    game_over()
                    pygame.display.update()
                    pygame.time.delay(2000)  # Pause for game over screen
                    running = False
                    break

            enemy_x[i] += enemy_x_change[i]
            if enemy_x[i] <= 0:
                enemy_x_change[i] = 0.2
                enemy_y[i] += enemy_y_change[i]
            elif enemy_x[i] >= 736:
                enemy_x_change[i] = -0.2
                enemy_y[i] += enemy_y_change[i]

            collision = is_collision(enemy_x[i], enemy_y[i], bullet_x, bullet_y)
            if collision:
                explosion_sound = mixer.Sound("explosion.wav")
                explosion_sound.play()
                bullet_state = "ready"
                bullet_y = player_y
                score_value += 1

                # Respawn enemy at random position
                enemy_x[i] = random.randint(0, 735)
                enemy_y[i] = random.randint(50, 150)

            enemy(enemy_x[i], enemy_y[i], i)

        # Bullet movement
        bullet_y, bullet_state = move_bullet(bullet_y, bullet_state)

        player(player_x, player_y)
        show_score(text_x, text_y)

        pygame.display.update()


if __name__ == "__main__":
    main()
