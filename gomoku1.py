import sys

# 棋盘大小，标准五子棋为 15x15
BOARD_SIZE = 15

def create_board():
    """初始化 15x15 的二维数组，'.' 表示空位"""
    return [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def print_board(board):
    """打印当前棋盘状态"""
    # 打印顶部的列号 (0-9 循环显示)
    print('  ' + ' '.join(str(i%10) for i in range(BOARD_SIZE)))
    for i, row in enumerate(board):
        # 打印左侧的行号和该行的棋盘状态
        print(str(i%10).rjust(2) + ' ' + ' '.join(row))

def is_valid_move(board, x, y):
    """检查坐标是否在棋盘范围内，并且该位置为空"""
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and board[y][x] == '.'

def make_move(board, x, y, player):
    """在指定位置落子"""
    board[y][x] = player

def check_win(board, x, y, player):
    """检查当前落子是否导致玩家获胜 (五子连珠)"""
    # 定义四个检查方向：水平、垂直、主对角线(\)、副对角线(/)
    directions = [(1,0), (0,1), (1,1), (1,-1)]
    for dx, dy in directions:
        count = 1  # 包含当前刚落下的棋子
        
        # 向正方向最多检查 4 步
        for i in range(1,5):
            nx, ny = x + dx*i, y + dy*i
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == player:
                count += 1
            else:
                break
                
        # 向反方向最多检查 4 步
        for i in range(1,5):
            nx, ny = x - dx*i, y - dy*i
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == player:
                count += 1
            else:
                break
                
        # 如果某条直线上存在连续 5 个相同棋子，判断获胜
        if count >= 5:
            return True
            
    return False

def main():
    board = create_board()
    players = ['X', 'O']  # X 先手，O 后手
    current = 0  # 当前玩家的索引 (0 或 1)
    
    while True:
        print_board(board)
        player = players[current]
        
        try:
            # 提示玩家输入坐标
            move = input(f'Player {player} enter move (x y): ')
            
            # 检查是否退出游戏
            if move.lower() in ['quit', 'exit']:
                print('Game ended')
                break
                
            parts = move.strip().split()
            if len(parts) != 2:
                print('Invalid input, use two numbers')
                continue
            x, y = map(int, parts)
        except ValueError:
            print('Please enter numbers')
            continue
            
        # 检查落子合法性
        if not is_valid_move(board, x, y):
            print('Invalid move, try again')
            continue
            
        # 执行落子
        make_move(board, x, y, player)
        
        # 当某一方落子后检查是否获胜
        if check_win(board, x, y, player):
            print_board(board)
            print(f'Player {player} wins!')
            break
            
        # 切换到下一个玩家
        current = 1 - current

if __name__ == '__main__':
    main()