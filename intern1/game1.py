import pygame
import sys
import threading
import time

pygame.init()

# 画面サイズ
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame マス目")

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRID_COLOR = (200, 200, 200) # マス目の線の色

# マス目の設定
cell_size = 50
player_x = 50
player_y = 50
oni_x = 550
oni_y = 550
running = True

num_cols = screen_width // cell_size
num_rows = screen_height // cell_size
# イベントループ
def move_oni():
    global oni_x
    global oni_y
    global running
    while running:
        dx = player_x - oni_x
        dy = player_y - oni_y
        if abs(dx) > abs(dy):
            oni_x += 50 if dx > 0 else -50
        elif dy != 0:
            oni_y += 50 if dy > 0 else -50
        time.sleep(0.5)

oni_thread = threading.Thread(target=move_oni)
oni_thread.start()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and player_y > 0:
                player_y -= cell_size # 上に移動
            elif event.key == pygame.K_s and player_y < 550:
                player_y += cell_size # 下に移動
            elif event.key == pygame.K_a and player_x > 0:
                player_x -= cell_size # 左に移動
            elif event.key == pygame.K_d and player_x < 550:
                player_x += cell_size # 右に移動
    screen.fill(WHITE)
    for row in range(num_rows):
        for col in range(num_cols):
            pygame.draw.rect(screen, GRID_COLOR, (col * cell_size, row * cell_size, cell_size, cell_size), 1) # 枠線のみ描画
    pygame.draw.rect(screen, (0, 0, 255), (player_x, player_y, cell_size, cell_size))
    pygame.draw.rect(screen, (0, 255, 0), (oni_x, oni_y, cell_size, cell_size))
    if player_x == oni_x and player_y == oni_y:
        running = False
    # 画面を更新
    pygame.display.flip()
    
pygame.quit()