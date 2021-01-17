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
thorns = pygame.sprite.Group()
slime = pygame.sprite.Group()
enemy = pygame.sprite.Group()
box_thorns = pygame.sprite.Group()
boxes = pygame.sprite.Group()
bullets = pygame.sprite.Group()
hero = pygame.sprite.Group()
horizontal_walls = pygame.sprite.Group()
vertical_walls = pygame.sprite.Group()
hearts = pygame.sprite.Group()
walls = pygame.sprite.Group()
doors = pygame.sprite.Group()


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
            self.rect.size = (70, 800)
        if direction == 'bottom':
            self.rect.x = 100
            self.rect.y = 673
            self.add(horizontal_walls)
        if direction == 'top':
            self.rect.x = 100
            self.rect.y = 0
            self.rect.size = (800, 85)
            self.add(horizontal_walls)


class Box(pygame.sprite.Sprite):
    box = pygame.transform.scale(load_image('box2.png'), (70, 70))

    def __init__(self, i, j, image=False):
        if image:
            self.image = image
            group = thorns
        else:
            self.image = Box.box
            group = boxes
        super().__init__(all_sprites, group, box_thorns)
        self.rect = self.image.get_rect()
        self.rect.size = (40, 30)
        self.rect.x = 100 + 50 * j
        self.rect.y = 125 + 50 * i

    def update(self):
        self.rect.size = (50, 50)


class Thorns(Box):
    thorn_im = pygame.transform.scale(load_image('thorns2.png', -2), (50, 50))
    thorn_activated = pygame.transform.scale(load_image('thorns3.png'), (50, 50))

    def __init__(self, i, j):
        super().__init__(i, j, Thorns.thorn_im)
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


Wall('left')
Wall('right')
Wall('top')
Wall('bottom')


