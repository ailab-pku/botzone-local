_games = [
    dict(
        name = "Reversi",
        title = "黑白棋",
        player = 2,
        extension = "cpp",
        keep_running = False,
        transform_code = {
            "supported": True,
            "request_from_json": "return request.x+' '+request.y;",
            "response_to_json": "var parts = response.split(' ').map(function (x) { return parseInt(x) });\nreturn {x:parts[0],y:parts[1]};",
            "response_from_json": "return response.x+' '+response.y;",
        }
    ),
    dict(
        name = "Minesweeper",
        title = "扫雷",
        player = 1,
        extension = "cpp",
        keep_running = False,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "Gomoku",
        title = "无禁手五子棋",
        player = 2,
        extension = "js",
        keep_running = False,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "Renju",
        title = "换手版五子棋",
        player = 2,
        extension = "js",
        keep_running = False,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "FightTheLandlord",
        title = "斗地主",
        player = 3,
        extension = "py3",
        keep_running = False,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "Snake",
        title = "贪食蛇",
        player = 2,
        extension = "cpp",
        keep_running = False,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "Pacman",
        title = "吃 豆 人",
        player = 4,
        extension = "cpp",
        keep_running = False,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "Pacman2",
        title = "吃豆人·改",
        player = 4,
        extension = "cpp",
        keep_running = False,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "Ataxx",
        title = "同化棋",
        player = 2,
        extension = "cpp",
        keep_running = False,
        transform_code = {
            "supported": True,
            "request_from_json": 'return request.x0 + " " + request.y0 + " " + request.x1 + " " + request.y1;',
            "response_to_json": "var parts = response.split(' ').map(function (x) { return parseInt(x) });\nreturn { x0: parts[0], y0: parts[1], x1: parts[2], y1: parts[3] };",
            "response_from_json": 'return response.x0 + " " + response.y0 + " " + response.x1 + " " + response.y1;',
        }
    ),
    dict(
        name = "Tetris",
        title = "俄罗斯方块",
        player = 2,
        extension = "cpp11",
        keep_running = False,
        transform_code = {
            "supported": True,
            "request_from_json": 'if ("x" in request)\n    return request.block + " " + request.x + " " + request.y + " " + request.o;\nreturn request.block + " " + request.color;',
            "response_to_json": 'var parts = response.split(" ").map(function (x) { return parseInt(x) });\nif (parts.length == 4) {\n    return {\n        block: parts[0],\n        x: parts[1],\n        y: parts[2],\n        o: parts[3]\n    };\n}\nvar res = {seq: []}, l = parts[1];\nres.block = parts[0];\nfor (var i = 0; i < l; i++) {\n    res.seq[i] = {\n        x: parts[i * 3 + 2],\n        y: parts[i * 3 + 3],\n        o: parts[i * 3 + 4]\n    }\n}\nreturn res;',
            "response_from_json": 'if ("seq" in response)\n    return response.block + " " + response.seq.length + response.seq.map(function (s) { return s.x + " " + s.y + " " + s.o; }).join(" ");\nreturn response.block + " " + response.x + " " + response.y + " " + response.o;',
        }
    ),
    dict(
        name = "Amazons",
        title = "亚马逊棋",
        player = 2,
        extension = "cpp11",
        keep_running = False,
        transform_code = {
            "supported": True,
            "request_from_json": "return [request.x0, request.y0, request.x1, request.y1, request.x2, request.y2].join(' ');",
            "response_to_json": "var all = response.split(' ').map(x => parseInt(x));\nreturn {\n    x0: all[0],\n    y0: all[1],\n    x1: all[2],\n    y1: all[3],\n    x2: all[4],\n    y2: all[5]\n};",
            "response_from_json": "return [response.x0, response.y0, response.x1, response.y1, response.x2, response.y2].join(' ');",
        }
    ),
    dict(
        name = "Tetris2",
        title = "俄罗斯方块·改",
        player = 2,
        extension = "cpp11",
        keep_running = False,
        transform_code = {
            "supported": True,
            "request_from_json": 'if ("x" in request)\n    return request.block + " " + request.x + " " + request.y + " " + request.o;\nreturn request.block + " " + request.color;',
            "response_to_json": 'var parts = response.split(" ").map(function (x) { return parseInt(x) });\nif (parts.length == 4) {\n    return {\n        block: parts[0],\n        x: parts[1],\n        y: parts[2],\n        o: parts[3]\n    };\n}\nvar res = {seq: []}, l = parts[1];\nres.block = parts[0];\nfor (var i = 0; i < l; i++) {\n    res.seq[i] = {\n        x: parts[i * 3 + 2],\n        y: parts[i * 3 + 3],\n        o: parts[i * 3 + 4]\n    }\n}\nreturn res;',
            "response_from_json": 'if ("seq" in response)\n    return response.block + " " + response.seq.length + response.seq.map(function (s) { return s.x + " " + s.y + " " + s.o; }).join(" ");\nreturn response.block + " " + response.x + " " + response.y + " " + response.o;',
        }
    ),
    dict(
        name = "Go",
        title = "围棋",
        player = 2,
        extension = "py3",
        keep_running = False,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "Tank",
        title = "坦克大战",
        player = 2,
        extension = "cpp17",
        keep_running = False,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "NoGo",
        title = "不围棋",
        player = 2,
        extension = "cpp17",
        keep_running = False,
        transform_code = {
            "supported": True,
            "request_from_json": 'return request.x + " " + request.y;',
            "response_to_json": "var x = response.split(' ');\nreturn {x: parseInt(x[0]), y: parseInt(x[1])};",
            "response_from_json": 'return request.x + " " + request.y;',
        }
    ),
    dict(
        name = "Tank2",
        title = "坦克大战·改",
        player = 2,
        extension = "cpp17",
        keep_running = False,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "Tank2S",
        title = "",
        player = 2,
        extension = "cpp17",
        keep_running = False,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "TicTacToe",
        title = "井字棋",
        player = 2,
        extension = "cpp17",
        keep_running = False,
        transform_code = {
            "supported": True,
            "request_from_json": "return request.x+' '+request.y;",
            "response_to_json": "var parts = response.split(' ').map(function (x) { return parseInt(x) });\nreturn {x:parts[0],y:parts[1]};",
            "response_from_json": "return response.x+' '+response.y;",
        }
    ),
    dict(
        name = "Kingz",
        title = "国王",
        player = 2,
        extension = "cpp11",
        keep_running = True,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "FightTheLandlord2",
        title = "斗地主·改",
        player = 3,
        extension = "py36",
        keep_running = False,
        transform_code = {
            "supported": False,
            "request_from_json": '',
            "response_to_json": '',
            "response_from_json": '',
        }
    ),
    dict(
        name = "ChineseStandardMahjong",
        title = "国标麻将·复式",
        player = 4,
        extension = "elfbin",
        keep_running = False,
        transform_code = {
            "supported": True,
            "request_from_json": 'return request;',
            "response_to_json": 'return response;',
            "response_from_json": 'return response;',
        }
    )
]
_games = {g['name'] : g for g in _games}

