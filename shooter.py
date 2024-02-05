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

# Variaveis ação do jogador
moving_left = False
moving_right = False

# Definir cores
BG = (144, 201, 120)

def draw_bg():
    screen.fill(BG)

# Classe do jogador
class Soldier(pygame.sprite.Sprite):
    # Inicializa o jogador
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.flip = False
        img = pygame.image.load(f'img/{self.char_type}/Idle/0.png')
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
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

        # Atualizar posição do retângulo
        self.rect.x += dx
        self.rect.y += dy

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
    player.draw()
    enemy.draw()

    # Movimento do jogador
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
            if event.key == pygame.K_ESCAPE:
                run = False

        # Botão do teclado liberado
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False

    # Atualiza a tela
    pygame.display.update()

# Fecha o game
pygame.quit()