class Door(pygame.sprite.Sprite):
    door_im = pygame.transform.scale(load_image('door.png', -2), (70, 135))
    open_close_door = [door_im,
                       pygame.transform.scale(load_image('door_close05.png'), (70, 135)),
                       pygame.transform.scale(load_image('door_close1.png'), (70, 135)),
                       pygame.transform.scale(load_image('door_close2.png'), (70, 135)),
                       pygame.transform.scale(load_image('door_close3.png'), (70, 135)),
                       pygame.transform.scale(load_image('door_close.png'), (70, 135))]
    door_open = [pygame.transform.scale(load_image('door_cl1.png'), (70, 135)),
                 pygame.transform.scale(load_image('door_cl2.png'), (70, 135)),
                 pygame.transform.scale(load_image('door_cl3.png'), (70, 135)),
                 pygame.transform.scale(load_image('door_cl4.png'), (70, 135)),
                 pygame.transform.scale(load_image('door_cl5.png'), (70, 135))]
    door_close = pygame.transform.rotate(open_close_door[-1], 180)

    def __init__(self, right=False):
        super().__init__(all_sprites, doors)
        if right:
            self.image = Door.door_close
            self.rect = self.image.get_rect()
            self.rect.x = 890
            self.rect.y = 330
            self.open = 5
            self.time = 0
            self.lights = 0
            self.close = 1
            self.close_flag = True
            self.mask = pygame.mask.from_surface(Door.door_close)
        else:
            self.image = Door.door_im
            self.rect = self.image.get_rect()
            self.rect.x = 40
            self.rect.y = 330
            self.close = 1
            self.time = pygame.time.get_ticks()

    def close_door(self, left=False):
        if self.close < 6 and pygame.time.get_ticks() - self.time > 50:
            if left:
                self.image = pygame.transform.rotate(Door.open_close_door[self.close], 180)
            else:
                self.image = Door.open_close_door[self.close]
            self.close += 1
            self.time = pygame.time.get_ticks()

    def open_door(self):
        if self.open > -1 and pygame.time.get_ticks() - self.time > 50:
            self.image = pygame.transform.rotate(Door.open_close_door[self.open], 180)
            self.open -= 1
            self.time = pygame.time.get_ticks()
        elif pygame.time.get_ticks() - self.time > 50:
            self.close_flag = False
            self.image = Door.door_open[self.lights]
            self.lights += 1
            self.lights %= 3
            self.time = pygame.time.get_ticks()

    def interaction(self):
        if pygame.sprite.collide_mask(self, Body) and not self.close_flag:
            generation_room()
            self.close = True


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, speed_x=0, speed_y=0, group='none', size=2):
        if group == 'bullets':
            super().__init__(all_sprites, bullets)
            size = 1.5
        elif group == 'hero':
            super().__init__(all_sprites, hero)
            self.flag_hero = False
            self.hitPoint = 5
        elif group == 'slime':
            super().__init__(all_sprites, slime, enemy)
            self.hitPoint = 2
        elif group == 'none':
            super().__init__(all_sprites)
        self.x, self.y = x, y
        self.columns = columns
        print(sheet.get_width(), sheet.get_height())
        if group == 'bullets':
            sheet = pygame.transform.scale(sheet, (120, 30))
        else:
            sheet = pygame.transform.scale(sheet, (sheet.get_width() * size, sheet.get_height() * size))
        print(sheet.get_width(), sheet.get_height())
        self.route = 0
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        if group == 'hero':
            self.rect.size = (60, 80)
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
                if not pygame.sprite.spritecollideany(self, walls):
                    self.y = 0
                self.rect.y -= bias
            else:
                self.rect.x += bias
                if not pygame.sprite.spritecollideany(self, walls):
                    self.x = 0
                self.rect.x -= bias
        if box:
            if axis == 'y':
                self.rect.y += bias
                if not pygame.sprite.spritecollideany(self, boxes):
                    self.y = 0
                    if bias < 0 and self in hero:
                        self.flag_hero = True
                self.rect.y -= bias
            else:
                self.rect.x += bias
                if not pygame.sprite.spritecollideany(self, boxes):
                    self.x = 0
                self.rect.x -= bias
            if self in hero and self.flag_hero:
                if pygame.sprite.spritecollideany(self, boxes):
                    self.rect.y -= 10
                    if pygame.sprite.spritecollideany(self, boxes):
                        self.flag_hero = False
                    self.rect.y += 10
                else:
                    self.flag_hero = False

    def zeroing(self):
        self.x = 0
        self.y = 0

    def update(self):
        self.rect = self.rect.move(self.x, self.y)
        if self.x == 0 and self.y == 0 and self in hero:
            self.cur_frame = 0 + self.route
        else:
            self.cur_frame = (self.cur_frame + 0.25) % self.columns + self.route
        self.image = self.frames[int(self.cur_frame)]


