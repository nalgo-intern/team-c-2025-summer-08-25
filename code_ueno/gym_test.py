import gymnasium as gym

# 環境を初期化
env = gym.make("CartPole-v1", render_mode="human")

# 環境をリセットして最初の観測値を生成
observation, info = env.reset()
for _ in range(1000):
    # ここにアクションを挿入する。アクションがランダムに生成される。
    action = env.action_space.sample()

    # アクションを入力し、次のステップに移行
    # 次の観測値、報酬、エピソードが終了したか中断されたかを受け取る
    observation, reward, terminated, truncated, info = env.step(action)

    # エピソードが終了した場合、新しいエピソードを開始するためリセット可能
    if terminated or truncated:
        observation, info = env.reset()

# 環境を終了
env.close()
