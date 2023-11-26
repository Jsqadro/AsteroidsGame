import sys
import pygame
import random
import math

pygame.init()

# Constants
WIDTH, HEIGHT = 1920, 1080
FPS = 60
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
SPAWN_INTERVAL = 3000
last_ufo_destroyed_time = 0
BONUS_RESPAWN_INTERVAL = 10000
last_gun_upgrade_time = 0
upgrade_duration = 1000
gun_upgraded = False
last_bonus_collected_time = 0


class Level:
    EASY = 0
    MEDIUM = 1
    HARD = 2


LEVELS = [
    {"asteroid_speed": 3, "asteroid_spawn_interval": 3000, "asteroid_image": "asteroid_level1.png"},
    {"asteroid_speed": 6, "asteroid_spawn_interval": 2000, "asteroid_image": "asteroid_level2.png"},
    {"asteroid_speed": 9, "asteroid_spawn_interval": 500, "asteroid_image": "asteroid_level3.png"},
]

current_level = Level.EASY

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")

PLAYER_IMAGE = pygame.transform.scale(pygame.image.load("spaceship.png"), (50, 50))
ENEMY_IMAGE = pygame.image.load("enemy.png")

SHOT_SOUND = pygame.mixer.Sound("shot.mp3")
EXPLOSION_SOUND = pygame.mixer.Sound("explosion.mp3")
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)


class GameObject(pygame.sprite.Sprite):
    def __init__(self, image, size=None):
        super().__init__()
        self.image = pygame.transform.scale(image, size) if size else image
        self.rect = self.image.get_rect()


