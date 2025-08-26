import gymnasium as gym
from gymnasium import spaces
import numpy as np

class ChaseEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.size = 10  # 10x10 グリッド
        # 観測空間：敵座標 + プレイヤー座標
        self.observation_space = spaces.Box(low=0, high=self.size-1, shape=(4,), dtype=np.int32)
        # 行動空間：0=上, 1=下, 2=左, 3=右
        self.action_space = spaces.Discrete(4)
        self.max_steps = 100
        self.current_step = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.enemy_pos = np.array([0, 0])
        self.player_pos = np.array([self.size-1, self.size-1])
        self.current_step = 0
        return np.concatenate([self.enemy_pos, self.player_pos]), {}

    def step(self, action):
        self.current_step += 1

        # 敵キャラの移動
        if action == 0: self.enemy_pos[1] = max(0, self.enemy_pos[1]-1)  # 上
        if action == 1: self.enemy_pos[1] = min(self.size-1, self.enemy_pos[1]+1)  # 下
        if action == 2: self.enemy_pos[0] = max(0, self.enemy_pos[0]-1)  # 左
        if action == 3: self.enemy_pos[0] = min(self.size-1, self.enemy_pos[0]+1)  # 右

        # 距離計算
        dist = np.linalg.norm(self.enemy_pos - self.player_pos)
        reward = -dist  # 距離が近いほど報酬が高くなる

        # 終了判定
        terminated = np.array_equal(self.enemy_pos, self.player_pos)
        truncated = self.current_step >= self.max_steps
        if terminated:
            reward = 100  # 捕まえたら大きな報酬

        obs = np.concatenate([self.enemy_pos, self.player_pos])
        info = {}
        return obs, reward, terminated, truncated, info

# 環境テスト
if __name__ == "__main__":
    env = ChaseEnv()
    obs, _ = env.reset()
    print("初期観測:", obs)
    for _ in range(5):
        action = env.action_space.sample()  # ランダム行動
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"行動:{action}, 観測:{obs}, 報酬:{reward}, 終了:{terminated}")
