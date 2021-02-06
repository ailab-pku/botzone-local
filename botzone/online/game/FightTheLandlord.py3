# todo 继续做呗

import random
import math
import json
from collections import Counter

###################################################牌型编码###################################################
# 红桃 方块 黑桃 草花
# 3 4 5 6 7 8 9 10 J Q K A 2 joker & Joker
# (0-h3 1-d3 2-s3 3-c3) (4-h4 5-d4 6-s4 7-c4) …… 52-joker 53-Joker
###################################################牌型编码###################################################

priorityPokerType = {
    "火箭":3,
    "炸弹":2
}
extraScorePokerType = {
    "空":0,
    "火箭":16,
    "炸弹":10,
    "单张":1,
    "一对":2,
    "单顺":6,
    "双顺":6,
    "三带零":4,
    "三带一":4,
    "三带二":4,
    "四带两只":8,
    "四带两对":8,
    "飞机不带翼":8,
    "航天飞机不带翼":10,
    "飞机带小翼":8,
    "飞机带大翼":8,
    "航天飞机带小翼":10,
    "航天飞机带大翼":10
}

pokerDown = [0 for i in range(54)]
solution = []
currTurn = -1
allDown = False

# 将数字换算成点数
def convertToPoint(x):
    return int(x/4) + 3 + (x==53)

def initGame(full_input):
    seedRandom = str(random.randint(0, 2147483647))

    if "initdata" not in full_input:
        full_input["initdata"] = {}
    try:
        full_input["initdata"] = json.loads(full_input["initdata"])
    except Exception:
        pass

    if "seed" in full_input["initdata"]:
        seedRandom = full_input["initdata"]["seed"] 
    

    if "allocation" in full_input["initdata"]:
        allocation = full_input["initdata"]["allocation"]
    else: # 产生大家各自有什么牌
        allo = [i for i in range(54)]
        random.shuffle(allo)
        allocation = [allo[0:20], allo[20:37], allo[37:54]]

    if "publiccard" in full_input["initdata"]:
        publiccard = full_input["initdata"]["publiccard"]
    else:
        publiccard = allocation[0][0:3]

    return full_input, seedRandom, allocation, publiccard

