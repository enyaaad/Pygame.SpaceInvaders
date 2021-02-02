import pygame
import os
import sys
import random
pygame.font.init()

mainClock = pygame.time.Clock()
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT),)
pygame.display.set_caption("Space Invaders")
fullscreen = False

# Загружаем спрайты
background = pygame.transform.scale(pygame.image.load(os.path.join("assets", "dgames.png")), (WIDTH, HEIGHT))
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Инициализирую переменные
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    # Отрисовка лазера
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    # Движение лазера
    def move(self, vel):
        self.y += vel

    # Случай,если выйдет за экран
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    # Случай столкновения
    def collision(self, obj):
        return collide(self, obj)

# Класс кораблей
class Ship:
    COOLDOWN = 30

    # Инициализирую переменные
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    # Отрисовка лазера противников
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    # попадание лазеров
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    # механика стрельбы игрокв
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    # Инициализирую переменные
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    # движение лазера игрока + попадание в  цели
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    # здоровье
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    # размеры шкалы
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

# соотношу цвета кораблей с цветами лазера
class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    # Инициализирую переменные
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    # движение вражеский кораблей
    def move(self, vel):
        self.y += vel

    # стрельба
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
# столкновение
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))

        lives_label = main_font.render(f"Жизней: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Уровень: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("Проиграл", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        pygame.display.update()
        mainClock.tick(60)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
        # создание вражеский кораблей
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
        # движение
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # перемещение влево
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # перемещение вправо
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # перемещение вверх
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # перемещение вниз
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            # столкновение с игроком и выход за карту
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)
def movie():
    WIN.blit(background, (0, 0))
    pygame.display.update()
    mainClock.tick(60)
    pygame.time.wait(5000)
    main_menu()

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    click = False
    run = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True
    while run:
        WIN.blit(BG, (0, 0))
        mx, my = pygame.mouse.get_pos()

        title_label = title_font.render("Space Invaders", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        button_2 = pygame.Rect(280, 100, 200, 50)
        button_3 = pygame.Rect(270, 500, 200, 50)
        pygame.draw.rect(WIN, (105, 105, 105), button_2)
        pygame.draw.rect(WIN, (105, 105, 105), button_3)
        title_label = title_font.render("Play", 1, (255,255,255))
        WIN.blit(title_label, (295, 100))
        title_label = title_font.render("Exit", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2 -1, 503))

        pygame.display.update()
        if button_2.collidepoint((mx, my)):
            if click:
                main()
                click = False
        if button_3.collidepoint((mx, my)):
            if click:
                pygame.quit()
                sys.exit()
                click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

    pygame.display.update()
    mainClock.tick(60)

    pygame.quit()



movie()

