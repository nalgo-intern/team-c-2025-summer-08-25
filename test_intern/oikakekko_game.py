import pygame
import sys
import random
from stable_baselines3 import PPO

# oni.pyから鬼の移動アルゴリズムを読み込む
from oni import get_oni_next_move

# 初期化
pygame.init()

# --- 環境とモデルの読み込み ---
# oni.py 内でモデルをロードするため、ここでは不要です。
# ただし、ani.pyがモデルを見つけられるように、パスを確認してください。

# --- グリッドの設定 ---
GRID_SIZE = 50
GRID_WIDTH = 10
GRID_HEIGHT = 10
WIDTH = GRID_WIDTH * GRID_SIZE
HEIGHT = GRID_HEIGHT * GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Chase Game")

# --- 色 ---
BLACK = (0, 0, 0)
BG_GREEN = (85, 107, 47)
RED = (255, 0, 0) # ゲームオーバー用に赤色を追加

# --- 画像読み込み ---
# 画像ファイルが存在しない場合でも動くように、エラーハンドリングを追加
try:
    OVERLAP_SIZE = 90
    OHTERS_SIZE = GRID_SIZE
    OFFSET = (OVERLAP_SIZE - GRID_SIZE) // 2
    grass_tile = pygame.image.load("grass_tile.png").convert_alpha()
    grass_tile = pygame.transform.scale(grass_tile, (OVERLAP_SIZE, OVERLAP_SIZE))
    grass_bush = pygame.image.load("grass_bush.png").convert_alpha()
    grass_bush = pygame.transform.scale(grass_bush, (OVERLAP_SIZE, OVERLAP_SIZE))
    hero_img = pygame.image.load("hero.png").convert_alpha()
    hero_img = pygame.transform.scale(hero_img, (OHTERS_SIZE, OHTERS_SIZE))
    rock_img = pygame.image.load("rock.png").convert_alpha()
    rock_img = pygame.transform.scale(rock_img, (OHTERS_SIZE, OHTERS_SIZE))
    oni_img = pygame.image.load("oni.png").convert_alpha()
    oni_img = pygame.transform.scale(oni_img, (OHTERS_SIZE, OHTERS_SIZE))
except pygame.error as e:
    print(f"画像ファイルのロード中にエラーが発生しました: {e}")
    print("ゲームは続行しますが、画像は表示されません。")
    # 代替の描画用Surfaceを作成
    grass_tile = pygame.Surface((OVERLAP_SIZE, OVERLAP_SIZE)); grass_tile.fill(BG_GREEN)
    grass_bush = pygame.Surface((OVERLAP_SIZE, OVERLAP_SIZE)); grass_bush.fill((0, 100, 0))
    hero_img = pygame.Surface((OHTERS_SIZE, OHTERS_SIZE)); hero_img.fill((0, 0, 255))
    rock_img = pygame.Surface((OHTERS_SIZE, OHTERS_SIZE)); rock_img.fill((128, 128, 128))
    oni_img = pygame.Surface((OHTERS_SIZE, OHTERS_SIZE)); oni_img.fill(RED)


# フィールド情報を二次元リストで作成
field = []
for y in range(GRID_HEIGHT):
    row = []
    for x in range(GRID_WIDTH):
        cell = {"type": "grass", "bush": False}
        row.append(cell)
    field.append(row)

# プレイヤーと鬼の初期位置をランダムに設定
while True:
    player_x = random.randint(0, GRID_WIDTH - 1)
    player_y = random.randint(0, GRID_HEIGHT - 1)
    oni_x = random.randint(0, GRID_WIDTH - 1)
    oni_y = random.randint(0, GRID_HEIGHT - 1)
    if (player_x, player_y) != (oni_x, oni_y):
        break