# J,Q,K,A,2-11,12,13,14,15
# 单张：1 一对：2 三带：零3、一4、二5 单顺：>=5 双顺：>=6
# 四带二：6、8 飞机：>=6
def checkPokerType(poker): # poker：list，表示一个人出牌的牌型
    poker.sort()
    lenPoker = len(poker)

    ################################################# 0张 #################################################
    if lenPoker == 0:
        return "空", [], []

    ################################################# 1张 #################################################
    if lenPoker == 1:
        return "单张", poker, []

    ################################################# 2张 #################################################
    if lenPoker == 2 and poker == [52, 53]:
        return "火箭", poker, []
    if lenPoker == 2 and convertToPoint(poker[0]) == convertToPoint(poker[1]):
        return "一对", poker, []
    if lenPoker == 2:
        return "错误", poker, []

    #################################### 转换成点数，剩下牌一定大于等于3张 ###################################
    # 扑克牌点数
    ptrOfPoker = [convertToPoint(i) for i in poker]
    firstPtrOfPoker = ptrOfPoker[0]
    # 计数 
    cntPoker = Counter(ptrOfPoker)
    keys, vals = list(cntPoker.keys()), list(cntPoker.values())

    ################################################# 4张 #################################################
    if lenPoker == 4 and vals.count(4) == 1:
        return "炸弹", poker, []
    
    ############################################## >=5张 单顺 #############################################
    singleSeq = [firstPtrOfPoker+i for i in range(lenPoker)]
    if (lenPoker >= 5) and (15 not in singleSeq) and (ptrOfPoker == singleSeq):
        return "单顺", poker, []
    
    ############################################## >=6张 双顺 #############################################
    pairSeq = [firstPtrOfPoker+i for i in range(int(lenPoker / 2))]
    pairSeq = [j for j in pairSeq for i in range(2)]
    if (lenPoker >= 6) and (lenPoker % 2 == 0) and (15 not in pairSeq) and (ptrOfPoker == pairSeq):
        return "双顺", poker, []
    
    ################################################# 3张带 ################################################
    if (lenPoker <= 5) and (vals.count(3) == 1):
        if vals.count(1) == 2:
            return "错误", poker, [] 
        specialPoker = keys[vals.index(3)]
        triplePoker = [i for i in poker if convertToPoint(i) == specialPoker]
        restPoker = [i for i in poker if i not in triplePoker]
        tripleNames = ["三带零", "三带一", "三带二"]
        return tripleNames[lenPoker - 3], triplePoker, restPoker

    ############################################## 6张 四带二只 ############################################
    if (lenPoker == 6) and (vals.count(4) == 1) and (vals.count(1) == 2):
        specialPoker = keys[vals.index(4)]
        quadruplePoker = [i for i in poker if convertToPoint(i) == specialPoker]
        restPoker = [i for i in poker if i not in quadruplePoker]
        return "四带两只", quadruplePoker, restPoker        

    ############################################## 8张 四带二对 ############################################
    if (lenPoker == 8) and (vals.count(4) == 1) and (vals.count(2) == 2):
        specialPoker = keys[vals.index(4)]
        quadruplePoker = [i for i in poker if convertToPoint(i) == specialPoker]
        restPoker = [i for i in poker if i not in quadruplePoker]
        return "四带两对", quadruplePoker, restPoker        
 
    # 分别表示张数有0、1、2、3张的是什么点数的牌
    keyList = [[], [], [], [], []]
    for idx in range(len(vals)):
        keyList[vals[idx]] += [keys[idx]]
    lenKeyList = [len(i) for i in keyList]
    ################################################## 飞机 ################################################ 
    if lenKeyList[3] > 1 and 15 not in keyList[3] and \
        (keyList[3] == [keyList[3][0] + i for i in range(lenKeyList[3])]):
        if lenKeyList[3] * 3 == lenPoker:
            return "飞机不带翼", poker, []
        triplePoker = [i for i in poker if convertToPoint(i) in keyList[3]]
        restPoker = [i for i in poker if i not in triplePoker]
        if (lenKeyList[3] == lenKeyList[1]) and (lenKeyList[1] * 4 == lenPoker):
            return "飞机带小翼", triplePoker, restPoker
        if (lenKeyList[3] == lenKeyList[2]) and (lenKeyList[2] * 5 == lenPoker):
            return "飞机带大翼", triplePoker, restPoker
        
    ################################################# 航天飞机 ############################################## 
    if lenKeyList[4] > 1 and lenKeyList[3] == 0 and 15 not in keyList[4] and \
        (keyList[4] == [keyList[4][0] + i for i in range(lenKeyList[4])]):
        if lenKeyList[4] * 4 == lenPoker:
            return "航天飞机不带翼", poker, []
        quadruplePoker = [i for i in poker if convertToPoint(i) in keyList[4]]
        restPoker = [i for i in poker if i not in quadruplePoker]
        if (lenKeyList[4] == lenKeyList[1]) and (lenKeyList[1] * 5 == lenPoker):
            return "航天飞机带小翼", quadruplePoker, restPoker
        if (lenKeyList[4] == lenKeyList[2]) and (lenKeyList[2] * 6 == lenPoker):
            return "航天飞机带大翼", quadruplePoker, restPoker
    
    return "错误", poker, []
        
