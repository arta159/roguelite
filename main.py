import os
import sys
import pygame


all_sprites = pygame.sprite.Group()
WIDTH = 400
HEIGHT = 300
speed_player = 5
player_bullet_speed = 10
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
head_control = False
SHOT_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SHOT_EVENT, 1000)


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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.x, self.y = x, y
        self.columns = columns
        sheet = pygame.transform.scale(sheet, (sheet.get_width() * 2, sheet.get_height() * 2))
        self.route = 0
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(self.x, self.y)
        self.x, self.y = 0, 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

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


def create_standard_bullet(person, move_x, move_y):
    x = person.rect.centerx
    y = person.rect.centery
    bullet = AnimatedSprite(load_image("ball_2.png"), 4, 1, x, y)
    bullet.x = move_x
    bullet.y = move_y


def attack(route):
    if route == 0:
        create_standard_bullet(Body, 0, player_bullet_speed)
    elif route == 12:
        create_standard_bullet(Body, 0, -player_bullet_speed)
    elif route == 4:
        create_standard_bullet(Body, -player_bullet_speed, 0)
    elif route == 8:
        create_standard_bullet(Body, +player_bullet_speed, 0)


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
        if event.key == pygame.K_w:
            Body.y += speed_player
            Head.y += speed_player
        elif events.key == pygame.K_s:
            Body.y -= speed_player
            Head.y -= speed_player
        elif events.key == pygame.K_a:
            Body.x += speed_player
            Head.x += speed_player
        elif events.key == pygame.K_d:
            Body.x -= speed_player
            Head.x -= speed_player
        elif events.key in (pygame.K_UP, pygame.K_DOWN,
                            pygame.K_RIGHT, pygame.K_LEFT):
            head_control = False
    if not head_control:
        Head.route = Body.route


def create_player(x, y):
    global Body, Head
    Body = AnimatedSprite(load_image("OnlyBody1.png", -1), 4, 4, x, y)
    Head = AnimatedSprite(load_image("OnlyHead.png", -1), 4, 4, x, y)


create_player(100, 100)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
            player_moved(event)
        elif event.type == SHOT_EVENT and head_control:
            attack(Head.route)
    screen.fill(pygame.Color('white'))
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(30)

terminate()