def collision_calculation(person, group='None'):
    flag = False
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
    if group == 'bullet':
        for i in boxes:
            i.rect.size = (45, 45)
        if pygame.sprite.spritecollideany(person, boxes) or pygame.sprite.spritecollideany(person, walls):
            person.kill()
            boxes.update()
    if pygame.sprite.spritecollideany(person, walls):
        if pygame.sprite.spritecollideany(person, vertical_walls) \
                and pygame.sprite.spritecollideany(person, horizontal_walls):
            if (person.rect.x < 500 and person.rect.y < 500 and person.x <= 0 and person.y <= 0) or \
                    person.rect.x < 500 and person.rect.y > 500 and person.x <= 0 and person.y >= 0 or \
                    person.rect.x > 500 and person.rect.y > 500 and person.x >= 0 and person.y >= 0 or \
                    person.rect.x > 500 and person.rect.y < 500 and person.x >= 0 and person.y <= 0:
                person.zeroing()
        if person.y != 0:
            person.check('y', -person.y * 2)
        if person.x != 0:
            person.check('x', -person.x * 2)
        flag = True
    if pygame.sprite.spritecollideany(person, boxes):
        if person.y != 0:
            person.check('y', -person.y * 2, box=True)
        if person.x != 0:
            person.check('x', -person.x * 2, box=True)
        flag = True
    if not flag and person in hero:
        person.flag_hero = False


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
    if (pygame.key.get_pressed()[pygame.K_d] and pygame.key.get_pressed()[pygame.K_LEFT]) or \
            (pygame.key.get_pressed()[pygame.K_a] and pygame.key.get_pressed()[pygame.K_RIGHT]) or \
            (pygame.key.get_pressed()[pygame.K_s] and pygame.key.get_pressed()[pygame.K_UP]) or \
            (pygame.key.get_pressed()[pygame.K_w] and pygame.key.get_pressed()[pygame.K_DOWN]):
        Body.route = Head.route
    if not pygame.key.get_pressed()[pygame.K_w] and not pygame.key.get_pressed()[pygame.K_s]:
        Body.y = 0
        Head.y = 0
    if not pygame.key.get_pressed()[pygame.K_a] and not pygame.key.get_pressed()[pygame.K_d]:
        Body.x = 0
        Head.x = 0
    if not pygame.key.get_pressed()[pygame.K_UP] and not pygame.key.get_pressed()[pygame.K_DOWN] \
            and not pygame.key.get_pressed()[pygame.K_LEFT] and not pygame.key.get_pressed()[pygame.K_RIGHT]:
        head_control = False
    if not head_control:
        Head.route = Body.route


def create_player(x, y):
    global Body, Head
    Body = AnimatedSprite(load_image("OnlyBody1.png", -2), 4, 4, x, y, group='hero')
    Head = AnimatedSprite(load_image("OnlyHead.png", -2), 4, 4, x, y, group='hero')


def create_map():
    filename = "data/" + 'map1.txt'
    if not os.path.isfile(filename):
        print(f"Файл с уровнем '{filename}' не найден")
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    for num, i in enumerate(level_map):
        for num2, j in enumerate(i):
            if j == '#':
                Box(num, num2)
            if j == '*':
                Thorns(num, num2)


def generation_room(first_generation=False):  # генерация комнаты
    global shot_flag, left_door, right_door, generation_room_flag
    if not first_generation:  # если комната генерируется впервые, то группы со спрайтами очищать не надо
        boxes.empty()
        thorns.empty()
        slime.empty()
        enemy.empty()
        box_thorns.empty()
        boxes.empty()
        bullets.empty()
    shot_flag = True  # генерируем все объекты комнаты кроме героя
    left_door = Door()
    right_door = Door(True)
    Body.rect.x = Head.rect.x = 150
    Body.rect.y = Head.rect.y = 350
    create_map()
    AnimatedSprite(load_image('slime.png'), 7, 1, 600, 600, group='slime')
    boxes.update()
    generation_room_flag = True


def draw():
    walls.draw(screen)
    doors.draw(screen)
    if Head.flag_hero:
        hero.draw(screen)
        box_thorns.draw(screen)
    else:
        box_thorns.draw(screen)
        hero.draw(screen)
    enemy.draw(screen)
    bullets.draw(screen)
    hearts.draw(screen)


first_generation = True
generation_room_flag = False
create_player(300, 300)
[Heart(_) for _ in range(1, 6)]
running = True
while running:
    if not generation_room_flag:
        generation_room(first_generation)
        first_generation = False
    player_moved()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == SHOT_EVENT:
            shot_flag = True
        if (event.type == SHOT_EVENT or shot_flag) and head_control:
            shot_flag = False
            attack(Head.route)
    screen.blit(fon, (100, 125))
    draw()
    [collision_calculation(_, 'bullet') for _ in bullets]
    [collision_calculation(_, 'slime') for _ in slime]
    collision_calculation(Head)
    right_door.interaction()
    left_door.close_door()
    right_door.close_door(True)
    if not slime:
        right_door.open_door()
    Body.x, Body.y = Head.x, Head.y
    all_sprites.update()
    pygame.display.flip()
    clock.tick(30)
terminate()
