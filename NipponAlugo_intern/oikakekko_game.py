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
pygame.display.set_caption("Grid Greed")

# 色
BLACK, WHITE, BG_GREEN, RED, YELLOW = (0,0,0), (255,255,255), (85,107,47), (255,0,0), (255,255,0)

# UI画像のスケールファクターを定義
UI_SCALE_FACTOR_DISPLAY = 0.15
UI_SCALE_FACTOR = 0.07

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
    leaf_img_original = pygame.image.load(os.path.join(BASE_DIR, "leaf.png")).convert_alpha()
    leaf_img = pygame.transform.scale(leaf_img_original, (50, 50))
    coin_img = pygame.image.load(os.path.join(BASE_DIR, "coin.png")).convert_alpha()
    coin_img = pygame.transform.scale(coin_img, (GRID_SIZE * 0.9, GRID_SIZE * 0.9))
    rope_img = pygame.image.load(os.path.join(BASE_DIR, "rope.png")).convert_alpha()
    coin_display_img = pygame.image.load(os.path.join(BASE_DIR, "coin_display.png")).convert_alpha()
    coin_display_img = pygame.transform.scale_by(coin_display_img, UI_SCALE_FACTOR_DISPLAY)
    number_images = []
    for i in range(21):
        img = pygame.image.load(os.path.join(BASE_DIR, f"number_{i}.png")).convert_alpha()
        img = pygame.transform.scale_by(img, UI_SCALE_FACTOR)
        number_images.append(img)
    slash_img = pygame.image.load(os.path.join(BASE_DIR, "slash.png")).convert_alpha()
    slash_img = pygame.transform.scale_by(slash_img, UI_SCALE_FACTOR)

except pygame.error as e:
    print(f"画像の読み込みに失敗しました: {e}")
    sys.exit()

# --- フォント・テキスト準備 ---
game_over_font, info_font = pygame.font.Font(None, 100), pygame.font.Font(None, 50)
game_over_text = game_over_font.render("GAME OVER", True, RED)
game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
restart_text = info_font.render("Press SPACE to Restart", True, WHITE)
restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
stage_clear_text = game_over_font.render("STAGE CLEAR!", True, YELLOW)
stage_clear_rect = stage_clear_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# --- グローバル変数 ---
player_x, player_y = 0, 0
field, last_move_time, coin_count = [], 0, 0
rope_pos = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
rope = None
oni_list = [] # ▼▼▼【変更】鬼のリストを追加 ▼▼▼
MODE = "START_SCREEN"

# ▼▼▼【変更】鬼をクラスで管理する ▼▼▼
class Oni:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.move_interval = random.randint(450, 650) # 鬼ごとに少し速度を変える
        self.last_move_time = 0
        self.image = oni_img

    def update_position(self, bfs_map, player_pos):
        next_pos = get_oni_next_move(bfs_map, (self.x, self.y), player_pos)
        self.x, self.y = next_pos

    def draw(self, surface):
        surface.blit(self.image, (self.x * GRID_SIZE, self.y * GRID_SIZE))
# ▲▲▲【変更】ここまで ▲▲▲

class Rope:
    def __init__(self, x_pixel, target_y_pixel):
        self.x, self.target_y, self.end_y = x_pixel, target_y_pixel, 0
        self.speed, self.finished = 8, False
        self.image = rope_img
    def update(self):
        if not self.finished: self.end_y = min(self.target_y, self.end_y + self.speed)
        if self.end_y == self.target_y: self.finished = True
    def draw(self, surface):
        if self.end_y > 0:
            scaled_rope = pygame.transform.scale(self.image, (self.image.get_width(), self.end_y))
            draw_x = self.x - scaled_rope.get_width() // 2
            surface.blit(scaled_rope, (draw_x, 0))

