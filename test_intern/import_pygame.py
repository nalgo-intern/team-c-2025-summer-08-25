import pygame
import numpy as np
import random
import sys
import os # Qテーブルの保存/ロード用

# --- ゲーム設定 ---
WIDTH, HEIGHT = 600, 400  # 画面サイズ
PLAYER_SIZE = 20          # プレイヤーのサイズ
SPEED = 5                 # プレイヤーの移動速度

# 色の定義
WHITE = (255, 255, 255)
RED = (255, 0, 0)   # 鬼 (Tagger)
BLUE = (0, 0, 255)  # 逃げる側 (Runner)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# --- Q学習パラメータ (鬼AI用) ---
# 状態空間の定義 (鬼から見た逃げる側の相対位置と近さ):
# 状態は (相対X方向, 相対Y方向, 近さ) のタプルで表現します。
# 相対X方向: -1 (逃げる側が左), 0 (同じX座標), 1 (逃げる側が右)
# 相対Y方向: -1 (逃げる側が上), 0 (同じY座標), 1 (逃げる側が下)
# 近さ: 0 (遠い), 1 (近い)
STATE_SPACE_SIZE = (3, 3, 2) # (相対X方向:左,同,右), (相対Y方向:上,同,下), (近さ:遠い,近い)

# 行動空間の定義 (鬼AIの行動):
# 0: 上, 1: 下, 2: 左, 3: 右, 4: 停止
ACTION_SPACE_SIZE = 5

# Qテーブルの初期化 (学習フェーズでTagger AI用)
# プログラム起動時に一度ゼロで初期化されるが、学習継続モードでは後でロードされる可能性がある
tagger_q_table = np.zeros(STATE_SPACE_SIZE + (ACTION_SPACE_SIZE,))
Q_TABLE_FILENAME = 'tagger_q_table.npy' # Qテーブルの保存ファイル名

# 学習パラメータ
LEARNING_RATE = 0.1       # 学習率 (α)
DISCOUNT_FACTOR = 0.9     # 割引率 (γ)
EXPLORATION_RATE = 1.0    # 探索率 (ε) - 初期値は1.0 (完全に探索)
EXPLORATION_DECAY_RATE = 0.9999 # 探索率の減衰率
MIN_EXPLORATION_RATE = 0.01 # 探索率の最小値

# 報酬 (鬼AIの視点)
REWARD_CAUGHT = 100       # 捕まえた時の大きなプラス報酬
REWARD_STEP = -1          # 1ステップごとにわずかなマイナス報酬 (早く捕まえることを奨励)
REWARD_LOSE = -50         # 逃げられた時のペナルティ (時間切れで捕まえられなかった場合)

# --- ゲームモード定義 ---
GAME_MODE_AI_LEARNS_TAGGER = 'ai_learns_tagger'     # AIが鬼の役割を学習
GAME_MODE_PRACTICE = 'practice'                     # 学習済みAIが鬼の役割を実践
GAME_MODE_HUMAN_TAGGER_PLAY = 'human_tagger_play'   # 人間が鬼を操作して遊ぶ (学習なし)


# --- プレイヤーコントロールタイプ ---
# Runnerは常に簡易AIなので、この定数はTaggerの学習/実践ロジックの可読性のため残す
CONTROL_TYPE_SIMPLE_AI = 'simple_ai'   # 簡易AI (追いかける/逃げる)
CONTROL_TYPE_RL_AI = 'rl_ai'           # 強化学習AI (Qテーブルに従う)
CONTROL_TYPE_HUMAN_WASD = 'human_wasd' # 人間がWASDで操作


# --- ゲームクラス ---
class Player:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)

    def draw(self, screen):
        # drawの際にも念のためrectの位置を更新
        self.rect.topleft = (self.x, self.y) 
        pygame.draw.rect(screen, self.color, self.rect)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        # 画面の境界チェック
        self.x = max(0, min(self.x, WIDTH - PLAYER_SIZE))
        self.y = max(0, min(self.y, HEIGHT - PLAYER_SIZE))
        # プレイヤーの移動後、rectの位置を更新する
        self.rect.topleft = (self.x, self.y)


