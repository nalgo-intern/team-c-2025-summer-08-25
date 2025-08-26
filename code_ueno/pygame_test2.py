import pygame
import sys

# 初期化
pygame.init()

# 画面サイズとマス設定
CELL_SIZE = 50
GRID_WIDTH, GRID_HEIGHT = 16, 12  # 16x12マス
WIDTH, HEIGHT = CELL_SIZE * GRID_WIDTH, CELL_SIZE * GRID_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("test2")

# プレイヤー設定
player_color = (0, 128, 255)
player_x, player_y = 5, 5  # マス座標
player_size = CELL_SIZE

# 障害物の設定（マス座標で指定）
obstacles = [(7, 5), (10, 8), (3, 3)]

# ゲームループ
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # キーを押したときにだけ反応する
        if event.type == pygame.KEYDOWN:
            new_x, new_y = player_x, player_y
            if event.key == pygame.K_w:
                new_y -= 1
            if event.key == pygame.K_s:
                new_y += 1
            if event.key == pygame.K_a:
                new_x -= 1
            if event.key == pygame.K_d:
                new_x += 1

            # 移動先が範囲内で、かつ障害物でなければ移動
            if (0 <= new_x < GRID_WIDTH and 
                0 <= new_y < GRID_HEIGHT and 
                (new_x, new_y) not in obstacles):
                player_x, player_y = new_x, new_y

    # 描画
    screen.fill((30, 30, 30))  # 背景色

    # グリッド線を描画
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (80, 80, 80), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, (80, 80, 80), (0, y), (WIDTH, y))

    # 障害物の描画
    for (ox, oy) in obstacles:
        pygame.draw.rect(screen, (200, 50, 50), (ox * CELL_SIZE, oy * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # プレイヤー描画
    pygame.draw.rect(
        screen,
        player_color,
        (player_x * CELL_SIZE, player_y * CELL_SIZE, player_size, player_size)
    )

    pygame.display.flip()
    clock.tick(60)  # 60FPS
