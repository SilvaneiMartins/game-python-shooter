import os
import csv
import button
import random
import pygame
from pygame.transform import scale

# Inicializa o game
pygame.init()

# Set the screen size
SCREEN_WIDTH = 900
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

# Crie a tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Sam Atirador')

# Definir taxa de quadros
clock = pygame.time.Clock()
FPS = 60

# Variaveis do game
GRAVITY = 0.75
SCROLL_THRESH = 200
TILE_SIZE = 40
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILES_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False

# Variaveis ação do jogador
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# Carregar Imagens
# Carregar imagens do botão
start_png = pygame.image.load('img/start_btn.png').convert_alpha()
exit_png = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_png = pygame.image.load('img/restart_btn.png').convert_alpha()
# Carregar imagens de fundo
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
# armazenar peças em uma lista
img_list = []
for x in range(TILES_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
# bala
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
# Granada
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
# Caixas de itens
heal_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load(
    'img/icons/grenade_box.png').convert_alpha()

# Armazenar imagens em um dicionário
item_boxes = {
    'Health': heal_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# Definir cores
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Carregar fonte
font = pygame.font.SysFont('JetBrainsMono Nerd Font', 20)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT -
                    mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7,
                    SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8,
                    SCREEN_HEIGHT - pine2_img.get_height()))

# Resetar o nível


def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # cria lista de tiles vazio
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

# Classe do jogador