class GameEnvironment:
    def __init__(self):
        self.reset()

    def reset(self):
        # プレイヤーの初期位置をランダムに設定
        self.tagger = Player(random.randint(0, WIDTH - PLAYER_SIZE),
                             random.randint(0, HEIGHT - PLAYER_SIZE),
                             RED)
        self.runner = Player(random.randint(0, WIDTH - PLAYER_SIZE),
                             random.randint(0, HEIGHT - PLAYER_SIZE),
                             BLUE)
        self.frame_iteration = 0
        return self._get_state()

    def _get_state(self):
        # 鬼 (Tagger) から見た逃げる側 (Runner) の相対位置と近さを状態として定義

        # 相対X方向 (TaggerにとってRunnerはどちらにいるか)
        if self.tagger.x < self.runner.x:
            rel_x_dir = 1  # RunnerはTaggerより右にいる (+X方向)
        elif self.tagger.x > self.runner.x:
            rel_x_dir = -1 # RunnerはTaggerより左にいる (-X方向)
        else:
            rel_x_dir = 0  # 同じX座標

        # 相対Y方向 (TaggerにとってRunnerはどちらにいるか)
        if self.tagger.y < self.runner.y:
            rel_y_dir = 1  # RunnerはTaggerより下にいる (+Y方向)
        elif self.tagger.y > self.runner.y:
            rel_y_dir = -1 # RunnerはTaggerより上にいる (-Y方向)
        else:
            rel_y_dir = 0  # 同じY座標

        # 近さ (TaggerとRunnerの距離が近いかどうか)
        distance = np.sqrt((self.tagger.x - self.runner.x)**2 + (self.tagger.y - self.runner.y)**2)
        proximity = 1 if distance < PLAYER_SIZE * 5 else 0 # 距離が近いかどうか

        # Qテーブルのインデックスに合わせるため、-1, 0, 1 を 0, 1, 2 に変換
        state_x = rel_x_dir + 1
        state_y = rel_y_dir + 1

        return (state_x, state_y, proximity)

    def step(self, tagger_action):
        self.frame_iteration += 1
        reward = REWARD_STEP  # 鬼AIは1ステップごとにペナルティ (早く捕まえるため)

        # --- 鬼 (Tagger) の行動 (渡されたアクションを適用) ---
        dx_tagger, dy_tagger = 0, 0
        if tagger_action == 0: dy_tagger = -SPEED # 上
        elif tagger_action == 1: dy_tagger = SPEED  # 下
        elif tagger_action == 2: dx_tagger = -SPEED # 左
        elif tagger_action == 3: dx_tagger = SPEED  # 右
        # tagger_action == 4: 停止 (dx, dy は0のまま)
        self.tagger.move(dx_tagger, dy_tagger)

        # --- 逃げる側 (Runner) の行動 (簡易AI: 鬼から遠ざかるように移動) ---
        dx_runner, dy_runner = 0, 0
        # RunnerのX座標がTaggerより小さい場合 (TaggerがRunnerの右にいる) -> Runnerはさらに左へ逃げる
        if self.runner.x < self.tagger.x:
            dx_runner = -SPEED
        # RunnerのX座標がTaggerより大きい場合 (TaggerがRunnerの左にいる) -> Runnerはさらに右へ逃げる
        elif self.runner.x > self.tagger.x:
            dx_runner = SPEED

        # RunnerのY座標がTaggerより小さい場合 (TaggerがRunnerの下にいる) -> Runnerはさらに上へ逃げる
        if self.runner.y < self.tagger.y:
            dy_runner = -SPEED
        # RunnerのY座標がTaggerより大きい場合 (TaggerがRunnerの上にいる) -> Runnerはさらに下へ逃げる
        elif self.runner.y > self.tagger.y:
            dy_runner = SPEED
        
        # ある程度の確率でランダムな動きを混ぜる (より予測不能に)
        if random.random() < 0.3: # 30%の確率でランダムな動き
            dx_runner = random.choice([-SPEED, 0, SPEED])
            dy_runner = random.choice([-SPEED, 0, SPEED])

        self.runner.move(dx_runner, dy_runner)

        game_over = False

        # --- 報酬計算 (鬼AIの視点) ---
        # 衝突判定
        if self.tagger.rect.colliderect(self.runner.rect):
            reward += REWARD_CAUGHT # 捕まえたら大きなプラス報酬
            game_over = True
            # print("鬼が捕まえた！")

        # 時間制限 (エピソードが長すぎるとペナルティ)
        if self.frame_iteration > 600:
            if not self.tagger.rect.colliderect(self.runner.rect): # 捕まえられなかった場合
                reward += REWARD_LOSE # 逃げられた場合のペナルティ
            game_over = True
            # print("時間切れ！")

        next_state = self._get_state()
        return next_state, reward, game_over

    def render(self, screen):
        screen.fill(BLACK)
        self.tagger.draw(screen)
        self.runner.draw(screen)
        pygame.display.flip()

