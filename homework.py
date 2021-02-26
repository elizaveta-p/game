import pygame
import sys
import os
import random
import pprint


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    print(fullname)
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
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Wall('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Wall(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super(Wall, self).__init__(tile_type, pos_x, pos_y)
        walls_group.add(self)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def update(self, x, y) -> None:
        self.rect = self.rect.move(x, y)
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(-x, -y)
        elif self.rect.x + self.rect.w == w or self.rect.y + self.rect.h == h or \
            self.rect.x + self.rect.w < 0 or self.rect.y + self.rect.h < 0:
            self.rect = self.rect.move(-x, -y)


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
    data = load_level('level.txt')
    player, x, y = generate_level(data)
    while running and state == 'play':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    player.update(0, tile_height)
                if event.key == pygame.K_UP:
                    player.update(0, -tile_height)
                if event.key == pygame.K_RIGHT:
                    player.update(tile_width, 0)
                if event.key == pygame.K_LEFT:
                    player.update(-tile_width, 0)
        all_sprites.draw(screen)
        pygame.display.flip()
    if not running:
        pygame.quit()


states = {'start screen': start_screen, 'play': play}

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('3rd')

    size = w, h = 550, 300
    screen = pygame.display.set_mode(size)

    fon = pygame.transform.scale(load_image('background.jpg'), (w, h))
    # grass_block = load_image('grass.png')
    # box_block = load_image('box.png')
    # mar_image = load_image('mar.png')

    player = None

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()

    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png')
    }
    player_image = load_image('mar.png')

    state = 'start screen'
    running = True
    clock = pygame.time.Clock()
    states[state]()
    # screen.fill("black")
    #
    # fps = 10
    #
    # all_sprites = pygame.sprite.Group()
    # vertical = pygame.sprite.Group()
    # horizontal = pygame.sprite.Group()
    #

    # state = 'start screen'
    # while running:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
    #         if event.type == pygame.MOUSEBUTTONDOWN and pygame.key.get_mods() == 4160:
    #             VerticalPlatform(event.pos[0], event.pos[1])
    #         elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    #             if character is not None:
    #                 all_sprites.remove(character)
    #             character = Character(event.pos[0], event.pos[1])
    #         elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
    #             Platform(event.pos[0], event.pos[1])
    #         elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
    #             if character is not None:
    #                 side_move = 'left'
    #         elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
    #             if character is not None:
    #                 side_move = 'right'
    #         if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
    #             if character is not None:
    #                 side_move = 'up'
    #         if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
    #             if character is not None:
    #                 side_move = 'down'
    #     if character is not None:
    #         character.update(side_move)
    #         side_move = None
    #     render()
    #     pygame.display.flip()
    #     clock.tick(fps)
    # pygame.quit()
