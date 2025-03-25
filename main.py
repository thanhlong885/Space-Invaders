import pygame
import os
import random
from pygame import mixer

pygame.init()

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Load images
def load_image(name):
    try:
        return pygame.image.load(os.path.join("images", name))
    except:
        print(f"Không tìm thấy hình ảnh {name}")
        surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 0, 0), (0, 0, 50, 50), 2)
        return surface

# Load all images
icon = load_image("spaceship.png")
pygame.display.set_icon(icon)

RED_SPACE_SHIP = load_image("monster_red.png")
GREEN_SPACE_SHIP = load_image("monster_green.png")
BLUE_SPACE_SHIP = load_image("monster_blue.png")
SPACE_SHIP = load_image("spaceship.png")
RED_LASER = load_image("pixel_laser_red.png")
GREEN_LASER = load_image("pixel_laser_green.png")
BLUE_LASER = load_image("pixel_laser_blue.png")
YELLOW_LASER = load_image("pixel_laser_yellow.png")
BG = pygame.transform.scale(load_image("background.jpg"), (WIDTH, HEIGHT))

# Load sounds
mixer.music.load(os.path.join("sounds", "background.wav"))
mixer.music.play(-1)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (0 <= self.y <= height)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                explosion_sound = mixer.Sound(os.path.join("sounds", "explosion.wav"))
                explosion_sound.play()
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Buff:
    def __init__(self, x, y, buff_type):
        self.x = x
        self.y = y
        self.buff_type = buff_type
        self.img = load_image(f"{buff_type}.png")
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return self.y > height

    def collision(self, obj):
        return collide(self, obj)

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.bullet_buff = False
        self.shield_buff = False
        self.shield_img = load_image("shield.png")
        self.shield_time = 0
        self.bullet_time = 0

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs[:]:
                    if laser.collision(obj):
                        explosion_sound = mixer.Sound(os.path.join("sounds", "explosion.wav"))
                        explosion_sound.play()
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        break

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
        if self.shield_buff:
            shield_x = self.x + self.get_width()//2 - self.shield_img.get_width()//2
            shield_y = self.y - self.shield_img.get_height() - 15
            window.blit(self.shield_img, (shield_x, shield_y))

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (
            self.x,
            self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width(),
            10
        ))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x,
            self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * (self.health / self.max_health),
            10
        ))

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(
                self.x + self.get_width()//2 - self.laser_img.get_width()//2,
                self.y - self.laser_img.get_height(),
                self.laser_img
            )
            self.lasers.append(laser)
            if self.bullet_buff:
                laser2 = Laser(
                    self.x + self.get_width()//2 - self.laser_img.get_width()//2 + 20,
                    self.y - self.laser_img.get_height(),
                    self.laser_img
                )
                self.lasers.append(laser2)
            self.cool_down_counter = 1
            bullet_sound = mixer.Sound(os.path.join("sounds", "laser.wav"))
            bullet_sound.play()

    def apply_buff(self, buff):
        if buff.buff_type == "bullet":
            self.bullet_buff = True
            self.COOLDOWN = 15
            self.bullet_time = 180
        elif buff.buff_type == "shield":
            self.shield_buff = True
            self.shield_time = 180
        elif buff.buff_type == "healing":
            self.health = min(self.max_health, self.health + 30)

    def update(self):
        if self.shield_time > 0:
            self.shield_time -= 1
            if self.shield_time == 0:
                self.shield_buff = False
        
        if self.bullet_time > 0:
            self.bullet_time -= 1
            if self.bullet_time == 0:
                self.bullet_buff = False
                self.COOLDOWN = 30

class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(
                self.x + self.get_width()//2 - self.laser_img.get_width()//2,
                self.y + self.get_height(),
                self.laser_img
            )
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def move_lasers(self, vel, player):
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                if player.shield_buff:
                    shield_rect = pygame.Rect(
                        player.x + player.get_width()//2 - player.shield_img.get_width()//2,
                        player.y - player.shield_img.get_height()//2,
                        player.shield_img.get_width(),
                        player.shield_img.get_height()
                    )
                    if shield_rect.collidepoint(laser.x + laser.img.get_width()//2, 
                                              laser.y + laser.img.get_height()//2):
                        explosion_sound = mixer.Sound(os.path.join("sounds", "explosion.wav"))
                        explosion_sound.play()
                        self.lasers.remove(laser)
                        continue
                
                if laser.collision(player):
                    explosion_sound = mixer.Sound(os.path.join("sounds", "explosion.wav"))
                    explosion_sound.play()
                    player.health -= 10
                    self.lasers.remove(laser)

def collide(obj1, obj2):
    if not hasattr(obj1, 'mask') or not hasattr(obj2, 'mask'):
        return False
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    buffs = []
    wave_length = 5
    enemy_vel = 1
    player_vel = 5
    laser_vel = 5
    buff_vel = 2

    player = Player(300, 630)
    clock = pygame.time.Clock()
    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)
        for buff in buffs:
            buff.draw(WIN)
        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for _ in range(wave_length):
                enemy = Enemy(
                    random.randrange(50, WIDTH-100),
                    random.randrange(-1500, -100),
                    random.choice(["red", "blue", "green"])
                )
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        if random.randrange(0, 2*60) == 1:
            buff = Buff(
                random.randrange(50, WIDTH-100),
                random.randrange(-500, -50),
                random.choice(["bullet", "shield", "healing"])
            )
            buffs.append(buff)

        for buff in buffs[:]:
            buff.move(buff_vel)
            if buff.off_screen(HEIGHT):
                buffs.remove(buff)
            elif buff.collision(player):
                player.apply_buff(buff)
                buffs.remove(buff)

        player.move_lasers(-laser_vel, enemies)
        player.update()

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Mouse click to beign...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()