def recover(history): # 只考虑倒数3个，返回最后一个有效牌型及主从牌，且返回之前有几个人选择了pass；id是为了防止某一出牌人在某一牌局后又pass，然后造成连续pass
    lenHistory = len(history)
    typePoker, mainPoker, restPoker, cntPass = "任意牌", [], [], 0

    while(lenHistory > 0):
        lastPoker = history[lenHistory - 1]
        typePoker, mainPoker, restPoker = checkPokerType(lastPoker)
        if typePoker == "空":
            cntPass += 1
            lenHistory -= 1
            continue
        break
    return typePoker, mainPoker, restPoker, cntPass

def getExtraScore(history):
    score = [0,0,0]
    lenH = len(history)
    for i in range(lenH):
        currBotID = i % 3
        currPoker = history[i]
        typePoker, mainPoker, _ = checkPokerType(currPoker)
        tmpScore = extraScorePokerType[typePoker]
        if "航天飞机" in typePoker and len(mainPoker) >= 12:
            tmpScore += 10
        score[currBotID] += tmpScore
    score = [i / 100 for i in score]
    return score

def printError(currTurn, ex, solution):
    score = []
    if currTurn <= 0:
        score = [-1, 2.5, 2.5]
    else:
        score = [2.5, -1, -1]
    if len(solution) == 0:
        solution = [[]]
    print(json.dumps({
            "command": "finish",
            "content": {
                "0": score[0],
                "1": score[1],
                "2": score[2]
            },
            "display": {
                "event": {
                    "player": currTurn,
                    "action": solution[-1]
                },
                "errorInfo": str(ex),
                "0": score[0],
                "1": score[1],
                "2": score[2]
            }
        }))
    exit(0)

def printRequest(nextTurn, printContent, currTurn, solution):
    solution = solution[-2:]
    if len(solution) == 1:
        solution = [[]] + solution
    printContent["history"] = solution
    print(json.dumps({
        "command": "request",
        "content": {
            str(nextTurn): printContent
        },
        "display": {
            "event": {
                "player": currTurn,
                "action": solution[-1]
            }
        }
    }))
    exit(0)

def printFinish(extraScore, currTurn, solution):
    score = []
    if currTurn and 1:
        score = [0, 2, 2]
    else:
        score = [2, 0, 0]
    score = [score[i]+extraScore[i] for i in range(3)]
    score[1] = (score[1] + score[2]) / 2
    score[2] = score[1]
    print(json.dumps({
        "command": "finish",
        "content": {
            "0": score[0],
            "1": score[1],
            "2": score[2]
        },
        "display": {
            "event": {
                "player": currTurn,
                "action": solution[-1]
            },
            "0": score[0],
            "1": score[1],
            "2": score[2]
        }
    }))  
    exit(0) 

