/*
 * cPacman2Judge
 * 作者：hy
 * 时间：2016/3/22 15:32:51
 * 最后更新：2016/10/11 13:21
 * 更新内容2：增加技能
 * 更新内容：人类玩家第一次超时不罚死啦；正确判断产生器不允许踩上的事情（并且将产生器围了起来）
 *
 * 【命名惯例】
 *  r/R/y/Y：Row，行，纵坐标
 *  c/C/x/X：Column，列，横坐标
 *  数组的下标都是[y][x]或[r][c]的顺序
 *  玩家编号0123
 *
 * 【坐标系】
 *   0 1 2 3 4 5 6 7 8
 * 0 +----------------> x
 * 1 |
 * 2 |
 * 3 |
 * 4 |
 * 5 |
 * 6 |
 * 7 |
 * 8 |
 *   v y
 *
 * 【提示】你可以使用
 * #ifndef _BOTZONE_ONLINE
 * 这样的预编译指令来区分在线评测和本地评测
 *
 * 【提示】一般的文本编辑器都会支持将代码块折叠起来
 * 如果你觉得自带代码太过冗长，可以考虑将整个namespace折叠
 */

#include <fstream>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <algorithm>
#include <string>
#include <cstring>
#include <stack>
#include <stdexcept>
#include "jsoncpp/json.h"

#define FIELD_MAX_HEIGHT 20
#define FIELD_MAX_WIDTH 20
#define MAX_GENERATOR_COUNT 4 // 每个象限1
#define MAX_PLAYER_COUNT 4
#define MAX_TURN 100

// 你也可以选用 using namespace std; 但是会污染命名空间
using std::string;
using std::swap;
using std::cin;
using std::cout;
using std::endl;
using std::getline;
using std::runtime_error;

// 平台提供的吃豆人相关逻辑处理程序
namespace Pacman
{

	const int dx[] = { 0, 1, 0, -1, 1, 1, -1, -1 }, dy[] = { -1, 0, 1, 0, -1, 1, 1, -1 };

	// 枚举定义；使用枚举虽然会浪费空间（sizeof(GridContentType) == 4），但是计算机处理32位的数字效率更高

	// 每个格子可能变化的内容，会采用“或”逻辑进行组合
	enum GridContentType
	{
		empty = 0, // 其实不会用到
		player1 = 1, // 1号玩家
		player2 = 2, // 2号玩家
		player3 = 4, // 3号玩家
		player4 = 8, // 4号玩家
		playerMask = 1 | 2 | 4 | 8, // 用于检查有没有玩家等
		smallFruit = 16, // 小豆子
		largeFruit = 32 // 大豆子
	};

	// 用玩家ID换取格子上玩家的二进制位
	GridContentType playerID2Mask[] = { player1, player2, player3, player4 };
	string playerID2str[] = { "0", "1", "2", "3" };

	// 让枚举也可以用这些运算了（不加会编译错误）
	template<typename T>
	inline T operator |=(T &a, const T &b)
	{
		return a = static_cast<T>(static_cast<int>(a) | static_cast<int>(b));
	}
	template<typename T>
	inline T operator |(const T &a, const T &b)
	{
		return static_cast<T>(static_cast<int>(a) | static_cast<int>(b));
	}
	template<typename T>
	inline T operator &=(T &a, const T &b)
	{
		return a = static_cast<T>(static_cast<int>(a) & static_cast<int>(b));
	}
	template<typename T>
	inline T operator &(const T &a, const T &b)
	{
		return static_cast<T>(static_cast<int>(a) & static_cast<int>(b));
	}
	template<typename T>
	inline T operator -(const T &a, const T &b)
	{
		return static_cast<T>(static_cast<int>(a) - static_cast<int>(b));
	}
	template<typename T>
	inline T operator ++(T &a)
	{
		return a = static_cast<T>(static_cast<int>(a) + 1);
	}
	template<typename T>
	inline T operator ~(const T &a)
	{
		return static_cast<T>(~static_cast<int>(a));
	}

	// 每个格子固定的东西，会采用“或”逻辑进行组合
	enum GridStaticType
	{
		emptyWall = 0, // 其实不会用到
		wallNorth = 1, // 北墙（纵坐标减少的方向）
		wallEast = 2, // 东墙（横坐标增加的方向）
		wallSouth = 4, // 南墙（纵坐标增加的方向）
		wallWest = 8, // 西墙（横坐标减少的方向）
		generator = 16 // 豆子产生器
	};

	// 用移动方向换取这个方向上阻挡着的墙的二进制位
	GridStaticType direction2OpposingWall[] = { wallNorth, wallEast, wallSouth, wallWest };

	// 方向，可以代入dx、dy数组，同时也可以作为玩家的动作
	enum Direction
	{
		stay = -1,
		up = 0,
		right = 1,
		down = 2,
		left = 3,
		shootUp = 4, // 向上发射金光
		shootRight = 5, // 向右发射金光
		shootDown = 6, // 向下发射金光
		shootLeft = 7 // 向左发射金光
	};

	// 场地上带有坐标的物件
	struct FieldProp
	{
		int row, col;
	};

	// 场地上的玩家
	struct Player : FieldProp
	{
		int strength;
		int powerUpLeft;
		bool dead;
	};

	// 回合新产生的豆子的坐标
	struct NewFruits
	{
		FieldProp newFruits[MAX_GENERATOR_COUNT * 8];
		int newFruitCount;
	} newFruits[MAX_TURN];
	int newFruitsCount = 0;

	// 状态转移记录结构
	struct TurnStateTransfer
	{
		enum StatusChange // 可组合
		{
			none = 0,
			ateSmall = 1,
			ateLarge = 2,
			powerUpDrop = 4,
			die = 8,
			error = 16
		};

		// 玩家选定的动作
		Direction actions[MAX_PLAYER_COUNT];

		// 此回合该玩家的状态变化
		StatusChange change[MAX_PLAYER_COUNT];

		// 此回合该玩家的力量变化
		int strengthDelta[MAX_PLAYER_COUNT];
	};

	// 游戏主要逻辑处理类，包括输入输出、回合演算、状态转移，全局唯一
	class GameField
	{
	private:
		// 我不会为了面向对象而把属性都放到private里

		// 记录每回合的变化（栈）
		TurnStateTransfer backtrack[MAX_TURN];