_id2name = {
'53e1db360003e29c2ba227b8' : 'Reversi',
'5417aecb2acc7d3007fb0a39' : 'Minesweeper',
'5433ee8126a551c62982afea' : 'Gomoku',
'543bd8aed6cc9d5e0fb94cf0' : 'Renju',
'545840890003e2b77caf768f' : 'FightTheLandlord',
'550183b60003e25477128460' : 'Snake',
'56f0f40eec0b4f26230d7848' : 'Pacman',
'57fdbe7b79fc08ec04cc49b0' : 'Pacman2',
'5809c7647f65182b044b5e3b' : 'Ataxx',
'58f3adf8d9c62b2c44cffe52' : 'Tetris',
'59463fb292a2ea07a5c6b5a8' : 'Amazons',
'59db27f2e206af05cdb010b3' : 'Tetris2',
'5a6939cbf055de48942ae2f3' : 'Go',
'5a9e5f0a7382f62abae6dba5' : 'Tank',
'5ab65ae77ec1de5c52e18940' : 'NoGo',
'5c908e0e7857b210f901be7d' : 'Tank2',
'5c9ef6ac9f425613e1da0765' : 'Tank2S',
'5d7f30ecbdd782060f8d3234' : 'TicTacToe',
'5daacfa8fc925f63c8301972' : 'Kingz',
'5e36c89c4019f43051e45589' : 'FightTheLandlord2',
'5e37dcf74019f43051e53201' : 'ChineseStandardMahjong'
}

def all():
    return _games

def get_by_name(name):
    '''
    Get game info by name. Return None if not found.
    '''
    return _games.get(name, None)

def get_by_id(id):
    '''
    Get game info by ID. Return None if not found.
    '''
    return _games.get(_id2name.get(id, None), None)