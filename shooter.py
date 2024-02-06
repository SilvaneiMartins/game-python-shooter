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

# Definir cores
BG = (144, 201, 120)
RED = (255, 0, 0)

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

# Classe do jogador
class Soldier(pygame.sprite.Sprite):
    # Inicializa o jogador
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
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
        animation_types = ['Idle', 'Run', 'Jump']
        for animation in animation_types:
            # Resetar a lista de temporária de imagens
            temp_list = []

            # Contar o número de arquivos no diretório
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))

            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    # Atualizar o jogador
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
            self.frame_index = 0

    def update_action(self, new_action):
        # Verifique a nova ação
        if new_action != self.action:
            self.action = new_action

            # Atualizar as configurações da animação
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    # Desenhar o jogador na tela
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

# Cria o jogador
player = Soldier("player", 200, 200, 3, 5)
enemy = Soldier("enemy", 400, 200, 3, 5)

run = True
while run:
    # Limita a taxa de quadros
    clock.tick(FPS)

    # Desenha o fundo
    draw_bg()

    # Atualiza a tela
    player.update_animation()
    player.draw()
    enemy.draw()

    # Movimento do jogador
    if player.alive:
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

    # Atualiza a tela
    pygame.display.update()

# Fecha o game
pygame.quit()
