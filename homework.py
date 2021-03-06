import pygame
import sys
import os
import random
import pprint
import numpy as np


board_w, board_h = None, None
start_x, start_y = None, None


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # print(fullname)
    if not os.path.isfile(fullname):
        print('not found')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    global board_h, board_w
    # print(filename)
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    board_h = len(level_map) * tile_height
    # и подсчитываем максимальную длину
    max_width = board_w = max(map(len, level_map))
    board_w *= tile_width

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    global start_x, start_y
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y, x] == '.':
                Tile('empty', x * tile_width - 15, y * tile_height - 35)
            elif level[y, x] == '#':
                Wall('wall', x * tile_width - 15, y * tile_height - 35)
            elif level[y, x] == '@':
                Tile('empty', x * tile_width - 15, y * tile_height - 35)
                start_x, start_y = x, y
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def update_level(a, b):
    global level
    for tile in tiles_group:
        all_sprites.remove(tile)
    level = np.roll(level, a, axis=b)
    # print(level)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y, x] == '.':
                Tile('empty', x * tile_width - 15, y * tile_height - 35)
            elif level[y, x] == '#':
                Wall('wall', x * tile_width - 15, y * tile_height - 35)
            elif level[y, x] == '@':
                Tile('empty', x * tile_width - 15, y * tile_height - 35)


def check_move(a, b):
    global level
    update_level(a, b)
    for line in range(len(level)):
        for col in range(len(level[line])):
            if level[line, col] == '#' and line == start_y and col == start_x:
                update_level(-a, b)


tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)


class Wall(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super(Wall, self).__init__(tile_type, pos_x, pos_y)
        walls_group.add(self)


class Border(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super(Border, self).__init__(all_sprites, borders_group)
        self.image = pygame.Surface((w, h),
                                    pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, pygame.Color("black"), (0, 0, w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x = 235 + (tile_width - self.image.get_width()) // 2
        self.rect.y = 115 + (tile_height - self.image.get_height()) // 2
        self.rect.w = tile_width
        self.rect.h = tile_height


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - w // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - h // 2)


def start_screen():
    global running, state
    screen.blit(fon, (0, 0))
    text = ['Перемещение героя', 'Герой перемещается при нажатии', 'на стрелки на клавиатуре']
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in text:
        line_rendered = font.render(line, True, (0, 0, 0))
        intro_rect = line_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(line_rendered, intro_rect)
    pygame.display.flip()
    while running and state == 'start screen':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                state = 'play'
    if not running:
        pygame.quit()
    play()


def play():
    global running, state, player
    # data = load_level(level)
    player, x, y = generate_level(level)
    Border(-tile_width, -tile_height + 5, board_w + tile_width * 2, 1)
    Border(-tile_width + 15, -tile_height, 1, board_h + tile_height * 2)
    Border(-tile_width + 15, board_h + tile_height - 5, board_w + tile_width * 2, 1)
    Border(board_w + tile_width - 15, -tile_height + 5, 1, board_h + tile_height * 2)
    while running and state == 'play':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    check_move(-1, 0)
                elif event.key == pygame.K_UP:
                    check_move(1, 0)
                elif event.key == pygame.K_RIGHT:
                    check_move(-1, 1)
                elif event.key == pygame.K_LEFT:
                    check_move(1, 1)
        screen.fill("black")
        all_sprites.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
    if not running:
        pygame.quit()


states = {'start screen': start_screen, 'play': play}

if __name__ == '__main__':
    level_name = 'new_level.txt'
    fullname = os.path.join('data', level_name)
    if not os.path.isfile(fullname):
        print('not found')
        sys.exit()
    pygame.init()
    pygame.display.set_caption('3rd')

    size = w, h = 550, 300
    screen = pygame.display.set_mode(size)

    fon = pygame.transform.scale(load_image('background.jpg'), (w, h))

    player = None

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    borders_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()

    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png')
    }
    player_image = load_image('mar.png')

    level = load_level(level_name)
    level = np.array([[y for y in x] for x in level], dtype=np.str_)
    # print(level)

    state = 'start screen'
    running = True
    clock = pygame.time.Clock()
    states[state]()
