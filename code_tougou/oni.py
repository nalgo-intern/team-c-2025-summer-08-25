import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO
from collections import deque
import os
import sys

# --- ダミー環境の定義 ---
# AIモデルをロードするために、モデルが学習した環境の形式を再現するためのダミークラス
# gymnasium.Envを継承することで、Stable Baselines3の環境チェックを通過できます
class DummyEnv(gym.Env):
    def __init__(self):
        # 親クラスのコンストラクタの呼び出し
        super().__init__()
        self.observation_space = gym.spaces.Box(low=0, high=9, shape=(4,), dtype=np.int32)
        self.action_space = gym.spaces.Discrete(4)
    
    # AIモデルのロードに必要となる、必須メソッドのスタブを定義
    # このメソッドは実際にゲーム内で使われるわけではありません
    def reset(self, seed=None, options=None):
        return self.observation_space.sample(), {}

    def step(self, action):
        return self.observation_space.sample(), 0, False, False, {}

# 学習済みモデルをロード
# グローバルスコープで一度だけロード
model_path = "model/enemy_model3.zip"
try:
    # Stable Baselines3のモデルは、`.zip`拡張子がないと正しくロードできない場合があります
    if not os.path.exists(model_path):
        # 以前のバージョンで保存したモデル名が `enemy_model3` だった場合に対応
        # この処理は、新しいモデルを保存する際に `.zip` を付けることで不要になります
        PPO.load("model/enemy_model3", env=DummyEnv()).save(model_path)
    
    # env=DummyEnv() を指定して、モデルが環境の観測・行動空間を認識できるようにします
    model = PPO.load(model_path, env=DummyEnv())
    print("AIモデルをロードしました。")
except FileNotFoundError:
    print(f"エラー: 学習済みモデル '{model_path}' が見つかりません。")
    print("AIが学習を完了しているか、パスが正しいか確認してください。")
    sys.exit()


def get_oni_next_move(grid, oni_pos, player_pos):
    """
    AIモデルを使用して、鬼が次に動くべき最適な座標を返す。

    :param grid: 2Dリストのマップデータ（岩や壁の情報）
    :param oni_pos: 鬼の現在座標 (x, y)
    :param player_pos: プレイヤーの現在座標 (x, y)
    :return: 鬼が次に移動すべき座標 (x, y)。移動できない場合は現在の座標を返す。
    """
    
    # 観測値（状態）を作成
    # AIは[鬼x, 鬼y, プレイヤーx, プレイヤーy]の形式で学習している
    obs = np.array([oni_pos[0], oni_pos[1], player_pos[0], player_pos[1]])
    
    # AIモデルに行動を予測させる
    action, _states = model.predict(obs)
    
    # 行動から座標の変更量を決定
    dx, dy = 0, 0
    if action == 0: dy = -1  # 上
    if action == 1: dy = 1   # 下
    if action == 2: dx = -1  # 左
    if action == 3: dx = 1   # 右

    next_x = oni_pos[0] + dx
    next_y = oni_pos[1] + dy

    # 移動先の座標がグリッドの範囲内であり、かつ壁(#)でないかチェック
    # AIモデルは壁の存在を学習していないため、このチェックが必須
    if 0 <= next_x < len(grid[0]) and 0 <= next_y < len(grid):
        if grid[next_y][next_x] != '#':
            return (next_x, next_y)
    
    # 移動先が有効でない場合、動かない
    return oni_pos


# --- 以下は使い方と動作テストの例 ---
if __name__ == '__main__':
    # サンプルマップの定義（'#'は壁, '.'は通路, 'O'は鬼, 'P'はプレイヤー）
    MAP_DATA = [
        "##########",
        "#O.......#",
        "#.#.######",
        "#.#.#....#",
        "#.#.#.##.#",
        "#...#..#P#",
        "##########",
    ]

    # 初期位置の設定
    oni_position = (1, 1)
    player_position = (8, 5)

    print(f"鬼の初期位置: {oni_position}")
    print(f"プレイヤーの位置: {player_position}")
    print("-" * 20)

    # 鬼を5ターン動かしてみるシミュレーション
    for i in range(5):
        # 鬼の次の移動先を取得
        next_move = get_oni_next_move(MAP_DATA, oni_position, player_position)
        
        print(f"ターン{i+1}: 鬼の次の動き -> {next_move}")
        
        # 鬼の位置を更新
        oni_position = next_move

        if oni_position == player_position:
            print("鬼がプレイヤーを捕まえた！")
            break
