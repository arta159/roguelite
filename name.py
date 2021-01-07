import os
import sys
import pygame
from random import randint

all_sprites = pygame.sprite.Group()
WIDTH = 1000
HEIGHT = 800
speed_player = 5
player_bullet_speed = 10
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
head_control = False
SHOT_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SHOT_EVENT, 1000)
walls = pygame.sprite.Group()
horizontal_walls = pygame.sprite.Group()
vertical_walls = pygame.sprite.Group()
boxes = pygame.sprite.Group()
bullets = pygame.sprite.Group()

def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


fon = pygame.transform.scale(load_image('floor.jpg'), (800, 550))


class Wall(pygame.sprite.Sprite):
    d = {'left': pygame.transform.scale(load_image('wall.jpg'), (100, 800)),
         'right': pygame.transform.rotate(pygame.transform.scale(load_image('wall.jpg'), (102, 800)), 180),
         'bottom': pygame.transform.scale(load_image('wall2.jpg'), (800, 125)),
         'top': pygame.transform.rotate(pygame.transform.scale(load_image('wall2.jpg'), (800, 125)), 180)}

    def __init__(self, direction):
        super().__init__(walls, all_sprites)
        self.image = Wall.d[direction]
        self.rect = self.image.get_rect()
        if direction == 'right':
            self.rect.right = WIDTH
            self.add(vertical_walls)
        if direction == 'left':
            self.rect.left = 0
            self.add(vertical_walls)
        if direction == 'bottom':
            self.rect.x = 100
            self.rect.y = 673
            self.add(horizontal_walls)
        if direction == 'top':
            self.rect.x = 100
            self.rect.y = 0
            self.add(horizontal_walls)


class Box(pygame.sprite.Sprite):
    box = pygame.transform.scale(load_image('box1.png'), (50, 50))

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Box.box
        self.rect = self.image.get_rect()
        self.rect.x = randint(110, 790)
        self.rect.y = randint(130, 550)
        while pygame.sprite.spritecollideany(self, boxes):
            self.rect.x = randint(110, 790)
            self.rect.y = randint(130, 550)
        self.add(boxes)


Wall('left')
Wall('right')
Wall('top')
Wall('bottom')
[Box() for i in range(5)]


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, speed_x=0, speed_y=0, group=False):
        if group:
            super().__init__(all_sprites, bullets)
        else:
            super().__init__(all_sprites)
        self.x, self.y = x, y
        self.columns = columns
        sheet = pygame.transform.scale(sheet, (sheet.get_width() * 2, sheet.get_height() * 2))
        self.route = 0
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        # self.x, self.y = speed_x, speed_y
        self.rect = self.rect.move(self.x, self.y)
        self.x, self.y = speed_x, speed_y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def character_update(self):
        if pygame.sprite.spritecollideany(self, walls):
            if pygame.sprite.spritecollideany(self, vertical_walls) \
                    and pygame.sprite.spritecollideany(self, horizontal_walls):
                if self.rect.x < 500 and self.rect.y < 500 and self.x <= 0 and self.y <= 0:
                    self.x = 0
                    self.y = 0
                if self.rect.x < 500 and self.rect.y > 500 and self.x <= 0 and self.y >= 0:
                    self.x = 0
                    self.y = 0
                if self.rect.x > 500 and self.rect.y > 500 and self.x >= 0 and self.y >= 0:
                    self.x = 0
                    self.y = 0
                if self.rect.x > 500 and self.rect.y < 500 and self.x >= 0 and self.y <= 0:
                    self.x = 0
                    self.y = 0
            if self.y > 0:
                self.rect.y -= 10
                if not pygame.sprite.spritecollideany(self, walls): # or not pygame.sprite.spritecollideany(self, boxes):
                    self.y = 0
                    print(1)
                self.rect.y += 10
            if self.y < 0:
                self.rect.y += 10
                print(pygame.sprite.spritecollideany(self, walls))
                if not pygame.sprite.spritecollideany(self, walls):# or not pygame.sprite.spritecollideany(self, boxes):
                    print(11)
                    self.y = 0
                self.rect.y -= 10
            if self.x > 0:
                self.rect.x -= 10
                if not pygame.sprite.spritecollideany(self, walls):# and not pygame.sprite.spritecollideany(self, boxes):
                    print(111)
                    self.x = 0
                self.rect.x += 10
            if self.x < 0:
                self.rect.x += 10
                if not pygame.sprite.spritecollideany(self, walls):# and not pygame.sprite.spritecollideany(self, boxes):
                    print(111)
                    self.x = 0
                self.rect.x -= 10
        if pygame.sprite.spritecollideany(self, boxes):
            if self.y > 0:
                self.rect.y -= 10
                if not pygame.sprite.spritecollideany(self, boxes): # or not pygame.sprite.spritecollideany(self, boxes):
                    self.y = 0
                self.rect.y += 10
            if self.y < 0:
                self.rect.y += 10
                if not pygame.sprite.spritecollideany(self, boxes):
                    self.y = 0
                self.rect.y -= 10
            if self.x > 0:
                self.rect.x -= 10
                if not pygame.sprite.spritecollideany(self, boxes):
                    self.x = 0
                self.rect.x += 10
            if self.x < 0:
                self.rect.x += 10
                if not pygame.sprite.spritecollideany(self, boxes):
                    self.x = 0
                self.rect.x -= 10
        self.rect = self.rect.move(self.x, self.y)
        if self.x != 0 or self.y != 0:
            self.cur_frame = (self.cur_frame + 0.25) % self.columns + self.route
        else:
            self.cur_frame = 0 + self.route
        self.image = self.frames[int(self.cur_frame)]

    def update(self):
        self.rect = self.rect.move(self.x, self.y)
        if self.x != 0 or self.y != 0:
            self.cur_frame = (self.cur_frame + 0.25) % self.columns + self.route
        else:
            self.cur_frame = 0 + self.route
        self.image = self.frames[int(self.cur_frame)]


