import pygame
import numpy as np
from stable_baselines3 import PPO
from enemy_env import ChaseEnv  # 自作環境

# -----------------------------
# 初期設定
# -----------------------------
GRID_SIZE = 10  # 10x10 グリッド
CELL_SIZE = 50  # 描画用1マスの大きさ
WINDOW_SIZE = GRID_SIZE * CELL_SIZE

# 色
WHITE = (255, 255, 255)
RED = (255, 0, 0)      # 敵キャラ
BLUE = (0, 0, 255)     # プレイヤー

# pygame 初期化
pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("追いかけっこゲーム")
clock = pygame.time.Clock()

# -----------------------------
# 環境とモデルの読み込み
# -----------------------------
env = ChaseEnv(player_controlled_by_human=True)
model = PPO.load("model\enemy_model", env=env)

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
    if keys[pygame.K_w]:
        env.player_pos[1] = max(0, env.player_pos[1]-1)
    if keys[pygame.K_s]:
        env.player_pos[1] = min(GRID_SIZE-1, env.player_pos[1]+1)
    if keys[pygame.K_a]:
        env.player_pos[0] = max(0, env.player_pos[0]-1)
    if keys[pygame.K_d]:
        env.player_pos[0] = min(GRID_SIZE-1, env.player_pos[0]+1)

    # 敵キャラの行動
    action, _states = model.predict(obs)
    obs, reward, terminated, truncated, info = env.step(action)

    # 描画
    # 敵
    pygame.draw.rect(screen, RED, (env.enemy_pos[0]*CELL_SIZE, env.enemy_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # プレイヤー
    pygame.draw.rect(screen, BLUE, (env.player_pos[0]*CELL_SIZE, env.player_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    pygame.display.flip()
    clock.tick(5)  # FPS 5

    # エピソード終了時
    if terminated or truncated:
        obs, _ = env.reset()

pygame.quit()
