import pygame
import sys

# 初期化
pygame.init()

# 画面サイズ
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("test")

# プレイヤー設定
player_size = 50
player_color = (0, 128, 255)
player_x, player_y = WIDTH // 2, HEIGHT // 2
player_speed = 5

# ゲームループ
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # キー入力の取得
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_y -= player_speed
    if keys[pygame.K_s]:
        player_y += player_speed
    if keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_d]:
        player_x += player_speed

    # 画面外に出ないように制御
    player_x = max(0, min(WIDTH - player_size, player_x))
    player_y = max(0, min(HEIGHT - player_size, player_y))

    # 描画
    screen.fill((30, 30, 30))  # 背景を黒に近い色に
    pygame.draw.rect(screen, player_color, (player_x, player_y, player_size, player_size))
    pygame.display.flip()

    clock.tick(60)  # 60FPS