		// 这个对象是否已经创建
		static bool constructed;

	public:
		// 场地的长和宽
		int height, width;
		int generatorCount;
		int GENERATOR_INTERVAL, LARGE_FRUIT_DURATION, LARGE_FRUIT_ENHANCEMENT, SKILL_COST;

		// 场地格子固定的内容
		GridStaticType fieldStatic[FIELD_MAX_HEIGHT][FIELD_MAX_WIDTH];

		// 场地格子会变化的内容
		GridContentType fieldContent[FIELD_MAX_HEIGHT][FIELD_MAX_WIDTH];
		int generatorTurnLeft; // 多少回合后产生豆子
		int aliveCount; // 有多少玩家存活
		int smallFruitCount;
		int turnID;
		FieldProp generators[MAX_GENERATOR_COUNT]; // 有哪些豆子产生器
		Player players[MAX_PLAYER_COUNT]; // 有哪些玩家

		// 玩家选定的动作
		Direction actions[MAX_PLAYER_COUNT];

		// 恢复到上次场地状态。可以一路恢复到最开始。
		// 恢复失败（没有状态可恢复）返回false
		bool PopState()
		{
			if (turnID <= 0)
				return false;

			const TurnStateTransfer &bt = backtrack[--turnID];
			int i, _;

			// 倒着来恢复状态

			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				GridContentType &content = fieldContent[_p.row][_p.col];
				TurnStateTransfer::StatusChange change = bt.change[_];

				// 5. 大豆回合恢复
				if (change & TurnStateTransfer::powerUpDrop)
					_p.powerUpLeft++;

				// 4. 吐出豆子
				if (change & TurnStateTransfer::ateSmall)
				{
					content |= smallFruit;
					smallFruitCount++;
				}
				else if (change & TurnStateTransfer::ateLarge)
				{
					content |= largeFruit;
					_p.powerUpLeft -= LARGE_FRUIT_DURATION;
				}

				// 2. 魂兮归来
				if (change & TurnStateTransfer::die)
				{
					_p.dead = false;
					aliveCount++;
					content |= playerID2Mask[_];
				}

				// 1. 移形换影
				if (!_p.dead && bt.actions[_] != stay && bt.actions[_] < shootUp)
				{
					fieldContent[_p.row][_p.col] &= ~playerID2Mask[_];
					_p.row = (_p.row - dy[bt.actions[_]] + height) % height;
					_p.col = (_p.col - dx[bt.actions[_]] + width) % width;
					fieldContent[_p.row][_p.col] |= playerID2Mask[_];
				}

				// 0. 救赎不合法的灵魂
				if (change & TurnStateTransfer::error)
				{
					_p.dead = false;
					aliveCount++;
					content |= playerID2Mask[_];
				}

				// *. 恢复力量
				_p.strength -= bt.strengthDelta[_];
			}

			// 3. 收回豆子
			if (generatorTurnLeft == GENERATOR_INTERVAL)
			{
				generatorTurnLeft = 1;
				NewFruits &fruits = newFruits[--newFruitsCount];
				for (i = 0; i < fruits.newFruitCount; i++)
				{
					fieldContent[fruits.newFruits[i].row][fruits.newFruits[i].col] &= ~smallFruit;
					smallFruitCount--;
				}
			}
			else
				generatorTurnLeft++;

			return true;
		}

		// 判断指定玩家向指定方向移动/施放技能是不是合法的（没有撞墙且没有踩到豆子产生器、力量足够）
		inline bool ActionValid(int playerID, Direction &dir) const
		{
			if (dir == stay)
				return true;
			const Player &p = players[playerID];
			if (dir >= shootUp)
				return dir < 8 && p.strength > SKILL_COST;
			return dir >= 0 && dir < 4 &&
				!(fieldStatic[p.row][p.col] & direction2OpposingWall[dir]);
		}

		// 在向actions写入玩家动作后，演算下一回合局面，并记录之前所有的场地状态，可供日后恢复。
		// 是终局的话就返回false
		bool NextTurn()
		{
			int _, i, j;

			TurnStateTransfer &bt = backtrack[turnID];
			memset(&bt, 0, sizeof(bt));

			// 0. 杀死不合法输入
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &p = players[_];
				if (!p.dead)
				{
					Direction &action = actions[_];
					if (action == stay)
						continue;

					if (!ActionValid(_, action))
					{
						bt.strengthDelta[_] += -p.strength;
						bt.change[_] = TurnStateTransfer::error;
						fieldContent[p.row][p.col] &= ~playerID2Mask[_];
						p.strength = 0;
						p.dead = true;
						aliveCount--;
					}
					else if (action < shootUp)
					{
						// 遇到比自己强♂壮的玩家是不能前进的
						GridContentType target = fieldContent
							[(p.row + dy[action] + height) % height]
							[(p.col + dx[action] + width) % width];
						if (target & playerMask)
							for (i = 0; i < MAX_PLAYER_COUNT; i++)
								if (target & playerID2Mask[i] && players[i].strength > p.strength)
									action = stay;
					}
				}
			}

