import json
from queue import Queue
from collections import OrderedDict


'''
 黑棋颜色用0表示，白棋则为1，黑棋先手
 棋盘为一个字符串，每一行用'\n'间隔，最外层有一圈边界
 边界用' '和'\n'表示，空位用'.'表示，当前玩家的棋子用'X'表示，对方棋子则是'x'
 坐标为左上角从（1,1）开始，x轴正方向向右，y轴正方向向下
'''

komi = 0.75     # 贴子，采用贴0又3/4子
WIDTH = 8   # 棋盘规模
TOTAL = WIDTH**2
direct = [-WIDTH-2, 1, WIDTH+2, -1]     # 上、右、下、左
empty = '\n'.join([' '*(WIDTH + 1)] + [' ' + '.'*WIDTH]*WIDTH + [' '*(WIDTH + 2)])
LEN = len(empty)    # 线性表示的棋盘长度


class Utils:
    # 处理json输入，将字符串变为json
    @staticmethod
    def json_input():
        raw = input()
        obj = json.loads(raw, object_pairs_hook=OrderedDict)
        return OrderedDict(obj)

    # 处理json输出，将json变为字符串
    @staticmethod
    def json_output(obj):
        raw = json.dumps(obj)
        print(raw)

    # 用来将二维坐标变成一维索引
    @staticmethod
    def xy_to_l(x, y):
        return y * (WIDTH + 2) + x

    # 用来将一维索引变为二维坐标
    @staticmethod
    def l_to_xy(l):
        ext = WIDTH + 2
        return l % ext, l // ext


# 用来确定同一颜色的连续的一团棋子
# 接受输入为合法字符串表示的棋盘和一个棋子的线性坐标
def slice_group(board, l):
    visit = [0]*LEN
    color = board[l]
    q = Queue()
    record = [l]
    visit[l] = 1
    q.put(l)
    while not q.empty():
        here = q.get()
        for d in direct:
            tmp = here + d
            if tmp < 0 or tmp >= LEN or visit[tmp] != 0 or board[tmp] != color:
                continue
            visit[tmp] = 1
            q.put(tmp)
            record.append(tmp)
    return record


# 用来计算一团同色棋子还有多少气
# 接受输入为合法字符串表示的棋盘和一个列表，列表是连续同色棋子团的线性坐标
def count_liberty(board, group):
    counted = [0] * LEN
    count = 0
    for l in group:
        for d in direct:
            tmp = l + d
            if tmp < 0 or tmp >= LEN or counted[tmp] != 0:
                continue
            if board[tmp] == '.':
                counted[tmp] = 1
                count += 1
    return count


# 将由group指定的坐标对应的棋子从棋盘上提走
def take(board, group):
    copy_board = bytearray(board, 'utf-8')
    for l in group:
        copy_board[l] = ord('.')
    return copy_board.decode('utf-8')


# 在棋盘上坐标(x,y)处为当前玩家'X'放置一个棋子
def settle(board, x, y, just_try=False):
    linear = Utils.xy_to_l(x, y)     # 用线性坐标
    if linear < 0 or linear >= LEN:
        return False, board, []
    if board[linear] != '.':
        return False, board, []
    new_board = bytearray(board, 'utf-8')
    new_board[linear] = ord('X')
    new_board = new_board.decode('utf-8')
    remove = []
    for d in direct:    # 只会影响到新放置的棋子周围的棋子
        tmp = linear + d
        if tmp < 0 or tmp >= LEN:
            continue
        if new_board[tmp] == 'x':   # 周围的对方棋子先受到影响
            affects = slice_group(new_board, tmp)
            liberty = count_liberty(new_board, affects)
            if liberty < 1:     # 对方这团棋子已经是死子了
                new_board = take(new_board, affects)
                for position in affects:
                    x_position, y_position = Utils.l_to_xy(position)
                    remove.append({"x": x_position, "y": y_position})
    # 提完对方棋子，再看自己是不是死棋
    new_group = slice_group(new_board, linear)
    liberty = count_liberty(new_board, new_group)
    if liberty < 1:     # 自杀棋步，不合规则
        return False, board, []
    elif just_try:
        return True, board, []
    else:
        return True, new_board, remove


