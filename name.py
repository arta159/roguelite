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
thorns = pygame.sprite.Group()
box_thorns = pygame.sprite.Group()
horizontal_walls = pygame.sprite.Group()
vertical_walls = pygame.sprite.Group()
boxes = pygame.sprite.Group()
bullets = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            image = image.convert()
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert().convert_alpha()
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

    def __init__(self, image=False):
        if image:
            self.image = image
            group = thorns
        else:
            self.image = Box.box
            group = boxes
        super().__init__(all_sprites, group)
        self.rect = self.image.get_rect()
        self.rect.size = (120, 160)
        self.rect.x = randint(110, 790)
        self.rect.y = randint(130, 550)
        self.mask = pygame.mask.from_surface(self.image)
        while pygame.sprite.spritecollideany(self, box_thorns):
            self.rect.x = randint(110, 790)
            self.rect.y = randint(130, 550)
        self.add(box_thorns)

    def update(self):
        self.rect.size = (50, 50)


class Thorns(Box):
    thorn_im = pygame.transform.scale(load_image('thorns2.png', -2), (50, 50))
    thorn_activated = pygame.transform.scale(load_image('thorns3.png'), (50, 50))

    def __init__(self):
        super().__init__(Thorns.thorn_im)
        self.push_thorns = False
        self.time = 0

    def update(self):
        if pygame.sprite.collide_mask(self, Head):
            self.push_thorns = True
        if self.push_thorns and not pygame.sprite.collide_mask(self, Head):
            self.image = Thorns.thorn_activated
            self.time = pygame.time.get_ticks()
            self.push_thorns = False
        if self.time and pygame.time.get_ticks() - self.time >= 3000:
            self.time = 0
            self.image = Thorns.thorn_im

        # self.image = Thorns.thorn_activated

Wall('left')
Wall('right')
Wall('top')
Wall('bottom')
[Box() for _ in range(5)]
[Thorns() for _ in range(3)]
boxes.update()


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

    def check(self, axis, bias, box=False):
        if not box:
            if axis == 'y':
                self.rect.y += bias
                if not pygame.sprite.spritecollideany(self, walls):  # or not pygame.sprite.spritecollideany(self, boxes):
                    self.y = 0
                self.rect.y -= bias
            else:
                self.rect.x += bias
                if not pygame.sprite.spritecollideany(self, walls):  # or not pygame.sprite.spritecollideany(self, boxes):
                    self.x = 0
                self.rect.x -= bias
        if box:
            if axis == 'y':
                self.rect.y += bias
                if not pygame.sprite.spritecollideany(self, boxes):
                    self.y = 0
                self.rect.y -= bias
            else:
                self.rect.x += bias
                if not pygame.sprite.spritecollideany(self, boxes):  # or not pygame.sprite.spritecollideany(self, boxes):
                    self.x = 0
                self.rect.x -= bias

    def zeroing(self):
        self.x = 0
        self.y = 0

    def update(self, bullet=False):
        self.rect = self.rect.move(self.x, self.y)
        if self.x != 0 or self.y != 0:
            self.cur_frame = (self.cur_frame + 0.25) % self.columns + self.route
        else:
            self.cur_frame = 0 + self.route
        self.image = self.frames[int(self.cur_frame)]


def collision_calculation(person, bullet=False):
    if pygame.sprite.spritecollideany(person, walls):
        if pygame.sprite.spritecollideany(person, vertical_walls) \
                and pygame.sprite.spritecollideany(person, horizontal_walls):
            if person.rect.x < 500 and person.rect.y < 500 and person.x <= 0 and person.y <= 0:
                person.zeroing()
            if person.rect.x < 500 and person.rect.y > 500 and person.x <= 0 and person.y >= 0:
                person.zeroing()
            if person.rect.x > 500 and person.rect.y > 500 and person.x >= 0 and person.y >= 0:
                person.zeroing()
            if person.rect.x > 500 and person.rect.y < 500 and person.x >= 0 and person.y <= 0:
                person.zeroing()
        if person.y > 0:
            person.check('y', -10)
        if person.y < 0:
            person.check('y', 10)
        if person.x > 0:
            person.check('x', -10)
        if person.x < 0:
            person.check('x', 10)
    if pygame.sprite.spritecollideany(person, boxes):
        if person.y > 0:
            person.check('y', -10, box=True)
        if person.y < 0:
            person.check('y', 10, box=True)
        if person.x > 0:
            person.check('x', -10, box=True)
        if person.x < 0:
            person.check('x', 10, box=True)
    if bullet and (pygame.sprite.spritecollideany(person, boxes)
                   or pygame.sprite.spritecollideany(person, walls)):
        person.kill()