_online = True
# 第一关地主pass的话会出错
try:
    if _online:
        full_input = json.loads(input())
    else:
        with open("logs.json") as fo:
            full_input = json.load(fo)
    
    full_input, seedRandom, allocation, publiccard = initGame(full_input)    
    random.seed(seedRandom)

    printContent = {}
    lenLog = len(full_input["log"])
    currPlayer = int(lenLog / 2) % 3
    if lenLog < 6:
        printContent = {
            "own":allocation[currPlayer],
            "history":[],
            "publiccard":publiccard
        }
    else:
        printContent = {
            "history":[]
        }
    if lenLog == 0: # judge的第一回合，处理大家有什么牌
        # content叫谁，allocation表示地主[0]:20张和农民[1]:17张 [2]:17张各自拥有什么牌
        printContent["history"] = [[], []]
        print(json.dumps({
            "command": "request",
            "content": {
                "0": printContent
            },
            "display": {
                "allocation": allocation,
                "publiccard" : publiccard
            },
            "initdata": {
                "allocation": allocation,
                "publiccard" : publiccard,
                "seed": seedRandom
            }
        }))
        exit(0) # 直接退出

    # 之后的回合，直接读
    rest = [[i for i in j] for j in allocation]

    botResult = full_input["log"][1]["0"]
    if botResult["verdict"] != "OK":
        raise ValueError("INVALID_INPUT_VERDICT_" + botResult["verdict"])
    tmp = botResult["response"]
    if len(tmp) == 0: 
        currTurn = 0
        solution += [[]]
        raise ValueError("INVALID_PASS") # 地主第一回合就pass，显然是错误的

    for i in range(1, lenLog, 2):
        currTurn = (currTurn + 1) % 3 # 0:landlord   1,2:farmer
        restOwn = rest[currTurn]
        botResult = full_input["log"][i][str(currTurn)]
        if botResult["verdict"] != "OK":
            raise ValueError("INVALID_INPUT_VERDICT_" + botResult["verdict"])
        tmp = botResult["response"]
        solution += [tmp]
        for i in tmp:
            if i not in allocation[currTurn]:
                raise ValueError("MISSING_CARD") # 这个人不应该有这张牌
            if i < 0 or i > 53:
                raise ValueError("OUT_OF_RANGE") # 给的牌超出了范围
            if pokerDown[i]:
                raise ValueError("REPEATED_CARD") # 这张牌之前已经被出过了
            pokerDown[i] = True
            restOwn.remove(i)
        if len(restOwn) == 0:
            allDown = True
        
    lenSolve = len(solution) # currTurn == (lenSolve - 1) % 3
    nextTurn = lenSolve % 3
    extraScore = getExtraScore(solution)

    currTypePoker, currMainPoker, currRestPoker = checkPokerType(solution[-1])
    if currTypePoker == "错误":
        raise ValueError("INVALID_CARDTYPE") # 牌型错误
    lastTypePoker, lastMainPoker, lastRestPoker, cntPass = recover(solution[:-1])
    if lastTypePoker == "任意牌" or lastTypePoker == "空" or cntPass == 2:
        if currTypePoker == "空":
            raise ValueError("INVALID_PASS") # 不合理的pass，显然是错误的
        else: # 任意出或者前二者都不要的话，自己可以随意出，因为上一轮也是自己的牌
            if allDown: # 这一回合的出牌者已经把牌都出完了，赢得了最终胜利
                printFinish(extraScore, currTurn, solution)          
            else:
                printRequest(nextTurn, printContent, currTurn, solution)
    if currTypePoker == "空":
        printRequest(nextTurn, printContent, currTurn, solution)
    lastPPT, currPPT = priorityPokerType.get(lastTypePoker, 1), priorityPokerType.get(currTypePoker, 1)
    if lastPPT < currPPT: # 现在的牌型比上一个牌型要大，直接过，这时候要考虑当前玩家所有牌都出完的情况
        if allDown:
            printFinish(extraScore, currTurn, solution) 
        else:    
            printRequest(nextTurn, printContent, currTurn, solution)
    if lastPPT > currPPT:
        raise ValueError("LESS_COMPARE") # 现在的牌型比上一个牌型要小
    if lastTypePoker != currTypePoker:
        raise ValueError("MISMATCH_CARDTYPE") # 牌型不一致
    lenCom = len(currMainPoker)
    if len(lastMainPoker) != lenCom or len(currRestPoker) != len(lastRestPoker):
        raise ValueError("MISMATCH_CARDLENGTH") # 牌型长度不一致
    currComMP, lastComMP = [convertToPoint(i) for i in currMainPoker], [convertToPoint(i) for i in lastMainPoker]
    
    comRes = [currComMP[i] > lastComMP[i] for i in range(lenCom)]
    if all(comRes):
        if allDown: # 这一回合的出牌者已经把牌都出完了，赢得了最终胜利
            printFinish(extraScore, currTurn, solution)        
        else:
            printRequest(nextTurn, printContent, currTurn, solution)
    else:
        raise ValueError("LESS_COMPARE") # 现在的牌型比上一个牌型要小

except ValueError as ex:
    printError(currTurn, ex, solution)
except Exception:
    printError(currTurn, "BAD_FORMAT", solution)