			// 1. 位置变化
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];

				bt.actions[_] = actions[_];

				if (_p.dead || actions[_] == stay || actions[_] >= shootUp)
					continue;

				// 移动
				fieldContent[_p.row][_p.col] &= ~playerID2Mask[_];
				_p.row = (_p.row + dy[actions[_]] + height) % height;
				_p.col = (_p.col + dx[actions[_]] + width) % width;
				fieldContent[_p.row][_p.col] |= playerID2Mask[_];
			}

			// 2. 玩家互殴
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				if (_p.dead)
					continue;

				// 判断是否有玩家在一起
				int player, containedCount = 0;
				int containedPlayers[MAX_PLAYER_COUNT];
				for (player = 0; player < MAX_PLAYER_COUNT; player++)
					if (fieldContent[_p.row][_p.col] & playerID2Mask[player])
						containedPlayers[containedCount++] = player;

				if (containedCount > 1)
				{
					// NAIVE
					for (i = 0; i < containedCount; i++)
						for (j = 0; j < containedCount - i - 1; j++)
							if (players[containedPlayers[j]].strength < players[containedPlayers[j + 1]].strength)
								swap(containedPlayers[j], containedPlayers[j + 1]);

					int begin;
					for (begin = 1; begin < containedCount; begin++)
						if (players[containedPlayers[begin - 1]].strength > players[containedPlayers[begin]].strength)
							break;

					// 这些玩家将会被杀死
					int lootedStrength = 0;
					for (i = begin; i < containedCount; i++)
					{
						int id = containedPlayers[i];
						Player &p = players[id];

						// 从格子上移走
						fieldContent[p.row][p.col] &= ~playerID2Mask[id];
						p.dead = true;
						int drop = p.strength / 2;
						bt.strengthDelta[id] += -drop;
						bt.change[id] |= TurnStateTransfer::die;
						lootedStrength += drop;
						p.strength -= drop;
						aliveCount--;
					}

					// 分配给其他玩家
					int inc = lootedStrength / begin;
					for (i = 0; i < begin; i++)
					{
						int id = containedPlayers[i];
						Player &p = players[id];
						bt.strengthDelta[id] += inc;
						p.strength += inc;
					}
				}
			}

			// 2.5 金光法器
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				if (_p.dead || actions[_] < shootUp)
					continue;

				_p.strength -= SKILL_COST;
				bt.strengthDelta[_] -= SKILL_COST;

				int r = _p.row, c = _p.col, player;
				Direction dir = actions[_] - shootUp;

				// 向指定方向发射金光（扫描格子直到被挡）
				while (!(fieldStatic[r][c] & direction2OpposingWall[dir]))
				{
					r = (r + dy[dir] + height) % height;
					c = (c + dx[dir] + width) % width;

					// 如果转了一圈回来……
					if (r == _p.row && c == _p.col)
						break;

					if (fieldContent[r][c] & playerMask)
						for (player = 0; player < MAX_PLAYER_COUNT; player++)
						{
							Player &p = players[player];

							// 本回合自杀者也会受到攻击
							if (p.row == r && p.col == c && (!p.dead || bt.change[player] == TurnStateTransfer::error))
							{
								players[player].strength -= SKILL_COST * 1.5;
								bt.strengthDelta[player] -= SKILL_COST * 1.5;
								_p.strength += SKILL_COST * 1.5;
								bt.strengthDelta[_] += SKILL_COST * 1.5;
							}
						}
				}
			}

			// *. 检查一遍有无死亡玩家
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				if (_p.dead || _p.strength > 0)
					continue;

				// 从格子上移走
				fieldContent[_p.row][_p.col] &= ~playerID2Mask[_];
				_p.dead = true;

				// 使其力量变为0
				bt.strengthDelta[_] += -_p.strength;
				bt.change[_] |= TurnStateTransfer::die;
				_p.strength = 0;
				aliveCount--;
			}


			// 3. 产生豆子
			if (--generatorTurnLeft == 0)
			{
				generatorTurnLeft = GENERATOR_INTERVAL;
				NewFruits &fruits = newFruits[newFruitsCount++];
				fruits.newFruitCount = 0;
				for (i = 0; i < generatorCount; i++)
					for (Direction d = up; d < 8; ++d)
					{
						// 取余，穿过场地边界
						int r = (generators[i].row + dy[d] + height) % height, c = (generators[i].col + dx[d] + width) % width;
						if (fieldStatic[r][c] & generator || fieldContent[r][c] & (smallFruit | largeFruit))
							continue;
						fieldContent[r][c] |= smallFruit;
						fruits.newFruits[fruits.newFruitCount].row = r;
						fruits.newFruits[fruits.newFruitCount++].col = c;
						smallFruitCount++;
					}
			}

			// 4. 吃掉豆子
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				if (_p.dead)
					continue;

				GridContentType &content = fieldContent[_p.row][_p.col];

				// 只有在格子上只有自己的时候才能吃掉豆子
				if (content & playerMask & ~playerID2Mask[_])
					continue;

				if (content & smallFruit)
				{
					content &= ~smallFruit;
					_p.strength++;
					bt.strengthDelta[_]++;
					smallFruitCount--;
					bt.change[_] |= TurnStateTransfer::ateSmall;
				}
				else if (content & largeFruit)
				{
					content &= ~largeFruit;
					if (_p.powerUpLeft == 0)
					{
						_p.strength += LARGE_FRUIT_ENHANCEMENT;
						bt.strengthDelta[_] += LARGE_FRUIT_ENHANCEMENT;
					}
					_p.powerUpLeft += LARGE_FRUIT_DURATION;
					bt.change[_] |= TurnStateTransfer::ateLarge;
				}
			}

			// 5. 大豆回合减少
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				if (_p.dead)
					continue;

				if (_p.powerUpLeft > 0)
				{
					bt.change[_] |= TurnStateTransfer::powerUpDrop;
					if (--_p.powerUpLeft == 0)
					{
						_p.strength -= LARGE_FRUIT_ENHANCEMENT;
						bt.strengthDelta[_] += -LARGE_FRUIT_ENHANCEMENT;
					}
				}
			}

			// *. 检查一遍有无死亡玩家
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				if (_p.dead || _p.strength > 0)
					continue;

				// 从格子上移走
				fieldContent[_p.row][_p.col] &= ~playerID2Mask[_];
				_p.dead = true;

				// 使其力量变为0
				bt.strengthDelta[_] += -_p.strength;
				bt.change[_] |= TurnStateTransfer::die;
				_p.strength = 0;
				aliveCount--;
			}

			++turnID;

			// 是否只剩一人？
			if (aliveCount <= 1)
			{
				for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
					if (!players[_].dead)
					{
						bt.strengthDelta[_] += smallFruitCount;
						players[_].strength += smallFruitCount;
					}
				return false;
			}

			// 是否回合超限？
			if (turnID >= 100)
				return false;

			return true;
		}

		// 读取并解析程序输入，本地调试或提交平台使用都可以。
		// 如果在本地调试，程序会先试着读取参数中指定的文件作为输入文件，失败后再选择等待用户直接输入。
		// 本地调试时可以接受多行以便操作，Windows下可以用 Ctrl-Z 或一个【空行+回车】表示输入结束，但是在线评测只需接受单行即可。
		// localFileName 可以为NULL
		// obtainedData 会输出自己上回合存储供本回合使用的数据
		// obtainedGlobalData 会输出自己的 Bot 上以前存储的数据
		// 返回值是自己的 playerID
		int ReadInput(const char *localFileName, string &obtainedData, string &obtainedGlobalData)
		{
			string str, chunk;
#ifdef _BOTZONE_ONLINE
			std::ios::sync_with_stdio(false); //ω\\)
			getline(cin, str);
#else
			if (localFileName)
			{
				std::ifstream fin(localFileName);
				if (fin)
					while (getline(fin, chunk) && chunk != "")
						str += chunk;
				else
					while (getline(cin, chunk) && chunk != "")
						str += chunk;
			}
			else
				while (getline(cin, chunk) && chunk != "")
					str += chunk;
#endif
			Json::Reader reader;
			Json::Value input;
			reader.parse(str, input);

			int len = input["requests"].size();

			// 读取场地静态状况
			Json::Value field = input["requests"][(Json::Value::UInt) 0],
				staticField = field["static"], // 墙面和产生器
				contentField = field["content"]; // 豆子和玩家
			height = field["height"].asInt();
			width = field["width"].asInt();
			LARGE_FRUIT_DURATION = field["LARGE_FRUIT_DURATION"].asInt();
			LARGE_FRUIT_ENHANCEMENT = field["LARGE_FRUIT_ENHANCEMENT"].asInt();
			SKILL_COST = field["SKILL_COST"].asInt();
			generatorTurnLeft = GENERATOR_INTERVAL = field["GENERATOR_INTERVAL"].asInt();

			PrepareInitialField(staticField, contentField);

			// 根据历史恢复局面
			for (int i = 1; i < len; i++)
			{
				Json::Value req = input["requests"][i];
				for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
					if (!players[_].dead)
						actions[_] = (Direction)req[playerID2str[_]]["action"].asInt();
				NextTurn();
			}

			obtainedData = input["data"].asString();
			obtainedGlobalData = input["globaldata"].asString();

			return field["id"].asInt();
		}

		// 根据 static 和 content 数组准备场地的初始状况
		void PrepareInitialField(const Json::Value &staticField, const Json::Value &contentField)
		{
			int r, c, gid = 0;
			generatorCount = 0;
			aliveCount = 0;
			smallFruitCount = 0;
			generatorTurnLeft = GENERATOR_INTERVAL;
			for (r = 0; r < height; r++)
				for (c = 0; c < width; c++)
				{
					GridContentType &content = fieldContent[r][c] = (GridContentType)contentField[r][c].asInt();
					GridStaticType &s = fieldStatic[r][c] = (GridStaticType)staticField[r][c].asInt();
					if (s & generator)
					{
						generators[gid].row = r;
						generators[gid++].col = c;
						generatorCount++;
					}
					if (content & smallFruit)
						smallFruitCount++;
					for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
						if (content & playerID2Mask[_])
						{
							Player &p = players[_];
							p.col = c;
							p.row = r;
							p.powerUpLeft = 0;
							p.strength = 1;
							p.dead = false;
							aliveCount++;
						}
				}
		}

		// 完成决策，输出结果。
		// action 表示本回合的移动方向，stay 为不移动，shoot开头的动作表示向指定方向施放技能
		// tauntText 表示想要叫嚣的言语，可以是任意字符串，除了显示在屏幕上不会有任何作用，留空表示不叫嚣
		// data 表示自己想存储供下一回合使用的数据，留空表示删除
		// globalData 表示自己想存储供以后使用的数据（替换），这个数据可以跨对局使用，会一直绑定在这个 Bot 上，留空表示删除
		void WriteOutput(Direction action, string tauntText = "", string data = "", string globalData = "") const
		{
			Json::Value ret;
			ret["response"]["action"] = action;
			ret["response"]["tauntText"] = tauntText;
			ret["data"] = data;
			ret["globaldata"] = globalData;

#ifdef _BOTZONE_ONLINE
			Json::FastWriter writer; // 在线评测的话能用就行……
#else
			Json::StyledWriter writer; // 本地调试这样好看 > <
#endif
			cout << writer.write(ret) << endl;
		}

		// 用于显示当前游戏状态，调试用。
		// 提交到平台后会被优化掉。
		inline void DebugPrint() const
		{
#ifndef _BOTZONE_ONLINE
			printf("回合号【%d】存活人数【%d】| 图例 产生器[G] 有玩家[0/1/2/3] 多个玩家[*] 大豆[o] 小豆[.]\n", turnID, aliveCount);
			for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				const Player &p = players[_];
				printf("[玩家%d(%d, %d)|力量%d|加成剩余回合%d|%s]\n",
					_, p.row, p.col, p.strength, p.powerUpLeft, p.dead ? "死亡" : "存活");
			}
			putchar(' ');
			putchar(' ');
			for (int c = 0; c < width; c++)
				printf("  %d ", c);
			putchar('\n');
			for (int r = 0; r < height; r++)
			{
				putchar(' ');
				putchar(' ');
				for (int c = 0; c < width; c++)
				{
					putchar(' ');
					printf((fieldStatic[r][c] & wallNorth) ? "---" : "   ");
				}
				printf("\n%d ", r);
				for (int c = 0; c < width; c++)
				{
					putchar((fieldStatic[r][c] & wallWest) ? '|' : ' ');
					putchar(' ');
					int hasPlayer = -1;
					for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
						if (fieldContent[r][c] & playerID2Mask[_])
							if (hasPlayer == -1)
								hasPlayer = _;
							else
								hasPlayer = 4;
					if (hasPlayer == 4)
						putchar('*');
					else if (hasPlayer != -1)
						putchar('0' + hasPlayer);
					else if (fieldStatic[r][c] & generator)
						putchar('G');
					else if (fieldContent[r][c] & playerMask)
						putchar('*');
					else if (fieldContent[r][c] & smallFruit)
						putchar('.');
					else if (fieldContent[r][c] & largeFruit)
						putchar('o');
					else
						putchar(' ');
					putchar(' ');
				}
				putchar((fieldStatic[r][width - 1] & wallEast) ? '|' : ' ');
				putchar('\n');
			}
			putchar(' ');
			putchar(' ');
			for (int c = 0; c < width; c++)
			{
				putchar(' ');
				printf((fieldStatic[height - 1][c] & wallSouth) ? "---" : "   ");
			}
			putchar('\n');
