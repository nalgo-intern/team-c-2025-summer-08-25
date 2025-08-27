import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random  # 簡易AIにランダム性を加えるために追加

class ChaseEnv(gym.Env):
    def __init__(self, player_controlled_by_human=False):
        super().__init__()
        self.size = 10  # 10x10 グリッド
        # 観測空間：(敵座標 + プレイヤー座標)
        self.observation_space = spaces.Box(low=0, high=self.size-1, shape=(4,), dtype=np.int32)
        # 行動空間：0=上, 1=下, 2=左, 3=右
        self.action_space = spaces.Discrete(4)
        self.max_steps = 100
        self.current_step = 0
        # ★追加：人間操作モードフラグ
        self.player_controlled_by_human = player_controlled_by_human

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.enemy_pos = np.array([0, 0])  # 敵の初期位置
        self.player_pos = np.array([self.size-1, self.size-1])  # プレイヤーの初期位置
        self.current_step = 0
        return np.concatenate([self.enemy_pos, self.player_pos]), {}

    def step(self, action):
        self.current_step += 1

        # --- 敵キャラ（AIエージェント）の移動 ---
        if action == 0: self.enemy_pos[1] = max(0, self.enemy_pos[1]-1)  # 上
        if action == 1: self.enemy_pos[1] = min(self.size-1, self.enemy_pos[1]+1)  # 下
        if action == 2: self.enemy_pos[0] = max(0, self.enemy_pos[0]-1)  # 左
        if action == 3: self.enemy_pos[0] = min(self.size-1, self.enemy_pos[0]+1)  # 右

        # --- プレイヤーキャラ（追いかけられる側）の簡易AI移動 ---
        if not self.player_controlled_by_human:
            player_dx, player_dy = 0, 0

            if self.enemy_pos[1] < self.player_pos[1]:
                player_dy = 1
            elif self.enemy_pos[1] > self.player_pos[1]:
                player_dy = -1

            if self.enemy_pos[0] < self.player_pos[0]:
                player_dx = 1
            elif self.enemy_pos[0] > self.player_pos[0]:
                player_dx = -1

            self.player_pos[0] = max(0, min(self.size-1, self.player_pos[0] + player_dx))
            self.player_pos[1] = max(0, min(self.size-1, self.player_pos[1] + player_dy))

            # 10%の確率でランダム移動
            if random.random() < 0.1:
                rand_move = random.choice([(-1,0), (1,0), (0,-1), (0,1), (0,0)])
                self.player_pos[0] = max(0, min(self.size-1, self.player_pos[0] + rand_move[0]))
                self.player_pos[1] = max(0, min(self.size-1, self.player_pos[1] + rand_move[1]))

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
    env_human_player = ChaseEnv(player_controlled_by_human=True)
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