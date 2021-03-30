def runMatch(env, bots):
    env.init(bots)
    score = env.reset()
    env.render()
    while score is None:
        score = env.step()
        env.render()
    else:
        print('Score:', score)

def testInterface():
    try:
        import botzone
        env_wrap = botzone.make('TicTacToe-wrap')
        env_impl = botzone.make('TicTacToe-v0')

        from botzone.online.bot import BotConfig, Bot
        bot_cpp = Bot(BotConfig.fromID('6017e6b10b59850f61c42b0a')) # cpp17+json+keep_running
        bot_pas = Bot(BotConfig.fromID('5ff96b0d38843939e7477556')) # pas+simple_io+no_keep_running
        from botzone.agents.tictactoe import TicTacToeAgent
        bot_impl = TicTacToeAgent()

        print('Using wrapper env + wrapper bot:')
        runMatch(env_wrap, [bot_cpp, bot_pas])

        print('Using wrapper env + python bot:')
        runMatch(env_wrap, [bot_impl, bot_impl])

        print('Using python env + wrapper bot:')
        runMatch(env_impl, [bot_cpp, bot_pas])

        print('Using python env + python bot:')
        runMatch(env_impl, [bot_impl, bot_impl])
    finally:
        env_wrap.close()
        bot_cpp.close()
        bot_pas.close()

def testBot():
    try:
        from botzone.online.bot import BotConfig, Bot
        bots = []
        bots.append(Bot(BotConfig.fromID('5ff9514438843939e7476086'))) # cpp17
        bots.append(Bot(BotConfig.fromID('5ff952f438843939e7476202'))) # cpp17a
        bots.append(Bot(BotConfig.fromID('5ff9528a38843939e74761c5'))) # py
        bots.append(Bot(BotConfig.fromID('601cecd85d7325256064e52d'))) # py3
        bots.append(Bot(BotConfig.fromID('5ff9534b38843939e7476296'))) # py36
        bots.append(Bot(BotConfig.fromID('5ff9650038843939e7476f1a'))) # java
        bots.append(Bot(BotConfig.fromID('5ff95d8738843939e74769b9'))) # js
        bots.append(Bot(BotConfig.fromID('5ff9599638843939e74766cb'))) # cs
        bots.append(Bot(BotConfig.fromID('5ff96b0d38843939e7477556'))) # pas

        import botzone
        env = botzone.make('TicTacToe-v0')
        from botzone.agents.tictactoe import TicTacToeAgent
        bot_impl = TicTacToeAgent()

        for bot in bots:
            print('Trying bot with language', bot.config.extension)
            runMatch(env, [bot_impl, bot])
    finally:
        for bot in bots:
            bot.close()

def testGame():
    samples = {
        'Amazons': '5bd136e00681335cc1f4d000',
        'Ataxx': '58d8c01327d1065e145ee3f7',
        'ChineseStandardMahjong': '5e918db24a3d0c0568f34083',
        'FightTheLandlord': '5af06df6a5858d0880e515f2',
        'Go': '5b00f35d765c7d10b6600016',
        'Gomoku': '543b462e71a5d5647363cbb0',
        'Kingz': '5e3539ae4019f43051e2e3f5',
        'Minesweeper': '547e71f4012273d146ac0e2d',
        'NoGo': '5fede20fd9383f7579afff06',
        'Pacman': '5724f78f8b8b8ad504b23e01',
        'Pacman2': '57fdc7900167d91505cda684',
        'Renju': '5444a5414319ba6866ff41ff',
        'Reversi': '5afe9e6f6cc5394385d40062',
        'Snake': '555ef3aa7110330007712994',
        'Tank': '5bc836510681335cc1ef467b',
        'Tank2': '5cb5abf18aa8bb6e75cc9b84',
        'Tank2S': '5cd5818a86d50d05a0095859',
        'Tetris': '58fddf2233b28604c34e2af5',
        'Tetris2': '59f860eb5a11ed72c933561e',
        'TicTacToe': '5ff9514438843939e7476086'
    }
    envs = {
        'Amazons': 'Amazons-v8',
        'Ataxx': 'Ataxx-v0',
        'ChineseStandardMahjong': 'ChineseStandardMahjong-v0-dup',
        'FightTheLandlord': 'FightTheLandlord-v0',
        'Go': 'Go-v8',
        'Gomoku': 'Gomoku-v15',
        'Kingz': 'Kingz-v0',
        'Minesweeper': 'MineSweeper-v0',
        'NoGo': 'NoGo-v9',
        'Pacman': 'Pacman-wrap',
        'Pacman2': 'Pacman2-wrap',
        'Renju': 'Renju-v15',
        'Reversi': 'Reversi-v0',
        'Snake': 'Snake-v0',
        'Tank': 'Tank-wrap',
        'Tank2': 'Tank2-wrap',
        'Tank2S': 'Tank2S-wrap',
        'Tetris': 'Tetris-wrap',
        'Tetris2': 'Tetris2-wrap',
        'TicTacToe': 'TicTacToe-v0'
    }
    import botzone
    from botzone.online.bot import BotConfig, Bot
    for game in sorted(samples.keys()):
        print('Trying game', game)
        try:
            env = botzone.make(envs[game])
            bots = [Bot(BotConfig.fromID(samples[game])) for i in range(env.player_num)]
            runMatch(env, bots)
        finally:
            env.close()
            for bot in bots:
                bot.close()

def testMahjong():
    top4 = ['5fed4d34d9383f7579af41fc', '5f0fc0f37e197a05f07f616a', '5f9d308c8121aa566529ab03', '5fe2cc74d9383f7579a4334b']
    from botzone.online.sandbox import SandBox
    SandBox.CONFIG_TIME_RATIO = 3
    try:
        import botzone
        env = botzone.make('ChineseStandardMahjong-v0-dup')
        from botzone.online.bot import BotConfig, Bot
        bots = [Bot(BotConfig.fromID(id, userfile = True)) for id in top4]
        runMatch(env, bots)
    finally:
        env.close()
        for bot in bots:
            bot.close()

if __name__ == '__main__':
    testInterface()
    testBot()
    testGame()
    testMahjong()