def terminate():
    pygame.quit()
    sys.exit()


def attack(route):
    if route == 0:
        AnimatedSprite(load_image("ball_2.png", -2), 4, 1, Body.rect.x, Body.rect.y,
                       speed_x=0, speed_y=player_bullet_speed, group=True)
    elif route == 12:
        AnimatedSprite(load_image("ball_2.png", -2), 4, 1, Body.rect.x, Body.rect.y,
                       speed_x=0, speed_y=-player_bullet_speed, group=True)
    elif route == 4:
        AnimatedSprite(load_image("ball_2.png", -2), 4, 1, Body.rect.x, Body.rect.y,
                       speed_x=-player_bullet_speed, speed_y=0, group=True)
    elif route == 8:
        AnimatedSprite(load_image("ball_2.png", -2), 4, 1, Body.rect.x, Body.rect.y,
                       speed_x=player_bullet_speed, speed_y=0, group=True)


def player_moved():
    global head_control
    if pygame.key.get_pressed()[pygame.K_UP]:
        if Body.route == 0:
            Body.route = 12
        Head.route = 12
        head_control = True
    if pygame.key.get_pressed()[pygame.K_DOWN]:
        if Body.route == 12:
            Body.route = 0
        Head.route = 0
        head_control = True
    if pygame.key.get_pressed()[pygame.K_LEFT]:
        if Body.route == 8:
            Body.route = 4
        Head.route = 4
        head_control = True
    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        if Body.route == 4:
            Body.route = 8
        Head.route = 8
        head_control = True
    if pygame.key.get_pressed()[pygame.K_w]:
        Body.route = 12
        Body.y = -speed_player
        Head.y = -speed_player
    if pygame.key.get_pressed()[pygame.K_s]:
        Body.route = 0
        Body.y = speed_player
        Head.y = speed_player
    if pygame.key.get_pressed()[pygame.K_a]:
        Body.route = 4
        Body.x = -speed_player
        Head.x = -speed_player
    if pygame.key.get_pressed()[pygame.K_d]:
        Body.route = 8
        Body.x = speed_player
        Head.x = speed_player
    if (pygame.key.get_pressed()[pygame.K_d] and pygame.key.get_pressed()[pygame.K_LEFT]) or\
            (pygame.key.get_pressed()[pygame.K_a] and pygame.key.get_pressed()[pygame.K_RIGHT]) or\
            (pygame.key.get_pressed()[pygame.K_s] and pygame.key.get_pressed()[pygame.K_UP]) or\
            (pygame.key.get_pressed()[pygame.K_w] and pygame.key.get_pressed()[pygame.K_DOWN]):
        Body.route = Head.route
    if not pygame.key.get_pressed()[pygame.K_w] and not pygame.key.get_pressed()[pygame.K_s]:
        Body.y = 0
        Head.y = 0
    if not pygame.key.get_pressed()[pygame.K_a] and not pygame.key.get_pressed()[pygame.K_d]:
        Body.x = 0
        Head.x = 0
    if not pygame.key.get_pressed()[pygame.K_UP] and not pygame.key.get_pressed()[pygame.K_DOWN]\
            and not pygame.key.get_pressed()[pygame.K_LEFT] and not pygame.key.get_pressed()[pygame.K_RIGHT]:
        head_control = False
    if not head_control:
        Head.route = Body.route


def create_player(x, y):
    global Body, Head
    Body = AnimatedSprite(load_image("OnlyBody1.png", -2), 4, 4, x, y)
    Head = AnimatedSprite(load_image("OnlyHead.png", -2), 4, 4, x, y)


flag = True
create_player(300, 300)
running = True
while running:
    player_moved()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == SHOT_EVENT:
            flag = True
        if (event.type == SHOT_EVENT or flag) and head_control:
            flag = False
            attack(Head.route)
    screen.blit(fon, (100, 125))
    all_sprites.draw(screen)
    [collision_calculation(_, True) for _ in bullets]
    collision_calculation(Head)
    Body.x, Body.y = Head.x, Head.y
    all_sprites.update()
    pygame.display.flip()
    clock.tick(30)
terminate()
