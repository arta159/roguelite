import os
import sys
import pygame
from random import randint

all_sprites = pygame.sprite.Group()
WIDTH = 1000
HEIGHT = 800
speed_player = 7
player_bullet_speed = 15
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
head_control = False
player_bullet_damage = 1
SHOT_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SHOT_EVENT, 1000)
walls = pygame.sprite.Group()
thorns = pygame.sprite.Group()
hearts = pygame.sprite.Group()
slime = pygame.sprite.Group()
enemy = pygame.sprite.Group()
box_thorns = pygame.sprite.Group()
horizontal_walls = pygame.sprite.Group()
vertical_walls = pygame.sprite.Group()
boxes = pygame.sprite.Group()
hero = pygame.sprite.Group()
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


class Heart(pygame.sprite.Sprite):  # класс овечающий за хп
    heart = load_image('heart.png')
    broken_heart = load_image('broken_heart.png')

    def __init__(self, posx):
        super().__init__(hearts, all_sprites)
        if Head.hitPoint >= posx:
            self.image = Heart.heart
        else:
            self.image = Heart.broken_heart
        self.rect = self.image.get_rect()
        self.rect.x = posx * self.image.get_width()

    def update(self):
        if Head.hitPoint <= 0:
            [_.kill() for _ in hero]
        [_.kill() for _ in hearts]
        [Heart(_) for _ in range(1, 6)]


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
    def __init__(self, sheet, columns, rows, x, y, speed_x=0, speed_y=0, group='none', size=2):
        if group == 'bullets':
            super().__init__(all_sprites, bullets)
        elif group == 'hero':
            super().__init__(all_sprites, hero)
            self.hitPoint = 5
        elif group == 'slime':
            super().__init__(all_sprites, slime, enemy)
            self.hitPoint = 2
        elif group == 'none':
            super().__init__(all_sprites)
        self.x, self.y = x, y
        self.columns = columns
        sheet = pygame.transform.scale(sheet, (sheet.get_width() * size, sheet.get_height() * size))
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
        if self.x == 0 and self.y == 0 and self in hero:
            self.cur_frame = 0 + self.route
        else:
            self.cur_frame = (self.cur_frame + 0.25) % self.columns + self.route
        self.image = self.frames[int(self.cur_frame)]


def collision_calculation(person, group='None'):
    if group == 'slime':
        person.zeroing()
        if Body.rect.x > person.rect.x:
            person.x = 3
        elif Body.rect.x < person.rect.x:
            person.x = -3
        if Body.rect.y > person.rect.y:
            person.y = 3
        elif Body.rect.y < person.rect.y:
            person.y = -3
        if pygame.sprite.spritecollideany(person, hero):
            Head.hitPoint -= 1
            person.rect.x, person.rect.y = person.rect.x - person.x * 15, person.rect.y - person.y * 15
        elif pygame.sprite.spritecollideany(person, bullets):
            person.hitPoint -= player_bullet_damage
            pygame.sprite.groupcollide(slime, bullets, False, True)
        if person.hitPoint == 0:
            person.kill()
    if group == 'bullet' and (pygame.sprite.spritecollideany(person, boxes)
                              or pygame.sprite.spritecollideany(person, walls)):
        person.kill()
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
            person.check('y', -person.y * 2)
        if person.y < 0:
            person.check('y', -person.y * 2)
        if person.x > 0:
            person.check('x', -person.x * 2)
        if person.x < 0:
            person.check('x', -person.x * 2)
    if pygame.sprite.spritecollideany(person, boxes):
        if person.y > 0:
            person.check('y', -person.y * 2, box=True)
        if person.y < 0:
            person.check('y', -person.y * 2, box=True)
        if person.x > 0:
            person.check('x', -person.x * 2, box=True)
        if person.x < 0:
            person.check('x', -person.x * 2, box=True)


def terminate():
    pygame.quit()
    sys.exit()


def attack(route):
    if route == 0:
        AnimatedSprite(load_image("ball_2.png", -2), 4, 1, Body.rect.centerx, Body.rect.centery,
                       speed_x=0, speed_y=player_bullet_speed, group='bullets', size=2)
    elif route == 12:
        AnimatedSprite(load_image("ball_2.png", -2), 4, 1, Body.rect.centerx, Body.rect.centery,
                       speed_x=0, speed_y=-player_bullet_speed, group='bullets', size=2)
    elif route == 4:
        AnimatedSprite(load_image("ball_2.png", -2), 4, 1, Body.rect.centerx, Body.rect.centery,
                       speed_x=-player_bullet_speed, speed_y=0, group='bullets', size=2)
    elif route == 8:
        AnimatedSprite(load_image("ball_2.png", -2), 4, 1, Body.rect.centerx, Body.rect.centery,
                       speed_x=player_bullet_speed, speed_y=0, group='bullets', size=2)


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
    Body = AnimatedSprite(load_image("OnlyBody1.png", -2), 4, 4, x, y, group='hero')
    Head = AnimatedSprite(load_image("OnlyHead.png", -2), 4, 4, x, y, group='hero')


AnimatedSprite(load_image('slime.png'), 7, 1, 600, 600, group='slime')
flag = True
create_player(300, 300)
[Heart(_) for _ in range(1, 6)]
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
    [collision_calculation(_, 'bullet') for _ in bullets]
    [collision_calculation(_, 'slime') for _ in slime]
    collision_calculation(Head)
    Body.x, Body.y = Head.x, Head.y
    all_sprites.update()
    pygame.display.flip()
    clock.tick(30)
terminate()
