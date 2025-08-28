import gymnasium as gym
from stable_baselines3 import PPO
from oni_env import ChaseEnv  # 自作環境をインポート

def main():
    # 環境作成
    env = ChaseEnv()

    # PPO モデル作成
    # "MlpPolicy" は多層パーセプトロン（全結合NN）を使用
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,  # 学習率
        n_steps=2048,         # 1回の rollout に使用するステップ数
        batch_size=64,
        gamma=0.9,           # 割引率
        gae_lambda=0.95,
        clip_range=0.2,
        verbose=1,
        policy_kwargs=dict(net_arch=[128,128])
    )

    # 学習（例: 10,000ステップ）
    model.learn(total_timesteps=50000)

    # 学習済みモデルを保存
    model.save("model/oni_model") #code_ueno内のmodelフォルダに入れることを想定

if __name__ == "__main__":
    main()