import pygame
import random
import os  # for upload pictures correctly

FPS = 60
WIDTH = 500
HEIGHT = 600

# color 
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# initialize all imported pygame modules
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # display 500*600
pygame.display.set_caption("SPACE GAME")
clock = pygame.time.Clock()

# upload pictures
background_img = pygame.image.load(os.path.join("img", "background.png")).convert()
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)
# rock_img = pygame.image.load(os.path.join("img", "rock.png")).convert()
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()

rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())

explore_animate = {}
explore_animate["large"] = []
explore_animate["small"] = []
explore_animate["player"] = []
for i in range(9):
    explore_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    explore_img.set_colorkey(BLACK)
    explore_animate["large"].append(pygame.transform.scale(explore_img, (75, 75)))
    explore_animate["small"].append(pygame.transform.scale(explore_img, (30, 30))) 

    player_explore_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    player_explore_img.set_colorkey(BLACK)
    explore_animate["player"].append(player_explore_img)   

power_imgs = {}
power_imgs["shield"] = pygame.image.load(os.path.join("img", "shield.png")).convert()
power_imgs["gun"] = pygame.image.load(os.path.join("img", "gun.png")).convert()

# upload music
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
explore_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))

pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.6)

die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))

# font
font_name = pygame.font.match_font("arial")
def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True , WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surface.blit(text_surface, text_rect)

# function
def new_rock():
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)

def draw_health(surface, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)  # boarder = 2

def draw_lifes(surface, lifes, img, x, y):
    for i in range(lifes):
        img_rect = img.get_rect()
        img_rect.x = x + 32 * i
        img_rect.y = y
        surface.blit(img, img_rect)

def draw_init():
    screen.blit(background_img, (0, 0) )  # put background_img at (0, 0)
    draw_text(screen, "SPACE GAME", 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, "Arrow keys control the spaceship", 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, "Space for shooting", 22, WIDTH/2, HEIGHT/2 + 40)
    draw_text(screen, "Press any button to start.", 18, WIDTH/2, HEIGHT * 5/6)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            if event.type == pygame.KEYUP:
                waiting = False
                return False

# class: Player, Rock, Bullet
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)  # let color black disappears
        # self.image = pygame.Surface((50, 40))
        # self.image.fill(GREEN)
        
        self.rect = self.image.get_rect()
        self.radius = 20  # for hit judgment
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)  # see the circle

        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.speedy = 8

        self.health = 100
        self.lifes = 3
        self.gun = 1
        self.gun_time = 0

        self.hidden = False
        self.hide_time = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT - 10

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
        # if key_pressed[pygame.K_UP]:
        #     self.rect.y -= self.speedy
        # if key_pressed[pygame.K_DOWN]:
        #     self.rect.y += self.speedy

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        # if self.rect.top < 0:
        #     self.rect.top = 0
        # if self.rect.bottom > HEIGHT:
        #     self.rect.bottom = HEIGHT

    def shoot(self):
        if not(self.hidden): 
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun > 1:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()


    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()


class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_original = random.choice(rock_imgs)
        self.image_original.set_colorkey(BLACK)
        self.image = self.image_original.copy()
        
        # self.image = pygame.Surface((30, 40))
        # self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.8 / 2)  # for hit judgment
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)  # see the circle

        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)
        self.speedy = random.randrange(2, 10)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rotate_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rotate_degree
        self.total_degree = self.total_degree % 360 
        self.image = pygame.transform.rotate(self.image_original, self.total_degree)
        
        # to fix the center
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()

        self.rect.y += self.speedy
        self.rect.x += self.speedx

        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):  # bullets shooted by player
        pygame.sprite.Sprite.__init__(self)

        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        # self.image = pygame.Surface((10, 20))
        # self.image.fill(YELLOW)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy

        if self.rect.bottom < 0:
            self.kill()  # sprites function

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)

        self.size = size
        self.image = explore_animate[self.size][0]
        
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_upate = now
            self.frame += 1
            if self.frame == len(explore_animate[self.size]):
                self.kill()
            else:
                self.image = explore_animate[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    def __init__(self, center):  
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield", "gun"])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy

        if self.rect.top < 0:
            self.kill()  

# sprites and groups

pygame.mixer.music.play(-1)  # loop music

# Game loop
running = True
show_init = True

while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()

        player = Player()  # OOP
        all_sprites.add(player)

        for i in range (8):  # creat 8 rocks
            new_rock()

        score = 0

    clock.tick(FPS)
    # get input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # update
    all_sprites.update()
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)  # this returns dictionary {rocks: bullets}
    for hit in hits:  # to create a new rock after one rock colliding
        random.choice(explore_sounds).play()
        score += hit.radius  # base on the radius of the rock
        explore = Explosion(hit.rect.center, "large") 
        all_sprites.add(explore)
        if random.random() > 0.8:
            power = Power(hit.rect.center)
            all_sprites.add(power)
            powers.add(power)
        new_rock()

    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)  # player is hitted by rocks
    for hit in hits:
        player.health -= hit.radius
        explore = Explosion(hit.rect.center, "small") 
        all_sprites.add(explore)
        new_rock()

        if player.health <= 0:
            death_explore = Explosion(player.rect.center, "player")
            all_sprites.add(death_explore)
            die_sound.play()
            player.lifes -= 1
            player.health = 100
            player.hide()

    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == "shield":
            player.health += 20
            shield_sound.play()
            if player.health > 100:
                player.health = 100

        elif hit.type == "gun":
            player.gunup()
            gun_sound.play()

    if player.lifes == 0 and not(death_explore.alive()):
        show_init = True

    # display
    screen.fill(WHITE)
    screen.blit(background_img, (0, 0) )  # put background_img at (0, 0)
    all_sprites.draw(screen)  # show all sprties on the screen
    draw_text(screen, str(score), 18, WIDTH/2, 10)
    draw_health(screen, player.health, 7, 10)
    draw_lifes(screen, player.lifes, player_mini_img, WIDTH -100, 15)
    pygame.display.update()  #this is must be in the end!! 

pygame.quit()