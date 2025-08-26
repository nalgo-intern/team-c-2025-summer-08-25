import gymnasium as gym
from stable_baselines3 import PPO
from enemy_env import ChaseEnv  # 自作環境をインポート

# 環境作成
env = ChaseEnv()

# PPO モデル作成
# "MlpPolicy" は多層パーセプトロン（全結合NN）を使用
model = PPO("MlpPolicy", env, verbose=1)

# 学習（例: 10,000ステップ）
model.learn(total_timesteps=10000)

# 学習済みモデルを保存
model.save("model/enemy_model")
