/*
 * cPacman2Judge
 * ���ߣ�hy
 * ʱ�䣺2016/3/22 15:32:51
 * �����£�2016/10/11 13:21
 * ��������2�����Ӽ���
 * �������ݣ�������ҵ�һ�γ�ʱ������������ȷ�жϲ�������������ϵ����飨���ҽ�������Χ��������
 *
 * ������������
 *  r/R/y/Y��Row���У�������
 *  c/C/x/X��Column���У�������
 *  ������±궼��[y][x]��[r][c]��˳��
 *  ��ұ��0123
 *
 * ������ϵ��
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
 * ����ʾ�������ʹ��
 * #ifndef _BOTZONE_ONLINE
 * ������Ԥ����ָ����������������ͱ�������
 *
 * ����ʾ��һ����ı��༭������֧�ֽ�������۵�����
 * ���������Դ�����̫���߳������Կ��ǽ�����namespace�۵�
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
#define MAX_GENERATOR_COUNT 4 // ÿ������1
#define MAX_PLAYER_COUNT 4
#define MAX_TURN 100

// ��Ҳ����ѡ�� using namespace std; ���ǻ���Ⱦ�����ռ�
using std::string;
using std::swap;
using std::cin;
using std::cout;
using std::endl;
using std::getline;
using std::runtime_error;

// ƽ̨�ṩ�ĳԶ�������߼��������
namespace Pacman
{

	const int dx[] = { 0, 1, 0, -1, 1, 1, -1, -1 }, dy[] = { -1, 0, 1, 0, -1, 1, 1, -1 };

	// ö�ٶ��壻ʹ��ö����Ȼ���˷ѿռ䣨sizeof(GridContentType) == 4�������Ǽ��������32λ������Ч�ʸ���

	// ÿ�����ӿ��ܱ仯�����ݣ�����á����߼��������
	enum GridContentType
	{
		empty = 0, // ��ʵ�����õ�
		player1 = 1, // 1�����
		player2 = 2, // 2�����
		player3 = 4, // 3�����
		player4 = 8, // 4�����
		playerMask = 1 | 2 | 4 | 8, // ���ڼ����û����ҵ�
		smallFruit = 16, // С����
		largeFruit = 32 // ����
	};

	// �����ID��ȡ��������ҵĶ�����λ
	GridContentType playerID2Mask[] = { player1, player2, player3, player4 };
	string playerID2str[] = { "0", "1", "2", "3" };

	// ��ö��Ҳ��������Щ�����ˣ����ӻ�������
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

	// ÿ�����ӹ̶��Ķ���������á����߼��������
	enum GridStaticType
	{
		emptyWall = 0, // ��ʵ�����õ�
		wallNorth = 1, // ��ǽ����������ٵķ���
		wallEast = 2, // ��ǽ�����������ӵķ���
		wallSouth = 4, // ��ǽ�����������ӵķ���
		wallWest = 8, // ��ǽ����������ٵķ���
		generator = 16 // ���Ӳ�����
	};

	// ���ƶ�����ȡ����������赲�ŵ�ǽ�Ķ�����λ
	GridStaticType direction2OpposingWall[] = { wallNorth, wallEast, wallSouth, wallWest };

	// ���򣬿��Դ���dx��dy���飬ͬʱҲ������Ϊ��ҵĶ���
	enum Direction
	{
		stay = -1,
		up = 0,
		right = 1,
		down = 2,
		left = 3,
		shootUp = 4, // ���Ϸ�����
		shootRight = 5, // ���ҷ�����
		shootDown = 6, // ���·�����
		shootLeft = 7 // ��������
	};

	// �����ϴ�����������
	struct FieldProp
	{
		int row, col;
	};

	// �����ϵ����
	struct Player : FieldProp
	{
		int strength;
		int powerUpLeft;
		bool dead;
	};

	// �غ��²����Ķ��ӵ�����
	struct NewFruits
	{
		FieldProp newFruits[MAX_GENERATOR_COUNT * 8];
		int newFruitCount;
	} newFruits[MAX_TURN];
	int newFruitsCount = 0;

	// ״̬ת�Ƽ�¼�ṹ
	struct TurnStateTransfer
	{
		enum StatusChange // �����
		{
			none = 0,
			ateSmall = 1,
			ateLarge = 2,
			powerUpDrop = 4,
			die = 8,
			error = 16
		};

		// ���ѡ���Ķ���
		Direction actions[MAX_PLAYER_COUNT];

		// �˻غϸ���ҵ�״̬�仯
		StatusChange change[MAX_PLAYER_COUNT];

		// �˻غϸ���ҵ������仯
		int strengthDelta[MAX_PLAYER_COUNT];
	};

	// ��Ϸ��Ҫ�߼������࣬��������������غ����㡢״̬ת�ƣ�ȫ��Ψһ
	class GameField
	{
	private:
		// �Ҳ���Ϊ���������������Զ��ŵ�private��

		// ��¼ÿ�غϵı仯��ջ��
		TurnStateTransfer backtrack[MAX_TURN];

		// ��������Ƿ��Ѿ�����
		static bool constructed;

	public:
		// ���صĳ��Ϳ�
		int height, width;
		int generatorCount;
		int GENERATOR_INTERVAL, LARGE_FRUIT_DURATION, LARGE_FRUIT_ENHANCEMENT, SKILL_COST;

		// ���ظ��ӹ̶�������
		GridStaticType fieldStatic[FIELD_MAX_HEIGHT][FIELD_MAX_WIDTH];

		// ���ظ��ӻ�仯������
		GridContentType fieldContent[FIELD_MAX_HEIGHT][FIELD_MAX_WIDTH];
		int generatorTurnLeft; // ���ٻغϺ��������
		int aliveCount; // �ж�����Ҵ��
		int smallFruitCount;
		int turnID;
		FieldProp generators[MAX_GENERATOR_COUNT]; // ����Щ���Ӳ�����
		Player players[MAX_PLAYER_COUNT]; // ����Щ���

		// ���ѡ���Ķ���
		Direction actions[MAX_PLAYER_COUNT];

		// �ָ����ϴγ���״̬������һ·�ָ����ʼ��
		// �ָ�ʧ�ܣ�û��״̬�ɻָ�������false
		bool PopState()
		{
			if (turnID <= 0)
				return false;

			const TurnStateTransfer &bt = backtrack[--turnID];
			int i, _;

			// �������ָ�״̬

			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				GridContentType &content = fieldContent[_p.row][_p.col];
				TurnStateTransfer::StatusChange change = bt.change[_];

				// 5. �󶹻غϻָ�
				if (change & TurnStateTransfer::powerUpDrop)
					_p.powerUpLeft++;

				// 4. �³�����
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

				// 2. �������
				if (change & TurnStateTransfer::die)
				{
					_p.dead = false;
					aliveCount++;
					content |= playerID2Mask[_];
				}

				// 1. ���λ�Ӱ
				if (!_p.dead && bt.actions[_] != stay && bt.actions[_] < shootUp)
				{
					fieldContent[_p.row][_p.col] &= ~playerID2Mask[_];
					_p.row = (_p.row - dy[bt.actions[_]] + height) % height;
					_p.col = (_p.col - dx[bt.actions[_]] + width) % width;
					fieldContent[_p.row][_p.col] |= playerID2Mask[_];
				}

				// 0. ���겻�Ϸ������
				if (change & TurnStateTransfer::error)
				{
					_p.dead = false;
					aliveCount++;
					content |= playerID2Mask[_];
				}

				// *. �ָ�����
				_p.strength -= bt.strengthDelta[_];
			}

			// 3. �ջض���
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

		// �ж�ָ�������ָ�������ƶ�/ʩ�ż����ǲ��ǺϷ��ģ�û��ײǽ��û�вȵ����Ӳ������������㹻��
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

		// ����actionsд����Ҷ�����������һ�غϾ��棬����¼֮ǰ���еĳ���״̬���ɹ��պ�ָ���
		// ���վֵĻ��ͷ���false
		bool NextTurn()
		{
			int _, i, j;

			TurnStateTransfer &bt = backtrack[turnID];
			memset(&bt, 0, sizeof(bt));

			// 0. ɱ�����Ϸ�����
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
						// �������Լ�ǿ��׳������ǲ���ǰ����
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

			// 1. λ�ñ仯
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];

				bt.actions[_] = actions[_];

				if (_p.dead || actions[_] == stay || actions[_] >= shootUp)
					continue;

				// �ƶ�
				fieldContent[_p.row][_p.col] &= ~playerID2Mask[_];
				_p.row = (_p.row + dy[actions[_]] + height) % height;
				_p.col = (_p.col + dx[actions[_]] + width) % width;
				fieldContent[_p.row][_p.col] |= playerID2Mask[_];
			}

			// 2. ��һ�Ź
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				if (_p.dead)
					continue;

				// �ж��Ƿ��������һ��
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

					// ��Щ��ҽ��ᱻɱ��
					int lootedStrength = 0;
					for (i = begin; i < containedCount; i++)
					{
						int id = containedPlayers[i];
						Player &p = players[id];

						// �Ӹ���������
						fieldContent[p.row][p.col] &= ~playerID2Mask[id];
						p.dead = true;
						int drop = p.strength / 2;
						bt.strengthDelta[id] += -drop;
						bt.change[id] |= TurnStateTransfer::die;
						lootedStrength += drop;
						p.strength -= drop;
						aliveCount--;
					}

					// ������������
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

			// 2.5 ��ⷨ��
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				if (_p.dead || actions[_] < shootUp)
					continue;

				_p.strength -= SKILL_COST;
				bt.strengthDelta[_] -= SKILL_COST;

				int r = _p.row, c = _p.col, player;
				Direction dir = actions[_] - shootUp;

				// ��ָ���������⣨ɨ�����ֱ��������
				while (!(fieldStatic[r][c] & direction2OpposingWall[dir]))
				{
					r = (r + dy[dir] + height) % height;
					c = (c + dx[dir] + width) % width;

					// ���ת��һȦ��������
					if (r == _p.row && c == _p.col)
						break;

					if (fieldContent[r][c] & playerMask)
						for (player = 0; player < MAX_PLAYER_COUNT; player++)
						{
							Player &p = players[player];

							// ���غ���ɱ��Ҳ���ܵ�����
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

			// *. ���һ�������������
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				if (_p.dead || _p.strength > 0)
					continue;

				// �Ӹ���������
				fieldContent[_p.row][_p.col] &= ~playerID2Mask[_];
				_p.dead = true;

				// ʹ��������Ϊ0
				bt.strengthDelta[_] += -_p.strength;
				bt.change[_] |= TurnStateTransfer::die;
				_p.strength = 0;
				aliveCount--;
			}


			// 3. ��������
			if (--generatorTurnLeft == 0)
			{
				generatorTurnLeft = GENERATOR_INTERVAL;
				NewFruits &fruits = newFruits[newFruitsCount++];
				fruits.newFruitCount = 0;
				for (i = 0; i < generatorCount; i++)
					for (Direction d = up; d < 8; ++d)
					{
						// ȡ�࣬�������ر߽�
						int r = (generators[i].row + dy[d] + height) % height, c = (generators[i].col + dx[d] + width) % width;
						if (fieldStatic[r][c] & generator || fieldContent[r][c] & (smallFruit | largeFruit))
							continue;
						fieldContent[r][c] |= smallFruit;
						fruits.newFruits[fruits.newFruitCount].row = r;
						fruits.newFruits[fruits.newFruitCount++].col = c;
						smallFruitCount++;
					}
			}

			// 4. �Ե�����
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				if (_p.dead)
					continue;

				GridContentType &content = fieldContent[_p.row][_p.col];

				// ֻ���ڸ�����ֻ���Լ���ʱ����ܳԵ�����
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

			// 5. �󶹻غϼ���
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

			// *. ���һ�������������
			for (_ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				Player &_p = players[_];
				if (_p.dead || _p.strength > 0)
					continue;

				// �Ӹ���������
				fieldContent[_p.row][_p.col] &= ~playerID2Mask[_];
				_p.dead = true;

				// ʹ��������Ϊ0
				bt.strengthDelta[_] += -_p.strength;
				bt.change[_] |= TurnStateTransfer::die;
				_p.strength = 0;
				aliveCount--;
			}

			++turnID;

			// �Ƿ�ֻʣһ�ˣ�
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

			// �Ƿ�غϳ��ޣ�
			if (turnID >= 100)
				return false;

			return true;
		}

		// ��ȡ�������������룬���ص��Ի��ύƽ̨ʹ�ö����ԡ�
		// ����ڱ��ص��ԣ�����������Ŷ�ȡ������ָ�����ļ���Ϊ�����ļ���ʧ�ܺ���ѡ��ȴ��û�ֱ�����롣
		// ���ص���ʱ���Խ��ܶ����Ա������Windows�¿����� Ctrl-Z ��һ��������+�س�����ʾ���������������������ֻ����ܵ��м��ɡ�
		// localFileName ����ΪNULL
		// obtainedData ������Լ��ϻغϴ洢�����غ�ʹ�õ�����
		// obtainedGlobalData ������Լ��� Bot ����ǰ�洢������
		// ����ֵ���Լ��� playerID
		int ReadInput(const char *localFileName, string &obtainedData, string &obtainedGlobalData)
		{
			string str, chunk;
#ifdef _BOTZONE_ONLINE
			std::ios::sync_with_stdio(false); //��\\)
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

			// ��ȡ���ؾ�̬״��
			Json::Value field = input["requests"][(Json::Value::UInt) 0],
				staticField = field["static"], // ǽ��Ͳ�����
				contentField = field["content"]; // ���Ӻ����
			height = field["height"].asInt();
			width = field["width"].asInt();
			LARGE_FRUIT_DURATION = field["LARGE_FRUIT_DURATION"].asInt();
			LARGE_FRUIT_ENHANCEMENT = field["LARGE_FRUIT_ENHANCEMENT"].asInt();
			SKILL_COST = field["SKILL_COST"].asInt();
			generatorTurnLeft = GENERATOR_INTERVAL = field["GENERATOR_INTERVAL"].asInt();

			PrepareInitialField(staticField, contentField);

			// ������ʷ�ָ�����
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

		// ���� static �� content ����׼�����صĳ�ʼ״��
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

		// ��ɾ��ߣ���������
		// action ��ʾ���غϵ��ƶ�����stay Ϊ���ƶ���shoot��ͷ�Ķ�����ʾ��ָ������ʩ�ż���
		// tauntText ��ʾ��Ҫ��������������������ַ�����������ʾ����Ļ�ϲ������κ����ã����ձ�ʾ������
		// data ��ʾ�Լ���洢����һ�غ�ʹ�õ����ݣ����ձ�ʾɾ��
		// globalData ��ʾ�Լ���洢���Ժ�ʹ�õ����ݣ��滻����������ݿ��Կ�Ծ�ʹ�ã���һֱ������� Bot �ϣ����ձ�ʾɾ��
		void WriteOutput(Direction action, string tauntText = "", string data = "", string globalData = "") const
		{
			Json::Value ret;
			ret["response"]["action"] = action;
			ret["response"]["tauntText"] = tauntText;
			ret["data"] = data;
			ret["globaldata"] = globalData;

#ifdef _BOTZONE_ONLINE
			Json::FastWriter writer; // ��������Ļ����þ��С���
#else
			Json::StyledWriter writer; // ���ص��������ÿ� > <
#endif
			cout << writer.write(ret) << endl;
		}

		// ������ʾ��ǰ��Ϸ״̬�������á�
		// �ύ��ƽ̨��ᱻ�Ż�����
		inline void DebugPrint() const
		{
#ifndef _BOTZONE_ONLINE
			printf("�غϺš�%d�����������%d��| ͼ�� ������[G] �����[0/1/2/3] ������[*] ��[o] С��[.]\n", turnID, aliveCount);
			for (int _ = 0; _ < MAX_PLAYER_COUNT; _++)
			{
				const Player &p = players[_];
				printf("[���%d(%d, %d)|����%d|�ӳ�ʣ��غ�%d|%s]\n",
					_, p.row, p.col, p.strength, p.powerUpLeft, p.dead ? "����" : "���");
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

		// ��ʼ����Ϸ������
		GameField()
		{
			if (constructed)
				throw runtime_error("�벻Ҫ�ٴ��� GameField �����ˣ�����������ֻӦ����һ������");
			constructed = true;

			turnID = 0;
		}

		//GameField(const GameField &b) : GameField() { }
	};

	bool GameField::constructed = false;
}

// һЩ��������
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
					// �ƣ�
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
			else if (!borderBroken[list[i]]) // ����һ���߽����
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

		// �Ƚ����и���Χ��
		for (int r = 0; r < portionH; r++)
			for (int c = 0; c < portionW; c++)
				gameField.fieldStatic[r][c] = Pacman::wallNorth | Pacman::wallEast | Pacman::wallSouth | Pacman::wallWest;

		unvisitedCount = portionH * portionW;

		// ��������������Ϊ���������ϰ��ﰡ��
		{
			int r = RandBetween(0, portionH - 1), c = RandBetween(0, portionW - 1);
			gameField.fieldStatic[r][c] |= Pacman::generator;
			gameField.fieldStatic[r][gameField.width - 1 - c] |= Pacman::generator;
			gameField.fieldStatic[gameField.height - 1 - r][c] |= Pacman::generator;
			gameField.fieldStatic[gameField.height - 1 - r][gameField.width - 1 - c] |= Pacman::generator;
		}

		// ��ͨ����
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

		// ���ɶԳƳ���
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

		// �ٴ�Χ�����еĲ�����
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

		// �������
		int triedCount = 0;
		while (true)
		{
			int r = RandBetween(0, portionH - 1), c = RandBetween(0, portionW - 1); // ���ְ�ȫ����
			if (++triedCount > 1000)
				return InitializeField(gameField);
			if (gameField.fieldStatic[r][c] & Pacman::generator)
				continue;

			// ��ֹ��������
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
		// ������
		while (true)
		{
			int r = RandBetween(0, portionH - 1), c = RandBetween(0, portionW - 1);

			if (++triedCount > 1000)
				return InitializeField(gameField);
			if (gameField.fieldStatic[r][c] & Pacman::generator || gameField.fieldContent[r][c] & Pacman::player1)
				continue;

			// ��ֹ��������
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

		// ������
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

		// ������ȡ״̬�����鷳���ѡ�����
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
						content["action"].isInt()) // ��֤�����ʽ��ȷ
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
					else if (raw["error"].isString() && raw["error"].asString() == "Timeout" && !humanTolerated[_]) // ������ҳ�ʱ�Ŀ��ݴ�ʩ
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