class Soldier(pygame.sprite.Sprite):
    # Inicializa o jogador
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # variáveis ​​específicas de IA
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # Carregar imagens de animação
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # Resetar a lista de temporária de imagens
            temp_list = []

            # Contar o número de arquivos no diretório
            num_of_frames = len(os.listdir(
                f'img/{self.char_type}/{animation}'))

            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(
                    img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    # Atualizar o jogador
    def update(self):
        self.update_animation()
        self.check_alive()

        # Atualizar cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    # Movimento do jogador
    def move(self, moving_left, moving_right):
        # Redefinir as variáveis de movimento
        screen_scroll = 0
        dx = 0
        dy = 0

        # Atribuir variáveis de movimento se estiver movendo para a esquerda ou para a direita
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Pulo
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # Aplicar gravidade
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # Checar colisão com o chão
        for tile in world.obstacle_list:
            # Checar colisão com o chão na direção x
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # se a IA atingir uma parede, faça-a virar
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # Checar colisão com o teto na direção y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # verifique se está abaixo do solo, ou seja, pulando
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # verifique se está acima do solo, ou seja, caindo
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # checar colisão com água
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # Checar colisão com a saída
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            # próximo nível
            level_complete = True

        # verifique se caiu no mapa
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # verifique se está saindo das bordas da tela
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # Atualizar posição do retângulo
        self.rect.x += dx
        self.rect.y += dy

        # Atualizar a posição do mapa
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    # Atirar
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(
                self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)

            # Reduzir munição
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50
            # Checar se o jogador está perto
            if self.vision.colliderect(player.rect):
                # Parar e atirar
                self.update_action(0)  # 0: idle

                # Atirar
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1

                    # Atualizar a visão
                    self.vision.center = (
                        self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # scroll do mapa
        self.rect.x += screen_scroll

    # Atualizar animação
    def update_animation(self):
        ANIMATION_COOLDOWN = 100

        # Atualizar imagem de animação
        self.image = self.animation_list[self.action][self.frame_index]

        # Verifique se passou tempo suficiente desde a última atualização
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # Se a animação terminar, reinicie
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # Verifique a nova ação
        if new_action != self.action:
            self.action = new_action

            # Atualizar as configurações da animação
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    # Desenhar o jogador na tela
    def draw(self):
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)

# Classe Mapa


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterar através de cada valor no arquivo de dados de nível
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)

                    if tile >= 0 and tile <= 8:  # parede
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:  # agua
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:  # decoração
                        decoration = Decoration(
                            img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:  # Cria o jogador
                        player = Soldier("player", x * TILE_SIZE,
                                         y * TILE_SIZE, 1.65, 5, 20, 5)
                        Health_bar = HealthBar(
                            10, 10, player.health, player.health)
                    elif tile == 16:  # criar inimigo
                        enemy = Soldier('enemy', x * TILE_SIZE,
                                        y * TILE_SIZE, 1.65, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:  # criar carixa de armas
                        item_box = ItemBox(
                            'Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:  # criar caixa de granadas
                        item_box = ItemBox(
                            'Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:  # criar caixa de saúde
                        item_box = ItemBox(
                            'Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
        return player, Health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

# Classe Decoração


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


# Classe Agua
class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


# Classe Sair
class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

# Classe Item Box


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y +
                            (TILE_SIZE // - self.image.get_height()))

    def update(self):
        # scroll
        self.rect.x += screen_scroll
        # checa se o jogador coletou a caixa de item
        if pygame.sprite.collide_rect(self, player):
            # verifique que tipo de caixa era
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3

            # remove a caixa de item
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # Atualizar com nova saúde
        self.health = health

        # Calcula a barra de saúde
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


# Classe da bala


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # Mover a bala
        self.rect.x += (self.direction * self.speed) + screen_scroll

        # Checar se a bala saiu da tela
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # Checar colisão com o mapa
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # Checar colisão com personagens
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

# Classe da granada


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # verifique a colisão com o nível
        for tile in world.obstacle_list:
            # verifique colisão com paredes
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # Checar colisão com o teto na direção y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # verifique se está abaixo do solo, ou seja pulando
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # verifique se está acima do solo, ou seja, caindo
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # verifique colisão com paredes
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        # atualizar posição da granada
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # temporizador de contagem regressiva
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            # causar danos a qualquer pessoa que esteja por perto
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50


# Classe da explosão
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(
                f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(
                img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # scroll
        self.rect.x += screen_scroll

        EXPLOSION_SPEED = 4

        # atualiza a animação da explosão
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1

            # se a animação da explosão terminar, então delete a explosão
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


# cria sprite do status do jogador
start_button = button.Button(
    SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_png, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110,
                            SCREEN_HEIGHT // 2 + 50, exit_png, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100,
                            SCREEN_HEIGHT // 2 - 50, restart_png, 2)

# Criar grupos de sprites
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Criar lista de tiles vazio
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# Carregar dados do nível e criar mundo
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
    # Limita a taxa de quadros
    clock.tick(FPS)

    # Start game
    if start_game == False:
        # Cria tela inicial (MENU)
        screen.fill(BG)

        # Adiciona botão de início
        if start_button.draw(screen):
            start_game = True
        # Adiciona botão de saída
        if exit_button.draw(screen):
            run = False
    else:
        # Criar o fundo
        draw_bg()

        # Cria o mapa
        world.draw()

        # mostra a vida
        health_bar.draw(player.health)

        # mostra a munição
        draw_text('Munição: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (110 + (x * 10), 45))
        # mostra as granadas
        draw_text('Granadas: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (120 + (x * 15), 68))

        # Atualiza player na tela
        player.update()
        player.draw()

        # Atualiza inimigo na tela
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        # Atualiza a tela após desenhar
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()

        # Desenhar grupos de sprites
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        # Movimento do jogador
        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (
                    0.6 * player.rect.size[0] * player.direction), player.rect.top, player.direction)
                grenade_group.add(grenade)

                # Reduzir granadas
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)  # 2: jump
            elif moving_left or moving_right:
                player.update_action(1)  # 1: run
            else:
                player.update_action(0)  # 0: idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

            # se o jogador completou o nível
            if level_complete:
                start_game = False
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # Carregar dados do nível e criar mundo
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
        else:
            screen_scroll = 0
            if restart_button.draw(screen):
                # resetar o jogo e o nível
                bg_scroll = 0
                world_data = reset_level()
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar = world.process_data(world_data)

    # Atualiza a tela

    for event in pygame.event.get():
        # Sai do game
        if event.type == pygame.QUIT:
            run = False

        # Teclas pressionadas
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        # Botão do teclado liberado
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                player.jump = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    # Atualiza a tela
    pygame.display.update()

# Fecha o game
pygame.quit()
