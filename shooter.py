import os
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

# Variaveis ação do jogador
moving_left = False
moving_right = False
shoot = False

# Carregar Imagens
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()

# Definir cores
BG = (144, 201, 120)
RED = (255, 0, 0)

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

# Classe do jogador
class Soldier(pygame.sprite.Sprite):
    # Inicializa o jogador
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
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

        # Carregar imagens de animação
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # Resetar a lista de temporária de imagens
            temp_list = []

            # Contar o número de arquivos no diretório
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))

            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

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
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        # Atualizar posição do retângulo
        self.rect.x += dx
        self.rect.y += dy

    # Atirar
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)

            # Reduzir munição
            self.ammo -= 1

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
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

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
        self.rect.x += (self.direction * self.speed)

        # Checar se a bala saiu da tela
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # Checar colisão com personagens
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        if pygame.sprite.spritecollide(enemy, bullet_group, False):
            if enemy.alive:
                enemy.health -= 25
                self.kill()

# Criar grupos de sprites
bullet_group = pygame.sprite.Group()


# Cria o jogador
player = Soldier("player", 200, 200, 3, 5, 20)
enemy = Soldier("enemy", 400, 200, 3, 5, 20)

run = True
while run:
    # Limita a taxa de quadros
    clock.tick(FPS)

    # Desenha o fundo
    draw_bg()

    # Atualiza player na tela
    player.update()
    player.draw()

    # Atualiza inimigo na tela
    enemy.update()
    enemy.draw()

    # Atualiza a tela após desenhar
    bullet_group.update()
    bullet_group.draw(screen)

    # Movimento do jogador
    if player.alive:
        if shoot:
            player.shoot()
        if player.in_air:
            player.update_action(2)#2: jump
        elif moving_left or moving_right:
            player.update_action(1)#1: run
        else:
            player.update_action(0)#0: idle
        player.move(moving_left, moving_right)

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

    # Atualiza a tela
    pygame.display.update()

# Fecha o game
pygame.quit()