def possible_moves(board):
    possibles = []
    for x in range(1, WIDTH + 1):
        for y in range(1, WIDTH + 1):
            good_move, next_board, remove = settle(board, x, y, True)
            if good_move:
                possibles.append([x, y])
    return possibles


def proportion(board, linear):
    my_count, op_count = 0, 0
    for d in direct:
        tmp = linear + d
        if tmp < 0 or tmp >= LEN:
            continue
        my_count += board[tmp] == 'X'
        op_count += board[tmp] == 'x'
    if my_count < 1:
        return 0.0
    elif op_count > 0:
        return 0.5
    else:
        return 1.0


def flood_fill(board, l):
    if l < 0 or l >= LEN or board[l] != '.':
        return False, board
    q = Queue()
    q.put(l)
    curboard = bytearray(board, 'utf-8')
    curboard[l] = ord('#')
    while not q.empty():
        here = q.get()
        for d in direct:
            tmp = here + d
            if tmp < 0 or tmp >= LEN or curboard[tmp] != ord('.'):
                continue
            curboard[tmp] = ord('#')
            q.put(tmp)
    return curboard.decode('utf-8')


def contact(board):
    flag1 = False
    flag2 = False
    for i in range(LEN):
        if board[i] == '#':
            for d in direct:
                tmp = i + d
                if tmp < 0 or tmp >= LEN:
                    continue
                if board[tmp] == 'X':
                    flag1 = True
                elif board[tmp] == 'x':
                    flag2 = True
    return flag1, flag2


def count_stones(board):
    while '.' in board:
        i = board.index('.')
        board = flood_fill(board, i)
        flag1, flag2 = contact(board)
        if flag1 and not flag2:
            board = board.replace('#', 'X')
        elif not flag1 and flag2:
            board = board.replace('#', 'x')
        else:
            board = board.replace('#', ':')
    base = board.count('X')
    extra = board.count(':')
    return base + extra / 2


