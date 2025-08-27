import pygame
import sys
import random
import os

# oni.pyから鬼の移動アルゴリズムを読み込む
from oni import get_oni_next_move

# 初期化
pygame.init()

# グリッド設定
GRID_SIZE = 60
GRID_WIDTH = 10
GRID_HEIGHT = 10
WIDTH = GRID_WIDTH * GRID_SIZE
HEIGHT = GRID_HEIGHT * GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Oni Chase Game")

# 色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG_GREEN = (85, 107, 47)
RED = (255, 0, 0) 

# --- 画像読み込み ---
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OVERLAP_SIZE = 90
    OHTERS_SIZE = GRID_SIZE
    OFFSET = (OVERLAP_SIZE - GRID_SIZE) // 2

    grass_tile = pygame.image.load(os.path.join(BASE_DIR, "grass_tile.png")).convert_alpha()
    grass_tile = pygame.transform.scale(grass_tile, (OVERLAP_SIZE, OVERLAP_SIZE))
    grass_bush = pygame.image.load(os.path.join(BASE_DIR, "grass_bush.png")).convert_alpha()
    grass_bush = pygame.transform.scale(grass_bush, (OVERLAP_SIZE, OVERLAP_SIZE))
    hero_img = pygame.image.load(os.path.join(BASE_DIR, "hero.png")).convert_alpha()
    hero_img = pygame.transform.scale(hero_img, (OHTERS_SIZE, OHTERS_SIZE))
    rock_img = pygame.image.load(os.path.join(BASE_DIR, "rock.png")).convert_alpha()
    rock_img = pygame.transform.scale(rock_img, (OHTERS_SIZE, OHTERS_SIZE))
    oni_img = pygame.image.load(os.path.join(BASE_DIR, "oni.png")).convert_alpha()
    oni_img = pygame.transform.scale(oni_img, (OHTERS_SIZE, OHTERS_SIZE))

    start_bg_img = pygame.image.load(os.path.join(BASE_DIR, "GAMESTART_SCREEN.png")).convert()
    start_bg_img = pygame.transform.scale(start_bg_img, (WIDTH, HEIGHT))

    copyright_img_original = pygame.image.load(os.path.join(BASE_DIR, "copyright.png")).convert_alpha()
    copyright_width = 150
    copyright_height = int(copyright_img_original.get_height() * (copyright_width / copyright_img_original.get_width()))
    copyright_img = pygame.transform.scale(copyright_img_original, (copyright_width, copyright_height))

    press_enter_img_original = pygame.image.load(os.path.join(BASE_DIR, "PRESS_ENTER.png")).convert_alpha()
    press_enter_width = 250
    press_enter_height = int(press_enter_img_original.get_height() * (press_enter_width / press_enter_img_original.get_width()))
    press_enter_img = pygame.transform.scale(press_enter_img_original, (press_enter_width, press_enter_height))

    # ▼▼▼【変更】葉っぱの画像を読み込む ▼▼▼
    leaf_img_original = pygame.image.load(os.path.join(BASE_DIR, "leaf.png")).convert_alpha()
    leaf_img = pygame.transform.scale(leaf_img_original, (50, 50)) # 葉っぱのサイズを調整
    # ▲▲▲【変更】ここまで ▲▲▲

except pygame.error as e:
    print(f"画像の読み込みに失敗しました: {e}")
    sys.exit()

# --- フォント・テキスト準備 (ゲームオーバー画面用) ---
game_over_font = pygame.font.Font(None, 100)
info_font = pygame.font.Font(None, 50)
game_over_text = game_over_font.render("GAME OVER", True, RED)
game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
restart_text = info_font.render("Press SPACE to Restart", True, WHITE)
restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))

# --- グローバル変数 (ゲームの状態を保持) ---
player_x, player_y = 0, 0
oni_x, oni_y = 0, 0
field = []
last_move_time = 0
oni_last_move_time = 0
MODE = "START_SCREEN"

