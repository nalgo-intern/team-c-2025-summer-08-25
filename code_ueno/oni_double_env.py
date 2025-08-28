import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random

# グリッド設定
GRID_SIZE = 50
GRID_WIDTH = 10
GRID_HEIGHT = 10
WIDTH = GRID_WIDTH * GRID_SIZE
HEIGHT = GRID_HEIGHT * GRID_SIZE

class ChaseEnv(gym.Env):
    def __init__(self, human_control=False):
        super().__init__()
        # 観測空間：(鬼1座標 + 鬼2座標 + プレイヤー座標)
        self.observation_space = spaces.Box(
            low=np.array([0,0,0,0,0,0]),
            high=np.array([GRID_WIDTH-1, GRID_HEIGHT-1,
                           GRID_WIDTH-1, GRID_HEIGHT-1,
                           GRID_WIDTH-1, GRID_HEIGHT-1]),
            dtype=np.int32
        )
        
        # 行動空間：鬼1と鬼2がそれぞれ 0=上,1=下,2=左,3=右
        self.action_space = spaces.MultiDiscrete([4,4])

        self.max_steps = 100
        self.current_step = 0

        # 岩座標
        self.rocks = set()

        # フィールド
        self.field = None

        # プレイヤー & 敵座標
        self.player_pos = None
        self.enemy_positions = []  # 2体の鬼を格納

        # 人間操作モード
        self.human_control = human_control

    def _init_field(self):
        """フィールドと岩・鬼・プレイヤーの初期配置を行う"""
        # プレイヤー初期位置
        self.player_pos = np.array([GRID_WIDTH // 2, GRID_HEIGHT // 2])
        
        # フィールド初期化
        self.field = [[{"type": "grass"} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.rocks.clear()

        # ランダムに岩を配置
        while len(self.rocks) < random.randint(5, 10):
            rx, ry = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            if (rx, ry) != tuple(self.player_pos):
                self.field[ry][rx]["type"] = "rock"
                self.rocks.add((rx, ry))

        # 鬼の初期位置を2体決定（被らないように）
        self.enemy_positions = []
        while len(self.enemy_positions) < 2:
            ex, ey = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            distance = abs(ex - self.player_pos[0]) + abs(ey - self.player_pos[1])
            pos = (ex, ey)
            if (
                pos != tuple(self.player_pos)
                and pos not in self.rocks
                and pos not in [tuple(p) for p in self.enemy_positions]
                and distance >= 3
            ):
                self.enemy_positions.append(np.array([ex, ey]))

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._init_field()
        self.current_step = 0

        obs = np.concatenate([self.enemy_positions[0],
                              self.enemy_positions[1],
                              self.player_pos])
        return obs, {}

    def applyAction(self, pos, action):
        """鬼の移動処理（岩や壁チェック込み）"""
        new_pos = pos.copy()
        if action == 0: new_pos[1] -= 1  # 上
        if action == 1: new_pos[1] += 1  # 下
        if action == 2: new_pos[0] -= 1  # 左
        if action == 3: new_pos[0] += 1  # 右

        # 無効な場合 → その場に留まる
        if (
            0 <= new_pos[0] < GRID_WIDTH
            and 0 <= new_pos[1] < GRID_HEIGHT
            and self.field[new_pos[1]][new_pos[0]]["type"] != "rock"
        ):
            return new_pos, False  # 有効移動
        else:
            return pos, True  # 岩などにぶつかった

    def step(self, actions):
        self.current_step += 1
        reward = 0

        # --- 鬼の移動 ---
        for i, action in enumerate(actions):
            old_dist = np.linalg.norm(self.enemy_positions[i] - self.player_pos)
            next_pos, hit_rock = self.applyAction(self.enemy_positions[i], action)
            self.enemy_positions[i] = next_pos

            # 岩にぶつかったら軽いペナルティ
            if hit_rock:
                reward -= 0.1

            # プレイヤーとの距離変化で shaping
            new_dist = np.linalg.norm(self.enemy_positions[i] - self.player_pos)
            if new_dist < old_dist:
                reward += 0.05  # 近づいたら加点
            else:
                reward -= 0.02  # 遠ざかったら減点

        # --- プレイヤーキャラ（簡易AI） ---
        if not self.human_control:
            player_dx, player_dy = 0, 0
            # 鬼の平均位置に基づいて逃げる
            avg_enemy = np.mean(self.enemy_positions, axis=0)
            if avg_enemy[1] < self.player_pos[1]:
                player_dy = 1
            elif avg_enemy[1] > self.player_pos[1]:
                player_dy = -1
            if avg_enemy[0] < self.player_pos[0]:
                player_dx = 1
            elif avg_enemy[0] > self.player_pos[0]:
                player_dx = -1

            next_player_pos = self.player_pos + np.array([player_dx, player_dy])
            if (
                0 <= next_player_pos[0] < GRID_WIDTH
                and 0 <= next_player_pos[1] < GRID_HEIGHT
                and self.field[next_player_pos[1]][next_player_pos[0]]["type"] != "rock"
            ):
                self.player_pos = next_player_pos

            # 10%の確率でランダム移動
            if random.random() < 0.1:
                rand_move = random.choice([(-1,0),(1,0),(0,-1),(0,1),(0,0)])
                self.player_pos[0] = max(0, min(GRID_WIDTH-1, self.player_pos[0] + rand_move[0]))
                self.player_pos[1] = max(0, min(GRID_HEIGHT-1, self.player_pos[1] + rand_move[1]))

        # --- 終了判定 ---
        terminated = any(np.array_equal(enemy, self.player_pos) for enemy in self.enemy_positions)
        truncated = self.current_step >= self.max_steps

        if terminated:
            reward += 100  # 捕まえた

        obs = np.concatenate([self.enemy_positions[0],
                              self.enemy_positions[1],
                              self.player_pos])
        info = {}
        return obs, reward, terminated, truncated, info

def main():
    print("--- 2体の鬼テスト ---")
    env = ChaseEnv()
    obs, _ = env.reset()
    print("初期観測:", obs)
    for i in range(10):
        actions = env.action_space.sample()  # 2体の鬼の行動
        obs, reward, terminated, truncated, info = env.step(actions)
        print(f"Step:{i+1}, 鬼1:{env.enemy_positions[0]}, 鬼2:{env.enemy_positions[1]}, P:{env.player_pos}, R:{reward:.2f}")
        if terminated or truncated:
            print("エピソード終了")
            break

if __name__ == "__main__":
    main()