class Player(GameObject):
    def __init__(self):
        super().__init__(PLAYER_IMAGE)
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.angle = 0
        self.acceleration = 0.04
        self.deceleration = 0.02
        self.speed = 0
        self.max_speed = 5
        self.invulnerable_until = 0

    def update(self):
        if 0 < self.invulnerable_until < pygame.time.get_ticks():
            self.invulnerable_until = 0

        keys = pygame.key.get_pressed()
        self.angle += 2 if keys[pygame.K_RIGHT] else -2 if keys[pygame.K_LEFT] else 0
        self.angle %= 360

        self.image = pygame.transform.rotate(PLAYER_IMAGE, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        if keys[pygame.K_UP]:
            self.speed += self.acceleration
            self.speed = min(self.speed, self.max_speed)
        else:
            self.speed -= self.deceleration
            self.speed = max(self.speed, 0)

        radian_angle = math.radians(self.angle)
        self.rect.x += self.speed * math.cos(radian_angle)
        self.rect.y += self.speed * math.sin(radian_angle)

        self.handle_screen_wrap()

    def handle_screen_wrap(self):
        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif self.rect.top > HEIGHT:
            self.rect.bottom = 0

    def upgrade_gun(self):
        global gun_upgraded
        if not gun_upgraded:
            gun_upgraded = True
            self.shoot_sound = pygame.mixer.Sound("upgraded_shoot.mp3")
            global last_gun_upgrade_time
            last_gun_upgrade_time = pygame.time.get_ticks()


class Asteroid(GameObject):
    def __init__(self, size, image_path):
        super().__init__(pygame.image.load(image_path), (size, size))
        self.speed = random.randint(1, 3)
        self.angle = random.randint(0, 360)
        self.set_initial_position()

    def set_initial_position(self):
        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            self.rect.x, self.rect.y = 0, random.randint(0, HEIGHT)
        elif side == "right":
            self.rect.x, self.rect.y = WIDTH, random.randint(0, HEIGHT)
        elif side == "top":
            self.rect.x, self.rect.y = random.randint(0, WIDTH), 0
        elif side == "bottom":
            self.rect.x, self.rect.y = random.randint(0, WIDTH), HEIGHT

    def update(self):
        radian_angle = math.radians(self.angle)
        self.rect.x += self.speed * math.cos(radian_angle)
        self.rect.y += self.speed * math.sin(radian_angle)
        self.handle_screen_wrap()
        self.speed = 1 + score / 10000
        self.handle_screen_wrap()

    def handle_screen_wrap(self):
        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif self.rect.top > HEIGHT:
            self.rect.bottom = 0

    def split(self):
        if self.rect.width > 25:
            new_sizes = [self.rect.width // 2, self.rect.width // 2]
            for new_size in new_sizes:
                new_asteroid = Asteroid(new_size, LEVELS[current_level]["asteroid_image"])
                new_asteroid.rect.center = self.rect.center
                all_sprites.add(new_asteroid)
                asteroids.add(new_asteroid)


class AsteroidSpawner:
    def __init__(self):
        self.last_spawn_time = pygame.time.get_ticks()

    def spawn_asteroid(self, asteroid_speed, asteroid_spawn_interval):
        current_time = pygame.time.get_ticks()
        interval = max(asteroid_spawn_interval - score // 500, 500) + 100  # Вычесть для увеличения спавна
        if current_time - self.last_spawn_time > interval:
            asteroid_size = random.randint(20, 50)
            asteroid = Asteroid(asteroid_size, LEVELS[current_level]["asteroid_image"])
            all_sprites.add(asteroid)
            asteroids.add(asteroid)
            self.last_spawn_time = current_time


class Bullet(GameObject):
    def __init__(self, x, y, angle):
        super().__init__(pygame.Surface((5, 5)))
        self.image.fill(WHITE)
        self.rect.center = (x, y)
        self.angle = math.radians(angle)
        self.speed = 15
        self.distance_travelled = 0

    def update(self):
        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)
        self.distance_travelled += self.speed
        self.handle_screen_wrap()

        if self.distance_travelled > 1000:
            self.kill()

    def handle_screen_wrap(self):
        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif self.rect.top > HEIGHT:
            self.rect.bottom = 0


class Score:
    def __init__(self, player_name, score=0):
        self.player_name = player_name
        self.score = int(score)


class UFO(GameObject):
    def __init__(self):
        super().__init__(ENEMY_IMAGE, size=(50, 50))

        edge = random.choice(["left", "right", "top", "bottom"])
        if edge == "left":
            self.rect.x = 0
            self.rect.y = random.randint(0, HEIGHT)
        elif edge == "right":
            self.rect.x = WIDTH
            self.rect.y = random.randint(0, HEIGHT)
        elif edge == "top":
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = 0
        elif edge == "bottom":
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = HEIGHT
        self.speed = 2
        self.angle = random.randint(0, 360)
        self.is_dead = False
        self.last_attack_time = pygame.time.get_ticks()

    def update(self):
        radian_angle = math.radians(self.angle)
        self.rect.x += self.speed * math.cos(radian_angle)
        self.rect.y += self.speed * math.sin(radian_angle)
        self.handle_screen_wrap()

    def handle_screen_wrap(self):
        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif self.rect.top > HEIGHT:
            self.rect.bottom = 0

    def attack_player(self, player):
        current_time = pygame.time.get_ticks()
        if not self.is_dead and current_time - self.last_attack_time > 1000:
            angle_to_player = math.atan2(player.rect.centery - self.rect.centery,
                                         player.rect.centerx - self.rect.centerx)
            angle_to_player_degrees = math.degrees(angle_to_player)

            spawn_offset = 30
            spawn_x = self.rect.centerx + spawn_offset * math.cos(angle_to_player)
            spawn_y = self.rect.centery + spawn_offset * math.sin(angle_to_player)

            bullet = EnemyBullet(spawn_x, spawn_y, angle_to_player_degrees)
            all_sprites.add(bullet)
            bullets.add(bullet)

            self.last_attack_time = current_time

    def take_damage(self):
        global last_ufo_destroyed_time
        if not self.is_dead:
            self.is_dead = True
            self.kill()
            last_ufo_destroyed_time = pygame.time.get_ticks()


class EnemyBullet(GameObject):
    def __init__(self, x, y, angle):
        super().__init__(pygame.Surface((5, 5)))
        self.image.fill(WHITE)
        self.rect.center = (x, y)
        self.angle = math.radians(angle)
        self.speed = 10
        self.distance_travelled = 0

    def update(self):
        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)
        self.distance_travelled += self.speed
        self.handle_screen_wrap()

        if self.distance_travelled > 1500:
            self.kill()

    def handle_screen_wrap(self):
        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif self.rect.top > HEIGHT:
            self.rect.bottom = 0


class LifeBonus(GameObject):
    def __init__(self):
        super().__init__(pygame.image.load("life_bonus.png"), size=(55, 55))
        self.respawn_bonus()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.respawn_time > BONUS_RESPAWN_INTERVAL:
            self.respawn_bonus()

        self.handle_screen_wrap()

    def respawn_bonus(self):
        self.rect.x = random.randint(0, WIDTH)
        self.rect.y = random.randint(0, HEIGHT)
        self.respawn_time = pygame.time.get_ticks()

    def handle_screen_wrap(self):
        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif self.rect.top > HEIGHT:
            self.rect.bottom = 0

    def handle_screen_wrap(self):
        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif self.rect.top > HEIGHT:
            self.rect.bottom = 0


class GunUpgradeBonus(GameObject):
    def __init__(self):
        super().__init__(pygame.image.load("gun_upgrade_bonus.png"), size=(55, 55))
        self.respawn_bonus()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.respawn_time > BONUS_RESPAWN_INTERVAL:
            self.respawn_bonus()

        self.handle_screen_wrap()

    def respawn_bonus(self):
        self.rect.x = random.randint(0, WIDTH)
        self.rect.y = random.randint(0, HEIGHT)
        self.respawn_time = pygame.time.get_ticks()  # Set the respawn time

    def handle_screen_wrap(self):
        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif self.rect.top > HEIGHT:
            self.rect.bottom = 0


def show_level_selection():
    global current_level
    screen.fill(BLACK)
    font = pygame.font.Font(None, 150)
    title_text = font.render("Select Level", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))

    level_text = font.render("Press 1, 2, or 3 to select level", True, WHITE)
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    current_level = int(event.unicode) - 1
                    waiting_for_key = False


