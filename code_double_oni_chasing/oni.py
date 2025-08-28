# oni_rl.py (新しいファイル名として推奨)
import gymnasium as gym
from stable_baselines3 import PPO
import numpy as np
from oni_double_env import ChaseEnv # 自作環境をインポート

# 学習済みモデルをロード
MODEL_PATH = "model/oni_double_model"
try:
    model = PPO.load(MODEL_PATH)
    print(f"学習済みモデル {MODEL_PATH} をロードしました。")
except Exception as e:
    print(f"モデルのロードに失敗しました: {e}")
    model = None # モデルがロードできない場合のフォールバック

def get_oni_next_move(env, oni_pos, player_pos):
    """
    強化学習モデルを使って、鬼の最適な行動を決定する。

    :param env: プレイしている環境オブジェクト (ChaseEnv)
    :param oni_pos: 鬼の現在座標 (x, y) - 実際にはenvオブジェクトから取得
    :param player_pos: プレイヤーの現在座標 (x, y) - 実際にはenvオブジェクトから取得
    :return: 鬼の次の行動 (0=上, 1=下, 2=左, 3=右)
    """
    # モデルがロードされていない場合はエラーを返すか、ランダムな行動を返す
    if model is None:
        print("警告: モデルがロードされていません。ランダムな行動を返します。")
        return env.action_space.sample()

    # 現在の環境状態（観測）をモデルの入力形式に整形する
    # ChaseEnvのstepメソッドは(enemy1, enemy2, player)の順で観測を返すので、それに合わせる
    # ただし、get_oni_next_move関数は単体の鬼の行動を決定するため、
    # 2体の鬼の行動を同時に決定するモデルの構造と合わない点に注意が必要。
    # この例では、モデルが2体の鬼の行動を同時に決定する前提で進める。
    
    # ここでは、外部から鬼の座標とプレイヤーの座標を渡すのではなく、
    # envオブジェクトの現在の状態を直接使用する方が自然。
    # しかし、元の関数の引数に合わせるため、この関数内で観測を作成する。
    
    # 観測空間の形式: (鬼1_x, 鬼1_y, 鬼2_x, 鬼2_y, P_x, P_y)
    # get_oni_next_moveは単体の鬼用なので、もう一方の鬼の座標も必要になる
    # これをどのように提供するかは、呼び出し元の実装による
    # 例: env.enemy_positionsを直接参照
    
    # 実際の観測はenvから取得するのがベストプラクティス
    # observation = env._get_obs() # もしenvにそのようなプライベートメソッドがあれば
    # 今回は元の引数に合わせたダミー観測を作成
    # 別の鬼の座標が不明なため、この関数は本来のRLモデルの使い方と少しずれる
    # 正しい使い方は、RLモデルに(鬼1,鬼2,プレイヤー)の3者情報をまとめて渡し、
    # 2つの行動(actions)を一度に取得すること

    # モデルは1つの観測から2つの行動を返す
    # 観測を作成 (この関数内では鬼1とプレイヤーの情報しかないので、鬼2はダミー)
    # これは非推奨な使い方。本来は2体まとめて行動を決定すべき
    # 観測 = np.concatenate([oni_pos, ダミーの鬼2_pos, player_pos])
    
    # 正しい呼び出し方 (2体まとめて推論)
    # obs = np.concatenate([env.enemy_positions[0], env.enemy_positions[1], env.player_pos])
    # actions, _states = model.predict(obs)
    # return actions # actionsは[鬼1の行動, 鬼2の行動]

    # この関数の役割を、単一の鬼の行動決定から
    # 「環境状態をモデルに渡し、2体の鬼の行動を取得する」に変更する
    obs = np.concatenate([env.enemy_positions[0], env.enemy_positions[1], env.player_pos])
    actions, _states = model.predict(obs)

    # 2体の鬼の行動を返す
    return actions

# --- 以下は使い方と動作テストの例 ---
if __name__ == '__main__':
    # 以下のテストは、元のoni.pyのBFSロジックとは全く異なる
    # 強化学習モデルの推論を試すためのものになる
    
    print("--- 強化学習モデルのテスト ---")
    
    # 学習環境と同じ環境オブジェクトを作成
    env = ChaseEnv()
    
    # 環境をリセットして初期観測を取得
    obs, info = env.reset()

    print("初期状態:")
    print(f"鬼1: {env.enemy_positions[0]}, 鬼2: {env.enemy_positions[1]}, P: {env.player_pos}")
    print("-" * 20)

    # 10ターン、モデルを使ってシミュレーション
    for i in range(10):
        # モデルに現在の観測を渡し、次の行動を取得
        # この関数は単一の鬼の行動を返すのではなく、
        # 2体の鬼の行動の配列を返すように変更した
        actions = get_oni_next_move(env, env.enemy_positions[0], env.player_pos)
        
        # 環境にアクションを適用
        obs, reward, terminated, truncated, info = env.step(actions)
        
        print(f"ターン{i+1}: 鬼1の行動 -> {actions[0]}, 鬼2の行動 -> {actions[1]}")
        print(f"  > 鬼1:{env.enemy_positions[0]}, 鬼2:{env.enemy_positions[1]}, P:{env.player_pos}, R:{reward:.2f}")

        if terminated:
            print("鬼がプレイヤーを捕まえた！")
            break
        if truncated:
            print("時間切れで終了")
            break