def terminate():
    pygame.quit()
    sys.exit()


def attack(route):
    if route == 0:
        AnimatedSprite(load_image("ball_2.png"), 4, 1, Body.rect.x, Body.rect.y,
                       speed_x=0, speed_y=player_bullet_speed, group=True)
    elif route == 12:
        AnimatedSprite(load_image("ball_2.png"), 4, 1, Body.rect.x, Body.rect.y,
                       speed_x=0, speed_y=-player_bullet_speed, group=True)
    elif route == 4:
        AnimatedSprite(load_image("ball_2.png"), 4, 1, Body.rect.x, Body.rect.y,
                       speed_x=-player_bullet_speed, speed_y=0, group=True)
    elif route == 8:
        AnimatedSprite(load_image("ball_2.png"), 4, 1, Body.rect.x, Body.rect.y,
                       speed_x=player_bullet_speed, speed_y=0, group=True)


def player_moved(events):
    global head_control
    if events.type == pygame.KEYDOWN:
        if events.key == pygame.K_UP:
            if Body.route == 0:
                Body.route = 12
            Head.route = 12
            head_control = True
        elif events.key == pygame.K_DOWN:
            if Body.route == 12:
                Body.route = 0
            Head.route = 0
            head_control = True
        elif events.key == pygame.K_LEFT:
            if Body.route == 8:
                Body.route = 4
            Head.route = 4
            head_control = True
        elif events.key == pygame.K_RIGHT:
            if Body.route == 4:
                Body.route = 8
            Head.route = 8
            head_control = True
        elif events.key == pygame.K_w:
            Body.route = 12
            Body.y -= speed_player
            Head.y -= speed_player
        elif events.key == pygame.K_s:
            Body.route = 0
            Body.y += speed_player
            Head.y += speed_player
        elif events.key == pygame.K_a:
            Body.route = 4
            Body.x -= speed_player
            Head.x -= speed_player
        elif events.key == pygame.K_d:
            Body.route = 8
            Body.x += speed_player
            Head.x += speed_player
    elif events.type == pygame.KEYUP:
        if event.key == pygame.K_w and Body.y != 0:
            Body.y = 0
            Head.y = 0
        elif events.key == pygame.K_s and Body.y != 0:
            Body.y = 0
            Head.y = 0
        elif events.key == pygame.K_a and Body.x != 0:
            Body.x = 0
            Head.x = 0
        elif events.key == pygame.K_d and Body.x != 0:
            Body.x = 0
            Head.x = 0
        elif events.key in (pygame.K_UP, pygame.K_DOWN,
                            pygame.K_RIGHT, pygame.K_LEFT):
            head_control = False
    if not head_control:
        Head.route = Body.route


def create_player(x, y):
    global Body, Head
    Body = AnimatedSprite(load_image("OnlyBody1.png", -1), 4, 4, x, y)
    Head = AnimatedSprite(load_image("OnlyHead.png", -1), 4, 4, x, y)


create_player(300, 300)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
            player_moved(event)
        elif event.type == SHOT_EVENT and head_control:
            attack(Head.route)
    screen.blit(fon, (100, 125))
    all_sprites.draw(screen)
    Head.character_update()
    Body.character_update()
    bullets.update()
    pygame.display.flip()
    clock.tick(30)
terminate()
