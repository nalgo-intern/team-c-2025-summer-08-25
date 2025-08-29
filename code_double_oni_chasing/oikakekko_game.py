import pygame
import sys
import random
import os
import numpy as np
import math
import json
from stable_baselines3 import PPO

# stage_infoフォルダのパスをシステムパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'stage_info'))
from stage_info import Stage1, Stage2, Stage3

# 初期化
pygame.init()

# グリッド設定
GRID_SIZE = 60
GRID_WIDTH = 10
GRID_HEIGHT = 10
WIDTH = GRID_WIDTH * GRID_SIZE
HEIGHT = GRID_HEIGHT * GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid Greed with RL Oni")

# 色
BLACK, WHITE, BG_GREEN, RED, YELLOW = (0,0,0), (255,255,255), (85,107,47), (255,0,0), (255,255,0)
BUTTON_COLOR = (100, 100, 100)

# UI画像のスケールファクターを定義
UI_SCALE_FACTOR_DISPLAY = 0.15
UI_SCALE_FACTOR = 0.07
UI_PANEL_SCALE = 0.8

# --- 画像読み込み ---
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGE_DIR = os.path.join(BASE_DIR, "image")
    OVERLAP_SIZE = 90
    OHTERS_SIZE = GRID_SIZE
    OFFSET = (OVERLAP_SIZE - GRID_SIZE) // 2

    grass_tile = pygame.image.load(os.path.join(IMAGE_DIR, "grass_tile.png")).convert_alpha()
    grass_tile = pygame.transform.scale(grass_tile, (OVERLAP_SIZE, OVERLAP_SIZE))
    grass_bush = pygame.image.load(os.path.join(IMAGE_DIR, "grass_bush.png")).convert_alpha()
    grass_bush = pygame.transform.scale(grass_bush, (OVERLAP_SIZE, OVERLAP_SIZE))
    hero_img = pygame.image.load(os.path.join(IMAGE_DIR, "hero.png")).convert_alpha()
    hero_img = pygame.transform.scale(hero_img, (OHTERS_SIZE, OHTERS_SIZE))
    rock_img = pygame.image.load(os.path.join(IMAGE_DIR, "rock.png")).convert_alpha()
    rock_img = pygame.transform.scale(rock_img, (OHTERS_SIZE, OHTERS_SIZE))
    oni_img = pygame.image.load(os.path.join(IMAGE_DIR, "oni.png")).convert_alpha()
    oni_img = pygame.transform.scale(oni_img, (OHTERS_SIZE, OHTERS_SIZE))
    start_bg_img = pygame.image.load(os.path.join(IMAGE_DIR, "GAMESTART_SCREEN.png")).convert()
    start_bg_img = pygame.transform.scale(start_bg_img, (WIDTH, HEIGHT))
    copyright_img_original = pygame.image.load(os.path.join(IMAGE_DIR, "copyright.png")).convert_alpha()
    copyright_width = 150
    copyright_height = int(copyright_img_original.get_height() * (copyright_width / copyright_img_original.get_width()))
    copyright_img = pygame.transform.scale(copyright_img_original, (copyright_width, copyright_height))
    press_enter_img_original = pygame.image.load(os.path.join(IMAGE_DIR, "PRESS_ENTER.png")).convert_alpha()
    press_enter_width = 250
    press_enter_height = int(press_enter_img_original.get_height() * (press_enter_width / press_enter_img_original.get_width()))
    press_enter_img = pygame.transform.scale(press_enter_img_original, (press_enter_width, press_enter_height))
    leaf_img_original = pygame.image.load(os.path.join(IMAGE_DIR, "leaf.png")).convert_alpha()
    leaf_img = pygame.transform.scale(leaf_img_original, (50, 50))
    coin_img = pygame.image.load(os.path.join(IMAGE_DIR, "coin.png")).convert_alpha()
    coin_img = pygame.transform.scale(coin_img, (GRID_SIZE * 0.9, GRID_SIZE * 0.9))
    rope_img = pygame.image.load(os.path.join(IMAGE_DIR, "rope.png")).convert_alpha()
    coin_display_img = pygame.image.load(os.path.join(IMAGE_DIR, "coin_display.png")).convert_alpha()
    coin_display_img = pygame.transform.scale_by(coin_display_img, UI_SCALE_FACTOR_DISPLAY)
    number_images = []
    for i in range(21):
        img = pygame.image.load(os.path.join(IMAGE_DIR, f"number_{i}.png")).convert_alpha()
        img = pygame.transform.scale_by(img, UI_SCALE_FACTOR)
        number_images.append(img)
    slash_img = pygame.image.load(os.path.join(IMAGE_DIR, "slash.png")).convert_alpha()
    slash_img = pygame.transform.scale_by(slash_img, UI_SCALE_FACTOR)

    game_over_img = pygame.image.load(os.path.join(IMAGE_DIR, "game_over.png")).convert_alpha()
    game_over_rect = game_over_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    stage_clear_img = pygame.image.load(os.path.join(IMAGE_DIR, "stage_clear.png")).convert_alpha()
    stage_clear_rect = stage_clear_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    restart_button_img = pygame.image.load(os.path.join(IMAGE_DIR, "restart_button.png")).convert_alpha()
    restart_rect = restart_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120)) # 位置を調整
    
    stage_panel_img = pygame.image.load(os.path.join(IMAGE_DIR, "stage_panel.png")).convert_alpha()
    stage_panel_img = pygame.transform.scale_by(stage_panel_img, UI_PANEL_SCALE)
    lock_icon_img = pygame.image.load(os.path.join(IMAGE_DIR, "lock_icon.png")).convert_alpha()
    lock_icon_img = pygame.transform.scale_by(lock_icon_img, UI_PANEL_SCALE)
    stage_select_str_img_original = pygame.image.load(os.path.join(IMAGE_DIR, "stage_select_str.png")).convert_alpha()
    stage_select_str_width = int(WIDTH * 0.8)
    stage_select_str_height = int(stage_select_str_img_original.get_height() * (stage_select_str_width / stage_select_str_img_original.get_width()))
    stage_select_str_img = pygame.transform.scale(stage_select_str_img_original, (stage_select_str_width, stage_select_str_height))
    stage_select_str_rect = stage_select_str_img.get_rect(center=(WIDTH // 2, 80))
    stage_select_background_img = pygame.image.load(os.path.join(IMAGE_DIR, "stage_select_background.png")).convert()
    stage_select_background_img = pygame.transform.scale(stage_select_background_img, (WIDTH, HEIGHT))
    stage_title_images = []
    for i in range(1, 6):
        img_path = os.path.join(IMAGE_DIR, f"STAGE{i}.png")
        img_original = pygame.image.load(img_path).convert_alpha()
        panel_height_for_title = int(stage_panel_img.get_height() * 0.5)
        img_scaled_height = panel_height_for_title
        img_scaled_width = int(img_original.get_width() * (img_scaled_height / img_original.get_height()))
        img_scaled = pygame.transform.scale(img_original, (img_scaled_width, img_scaled_height))
        stage_title_images.append(img_scaled)

except pygame.error as e:
    print(f"画像の読み込みに失敗しました: {e}"); sys.exit()

# --- 学習済みモデルのロード ---
MODEL_PATH = os.path.join(BASE_DIR, "model", "oni_double_model.zip")
try:
    model = PPO.load(MODEL_PATH)
    print(f"学習済みモデル {MODEL_PATH} をロードしました。")
except Exception as e:
    print(f"モデルのロードに失敗しました: {e}\nモデルなしでゲームを開始します。"); model = None

# --- フォント・テキスト準備 ---
title_font, info_font = pygame.font.Font(None, 120), pygame.font.Font(None, 50)
game_over_font = pygame.font.Font(None, 100)
title_text = title_font.render("Grid Greed", True, WHITE)
title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
start_text = info_font.render("Press SPACE to Start", True, WHITE)
start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
game_over_text = game_over_font.render("GAME OVER", True, RED)
game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
restart_text = info_font.render("Press SPACE to Select Stage", True, WHITE)
restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
stage_clear_text = game_over_font.render("STAGE CLEAR!", True, YELLOW)
stage_clear_rect = stage_clear_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# --- グローバル変数 ---
player_x, player_y = 0, 0
field, last_move_time, coin_count = [], 0, 0
rope_pos = (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2 - 1)
rope = None
oni_positions = []
scroll_y, is_scrolling = 0, False
unlocked_stage = 1
current_stage_id = 0
MODE = "START_SCREEN"

# --- セーブ・ロード機能 ---
SAVE_FILE = os.path.join(BASE_DIR, "save_data.json")
def save_progress():
    with open(SAVE_FILE, 'w') as f: json.dump({"unlocked_stage": unlocked_stage}, f)
def load_progress():
    global unlocked_stage
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
                unlocked_stage = data.get("unlocked_stage", 1)
        except json.JSONDecodeError: unlocked_stage = 1

# --- 各クラス定義 ---
class Stage:
    def __init__(self, stage_id, y_pos, module):
        self.id, self.locked, self.module = stage_id, True, module
        self.panel_rect = stage_panel_img.get_rect(center=(WIDTH // 2, y_pos))
        if 0 < self.id <= len(stage_title_images):
            self.title_image = stage_title_images[self.id - 1]
            self.title_rect = self.title_image.get_rect(center=self.panel_rect.center)
    def update_lock_status(self, max_unlocked):
        if self.id <= max_unlocked: self.locked = False
    def draw(self, surface, scroll):
        draw_rect = self.panel_rect.move(0, scroll)
        if -self.panel_rect.height < draw_rect.top < HEIGHT:
            surface.blit(stage_panel_img, draw_rect)
            if self.locked:
                surface.blit(lock_icon_img, lock_icon_img.get_rect(center=draw_rect.center))
            else:
                surface.blit(self.title_image, self.title_rect.move(0, scroll))
    def is_clicked(self, pos, scroll):
        return not self.locked and self.panel_rect.move(0, scroll).collidepoint(pos)

STAGE_Y_START = 220
STAGE_Y_SPACING = 250
stages = [Stage(1, STAGE_Y_START + STAGE_Y_SPACING * 0, Stage1), Stage(2, STAGE_Y_START + STAGE_Y_SPACING * 1, Stage2), Stage(3, STAGE_Y_START + STAGE_Y_SPACING * 2, Stage3), Stage(4, STAGE_Y_START + STAGE_Y_SPACING * 3, Stage3), Stage(5, STAGE_Y_START + STAGE_Y_SPACING * 4, Stage3)]

def apply_oni_action(oni_pos, action):
    next_pos = oni_pos.copy()
    if action == 0: next_pos[1] -= 1
    elif action == 1: next_pos[1] += 1
    elif action == 2: next_pos[0] -= 1
    elif action == 3: next_pos[0] += 1
    if 0 <= next_pos[0] < GRID_WIDTH and 0 <= next_pos[1] < GRID_HEIGHT and field[next_pos[1]][next_pos[0]]["type"] != "rock":
        return next_pos
    return oni_pos

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
            surface.blit(scaled_rope, scaled_rope.get_rect(midbottom=(self.x, self.end_y)))

def reset_game(stage_data):
    global player_x, player_y, field, last_move_time, coin_count, rope, oni_positions, current_stage_id
    current_stage_id = stage_data.id
    player_x, player_y = rope_pos; coin_count = 0; rope = None; oni_positions = []
    field = [[{"type": "grass", "bush": False, "coin": False} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if stage_data.module.ROCK_LAYOUT[y][x] == 1: field[y][x]["type"] = "rock"
            if stage_data.module.BUSH_LAYOUT[y][x] == 1: field[y][x]["bush"] = True
            if stage_data.module.COIN_LAYOUT[y][x] == 1: field[y][x]["coin"] = True
    occupied_positions = {(player_x, player_y)}
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if field[y][x]["type"] == "rock": occupied_positions.add((x,y))
    for _ in range(2):
        while True:
            ox, oy = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            distance = abs(ox - player_x) + abs(oy - player_y)
            if (ox, oy) not in occupied_positions and distance >= 3:
                oni_positions.append(np.array([ox, oy])); occupied_positions.add((ox, oy)); break
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
        surface.blit(rotated_leaf, rotated_leaf.get_rect(center=(int(self.x), int(self.y))))

def draw_coin_counter(surface, count):
    start_x = 10; surface.blit(coin_display_img, (start_x, 10))
    current_x = start_x + coin_display_img.get_width() + 5
    count_str = str(count) if count > 0 else "0"
    for digit in count_str:
        num_img = number_images[int(digit)]; surface.blit(num_img, (current_x, 23)); current_x += num_img.get_width() + 2
    surface.blit(slash_img, (current_x, 23)); current_x += slash_img.get_width() + 2
    total_str = "20"
    for digit in total_str:
        num_img = number_images[int(digit)]; surface.blit(num_img, (current_x, 23)); current_x += num_img.get_width() + 2

# --- メインループ ---
clock = pygame.time.Clock()
MOVE_INTERVAL_NORMAL, MOVE_INTERVAL_SLOW = 150, 600
ONI_MOVE_INTERVAL = 400
last_oni_move_time = 0
blink_interval, leaf_spawn_interval = 500, 600
last_blink_time, last_leaf_spawn_time = 0, 0
show_press_enter, leaves = True, []

load_progress()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        if MODE == "START_SCREEN":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                MODE = "STAGE_SELECT"
        
        elif MODE == "STAGE_SELECT":
            if event.type == pygame.MOUSEWHEEL:
                is_scrolling = True; scroll_y += event.y * 20
                total_height = STAGE_Y_SPACING * (len(stages) - 1)
                first_panel_top = stages[0].panel_rect.top
                max_scroll = HEIGHT - (first_panel_top + total_height) - 50
                if max_scroll > 0: max_scroll = 0
                scroll_y = max(min(scroll_y, 0), max_scroll)
            if event.type == pygame.MOUSEBUTTONUP:
                if not is_scrolling:
                    for stage in stages:
                        if stage.is_clicked(event.pos, scroll_y):
                            reset_game(stage); MODE = "PLAYING"; break
                is_scrolling = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                is_scrolling = False

        elif MODE == "GAME_OVER" or MODE == "STAGE_CLEAR":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                MODE = "STAGE_SELECT"
    
    # --- モード別の描画・ロジック処理 ---
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
    
    elif MODE == "STAGE_SELECT":
        screen.blit(stage_select_background_img, (0,0))
        for stage in stages:
            stage.update_lock_status(unlocked_stage)
            stage.draw(screen, scroll_y)
        screen.blit(stage_select_str_img, stage_select_str_rect)
        unlocked_stage = min(unlocked_stage, len(stages) + 1)

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
            if current_stage_id >= unlocked_stage:
                unlocked_stage = current_stage_id + 1
                save_progress()
        if rope: rope.update()
        if model is not None and current_time - last_oni_move_time > ONI_MOVE_INTERVAL:
            obs = np.concatenate([oni_positions[0], oni_positions[1], np.array([player_x, player_y])])
            actions, _states = model.predict(obs, deterministic=True)
            oni_positions[0] = apply_oni_action(oni_positions[0], actions[0])
            oni_positions[1] = apply_oni_action(oni_positions[1], actions[1])
            last_oni_move_time = current_time
        for oni_pos in oni_positions:
            if np.array_equal(oni_pos, np.array([player_x, player_y])):
                MODE = "GAME_OVER"; break
        
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
        for oni_pos_array in oni_positions:
            screen.blit(oni_img, (oni_pos_array[0] * GRID_SIZE, oni_pos_array[1] * GRID_SIZE))
        draw_coin_counter(screen, coin_count)

    elif MODE == "GAME_OVER" or MODE == "STAGE_CLEAR":
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
        for oni_pos_array in oni_positions:
            screen.blit(oni_img, (oni_pos_array[0] * GRID_SIZE, oni_pos_array[1] * GRID_SIZE))
        draw_coin_counter(screen, coin_count)
        
        if MODE == "GAME_OVER":
            screen.blit(game_over_text, game_over_rect)
        else: # STAGE_CLEAR
            screen.blit(stage_clear_text, stage_clear_rect)
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(60)