# ランダムに岩を配置
num_rocks = random.randint(5, 10)
rocks_set = set()
while len(rocks_set) < num_rocks:
    rx = random.randint(0, GRID_WIDTH - 1)
    ry = random.randint(0, GRID_HEIGHT - 1)
    # プレイヤーと鬼の初期位置と被らないようにチェック
    if (rx, ry) not in [(player_x, player_y), (oni_x, oni_y)]:
        field[ry][rx]["type"] = "rock"
        rocks_set.add((rx, ry))

# 草むらを10%の確率で追加
for y in range(GRID_HEIGHT):
    for x in range(GRID_WIDTH):
        if field[y][x]["type"] == "grass" and random.random() < 0.1:
            field[y][x]["bush"] = True
        if 0 <= y - 1 and field[y - 1][x]["bush"] == True and random.random() < 0.4:
            field[y][x]["bush"] = True
        if 0 <= x - 1 and field[y][x - 1]["bush"] == True and random.random() < 0.4:
            field[y][x]["bush"] = True  

# ゲームオーバー用のフォントを準備
game_over_font = pygame.font.Font(None, 100)
game_over_text = game_over_font.render("GAME OVER", True, RED)
game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# メインループ
clock = pygame.time.Clock()
move_interval = 150 
last_move_time = 0
oni_move_interval = 500
oni_last_move_time = 0
game_over = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # ゲームオーバーでなければ、キャラクターの移動処理を行う
    if not game_over:
        current_time = pygame.time.get_ticks()

        # --- プレイヤーの移動処理 ---
        keys = pygame.key.get_pressed()
        if current_time - last_move_time > move_interval:
            new_x, new_y = player_x, player_y
            if keys[pygame.K_w] and player_y > 0: new_y -= 1
            elif keys[pygame.K_s] and player_y < GRID_HEIGHT - 1: new_y += 1
            elif keys[pygame.K_a] and player_x > 0: new_x -= 1
            elif keys[pygame.K_d] and player_x < GRID_WIDTH - 1: new_x += 1
            
            if (new_x, new_y) != (player_x, player_y):
                if field[new_y][new_x]["type"] != "rock":
                    player_x, player_y = new_x, new_y
                last_move_time = current_time

        # --- 鬼の移動処理 ---
        if current_time - oni_last_move_time > oni_move_interval:
            # oni.pyの関数が読み込める形式にマップを変換
            map_data_for_oni = []
            for y in range(GRID_HEIGHT):
                row_str = ""
                for x in range(GRID_WIDTH):
                    if field[y][x]["type"] == "rock":
                        row_str += "#"
                    else:
                        row_str += "."
                map_data_for_oni.append(row_str)

            oni_next_position = get_oni_next_move(map_data_for_oni, (oni_x, oni_y), (player_x, player_y))
            oni_x, oni_y = oni_next_position
            oni_last_move_time = current_time

        # --- 当たり判定（ゲームオーバー処理） ---
        if (oni_x, oni_y) == (player_x, player_y):
            print("ゲームオーバー！鬼に捕まりました。")
            game_over = True
    
    # --- 描画処理 ---
    screen.fill(BG_GREEN) 
    # グリッド描画
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            cell = field[y][x]
            blit_pos = (x * GRID_SIZE - OFFSET, y * GRID_SIZE - OFFSET)
            screen.blit(grass_tile, blit_pos)
            if cell["bush"]:
                screen.blit(grass_bush, blit_pos)
            if cell["type"] == "rock":
                screen.blit(rock_img, (x * GRID_SIZE, y * GRID_SIZE))

    # グリッド線
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))

    # プレイヤーと鬼を描画
    screen.blit(hero_img, (player_x * GRID_SIZE, player_y * GRID_SIZE))
    screen.blit(oni_img, (oni_x * GRID_SIZE, oni_y * GRID_SIZE))

    # ゲームオーバー時に文字を描画
    if game_over:
        screen.blit(game_over_text, game_over_rect)
    
    pygame.display.flip()

    if game_over:
        pygame.time.wait(3000)
        break

    clock.tick(60)

# ゲームループが終了したら、Pygameを終了
pygame.quit()
sys.exit()
