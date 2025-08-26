import pygame
import sys
import random

# 初期化
pygame.init()

# グリッド設定
GRID_SIZE = 40
GRID_WIDTH = 10
GRID_HEIGHT = 10
WIDTH = GRID_WIDTH * GRID_SIZE
HEIGHT = GRID_HEIGHT * GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid with Rocks and Grass")

# 色
BLACK = (0, 0, 0)
# 背景色を茶色から緑に変更
BG_GREEN = (85, 107, 47) 

# プレイヤー初期位置
player_x, player_y = 0, 0


# --- ▼▼▼ 画像読み込み部分を修正 ▼▼▼ ---

# マス目より少し大きいサイズを定義
OVERLAP_SIZE = 70 
# 勇者と岩のサイズを変更
OHTERS_SIZE = GRID_SIZE
# 中央に配置するためのズレを計算
OFFSET = (OVERLAP_SIZE - GRID_SIZE) // 2

# 草タイルを少し大きくリサイズ
grass_tile = pygame.image.load("grass_tile.png").convert_alpha()
grass_tile = pygame.transform.scale(grass_tile, (OVERLAP_SIZE, OVERLAP_SIZE))

# 草むらも合わせて少し大きくリサイズ
grass_bush = pygame.image.load("grass_bush.png").convert_alpha()
grass_bush = pygame.transform.scale(grass_bush, (OVERLAP_SIZE, OVERLAP_SIZE))

# 勇者はマス目ぴったりのサイズに
hero_img = pygame.image.load("hero.png").convert_alpha()
hero_img = pygame.transform.scale(hero_img, (OHTERS_SIZE, OHTERS_SIZE))

# 岩の画像を追加
rock_img = pygame.image.load("rock.png").convert_alpha()
# 岩はマス目ぴったりのサイズに
rock_img = pygame.transform.scale(rock_img, (OHTERS_SIZE, OHTERS_SIZE))

# --- ▲▲▲ 画像読み込み部分の修正ここまで ▲▲▲ ---


# フィールド情報を二次元リストで作成
field = []
for y in range(GRID_HEIGHT):
    row = []
    for x in range(GRID_WIDTH):
        cell = {"type": "grass", "bush": False}
        row.append(cell)
    field.append(row)

# ランダムに岩を配置
num_rocks = random.randint(5, 10)
rocks_set = set()
while len(rocks_set) < num_rocks:
    rx = random.randint(0, GRID_WIDTH - 1)
    ry = random.randint(0, GRID_HEIGHT - 1)
    if (rx, ry) != (player_x, player_y):
        field[ry][rx]["type"] = "rock"
        rocks_set.add((rx, ry))

# 草むらを10%の確率で追加（岩セルには追加しない）
for y in range(GRID_HEIGHT):
    for x in range(GRID_WIDTH):
        if field[y][x]["type"] == "grass" and random.random() < 0.1:
            field[y][x]["bush"] = True
        if 0 <= y - 1 and field[y - 1][x]["bush"] == True and random.random() < 0.4:
                field[y][x]["bush"] = True
        if 0 <= x - 1 and field[y][x - 1]["bush"] == True and random.random() < 0.4:
                field[y][x]["bush"] = True       

# メインループ
clock = pygame.time.Clock()

# 移動速度制御のための変数を追加
move_interval = 150  # 移動間隔（ミリ秒）。数値を小さくすると速くなる
last_move_time = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- ▼▼▼ ここから長押し移動の処理 ▼▼▼ ---

    # 現在の時間を取得
    current_time = pygame.time.get_ticks()
    # キーが押され続けているかを取得
    keys = pygame.key.get_pressed()

    # 前回の移動から一定時間が経過していたら、移動処理を行う
    if current_time - last_move_time > move_interval:
        new_x, new_y = player_x, player_y

        if keys[pygame.K_w] and player_y > 0:
            new_y -= 1
        elif keys[pygame.K_s] and player_y < GRID_HEIGHT - 1:
            new_y += 1
        elif keys[pygame.K_a] and player_x > 0:
            new_x -= 1
        elif keys[pygame.K_d] and player_x < GRID_WIDTH - 1:
            new_x += 1
        
        # 実際に移動があったかチェック
        if (new_x, new_y) != (player_x, player_y):
            # 岩の位置じゃなければ移動
            if field[new_y][new_x]["type"] != "rock":
                player_x, player_y = new_x, new_y
            
            # 移動があったので、最終移動時間を更新
            last_move_time = current_time

    # --- ▲▲▲ 長押し移動の処理ここまで ▲▲▲ ---


    # --- 描画 ---
    # 背景を緑色で塗りつぶす
    screen.fill(BG_GREEN) 
    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            cell = field[y][x]
            if cell["type"] == "grass":
                blit_pos = (x * GRID_SIZE - OFFSET, y * GRID_SIZE - OFFSET)
                screen.blit(grass_tile, blit_pos)
                if cell["bush"]:
                    screen.blit(grass_bush, blit_pos)
            elif cell["type"] == "rock":
                # 岩の下に草が描画されないように修正
                screen.blit(rock_img, (x * GRID_SIZE, y * GRID_SIZE))

    # プレイヤーはマス目の中に描画
    screen.blit(hero_img, (player_x * GRID_SIZE, player_y * GRID_SIZE))

    # グリッド線
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))

    pygame.display.flip()
    clock.tick(60)