#endif
		}

		Json::Value SerializeCurrentTurnChange()
		{
			Json::Value result;
			TurnStateTransfer &bt = backtrack[turnID - 1];
			for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				result["actions"][_] = bt.actions[_];
				result["strengthDelta"][_] = bt.strengthDelta[_];
				result["change"][_] = bt.change[_];
			}
			return result;
		}

		// 初始化游戏管理器
		GameField()
		{
			if (constructed)
				throw runtime_error("请不要再创建 GameField 对象了，整个程序中只应该有一个对象");
			constructed = true;

			turnID = 0;
		}

		//GameField(const GameField &b) : GameField() { }
	};

	bool GameField::constructed = false;
}

// 一些辅助程序
namespace Helpers
{

	inline int RandBetween(int a, int b)
	{
		if (a > b)
			swap(a, b);
		return rand() % (b - a) + a;
	}

	void RandomPlay(Pacman::GameField &gameField)
	{
		std::stack<Pacman::GameField> s;
		Pacman::GameField last;
		while (true)
		{
			for (int i = 0; i < MAX_PLAYER_COUNT; i++)
			{
				if (gameField.players[i].dead)
					continue;
				Pacman::Direction valid[9];
				int vCount = 0;
				for (Pacman::Direction d = Pacman::stay; d < 8; ++d)
					if (gameField.ActionValid(i, d))
						valid[vCount++] = d;
				gameField.actions[i] = valid[RandBetween(0, vCount)];
			}

			bool hasNext = gameField.NextTurn();
			s.push(gameField);

			if (!hasNext)
				break;
		}
		while (!s.empty())
		{
			Pacman::GameField &t = s.top(), &g = gameField;
			if (!(t.aliveCount != g.aliveCount ||
				memcmp(t.fieldContent, g.fieldContent, sizeof(t.fieldContent)) != 0 ||
				memcmp(t.fieldStatic, g.fieldStatic, sizeof(t.fieldStatic)) != 0 ||
				t.generatorTurnLeft != g.generatorTurnLeft ||
				t.turnID != g.turnID ||
				t.smallFruitCount != g.smallFruitCount))
			{
				for (int i = 0; i < 4; i++)
					if (t.players[i].col != g.players[i].col ||
						t.players[i].row != g.players[i].row ||
						t.players[i].dead != g.players[i].dead ||
						t.players[i].powerUpLeft != g.players[i].powerUpLeft ||
						t.players[i].strength != g.players[i].strength)
					{
						t.DebugPrint();
						g.DebugPrint();
						return;
					}
			}
			else
			{
				t.DebugPrint();
				g.DebugPrint();
				return;
			}

			last = gameField;
			s.pop();
			gameField.PopState();
		}
	}

