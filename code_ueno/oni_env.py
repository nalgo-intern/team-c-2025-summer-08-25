import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random  # 簡易AIにランダム性を加えるために追加

# グリッド設定
GRID_SIZE = 50
GRID_WIDTH = 10
GRID_HEIGHT = 10
WIDTH = GRID_WIDTH * GRID_SIZE
HEIGHT = GRID_HEIGHT * GRID_SIZE

class ChaseEnv(gym.Env):
    def __init__(self, human_control =False):
        super().__init__()
        # 観測空間：(敵座標 + プレイヤー座標)
        self.observation_space = spaces.Box(
            low=np.array([0,0,0,0]),
            high=np.array([GRID_WIDTH-1, GRID_HEIGHT-1, GRID_WIDTH-1, GRID_HEIGHT-1]),
            dtype=np.int32
        )
        
        # 行動空間：0=上, 1=下, 2=左, 3=右
        self.action_space = spaces.Discrete(4)
        self.max_steps = 100
        self.current_step = 0

        # 岩座標を管理するセット
        self.rocks = set()

        # ★追加：人間操作モードフラグ
        self.human_control = human_control

    def _init_field(self):
        """フィールドと岩・鬼・プレイヤーの初期配置を行う"""
        # プレイヤー初期位置
        self.player_pos = np.array([GRID_WIDTH // 2, GRID_HEIGHT // 2])
        
        # フィールド初期化
        self.field = [[{"type": "grass", "bush": False} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # ランダムに岩を配置
        while len(self.rocks) < random.randint(5, 10):
            rx, ry = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            if (rx, ry) != tuple(self.player_pos):
                self.field[ry][rx]["type"] = "rock"
                self.rocks.add((rx, ry))

        # 鬼の初期位置を決定
        while True:
            ex, ey = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            distance = abs(ex - self.player_pos[0]) + abs(ey - self.player_pos[1])
            if (ex, ey) != tuple(self.player_pos) and self.field[ey][ex]["type"] != "rock" and distance >= 3:
                self.enemy_pos = np.array([ex, ey])
                break

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.enemy_pos = np.array([0, 0])  # 敵の初期位置
        self.player_pos = np.array([GRID_WIDTH-5, GRID_HEIGHT-5])  # プレイヤーの初期位置
        self.rocks.clear()  # 前回の岩をリセット
        self._init_field()
        self.current_step = 0
        return np.concatenate([self.enemy_pos, self.player_pos]), {}

    def step(self, action):
        self.current_step += 1

        # --- 敵キャラの移動 ---
        next_enemy_pos = self.enemy_pos.copy()
        if action == 0: next_enemy_pos[1] -= 1  # 上
        if action == 1: next_enemy_pos[1] += 1  # 下
        if action == 2: next_enemy_pos[0] -= 1  # 左
        if action == 3: next_enemy_pos[0] += 1  # 右

        # 岩を通れない判定
        if (0 <= next_enemy_pos[0] < GRID_WIDTH and 0 <= next_enemy_pos[1] < GRID_HEIGHT and self.field[next_enemy_pos[1]][next_enemy_pos[0]]["type"] != "rock"):
            self.enemy_pos = next_enemy_pos
        
        #print(f"self.player_controlled_by_human = {self.player_controlled_by_human}")

        # --- プレイヤーキャラ（簡易AI）の移動 ---
        if not self.human_control:
            player_dx, player_dy = 0, 0
            if self.enemy_pos[1] < self.player_pos[1]:
                player_dy = 1
            elif self.enemy_pos[1] > self.player_pos[1]:
                player_dy = -1
            if self.enemy_pos[0] < self.player_pos[0]:
                player_dx = 1
            elif self.enemy_pos[0] > self.player_pos[0]:
                player_dx = -1

            
            next_player_pos = self.player_pos + np.array([player_dx, player_dy])

            if (0 <= next_player_pos[0] < GRID_WIDTH and 0 <= next_player_pos[1] < GRID_HEIGHT and self.field[next_player_pos[1]][next_player_pos[0]]["type"] != "rock"):
                self.player_pos = next_player_pos

            # 10%の確率でランダム移動
            if random.random() < 0.1:
                rand_move = random.choice([(-1,0), (1,0), (0,-1), (0,1), (0,0)])
                self.player_pos[0] = max(0, min(GRID_WIDTH-1, self.player_pos[0] + rand_move[0]))
                self.player_pos[1] = max(0, min(GRID_HEIGHT-1, self.player_pos[1] + rand_move[1]))

        # 報酬設計
        dist = np.linalg.norm(self.enemy_pos - self.player_pos)
        reward = -dist
        terminated = np.array_equal(self.enemy_pos, self.player_pos)
        truncated = self.current_step >= self.max_steps
        
        if terminated:
            reward = 100

        obs = np.concatenate([self.enemy_pos, self.player_pos])
        info = {}
        return obs, reward, terminated, truncated, info

def main():
    print("--- 簡易AIで動くプレイヤーのテスト ---")
    env_ai_player = ChaseEnv()
    obs_ai, _ = env_ai_player.reset()
    print("初期観測 (AIプレイヤー):", obs_ai)
    for i in range(5):
        action_ai = env_ai_player.action_space.sample()
        obs_ai, reward_ai, terminated_ai, truncated_ai, info_ai = env_ai_player.step(action_ai)
        print(f"ステップ:{i+1}, 敵:{env_ai_player.enemy_pos}, P(AI):{env_ai_player.player_pos}, 報酬:{reward_ai:.2f}, 終了:{terminated_ai}")
        
        if terminated_ai or truncated_ai:
            print("AIプレイヤーエピソード終了")
            break

    print("\n--- 人間が操作するプレイヤーのテスト（ダミー） ---")
    env_human_player = ChaseEnv(human_control = True)
    obs_human, _ = env_human_player.reset()
    print("初期観測 (人間プレイヤー):", obs_human)
    for i in range(5):
        action_human = env_human_player.action_space.sample()
        obs_human, reward_human, terminated_human, truncated_human, info_human = env_human_player.step(action_human)
        print(f"ステップ:{i+1}, 敵:{env_human_player.enemy_pos}, P(人間):{env_human_player.player_pos}, 報酬:{reward_human:.2f}, 終了:{terminated_human}")
        
        if terminated_human or truncated_human:
            print("人間プレイヤーエピソード終了")
            break

# 環境テスト
if __name__ == "__main__":
    main()