def show_end_screen():
    global score

    screen.fill(BLACK)
    font = pygame.font.Font(None, 150)
    game_over_text = font.render("Game Over", True, WHITE)
    score_text = font.render("Score: {}".format(score), True, WHITE)
    retry_text = font.render("Press ESC to close", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2 + 100))
    pygame.display.flip()

    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    waiting_for_key = False

    player_name = input_name()
    high_scores = load_high_scores()
    high_scores.append(Score(player_name, score))
    high_scores.sort(key=lambda s: s.score, reverse=True)
    save_high_scores(high_scores)

    show_high_scores(high_scores)


def input_name(score):
    font = pygame.font.Font(None, 100)
    score_text = font.render(f"Score: {score}", True, WHITE)
    input_text = font.render("Enter your name:", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, HEIGHT // 2 + 100))
    pygame.display.flip()

    input_active = True
    input_string = ""
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_string = input_string[:-1]
                else:
                    input_string += event.unicode

        input_render = font.render(input_string, True, WHITE)
        screen.blit(input_render, (WIDTH // 2 - 150, HEIGHT // 2 + 200))
        pygame.display.flip()

    return input_string


def load_high_scores():
    try:
        with open("high_scores.txt", "r") as file:
            lines = file.readlines()
            high_scores = [Score(*line.strip().split(":")) for line in lines]
            for score in high_scores:
                score.score = int(score.score)
    except FileNotFoundError:
        high_scores = []
    return high_scores


def save_high_scores(high_scores):
    with open("high_scores.txt", "w") as file:
        for score in high_scores:
            file.write(f"{score.player_name}:{score.score}\n")


def show_high_scores(high_scores):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 100)
    title_text = font.render("High Scores", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    y_position = 200
    for i, score in enumerate(high_scores, start=1):
        score_text = font.render(f"{i}. {score.player_name}: {score.score}", True, WHITE)
        x_position = WIDTH // 2 - score_text.get_width() // 2
        for char in score_text.get_text():
            char_render = font.render(char, True, WHITE)
            screen.blit(char_render, (x_position, y_position))
            x_position += char_render.get_width() + 5  # Adjust the spacing here
        y_position += 70

    pygame.display.flip()

    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    waiting_for_key = False


def show_start_screen():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 150)
    title_text = font.render("Asteroids Game", True, WHITE)
    start_text = font.render("Press SPACE to start", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    waiting_for_key = True
    while waiting_for_key:
        for EVENT in pygame.event.get():
            if EVENT.type == pygame.QUIT:
                pygame.quit()
                quit()
            if EVENT.type == pygame.KEYUP and EVENT.key == pygame.K_SPACE:
                waiting_for_key = False


def display_level(level):
    font = pygame.font.Font(None, 36)
    level_text = font.render("Level: {}".format(level + 1), True, WHITE)
    screen.blit(level_text, (10, HEIGHT - 40))


def show_leaderboard():
    global score
    screen.fill(BLACK)
    font_title = pygame.font.Font(None, 150)
    font_text = pygame.font.Font(None, 50)

    title_text = font_title.render("Leaderboard", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    high_scores = load_high_scores()

    y_position = 200
    for i, score_entry in enumerate(high_scores[:10], start=1):
        score_text = font_text.render(f"{i}. {score_entry.player_name}: {score_entry.score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, y_position))
        y_position += 70

    input_string = input_name(score)

    if input_string:
        high_scores.append(Score(input_string, score))
        high_scores.sort(key=lambda s: s.score, reverse=True)
        save_high_scores(high_scores)

    pygame.display.flip()

    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    waiting_for_key = False



show_level_selection()
show_start_screen()

all_sprites = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

life_bonus = LifeBonus()
all_sprites.add(life_bonus)

gun_upgrade_bonus = GunUpgradeBonus()
all_sprites.add(gun_upgrade_bonus)


score, lives = 0, 3
font = pygame.font.Font(None, 100)
clock = pygame.time.Clock()

for _ in range(15):
    asteroid_size = random.randint(20, 50)
    asteroid = Asteroid(asteroid_size, LEVELS[current_level]["asteroid_image"])
    all_sprites.add(asteroid)
    asteroids.add(asteroid)

ufo = UFO()
all_sprites.add(ufo)
clock = pygame.time.Clock()

running = True
last_shot_time = pygame.time.get_ticks()
last_spawn_time = pygame.time.get_ticks()

paused = False
asteroid_spawner = AsteroidSpawner()

while running:
    current_time = pygame.time.get_ticks()
    asteroid_spawner.spawn_asteroid(LEVELS[current_level]["asteroid_speed"],
                                    LEVELS[current_level]["asteroid_spawn_interval"])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not paused:
                    if current_time - last_shot_time > 10:
                        bullet = Bullet(player.rect.centerx, player.rect.centery, player.angle)
                        all_sprites.add(bullet)
                        bullets.add(bullet)
                        last_shot_time = current_time
                        SHOT_SOUND.play()
                else:
                    paused = False
            elif event.key == pygame.K_ESCAPE:
                paused = not paused

    if not paused:
        player.update()
        ufo.update()
        life_bonus.update()

        if not ufo.is_dead:
            ufo.attack_player(player)
        else:
            if current_time - last_ufo_destroyed_time > 10000 and ufo.is_dead:
                ufo = UFO()
                all_sprites.add(ufo)
                last_ufo_destroyed_time = 0

        for asteroid in asteroids:
            asteroid.update()
            if not pygame.sprite.spritecollide(asteroid, asteroids, False, pygame.sprite.collide_rect):
                all_sprites.add(asteroid)

        if current_time - last_spawn_time > SPAWN_INTERVAL:
            asteroid_size = random.randint(20, 50)
            asteroid = Asteroid(asteroid_size, LEVELS[current_level]["asteroid_image"])
            all_sprites.add(asteroid)
            asteroids.add(asteroid)
            last_spawn_time = current_time

        all_sprites.update()

        ufo_hits = pygame.sprite.spritecollide(ufo, bullets, False)
        for bullet in ufo_hits:
            bullet.kill()
            ufo.kill()
            last_ufo_destroyed_time = current_time
            ufo.is_dead = True
            score += 300

        hits = pygame.sprite.groupcollide(bullets, asteroids, True, False)
        for bullet, asteroid_list in hits.items():
            for asteroid in asteroid_list:
                asteroid.split()
                asteroid.kill()
                EXPLOSION_SOUND.play()
                score += 100

        hits = pygame.sprite.spritecollide(player, asteroids, False)
        if player.invulnerable_until == 0 and hits:
            lives -= 1
            if lives <= 0:
                running = False
            else:
                player.rect.center = (WIDTH // 2, HEIGHT // 2)
                player.invulnerable_until = current_time + 3000

        hits = pygame.sprite.spritecollide(player, bullets, False)
        if player.invulnerable_until == 0 and hits:
            lives -= 0.5
            if lives <= 0:
                running = False
            else:
                player.rect.center = (WIDTH // 2, HEIGHT // 2)
                player.invulnerable_until = current_time + 3000

        bonus_hit = pygame.sprite.spritecollide(player, [life_bonus], False)
        if bonus_hit:
            life_bonus.rect.x = WIDTH + 1000
            life_bonus.rect.y = HEIGHT + 1000
            lives += 1
            last_bonus_collected_time = current_time

        gun_upgrade_bonus_hit = pygame.sprite.spritecollide(player, [gun_upgrade_bonus], False)
        if gun_upgrade_bonus_hit:
            gun_upgrade_bonus.rect.x = WIDTH + 1000
            gun_upgrade_bonus.rect.y = HEIGHT + 1000
            player.upgrade_gun()
            gun_upgraded = True

        if gun_upgraded and current_time - last_gun_upgrade_time < upgrade_duration:
            if not paused and current_time - last_shot_time > 1:
                bullet1 = Bullet(player.rect.centerx, player.rect.centery, player.angle)
                bullet2 = Bullet(player.rect.centerx, player.rect.centery, player.angle + 15)
                bullet3 = Bullet(player.rect.centerx, player.rect.centery, player.angle - 15)

                all_sprites.add(bullet1, bullet2, bullet3)
                bullets.add(bullet1, bullet2, bullet3)

                last_shot_time = current_time
                SHOT_SOUND.play()

        if current_time - last_gun_upgrade_time >= upgrade_duration:
            gun_upgraded = False

        screen.fill(BLACK)
        all_sprites.draw(screen)
        display_level(current_level)

        score_text = font.render("Score: {}".format(score), True, WHITE)
        screen.blit(score_text, (10, 10))

        lives_text = font.render("Lives: {}".format(lives), True, WHITE)
        screen.blit(lives_text, (WIDTH - 300, 10))


    else:
        font_pause = pygame.font.Font(None, 150)
        pause_text = font_pause.render("Paused", True, WHITE)
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(FPS)
    if lives <= 0:
        running = False
        show_leaderboard()

pygame.mixer.music.stop()
pygame.quit()