	bool visited[FIELD_MAX_HEIGHT][FIELD_MAX_WIDTH];
	Pacman::Direction dirEnumerateList[][4] = {
		{ Pacman::up, Pacman::right, Pacman::down, Pacman::left },
		{ Pacman::up, Pacman::right, Pacman::left, Pacman::down },
		{ Pacman::up, Pacman::down, Pacman::right, Pacman::left },
		{ Pacman::up, Pacman::down, Pacman::left, Pacman::right },
		{ Pacman::up, Pacman::left, Pacman::right, Pacman::down },
		{ Pacman::up, Pacman::left, Pacman::down, Pacman::right },
		{ Pacman::right, Pacman::up, Pacman::down, Pacman::left },
		{ Pacman::right, Pacman::up, Pacman::left, Pacman::down },
		{ Pacman::right, Pacman::down, Pacman::up, Pacman::left },
		{ Pacman::right, Pacman::down, Pacman::left, Pacman::up },
		{ Pacman::right, Pacman::left, Pacman::up, Pacman::down },
		{ Pacman::right, Pacman::left, Pacman::down, Pacman::up },
		{ Pacman::down, Pacman::up, Pacman::right, Pacman::left },
		{ Pacman::down, Pacman::up, Pacman::left, Pacman::right },
		{ Pacman::down, Pacman::right, Pacman::up, Pacman::left },
		{ Pacman::down, Pacman::right, Pacman::left, Pacman::up },
		{ Pacman::down, Pacman::left, Pacman::up, Pacman::right },
		{ Pacman::down, Pacman::left, Pacman::right, Pacman::up },
		{ Pacman::left, Pacman::up, Pacman::right, Pacman::down },
		{ Pacman::left, Pacman::up, Pacman::down, Pacman::right },
		{ Pacman::left, Pacman::right, Pacman::up, Pacman::down },
		{ Pacman::left, Pacman::right, Pacman::down, Pacman::up },
		{ Pacman::left, Pacman::down, Pacman::up, Pacman::right },
		{ Pacman::left, Pacman::down, Pacman::right, Pacman::up }
	};
	int unvisitedCount;
	bool borderBroken[4];

	bool EnsureConnected(Pacman::GameField &gameField, int r, int c, int maxH, int maxW)
	{
		visited[r][c] = true;
		if (--unvisitedCount == 0)
			return true;
		Pacman::Direction *list = dirEnumerateList[RandBetween(0, 24)];
		for (int i = 0; i < 4; i++)
		{
			int nr = r + Pacman::dy[list[i]], nc = c + Pacman::dx[list[i]];
			if (nr < maxH && nr >= 0 && nc < maxW && nc >= 0)
			{
				if (!visited[nr][nc])
				{
					if (gameField.fieldStatic[nr][nc] & Pacman::generator)
					{
						visited[nr][nc] = true;
						if (--unvisitedCount == 0)
							return true;
						continue;
					}
					// 破！
					gameField.fieldStatic[r][c] &= ~Pacman::direction2OpposingWall[list[i]];
					if (list[i] == Pacman::up)
						gameField.fieldStatic[nr][nc] &= ~Pacman::wallSouth;
					if (list[i] == Pacman::down)
						gameField.fieldStatic[nr][nc] &= ~Pacman::wallNorth;
					if (list[i] == Pacman::left)
						gameField.fieldStatic[nr][nc] &= ~Pacman::wallEast;
					if (list[i] == Pacman::right)
						gameField.fieldStatic[nr][nc] &= ~Pacman::wallWest;
					if (EnsureConnected(gameField, nr, nc, maxH, maxW))
						return true;
				}
			}
			else if (!borderBroken[list[i]]) // 打破一个边界壁障
			{
				borderBroken[list[i]] = true;
				gameField.fieldStatic[r][c] &= ~Pacman::direction2OpposingWall[list[i]];
			}
		}
		return false;
	}

