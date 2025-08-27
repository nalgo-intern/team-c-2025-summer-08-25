# oni.py
from collections import deque

def bfs(grid, start_pos, end_pos):
    """
    BFSを使って、grid上のstart_posからend_posまでの最短経路を探索する。

    :param grid: 2Dリストのマップデータ ('#'は壁, '.'は通路)
    :param start_pos: 開始座標 (x, y)
    :param end_pos: 目的地の座標 (x, y)
    :return: 最短経路のリスト。見つからない場合はNone。
    """
    width, height = len(grid[0]), len(grid)
    queue = deque([[start_pos]])  # キューには経路のリストを入れる
    visited = {start_pos}

    while queue:
        path = queue.popleft()
        x, y = path[-1]

        if (x, y) == end_pos:
            return path  # 目的地に到達したら経路を返す

        # 上下左右の4方向を探索
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy

            # マップの範囲内かつ、壁ではなく、未訪問の場所かチェック
            if 0 <= nx < width and 0 <= ny < height and \
               grid[ny][nx] != '#' and (nx, ny) not in visited:
                
                visited.add((nx, ny))
                new_path = list(path)
                new_path.append((nx, ny))
                queue.append(new_path)
    
    return None # 目的地までの経路が見つからなかった場合

def get_oni_next_move(grid, oni_pos, player_pos):
    """
    鬼が次に動くべき最適な座標を返す。

    :param grid: 2Dリストのマップデータ
    :param oni_pos: 鬼の現在座標 (x, y)
    :param player_pos: プレイヤーの現在座標 (x, y)
    :return: 鬼が次に移動すべき座標 (x, y)。経路がない場合は現在の座標を返す。
    """
    # BFSで鬼からプレイヤーへの最短経路を探す
    path = bfs(grid, oni_pos, player_pos)

    if path and len(path) > 1:
        # 経路が見つかった場合、現在の位置の次(インデックス1)が次の一歩
        return path[1]
    else:
        # 経路が見つからない、または既に隣接している場合は動かない
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