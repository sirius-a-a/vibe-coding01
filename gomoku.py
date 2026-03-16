import sys

BOARD_SIZE = 15

def create_board():
    return [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def print_board(board):
    print('  ' + ' '.join(str(i%10) for i in range(BOARD_SIZE)))
    for i, row in enumerate(board):
        print(str(i%10).rjust(2) + ' ' + ' '.join(row))

def is_valid_move(board, x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and board[y][x] == '.'

def make_move(board, x, y, player):
    board[y][x] = player

def check_win(board, x, y, player):
    directions = [(1,0), (0,1), (1,1), (1,-1)]
    for dx, dy in directions:
        count = 1
        for i in range(1,5):
            nx, ny = x + dx*i, y + dy*i
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == player:
                count += 1
            else:
                break
        for i in range(1,5):
            nx, ny = x - dx*i, y - dy*i
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == player:
                count += 1
            else:
                break
        if count >= 5:
            return True
    return False

def main():
    board = create_board()
    players = ['X', 'O']
    current = 0
    while True:
        print_board(board)
        player = players[current]
        try:
            move = input(f'Player {player} enter move (x y): ')
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
        if not is_valid_move(board, x, y):
            print('Invalid move, try again')
            continue
        make_move(board, x, y, player)
        if check_win(board, x, y, player):
            print_board(board)
            print(f'Player {player} wins!')
            break
        current = 1 - current

if __name__ == '__main__':
    main()