	void InitializeField(Pacman::GameField &gameField)
	{
		int portionH = (gameField.height + 1) / 2,
			portionW = (gameField.width + 1) / 2;

		// 先将所有格子围上
		for (int r = 0; r < portionH; r++)
			for (int c = 0; c < portionW; c++)
				gameField.fieldStatic[r][c] = Pacman::wallNorth | Pacman::wallEast | Pacman::wallSouth | Pacman::wallWest;

		unvisitedCount = portionH * portionW;

		// 创建产生器（因为产生器是障碍物啊）
		{
			int r = RandBetween(0, portionH - 1), c = RandBetween(0, portionW - 1);
			gameField.fieldStatic[r][c] |= Pacman::generator;
			gameField.fieldStatic[r][gameField.width - 1 - c] |= Pacman::generator;
			gameField.fieldStatic[gameField.height - 1 - r][c] |= Pacman::generator;
			gameField.fieldStatic[gameField.height - 1 - r][gameField.width - 1 - c] |= Pacman::generator;
		}

		// 打通壁障
		memset(visited, 0, sizeof(visited));
		memset(borderBroken, 0, sizeof(borderBroken));
		EnsureConnected(gameField, RandBetween(0, portionH), RandBetween(0, portionW), portionH, portionW);

		if (!borderBroken[Pacman::left])
			gameField.fieldStatic[RandBetween(0, portionH)][0] &= ~Pacman::wallWest;
		if (!borderBroken[Pacman::right])
			gameField.fieldStatic[RandBetween(0, portionH)][portionW - 1] &= ~Pacman::wallEast;
		if (!borderBroken[Pacman::up])
			gameField.fieldStatic[0][RandBetween(0, portionW)] &= ~Pacman::wallNorth;
		if (!borderBroken[Pacman::down])
			gameField.fieldStatic[portionH - 1][RandBetween(0, portionW)] &= ~Pacman::wallSouth;

		// 生成对称场地
		for (int r = 0; r < portionH; r++)
			for (int c = 0; c < portionW; c++)
			{
				bool
					n = !!(gameField.fieldStatic[r][c] & Pacman::wallNorth),
					w = !!(gameField.fieldStatic[r][c] & Pacman::wallWest),
					s = !!(gameField.fieldStatic[r][c] & Pacman::wallSouth),
					e = !!(gameField.fieldStatic[r][c] & Pacman::wallEast);
				Pacman::GridStaticType hasGenerator = gameField.fieldStatic[r][c] & Pacman::generator;
				if ((c == 0 || c == portionW - 1) && rand() % 4 == 0)
				{
					if (c == 0)
						w = false;
					else
						e = false;
				}
				if ((r == 0 || r == portionH - 1) && rand() % 4 == 0)
				{
					if (r == 0)
						n = false;
					else
						s = false;
				}
				if (r * 2 + 1 == gameField.height)
					s = n;
				if (c * 2 + 1 == gameField.width)
					e = w;

				gameField.fieldStatic[r][c] =
					(n ? Pacman::wallNorth : Pacman::emptyWall) | hasGenerator |
					(w ? Pacman::wallWest : Pacman::emptyWall) |
					(s ? Pacman::wallSouth : Pacman::emptyWall) |
					(e ? Pacman::wallEast : Pacman::emptyWall);
				gameField.fieldStatic[r][gameField.width - 1 - c] =
					(n ? Pacman::wallNorth : Pacman::emptyWall) | hasGenerator |
					(w ? Pacman::wallEast : Pacman::emptyWall) |
					(s ? Pacman::wallSouth : Pacman::emptyWall) |
					(e ? Pacman::wallWest : Pacman::emptyWall);
				gameField.fieldStatic[gameField.height - 1 - r][c] =
					(n ? Pacman::wallSouth : Pacman::emptyWall) | hasGenerator |
					(w ? Pacman::wallWest : Pacman::emptyWall) |
					(s ? Pacman::wallNorth : Pacman::emptyWall) |
					(e ? Pacman::wallEast : Pacman::emptyWall);
				gameField.fieldStatic[gameField.height - 1 - r][gameField.width - 1 - c] =
					(n ? Pacman::wallSouth : Pacman::emptyWall) | hasGenerator |
					(w ? Pacman::wallEast : Pacman::emptyWall) |
					(s ? Pacman::wallNorth : Pacman::emptyWall) |
					(e ? Pacman::wallWest : Pacman::emptyWall);

				gameField.fieldContent[r][c] =
					gameField.fieldContent[r][gameField.width - 1 - c] =
					gameField.fieldContent[gameField.height - 1 - r][c] =
					gameField.fieldContent[gameField.height - 1 - r][gameField.width - 1 - c] =
					Pacman::empty;
			}

		// 再次围上所有的产生器
		for (int r = 0; r < gameField.height; r++)
			for (int c = 0; c < gameField.width; c++)
				if (gameField.fieldStatic[r][c] & Pacman::generator)
				{
					gameField.fieldStatic[r][c] |= Pacman::wallNorth | Pacman::wallEast | Pacman::wallSouth | Pacman::wallWest;
					for (Pacman::Direction dir = Pacman::up; dir < 4; ++dir)
					{
						Pacman::GridStaticType &s = gameField.fieldStatic
							[(r + Pacman::dy[dir] + gameField.height) % gameField.height]
							[(c + Pacman::dx[dir] + gameField.width) % gameField.width];
						if (dir == Pacman::up)
							s |= Pacman::wallSouth;
						if (dir == Pacman::down)
							s |= Pacman::wallNorth;
						if (dir == Pacman::left)
							s |= Pacman::wallEast;
						if (dir == Pacman::right)
							s |= Pacman::wallWest;
					}
				}

		// 创建玩家
		int triedCount = 0;
		while (true)
		{
			int r = RandBetween(0, portionH - 1), c = RandBetween(0, portionW - 1); // 保持安全距离
			if (++triedCount > 1000)
				return InitializeField(gameField);
			if (gameField.fieldStatic[r][c] & Pacman::generator)
				continue;

			// 防止出生照面
			int x, y;
			for (y = 0; y < r; y++)
				if (gameField.fieldStatic[y][c] & (Pacman::wallNorth | Pacman::wallSouth))
					break;
			if (y == r && !(gameField.fieldStatic[r][c] & Pacman::wallNorth))
				continue;
			for (y = r + 1; y < portionH; y++)
				if (gameField.fieldStatic[y][c] & (Pacman::wallNorth | Pacman::wallSouth))
					break;
			if (y == portionH && !(gameField.fieldStatic[r][c] & Pacman::wallSouth))
				continue;
			for (x = 0; x < c; x++)
				if (gameField.fieldStatic[r][x] & (Pacman::wallEast | Pacman::wallWest))
					break;
			if (x == c && !(gameField.fieldStatic[r][c] & Pacman::wallWest))
				continue;
			for (x = c + 1; x < portionW; x++)
				if (gameField.fieldStatic[r][x] & (Pacman::wallEast | Pacman::wallWest))
					break;
			if (x == portionW && !(gameField.fieldStatic[r][c] & Pacman::wallEast))
				continue;

			gameField.fieldContent[r][c] |= Pacman::player1;
			gameField.fieldContent[r][gameField.width - 1 - c] |= Pacman::player2;
			gameField.fieldContent[gameField.height - 1 - r][c] |= Pacman::player3;
			gameField.fieldContent[gameField.height - 1 - r][gameField.width - 1 - c] |= Pacman::player4;
			break;
		}

		triedCount = 0;
		// 创建大豆
		while (true)
		{
			int r = RandBetween(0, portionH - 1), c = RandBetween(0, portionW - 1);

			if (++triedCount > 1000)
				return InitializeField(gameField);
			if (gameField.fieldStatic[r][c] & Pacman::generator || gameField.fieldContent[r][c] & Pacman::player1)
				continue;

			// 防止出生照面
			int x, y;
			for (y = 0; y < r; y++)
				if (gameField.fieldStatic[y][c] & (Pacman::wallNorth | Pacman::wallSouth))
					break;
			if (y == r && !(gameField.fieldStatic[r][c] & Pacman::wallNorth))
				continue;
			for (y = r + 1; y < portionH; y++)
				if (gameField.fieldStatic[y][c] & (Pacman::wallNorth | Pacman::wallSouth))
					break;
			if (y == portionH && !(gameField.fieldStatic[r][c] & Pacman::wallSouth))
				continue;
			for (x = 0; x < c; x++)
				if (gameField.fieldStatic[r][x] & (Pacman::wallEast | Pacman::wallWest))
					break;
			if (x == c && !(gameField.fieldStatic[r][c] & Pacman::wallWest))
				continue;
			for (x = c + 1; x < portionW; x++)
				if (gameField.fieldStatic[r][x] & (Pacman::wallEast | Pacman::wallWest))
					break;
			if (x == portionW && !(gameField.fieldStatic[r][c] & Pacman::wallEast))
				continue;

			gameField.fieldContent[r][c] |= Pacman::largeFruit;
			gameField.fieldContent[r][gameField.width - 1 - c] |= Pacman::largeFruit;
			gameField.fieldContent[gameField.height - 1 - r][c] |= Pacman::largeFruit;
			gameField.fieldContent[gameField.height - 1 - r][gameField.width - 1 - c] |= Pacman::largeFruit;
			break;
		}

		// 撒豆子
		gameField.smallFruitCount = 0;
		for (int r = 0; r < portionH - 1; r++)
			for (int c = 0; c < portionW - 1; c++)
			{
				if (gameField.fieldStatic[r][c] & Pacman::generator ||
					gameField.fieldContent[r][c] & (Pacman::player1 | Pacman::largeFruit) ||
					rand() % 7 > 2)
					continue;
				gameField.fieldContent[r][c] =
					gameField.fieldContent[r][gameField.width - 1 - c] =
					gameField.fieldContent[gameField.height - 1 - r][c] =
					gameField.fieldContent[gameField.height - 1 - r][gameField.width - 1 - c] =
					Pacman::smallFruit;
				gameField.smallFruitCount++;
			}

		// 暴力获取状态（怕麻烦而已……）
		int gid = 0;
		gameField.generatorCount = 0;
		gameField.aliveCount = 0;
		gameField.generatorTurnLeft = gameField.GENERATOR_INTERVAL;
		for (int r = 0; r < gameField.height; r++)
			for (int c = 0; c < gameField.width; c++)
			{
				Pacman::GridContentType &content = gameField.fieldContent[r][c];
				Pacman::GridStaticType &s = gameField.fieldStatic[r][c];
				if (s & Pacman::generator)
				{
					gameField.generators[gid].row = r;
					gameField.generators[gid++].col = c;
					gameField.generatorCount++;
				}
				for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
					if (content & Pacman::playerID2Mask[_])
					{
						Pacman::Player &p = gameField.players[_];
						p.col = c;
						p.row = r;
						p.powerUpLeft = 0;
						p.strength = 1;
						p.dead = false;
						gameField.aliveCount++;
					}
			}
	}
}

