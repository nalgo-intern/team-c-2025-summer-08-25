import pygame
import numpy as np
from stable_baselines3 import PPO
from oni_env import ChaseEnv

GRID_WIDTH = 10
GRID_HEIGHT = 10
CELL_SIZE = 50
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

WHITE = (255, 255, 255)
RED = (255, 0, 0)   # 敵
BLUE = (0, 0, 255)  # プレイヤー
BLACK = (0, 0, 0)   #岩

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("追いかけっこゲーム")
clock = pygame.time.Clock()

# -----------------------------
# 環境とモデルの読み込み
# -----------------------------
env = ChaseEnv(human_control = True)
model = PPO.load("model/oni_model", env=env)

# 初期化
obs, _ = env.reset()

# -----------------------------
# ゲームループ
# -----------------------------
running = True
while running:
    screen.fill(WHITE)
    
    # プレイヤー操作
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_w]:
        dy = -1
    if keys[pygame.K_s]:
        dy = 1
    if keys[pygame.K_a]:
        dx = -1
    if keys[pygame.K_d]:
        dx = 1
    
    next_player_pos = env.player_pos + np.array([dx, dy])

    # 岩にぶつからないように移動
    if (0 <= next_player_pos[0] < GRID_WIDTH) and (0 <= next_player_pos[1] < GRID_HEIGHT):
        if (next_player_pos[0], next_player_pos[1]) not in env.rocks:
            env.player_pos = next_player_pos

    # 敵キャラの行動
    action, _states = model.predict(obs)
    obs, reward, terminated, truncated, info = env.step(action)

    # 描画
    for rx, ry in env.rocks:
        pygame.draw.rect(screen, BLACK, (rx*CELL_SIZE, ry*CELL_SIZE, CELL_SIZE, CELL_SIZE))  # 岩
    
    pygame.draw.rect(screen, RED, (env.enemy_pos[0]*CELL_SIZE, env.enemy_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, BLUE, (env.player_pos[0]*CELL_SIZE, env.player_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    pygame.display.flip()
    clock.tick(5)

    # エピソード終了
    if terminated or truncated:
        obs, _ = env.reset()

pygame.quit()
