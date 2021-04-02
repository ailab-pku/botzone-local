from botzone.envs.registration import register
from botzone.online import games

# Wrapper Env from Botzone Online
for game in games.all():
    register(id = '%s-wrap' % game)

# Python Env for botzone
register(
    id = 'Amazons-v8',
    entry_point = 'botzone.envs.botzone.amazons:AmazonsEnv',
    size = 8
)
register(
    id = 'Amazons-v10',
    entry_point = 'botzone.envs.botzone.amazons:AmazonsEnv',
    size = 10
)
register(
    id = 'Ataxx-v0',
    entry_point = 'botzone.envs.botzone.ataxx:AtaxxEnv',
    limit = 400
)
register(
    id = 'FightTheLandlord-v0',
    entry_point = 'botzone.envs.botzone.fightthelandlord:FightTheLandlordEnv',
    small = True
)
register(
    id = 'FightTheLandlord-v1',
    entry_point = 'botzone.envs.botzone.fightthelandlord:FightTheLandlordEnv',
    small = False
)
register(
    id = 'Go-v8',
    entry_point = 'botzone.envs.botzone.go:GoEnv',
    size = 8,
    komi = 0.75
)
register(
    id = 'Go-v9',
    entry_point = 'botzone.envs.botzone.go:GoEnv',
    size = 9,
    komi = 3.25
)
register(
    id = 'Go-v13',
    entry_point = 'botzone.envs.botzone.go:GoEnv',
    size = 13,
    komi = 3.25
)
register(
    id = 'Go-v19',
    entry_point = 'botzone.envs.botzone.go:GoEnv',
    size = 19,
    komi = 3.25
)
register(
    id = 'Gomoku-v15',
    entry_point = 'botzone.envs.botzone.gomoku:GomokuEnv',
    size = 15
)
register(
    id = 'MineSweeper-v0',
    entry_point = 'botzone.envs.botzone.minesweeper:MineSweeperEnv'
)
register(
    id = 'NoGo-v9',
    entry_point = 'botzone.envs.botzone.nogo:NoGoEnv',
    size = 9
)
register(
    id = 'Renju-v15',
    entry_point = 'botzone.envs.botzone.renju:RenjuEnv',
    size = 15
)
register(
    id = 'Reversi-v0',
    entry_point = 'botzone.envs.botzone.reversi:ReversiEnv'
)
register(
    id = 'Snake-v0',
    entry_point = 'botzone.envs.botzone.snake:SnakeEnv'
)
register(
    id = 'TicTacToe-v0',
    entry_point = 'botzone.envs.botzone.tictactoe:TicTacToeEnv'
)

register(
    id = 'ChineseStandardMahjong-v0-dup',
    entry_point = 'botzone.envs.botzone.chinesestandardmahjong:ChineseStandardMahjongEnv',
    duplicate = True
)

register(
    id = 'ChineseStandardMahjong-v0',
    entry_point = 'botzone.envs.botzone.chinesestandardmahjong:ChineseStandardMahjongEnv',
    duplicate = False
)

register(
    id = 'Kingz-v0',
    entry_point = 'botzone.envs.botzone.kingz:KingzEnv',
    limit = 300
)