int main()
{
	Pacman::GameField gameField;
	string str, chunk;
	while (getline(cin, chunk) && chunk != "")
		str += chunk;

	Json::Reader reader;
	Json::Value input, output, initdata, temp, fieldStatic, fieldContent;
	unsigned int seed;
	reader.parse(str, input);

	initdata = input["initdata"];

	if (initdata.isString())
		reader.parse(initdata.asString(), initdata);
	if (initdata.isString())
		reader.parse("{}", initdata);

	temp = initdata["seed"];
	if (temp.isInt())
		srand(seed = temp.asUInt());
	else
		srand(seed = time(0));
	output["initdata"]["seed"] = seed;

	temp = initdata["width"];
	if (rand() % 3 == 0)
		gameField.width = Helpers::RandBetween(6, 12);
	else
		gameField.width = Helpers::RandBetween(9, 12);
	if (temp.isInt())
	{
		int t = temp.asInt();
		if (t >= 6 && t < 12)
			gameField.width = t;
	}
	output["initdata"]["width"] = gameField.width;

	temp = initdata["height"];
	if (rand() % 3 == 0)
		gameField.height = Helpers::RandBetween(6, 12);
	else
		gameField.height = Helpers::RandBetween(9, 12);
	if (temp.isInt())
	{
		int t = temp.asInt();
		if (t >= 6 && t < 12)
			gameField.height = t;
	}
	output["initdata"]["height"] = gameField.height;

	temp = initdata["GENERATOR_INTERVAL"];
	gameField.GENERATOR_INTERVAL = 20;
	if (temp.isInt())
		gameField.GENERATOR_INTERVAL = temp.asInt();
	output["initdata"]["GENERATOR_INTERVAL"] = gameField.GENERATOR_INTERVAL;

	temp = initdata["SKILL_COST"];
	gameField.SKILL_COST = 4;
	if (temp.isInt())
		gameField.SKILL_COST = temp.asInt();
	output["initdata"]["SKILL_COST"] = gameField.SKILL_COST;

	temp = initdata["LARGE_FRUIT_DURATION"];
	gameField.LARGE_FRUIT_DURATION = 10;
	if (temp.isInt())
		gameField.LARGE_FRUIT_DURATION = temp.asInt();
	output["initdata"]["LARGE_FRUIT_DURATION"] = gameField.LARGE_FRUIT_DURATION;

	temp = initdata["LARGE_FRUIT_ENHANCEMENT"];
	gameField.LARGE_FRUIT_ENHANCEMENT = 10;
	if (temp.isInt())
		gameField.LARGE_FRUIT_ENHANCEMENT = temp.asInt();
	output["initdata"]["LARGE_FRUIT_ENHANCEMENT"] = gameField.LARGE_FRUIT_ENHANCEMENT;

	fieldStatic = initdata["static"];
	fieldContent = initdata["content"];
	if (fieldStatic.isArray() && !fieldStatic.isNull() && fieldContent.isArray() && !fieldContent.isNull())
		gameField.PrepareInitialField(fieldStatic, fieldContent);
	else
	{
		fieldStatic = Json::Value(Json::arrayValue);
		fieldContent = Json::Value(Json::arrayValue);
		Helpers::InitializeField(gameField);
		for (int r = 0; r < gameField.height; r++)
			for (int c = 0; c < gameField.width; c++)
			{
				fieldStatic[r][c] = gameField.fieldStatic[r][c];
				fieldContent[r][c] = gameField.fieldContent[r][c];
			}
	}
	output["initdata"]["static"] = fieldStatic;
	output["initdata"]["content"] = fieldContent;

	//int count = 0;
	//while (true)
	//{
	//	Helpers::RandomPlay(gameField);
	//	cout << "Play" << count++ << " Finished" << endl;
	//}

	input = input["log"];

	int size = input.size();
	if (size == 0)
	{
		for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
		{
			output["content"][Pacman::playerID2str[_]] = output["initdata"];
			output["content"][Pacman::playerID2str[_]]["id"] = _;
		}
		output["command"] = "request";
		output["display"] = output["initdata"];
	}
	else
	{
		output.removeMember("initdata");
		bool humanTolerated[MAX_PLAYER_COUNT] = { false, false, false, false };
		Json::Value request;
		for (int i = 1; i < size; i += 2)
		{
			bool isLast = size - 1 == i;
			Json::Value response = input[i];
			for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				if (!gameField.players[_].dead)
				{
					Json::Value content,
						raw = response[Pacman::playerID2str[_]],
						answer = raw["response"].isNull() ?
							raw["content"] : raw["response"];
					if (((answer.isString() &&
						reader.parse(answer.asString(), content)) ||
						(answer.isObject() &&
							(content = answer, true))) &&
						content["action"].isInt()) // 保证输入格式正确
					{
						if (isLast)
						{
							request[Pacman::playerID2str[_]]["action"] = gameField.actions[_] = (Pacman::Direction)content["action"].asInt();
							Json::Value taunt = content["tauntText"];
							if (taunt.isString())
								request[Pacman::playerID2str[_]]["tauntText"] = taunt.asString().substr(0, 40);
						}
						else
							gameField.actions[_] = (Pacman::Direction)content["action"].asInt();
					}
					else if (raw["error"].isString() && raw["error"].asString() == "Timeout" && !humanTolerated[_]) // 人类玩家超时的宽容措施
					{
						humanTolerated[_] = true;
						if (isLast)
							request[Pacman::playerID2str[_]]["action"] = gameField.actions[_] = Pacman::stay;
						else
							gameField.actions[_] = Pacman::stay;
					}
					else
					{
						if (isLast)
						{
							request[Pacman::playerID2str[_]]["action"] = gameField.actions[_] = (Pacman::Direction) - 10;
							request[Pacman::playerID2str[_]]["reason"] = "INVALID_INPUT_VERDICT_" + raw["verdict"].asString();
						}
						else
							gameField.actions[_] = (Pacman::Direction) - 10;
					}
				}
			}
			if (!gameField.NextTurn())
			{
				output["command"] = "finish";
				int rank[] = { 0, 0, 0, 0 };
				int rank2player[] = { 0, 1, 2, 3 };
				for (int j = 0; j < MAX_PLAYER_COUNT; j++)
					for (int k = 0; k < MAX_PLAYER_COUNT - j - 1; k++)
						if (gameField.players[rank2player[k]].strength > gameField.players[rank2player[k + 1]].strength)
							swap(rank2player[k], rank2player[k + 1]);

				int scorebase = 1;
				rank[rank2player[0]] = 1;
				for (int j = 1; j < MAX_PLAYER_COUNT; j++)
				{
					if (gameField.players[rank2player[j - 1]].strength < gameField.players[rank2player[j]].strength)
						scorebase = j + 1;
					rank[rank2player[j]] = scorebase;
				}

				int total = 0;
				for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
					total += gameField.players[_].strength;

				if (total == 0)
					total = 1;

				for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
					output["content"][Pacman::playerID2str[_]] = (rank[_] * 1000 + 10000 * gameField.players[_].strength / total) / 100.0;

				output["display"] = request;
				output["display"]["result"] = output["content"];
				output["display"]["trace"] = gameField.SerializeCurrentTurnChange();
			}
			else if (isLast)
			{
				output["command"] = "request";
				output["display"] = request;
				for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
					request[Pacman::playerID2str[_]].removeMember("tauntText");

				for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
					if (!gameField.players[_].dead)
						output["content"][Pacman::playerID2str[_]] = request;

				output["display"]["trace"] = gameField.SerializeCurrentTurnChange();
			}
		}
	}

#ifdef _BOTZONE_ONLINE
	Json::FastWriter writer;
#else
	Json::StyledWriter writer;
#endif

	cout << writer.write(output) << endl;
	return 0;
}