def output_from_log(log):
    board = empty
    length = len(log)
    output = OrderedDict()
    # 第一回合输入的log是空的，此时的输出是缺省值
    if length < 1:
        output["command"] = "request"
        output["display"] = ""
        output["content"] = {"0": {"x": -2, "y": -2}}
        return output
    else:
        # 已经不是第一回合了
        i = -1
        count_for_pass = 0          # 用来记录连续虚着的次数
        records = OrderedDict()     # 用来记录历史局面
        while True:
            i += 2
            is_last = (i == length - 1)     # 判断是否是最近一次response
            #bot_color = str(int(((i - 1) / 2) % 2))         # 1->0,3->1,5->0,7->1....
            bot_color = [bot for bot in log[i].keys()][0]
            turn_num = (i + 1) // 2
            verdict = log[i][bot_color].get("verdict")
            response = log[i][bot_color].get("response") or log[i][bot_color].get("content") or {}
            if type(response) == str: response = {}
            x, y = None, None
            try:
                x, y = response["x"], response["y"]
            except:
                pass
            if not is_last:
                # 不是最近一次response
                if x == -1 and y == -1:     # 虚着点
                    count_for_pass += 1
                else:
                    count_for_pass = 0
                    good_move, board, remove = settle(board, x, y)  # 相信以往的输入都是合法的，直接执行
                board = board.swapcase()    # 交换'X'和'x'，表示当前玩家的改变
                # FIXME 如果一方局面重复了对方曾经的情形，也会被判负
                records[board] = turn_num   # 记录盘面和对应的轮数
            else:
                # 是最后一次response
                # 先检查是否还可以继续棋局（这里暂时先不做了）
                current_possible = possible_moves(board)
                opposite_possible = possible_moves(board.swapcase())
                len1 = len(current_possible)
                if False and len1 < 1:
                    output["command"] = "request"
                    output["display"] = ""
                    tmp = str(1-int(bot_color))
                    output["content"] = {tmp: {"x": -1, "y": -1}}
                    '''
                    output["command"] = "finish"
                    score = [0, 0]
                    stones = count_stones(board)
                    threshold = TOTAL / 2
                    # 先手贴子
                    if bot_color == 0:
                        threshold += komi
                    else:
                        threshold -= komi
                    output["display"] = {}
                    output["display"]["stones"] = \
                        {bot_color: stones, str(1-int(bot_color)): TOTAL-stones, "komi": komi}
                    if stones > threshold:
                        output["display"]["winner"] = int(bot_color)
                        score[int(bot_color)] += 2
                    elif stones < threshold:
                        output["display"]["winner"] = 1 - int(bot_color)
                        score[1 - int(bot_color)] += 2
                    else:
                        output["display"]["winner"] = "none"
                        score = [1, 1]
                    output["content"] = {"0": score[0], "1": score[1]}
                    '''
                    return output
                if type(x) != int or type(y) != int:  # 输入的格式不对
                    output["display"] = \
                        {"winner": 1 - int(bot_color),
                         "error": "INVALID_INPUT_VERDICT_" + verdict,
                         "error_info": "输入数据不是整数"}
                    output["command"] = "finish"
                    score = [2, 2]
                    score[int(bot_color)] -= 2
                    output["content"] = {"0": score[0], "1": score[1]}
                    return output
                # 当前玩家虚着
                if x == -1 and y == -1:
                    count_for_pass += 1
                    # 连续两次虚着，棋局终了
                    if count_for_pass >= 2:
                        output["command"] = "finish"
                        score = [0, 0]
                        stones = count_stones(board)
                        threshold = TOTAL / 2
                        # 先手贴子
                        if int(bot_color) == 0:
                            threshold += komi
                        else:
                            threshold -= komi
                        output["display"] = {}
                        output["display"]["stones"] = \
                            {bot_color: stones, str(1 - int(bot_color)): TOTAL - stones, "komi": komi}
                        if stones > threshold:
                            output["display"]["winner"] = int(bot_color)
                            score[int(bot_color)] += 2
                        elif stones < threshold:
                            output["display"]["winner"] = 1 - int(bot_color)
                            score[1 - int(bot_color)] += 2
                        output["content"] = {"0": score[0], "1": score[1]}
                        return output
                    # 没达到连续2次，继续棋局
                    else:
                        board = board.swapcase()
                        turn = records.get(board)   # 从记录中查看是否出现以往盘面
                        if turn is not None:        # 重复盘面出现，输入不合法
                            output["command"] = "finish"
                            output["display"] = \
                                {"winner": 1 - int(bot_color),
                                 "error": "CIRCULAR_MOVE",
                                 "error_info": "出现全同局面，与第" + str(turn) + "回合相同"}
                            score = [2, 2]
                            score[int(bot_color)] -= 2
                            output["content"] = {"0": score[0], "1": score[1]}
                            return output
                        else:
                            output["command"] = "request"
                            output["display"] = ""
                            tmp = str(1-int(bot_color))
                            output["content"] = {tmp: {"x": -1, "y": -1}}
                            return output
                # 当前玩家没有虚着
                else:
                    good_move, board, remove = settle(board, x, y)
                    board = board.swapcase()
                    # 不合法的落子，也不允许自杀走子
                    if not good_move:
                        output["command"] = "finish"
                        output["display"] = \
                            {"winner": 1-int(bot_color),
                             "error": "INVALID_MOVE",
                             "error_info": "走子违反规则，落在禁着点"}
                        score = [2, 2]
                        score[int(bot_color)] -= 2
                        output["content"] = {"0": score[0], "1": score[1]}
                        return output
                    # 合法落子
                    else:
                        turn = records.get(board)
                        if turn is not None:
                            output["command"] = "finish"
                            output["display"] = \
                                {"winner": 1 - int(bot_color),
                                 "error": "CIRCULAR_MOVE",
                                 "error_info": "出现全同局面，与第" + str(turn) + "回合相同"}
                            score = [2, 2]
                            score[int(bot_color)] -= 2
                            output["content"] = {"0": score[0], "1": score[1]}
                            return output
                        else:
                            output["command"] = "request"
                            output["display"] = \
                                {"color": int(bot_color), "x": x, "y": y, "remove": remove}
                            tmp = str(1 - int(bot_color))
                            output["content"] = {tmp: {"x": x, "y": y}}
                            return output


def main():
    raw = Utils.json_input()
    log = raw["log"]
    output = output_from_log(log)
    Utils.json_output(output)


if __name__ == '__main__':
    main()