def reset_game():
    global player_x, player_y, field, last_move_time, coin_count, rope, oni_list
    player_x, player_y = rope_pos; coin_count = 0; rope = None
    oni_list = [] # 鬼のリストをリセット

    field = [[{"type": "grass", "bush": False, "coin": False} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    occupied_positions = {(player_x, player_y)} # プレイヤーの位置を占有済みとする

    rocks_set = set()
    while len(rocks_set) < random.randint(5, 10):
        rx, ry = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        if (rx, ry) not in occupied_positions:
            field[ry][rx]["type"] = "rock"; rocks_set.add((rx, ry)); occupied_positions.add((rx, ry))
    
    coins_placed = 0
    while coins_placed < 20:
        cx, cy = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        if (cx, cy) not in occupied_positions and not field[cy][cx]["coin"]:
            field[cy][cx]["coin"] = True; coins_placed += 1
    
    # ▼▼▼【変更】鬼を2体生成する ▼▼▼
    for _ in range(2):
        while True:
            ox, oy = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            distance = abs(ox - player_x) + abs(oy - player_y)
            if (ox, oy) not in occupied_positions and distance >= 3:
                oni_list.append(Oni(ox, oy))
                occupied_positions.add((ox, oy))
                break
    # ▲▲▲【変更】ここまで ▲▲▲

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if field[y][x]["type"] == "grass" and random.random() < 0.1: field[y][x]["bush"] = True
            if 0 <= y - 1 and field[y - 1][x]["bush"] and random.random() < 0.4: field[y][x]["bush"] = True
            if 0 <= x - 1 and field[y][x - 1]["bush"] and random.random() < 0.4: field[y][x]["bush"] = True
    
    last_move_time = 0

class Leaf:
    def __init__(self):
        self.x, self.y = random.randint(WIDTH // 2, WIDTH + 50), random.randint(-50, 0)
        self.speed_x, self.speed_y = random.uniform(-1.5, 0.5), random.uniform(0.5, 2.0)
        self.rotation, self.rotation_speed = random.uniform(0, 360), random.uniform(-3, 3)
    def update(self):
        self.x += self.speed_x; self.y += self.speed_y; self.rotation += self.rotation_speed
        if self.rotation > 360: self.rotation -= 360
        elif self.rotation < 0: self.rotation += 360
    def draw(self, surface):
        rotated_leaf = pygame.transform.rotate(leaf_img, self.rotation)
        leaf_rect = rotated_leaf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_leaf, leaf_rect)

def draw_coin_counter(surface, count):
    start_x = 10
    surface.blit(coin_display_img, (start_x, 10))
    current_x = start_x + coin_display_img.get_width() + 5
    count_str = str(count)
    if not count_str: count_str = "0"
    for digit in count_str:
        num_img = number_images[int(digit)]
        surface.blit(num_img, (current_x, 23))
        current_x += num_img.get_width() + 2
    surface.blit(slash_img, (current_x, 23))
    current_x += slash_img.get_width() + 2
    total_str = "20"
    for digit in total_str:
        num_img = number_images[int(digit)]
        surface.blit(num_img, (current_x, 23))
        current_x += num_img.get_width() + 2

# メインループ
clock = pygame.time.Clock()
MOVE_INTERVAL_NORMAL, MOVE_INTERVAL_SLOW = 150, 600
blink_interval, leaf_spawn_interval = 500, 600
last_blink_time, last_leaf_spawn_time = 0, 0
show_press_enter, leaves = True, []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if MODE == "START_SCREEN" and event.key == pygame.K_SPACE:
                reset_game(); MODE = "PLAYING"
            elif (MODE == "GAME_OVER" or MODE == "STAGE_CLEAR") and event.key == pygame.K_SPACE:
                MODE = "START_SCREEN"

    if MODE == "START_SCREEN":
        current_time = pygame.time.get_ticks()
        if current_time - last_blink_time > blink_interval:
            show_press_enter = not show_press_enter; last_blink_time = current_time
        if current_time - last_leaf_spawn_time > leaf_spawn_interval:
            leaves.append(Leaf()); last_leaf_spawn_time = current_time
        for leaf in leaves[:]:
            leaf.update()
            if not (-50 < leaf.x < WIDTH + 50 and -50 < leaf.y < HEIGHT + 50): leaves.remove(leaf)
        screen.blit(start_bg_img, (0, 0))
        for leaf in leaves: leaf.draw(screen)
        copyright_rect = copyright_img.get_rect(centerx=WIDTH // 2, bottom=HEIGHT - 10)
        screen.blit(copyright_img, copyright_rect)
        if show_press_enter:
            press_enter_rect = press_enter_img.get_rect(centerx=WIDTH // 2, bottom=copyright_rect.top - 10)
            screen.blit(press_enter_img, press_enter_rect)
    
    elif MODE == "PLAYING":
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        current_move_interval = MOVE_INTERVAL_SLOW if field[player_y][player_x]["bush"] else MOVE_INTERVAL_NORMAL
        if current_time - last_move_time > current_move_interval:
            new_x, new_y = player_x, player_y
            if keys[pygame.K_w] and player_y > 0: new_y -= 1
            elif keys[pygame.K_s] and player_y < GRID_HEIGHT - 1: new_y += 1
            elif keys[pygame.K_a] and player_x > 0: new_x -= 1
            elif keys[pygame.K_d] and player_x < GRID_WIDTH - 1: new_x += 1
            if (new_x, new_y) != (player_x, player_y) and field[new_y][new_x]["type"] != "rock":
                player_x, player_y = new_x, new_y; last_move_time = current_time
        if field[player_y][player_x]["coin"]:
            field[player_y][player_x]["coin"] = False; coin_count += 1
            if coin_count >= 15 and rope is None:
                rope = Rope(rope_pos[0] * GRID_SIZE + GRID_SIZE // 2, rope_pos[1] * GRID_SIZE + GRID_SIZE // 2)
        if rope and rope.finished and (player_x, player_y) == rope_pos:
            MODE = "STAGE_CLEAR"
        if rope: rope.update()
        
        # ▼▼▼【変更】すべての鬼をループで処理 ▼▼▼
        bfs_map = ["".join(["#" if cell["type"] == "rock" else "." for cell in row]) for row in field]
        for oni in oni_list:
            if current_time - oni.last_move_time > oni.move_interval:
                oni.update_position(bfs_map, (player_x, player_y))
                oni.last_move_time = current_time
            if (oni.x, oni.y) == (player_x, player_y):
                MODE = "GAME_OVER"
                break # 一体でも捕まったらループを抜ける
        # ▲▲▲【変更】ここまで ▲▲▲

        # 描画 (プレイ中)
        screen.fill(BG_GREEN) 
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = field[y][x]
                if cell["type"] == "grass":
                    screen.blit(grass_tile, (x * GRID_SIZE - OFFSET, y * GRID_SIZE - OFFSET))
                    if cell["bush"]: screen.blit(grass_bush, (x * GRID_SIZE - OFFSET, y * GRID_SIZE - OFFSET))
                elif cell["type"] == "rock": screen.blit(rock_img, (x * GRID_SIZE, y * GRID_SIZE))
                if cell["coin"]:
                    coin_rect = coin_img.get_rect(center=(x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2))
                    screen.blit(coin_img, coin_rect)
        if rope: rope.draw(screen)
        for x in range(0, WIDTH, GRID_SIZE): pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE): pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))
        screen.blit(hero_img, (player_x * GRID_SIZE, player_y * GRID_SIZE))
        # ▼▼▼【変更】すべての鬼を描画 ▼▼▼
        for oni in oni_list:
            oni.draw(screen)
        # ▲▲▲【変更】ここまで ▲▲▲
        draw_coin_counter(screen, coin_count)

    elif MODE == "GAME_OVER":
        screen.blit(game_over_text, game_over_rect); screen.blit(restart_text, restart_rect)
    elif MODE == "STAGE_CLEAR":
        screen.blit(stage_clear_text, stage_clear_rect); screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(60)