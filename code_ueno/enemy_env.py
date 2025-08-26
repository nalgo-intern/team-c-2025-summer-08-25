#branch test
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random # 簡易AIにランダム性を加えるために追加

class ChaseEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.size = 10  # 10x10 グリッド
        # 観測空間：(敵座標 + プレイヤー座標) ←この座標を最大 self.size-1(今回だと9) 最小9まで観測できることを表す。
        self.observation_space = spaces.Box(low=0, high=self.size-1, shape=(4,), dtype=np.int32)
        # 行動空間：0=上, 1=下, 2=左, 3=右
        self.action_space = spaces.Discrete(4)
        self.max_steps = 100 #ゲームの制限時間となるゲーム開始から100回鬼側と逃げる側が行動をしたらエピソード終了
        self.current_step = 0 

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.enemy_pos = np.array([0, 0])  #敵側の初期状態を表す[0,0]の場合、グリッドの左上隅
        self.player_pos = np.array([self.size-1, self.size-1])#プレイヤー側の初期状態を表す[self.size-1, self.size-1]の場合,[9,9]なので、右下を表す。
        self.current_step = 0 #制限時間（行動した回数）を0に
        return np.concatenate([self.enemy_pos, self.player_pos]), {}

    def step(self, action):
        self.current_step += 1

        # --- 敵キャラ（AIエージェント）の移動 ---
        # このactionは、強化学習エージェント（鬼側）が決定した行動
        if action == 0: self.enemy_pos[1] = max(0, self.enemy_pos[1]-1)  # 上
        if action == 1: self.enemy_pos[1] = min(self.size-1, self.enemy_pos[1]+1)  # 下
        if action == 2: self.enemy_pos[0] = max(0, self.enemy_pos[0]-1)  # 左
        if action == 3: self.enemy_pos[0] = min(self.size-1, self.enemy_pos[0]+1)  # 右

        # --- プレイヤーキャラ（追いかけられる側）の簡易AI移動 ---
        # player_controlled_by_humanがTrueの場合、このAIは動きません。
        if not self.player_controlled_by_human: # <--- ここでフラグをチェック
            player_dx, player_dy = 0, 0

            # 鬼がプレイヤーより上にいる場合、プレイヤーは下へ移動
            if self.enemy_pos[1] < self.player_pos[1]:
                player_dy = 1
            # 鬼がプレイヤーより下にいる場合、プレイヤーは上へ移動
            elif self.enemy_pos[1] > self.player_pos[1]:
                player_dy = -1

            # 鬼がプレイヤーより左にいる場合、プレイヤーは右へ移動
            if self.enemy_pos[0] < self.player_pos[0]:
                player_dx = 1
            # 鬼がプレイヤーより右にいる場合、プレイヤーは左へ移動
            elif self.enemy_pos[0] > self.player_pos[0]:
                player_dx = -1

            # 移動を適用し、グリッドの境界チェックを行う
            self.player_pos[0] = max(0, min(self.size-1, self.player_pos[0] + player_dx))
            self.player_pos[1] = max(0, min(self.size-1, self.player_pos[1] + player_dy))
            
            # オプション：プレイヤーAIに少しランダム性を加えることで、敵AIがより多様な状況で学習できるようにすることも可能
            if random.random() < 0.1: # 10%の確率でランダムな動き
                rand_move = random.choice([(-1,0), (1,0), (0,-1), (0,1), (0,0)])
                self.player_pos[0] = max(0, min(self.size-1, self.player_pos[0] + rand_move[0]))
                self.player_pos[1] = max(0, min(self.size-1, self.player_pos[1] + rand_move[1]))


        # 距離計算
        dist = np.linalg.norm(self.enemy_pos - self.player_pos)
        reward = -dist  # 距離が近いほど報酬が高くなる

        # 終了判定
        terminated = np.array_equal(self.enemy_pos, self.player_pos)
        truncated = self.current_step >= self.max_steps
        if terminated:
            reward = 100  # 捕まえたら大きな報酬

        obs = np.concatenate([self.enemy_pos, self.player_pos]) #更新された敵とプレイヤーの位置を結合し、次の観測（状態）として返します。
        info = {}
        return obs, reward, terminated, truncated, info

# 環境テスト
if __name__ == "__main__":
    # 簡易AIで動くプレイヤー (デフォルト)
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
    # 人間が操作するプレイヤー (AIは動かない)
    env_human_player = ChaseEnv(player_controlled_by_human=True)
    obs_human, _ = env_human_player.reset()
    print("初期観測 (人間プレイヤー):", obs_human)
    # ここではenv.step()を呼ぶと、敵キャラだけがランダムに動きます。
    # プレイヤーキャラは外部（メインループ）で動かす想定なので、ここでは動きません。
    # このテストコードは、プレイヤーキャラの移動をメインループで行うためのダミーです。
    for i in range(5):
        action_human = env_human_player.action_space.sample() # 敵キャラはランダム行動
        # プレイヤーキャラを手動で動かす場合、env.player_posを直接更新するロジックがここに入る
        # 例: env_human_player.player_pos[0] += 1
        obs_human, reward_human, terminated_human, truncated_human, info_human = env_human_player.step(action_human)
        print(f"ステップ:{i+1}, 敵:{env_human_player.enemy_pos}, P(人間):{env_human_player.player_pos}, 報酬:{reward_human:.2f}, 終了:{terminated_human}")
        if terminated_human or truncated_human:
            print("人間プレイヤーエピソード終了")
            break