# --- ヘルパー関数: 人間のキー入力をQ学習の行動に変換 ---
# AI学習モードではこの関数は使用されません
def get_human_tagger_action():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: return 0 # 上
    if keys[pygame.K_s]: return 1 # 下
    if keys[pygame.K_a]: return 2 # 左
    if keys[pygame.K_d]: return 3 # 右
    return 4 # 停止


# --- メイン関数 ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame RL 鬼ごっこ (AI自律学習)")
    clock = pygame.time.Clock()

    env = GameEnvironment()
    
    global EXPLORATION_RATE # グローバル変数としてexploration_rateを使用
    global tagger_q_table   # グローバル変数としてtagger_q_tableを使用

    # --- ゲームモードの選択 ---
    # ここを変更して学習フェーズ、実践フェーズ、人間操作プレイモードを切り替えます
    current_game_mode = GAME_MODE_AI_LEARNS_TAGGER # ← ここを変更してください
    # (例: GAME_MODE_PRACTICE または GAME_MODE_HUMAN_TAGGER_PLAY)

    if current_game_mode == GAME_MODE_AI_LEARNS_TAGGER:
        # --- AIが鬼を自律的に学習するフェーズ ---
        print("学習フェーズ開始: 鬼(赤)がAIとして自律的に学習します。逃げる側(青)は簡易AIとして動作。")
        print("学習が完了するか、ウィンドウを閉じるとQテーブルが保存されます。")

        # --- Qテーブルのロードまたはゼロ初期化 ---
        if os.path.exists(Q_TABLE_FILENAME):
            tagger_q_table = np.load(Q_TABLE_FILENAME)
            print(f"学習済みQテーブル '{Q_TABLE_FILENAME}' をロードし、学習を継続します。")
            # 探索率も前回の終了時点から再開したい場合、ここでロードする必要がありますが、
            # 初期値1.0から減衰させるのが一般的なので、ここではEXPLORATION_RATEはそのまま
            # (必要であれば、Qテーブルと一緒に保存/ロードするように拡張できます)
        else:
            tagger_q_table = np.zeros(STATE_SPACE_SIZE + (ACTION_SPACE_SIZE,))
            print("Qテーブルが見つからないため、ゼロから新しいQテーブルを作成しました。")
        # ------------------------------------

        num_episodes = 20000 # AIによる学習のエピソード数 (適宜調整)
        episode_rewards = []
        
        for episode in range(num_episodes):
            state = env.reset()
            episode_reward = 0
            done = False

            while not done:
                # Pygameイベント処理 (ウィンドウを閉じる)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        # ウィンドウが閉じられた場合、その時点までのQテーブルを保存してから終了
                        np.save(Q_TABLE_FILENAME, tagger_q_table)
                        print(f"学習中にウィンドウが閉じられました。Qテーブルを'{Q_TABLE_FILENAME}'に保存しました。")
                        pygame.quit()
                        sys.exit()

                # 鬼 (Tagger) AIの行動決定 (探索と活用のトレードオフ ε-greedy法)
                if random.uniform(0, 1) < EXPLORATION_RATE:
                    tagger_action = random.randint(0, ACTION_SPACE_SIZE - 1) # ランダムに行動 (探索)
                else:
                    tagger_action = np.argmax(tagger_q_table[state]) # Qテーブルから最適な行動を選択 (活用)

                # ゲームを1ステップ進める
                next_state, reward, done = env.step(tagger_action)

                # Q値の更新
                old_value = tagger_q_table[state + (tagger_action,)]
                next_max = np.max(tagger_q_table[next_state])
                
                new_value = old_value + LEARNING_RATE * (reward + DISCOUNT_FACTOR * next_max - old_value)
                tagger_q_table[state + (tagger_action,)] = new_value

                state = next_state
                episode_reward += reward

                env.render(screen)
                clock.tick(60) # 1秒間に60フレーム

            episode_rewards.append(episode_reward)

            # 探索率の減衰
            EXPLORATION_RATE = max(MIN_EXPLORATION_RATE, EXPLORATION_RATE * EXPLORATION_DECAY_RATE)

            if episode % 100 == 0:
                avg_reward_100_episodes = np.mean(episode_rewards[-100:]) if episode_rewards else 0
                print(f"エピソード: {episode}/{num_episodes}, 探索率: {EXPLORATION_RATE:.4f}, 平均報酬 (過去100エピソード): {avg_reward_100_episodes:.2f}")

        # 学習終了後、Qテーブルを保存
        np.save(Q_TABLE_FILENAME, tagger_q_table)
        print(f"学習終了。Qテーブルを'{Q_TABLE_FILENAME}'に保存しました。")
        print("\nこれで実践フェーズに移行できます。`current_game_mode` を `GAME_MODE_PRACTICE` に変更して再実行してください。")

    elif current_game_mode == GAME_MODE_PRACTICE:
        # --- 実践フェーズ ---
        print("実践フェーズ開始: 鬼(赤)が学習済み戦略で実践、逃げる側(青)は簡易AIとして動作")
        
        # 学習済みQテーブルのロード
        if os.path.exists(Q_TABLE_FILENAME):
            tagger_q_table = np.load(Q_TABLE_FILENAME)
            print(f"学習済みQテーブル '{Q_TABLE_FILENAME}' をロードしました。")
        else:
            print(f"エラー: 学習済みQテーブル '{Q_TABLE_FILENAME}' が見つかりません。")
            print("まず学習フェーズを実行してQテーブルを保存してください。")
            pygame.quit()
            sys.exit()

        # 実践フェーズでは探索を行わない (完全に活用)
        EXPLORATION_RATE_PRACTICE = 0 
        num_episodes = 100 # 実践は少なめのエピソードで
        episode_rewards = []

        for episode in range(num_episodes):
            state = env.reset()
            episode_reward = 0
            done = False

            while not done:
                # Pygameイベント処理 (ウィンドウを閉じる)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                # 鬼 (Tagger) AIの行動決定 (活用のみ)
                tagger_action = np.argmax(tagger_q_table[state])

                # ゲームを1ステップ進める
                next_state, reward, done = env.step(tagger_action)

                state = next_state
                episode_reward += reward

                env.render(screen)
                clock.tick(60) # 1秒間に60フレーム

            episode_rewards.append(episode_reward)

            if episode % 10 == 0:
                avg_reward_10_episodes = np.mean(episode_rewards[-10:]) if episode_rewards else 0
                print(f"実践エピソード: {episode}/{num_episodes}, 報酬: {episode_reward}, 平均報酬 (過去10エピソード): {avg_reward_10_episodes:.2f}")

        print("実践フェーズ終了")

    elif current_game_mode == GAME_MODE_HUMAN_TAGGER_PLAY:
        # --- 人間が鬼を操作して遊ぶモード (AI学習なし) ---
        print("プレイフェーズ開始: 人間(WASD)が鬼を操作、逃げる側(青)は簡易AIとして動作")
        print("WASDキーで赤い鬼を動かして、青い逃げる側を捕まえよう！")

        while True: # 無限ループでプレイ
            state = env.reset() # 新しいゲームを開始
            game_over = False

            while not game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                
                # 人間のキー入力から鬼のアクションを取得
                tagger_action = get_human_tagger_action()

                # ゲームを1ステップ進める (報酬や次状態は計算されるが、Qテーブルは更新されない)
                next_state, reward, game_over = env.step(tagger_action)

                env.render(screen)
                clock.tick(60) # 1秒間に60フレーム
            
            # ゲームオーバー後、少し待ってから次のエピソードへ
            pygame.time.wait(1000) # 1秒待機


    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