# --- ゲームの初期化/リセットを行う関数 ---
def reset_game():
    global player_x, player_y, oni_x, oni_y, field, last_move_time, oni_last_move_time
    player_x, player_y = GRID_WIDTH // 2, GRID_HEIGHT // 2
    field = [[{"type": "grass", "bush": False} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    rocks_set = set()
    while len(rocks_set) < random.randint(5, 10):
        rx, ry = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        if (rx, ry) != (player_x, player_y):
            field[ry][rx]["type"] = "rock"
            rocks_set.add((rx, ry))
    while True:
        oni_x, oni_y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        distance = abs(oni_x - player_x) + abs(oni_y - player_y)
        if (oni_x, oni_y) != (player_x, player_y) and field[oni_y][oni_x]["type"] != "rock" and distance >= 3:
            break
    last_move_time = 0
    oni_last_move_time = 0

# ▼▼▼【変更】葉っぱのクラスを定義 ▼▼▼
class Leaf:
    def __init__(self):
        # 画面右上付近からランダムな位置で生成
        self.x = random.randint(WIDTH // 2, WIDTH + 50) 
        self.y = random.randint(-50, 0)
        self.speed_x = random.uniform(-1.5, 0.5) # 右下への流れと左右の揺れ
        self.speed_y = random.uniform(0.5, 2.0)
        self.rotation = random.uniform(0, 360) # 初期回転角度
        self.rotation_speed = random.uniform(-3, 3) # 回転速度

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rotation += self.rotation_speed
        if self.rotation > 360:
            self.rotation -= 360
        elif self.rotation < 0:
            self.rotation += 360

    def draw(self, surface):
        rotated_leaf = pygame.transform.rotate(leaf_img, self.rotation)
        # 回転した画像の中心が元の位置になるように調整
        leaf_rect = rotated_leaf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_leaf, leaf_rect)

# ▲▲▲【変更】ここまで ▲▲▲

# メインループ
clock = pygame.time.Clock()
move_interval = 150 
oni_move_interval = 500

blink_interval = 500  # 点滅間隔（ミリ秒）
last_blink_time = 0
show_press_enter = True

# ▼▼▼【変更】葉っぱのリストと生成タイマーを追加 ▼▼▼
leaves = []
leaf_spawn_interval = 600 # 葉っぱを生成する間隔（ミリ秒）
last_leaf_spawn_time = 0
# ▲▲▲【変更】ここまで ▲▲▲

while True:
    # --- イベント処理 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if MODE == "START_SCREEN" and event.key == pygame.K_SPACE:
                reset_game()
                MODE = "PLAYING"
            elif MODE == "GAME_OVER" and event.key == pygame.K_SPACE:
                MODE = "START_SCREEN"

    # --- モード別の処理 ---
    if MODE == "START_SCREEN":
        current_time = pygame.time.get_ticks()

        # 点滅ロジック
        if current_time - last_blink_time > blink_interval:
            show_press_enter = not show_press_enter
            last_blink_time = current_time
        
        screen.blit(start_bg_img, (0, 0))
        
        # ▼▼▼【変更】葉っぱの更新と描画ロジックを追加 ▼▼▼
        # 葉っぱを生成
        if current_time - last_leaf_spawn_time > leaf_spawn_interval:
            leaves.append(Leaf())
            last_leaf_spawn_time = current_time

        # 葉っぱの更新
        for leaf in leaves[:]: # リストをイテレート中に削除できるようにスライスコピー
            leaf.update()
            # 画面外に出たら削除
            if leaf.y > HEIGHT + 50 or leaf.x < -50 or leaf.x > WIDTH + 50:
                leaves.remove(leaf)

        # 葉っぱの描画
        for leaf in leaves:
            leaf.draw(screen)
        # ▲▲▲【変更】ここまで ▲▲▲

        copyright_rect = copyright_img.get_rect(centerx=WIDTH // 2, bottom=HEIGHT - 10)
        screen.blit(copyright_img, copyright_rect)

        if show_press_enter:
            press_enter_rect = press_enter_img.get_rect(centerx=WIDTH // 2, bottom=copyright_rect.top - 10)
            screen.blit(press_enter_img, press_enter_rect)
    
    elif MODE == "PLAYING":
        current_time = pygame.time.get_ticks()

        # プレイヤー移動
        keys = pygame.key.get_pressed()
        if current_time - last_move_time > move_interval:
            new_x, new_y = player_x, player_y
            if keys[pygame.K_w] and player_y > 0: new_y -= 1
            elif keys[pygame.K_s] and player_y < GRID_HEIGHT - 1: new_y += 1
            elif keys[pygame.K_a] and player_x > 0: new_x -= 1
            elif keys[pygame.K_d] and player_x < GRID_WIDTH - 1: new_x += 1
            if (new_x, new_y) != (player_x, player_y) and field[new_y][new_x]["type"] != "rock":
                player_x, player_y = new_x, new_y
                last_move_time = current_time

        # 鬼の移動
        if current_time - oni_last_move_time > oni_move_interval:
            bfs_map = ["".join(["#" if cell["type"] == "rock" else "." for cell in row]) for row in field]
            oni_x, oni_y = get_oni_next_move(bfs_map, (oni_x, oni_y), (player_x, player_y))
            oni_last_move_time = current_time

        # 当たり判定
        if (oni_x, oni_y) == (player_x, player_y):
            MODE = "GAME_OVER"

        # 描画 (プレイ中)
        screen.fill(BG_GREEN) 
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = field[y][x]
                if cell["type"] == "grass":
                    screen.blit(grass_tile, (x * GRID_SIZE - OFFSET, y * GRID_SIZE - OFFSET))
                    if cell["bush"]:
                        screen.blit(grass_bush, (x * GRID_SIZE - OFFSET, y * GRID_SIZE - OFFSET))
                elif cell["type"] == "rock":
                    screen.blit(rock_img, (x * GRID_SIZE, y * GRID_SIZE))

        for x in range(0, WIDTH, GRID_SIZE): pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE): pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))

        screen.blit(hero_img, (player_x * GRID_SIZE, player_y * GRID_SIZE))
        screen.blit(oni_img, (oni_x * GRID_SIZE, oni_y * GRID_SIZE))
    
    elif MODE == "GAME_OVER":
        screen.blit(game_over_text, game_over_rect)
        screen.blit(restart_text, restart_rect)

    # --- 画面更新 ---
    pygame.display.flip()
    clock.tick(60)