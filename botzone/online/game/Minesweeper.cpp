#include <iostream>
#include <sstream>
#include <string>
#include <ctime>
#include <cstdlib>
#include "jsoncpp/json.h"

#define MAX_WIDTH 80
#define MAX_HEIGHT 40

using namespace std;
int fieldHeight, fieldWidth, mineCount, seed, unrevealedCount, nonActiveMineCount;
int mineField[MAX_HEIGHT][MAX_WIDTH];
// 0-8：数字
// 9：雷
bool revealed[MAX_HEIGHT][MAX_WIDTH];

// 输出用
int changedCount = 0;
bool isLast = false;
Json::Value currChangedPoses;

void InitializeField()
{
	for (int currMine = 0; currMine < mineCount;)
	{
		int row = rand() % fieldHeight, col = rand() % fieldWidth;
		if (mineField[row][col] != 9)
		{
			mineField[row][col] = 9;
			currMine++;
		}
	}

	for (int row = 0; row < fieldHeight; row++)
	for (int col = 0; col < fieldWidth; col++)
	if (mineField[row][col] != 9)
	{
		int surroundingMineCount = 0;
		for (int dr = -1; dr < 2; dr++)
		for (int dc = -1; dc < 2; dc++)
		if (row + dr >= 0 && row + dr < fieldHeight && col + dc >= 0 && col + dc < fieldWidth &&
			(dr != dc || dr != 0) && mineField[row + dr][col + dc] == 9)
			surroundingMineCount++;
		mineField[row][col] = surroundingMineCount;
	}
}

void ReadSavedField(string field)
{
	for (int i = 0; i < field.size(); i++)
	{
		mineField[i / fieldWidth][i % fieldWidth] = field[i] - '0';
	}
}

Json::Value DisplayField()
{
	return currChangedPoses;
}

string SaveField()
{
	char result[MAX_HEIGHT * MAX_WIDTH + 1];
	for (int row = 0; row < fieldHeight; row++)
	for (int col = 0; col < fieldWidth; col++)
		result[row * fieldWidth + col] = mineField[row][col] + '0';
	result[fieldHeight * fieldWidth] = 0;
	return result;
}

bool ProcClick(int row, int col)
{
	if (isLast && !revealed[row][col])
	{
		currChangedPoses[changedCount]["val"] = mineField[row][col];
		currChangedPoses[changedCount]["row"] = row;
		currChangedPoses[changedCount++]["col"] = col;
	}
	revealed[row][col] = true;
	unrevealedCount--;
	if (mineField[row][col] == 9)
		return false;
	if (mineField[row][col] == 0)
	{
		for (int dr = -1; dr < 2; dr++)
		for (int dc = -1; dc < 2; dc++)
		if (row + dr >= 0 && row + dr < fieldHeight && col + dc >= 0 && col + dc < fieldWidth &&
			(dr != dc || dr != 0) && !revealed[row + dr][col + dc])
			ProcClick(row + dr, col + dc);
	}
	return true;
}

int main()
{
	string str;
	getline(cin, str);
	Json::Reader reader;
	Json::Value input, output, temp, initdata;
	reader.parse(str, input);

	initdata = input["initdata"];
	if (initdata.isString())
		reader.parse(initdata.asString(), initdata);
	if (initdata.isString())
		reader.parse("{}", initdata);

	// 按照初始化参数进行初始化
	temp = initdata["width"];
	if (temp.isInt())
	{
		fieldWidth = temp.asInt();
		if (fieldWidth <= 10 || fieldWidth > 100)
			fieldWidth = 40;
	}
	else
		fieldWidth = 30;

	output["initdata"]["width"] = fieldWidth;

	temp = initdata["height"];
	if (temp.isInt())
	{
		fieldHeight = temp.asInt();
		if (fieldHeight <= 10 || fieldHeight > 60)
			fieldHeight = 20;
	}
	else
		fieldHeight = 20;

	output["initdata"]["height"] = fieldHeight;

	unrevealedCount = fieldHeight * fieldWidth;

	temp = initdata["minecount"];
	if (temp.isInt())
	{
		nonActiveMineCount = mineCount = temp.asInt();
		if (mineCount <= 10 || mineCount > 100)
			mineCount = 40;
	}
	else
		nonActiveMineCount = mineCount = 80;

	output["initdata"]["minecount"] = mineCount;

	temp = initdata["seed"];
	if (temp.isInt())
	{
		int seed = temp.asInt();
		srand(seed);
		output["initdata"]["seed"] = seed;
	}
	else
	{
		int seed = time(0);
		srand(seed);
		output["initdata"]["seed"] = seed;
	}

	temp = initdata["field"];
	if (temp.isString())
	{
		string field = temp.asString();
		output["initdata"]["field"] = field;
		ReadSavedField(field);
	}
	else
	{
		InitializeField();
		output["initdata"]["field"] = SaveField();
	}

	temp = initdata["firstclick"];
	if (!temp.isNull())
	{
		ProcClick(temp["row"].asInt(), temp["col"].asInt());
	}

	input = input["log"];

	// 根据历史输入恢复状态
	bool gameEnd = false;
	if (input.size() == 0)
	{
		temp = initdata["skipfirst"];
		if (temp.isBool() && temp.asBool())
		{
			// 找出一个保证没有雷的点
			int safeCol, safeRow;
			for (safeRow = 0; safeRow < fieldHeight; safeRow++)
			for (safeCol = 0; safeCol < fieldWidth; safeCol++)
			{
				if (mineField[safeRow][safeCol] == 0)
					goto FoundSafePoint;
			}
			do
			{
				safeCol = rand() % fieldWidth;
				safeRow = rand() % fieldHeight;
			} while (mineField[safeRow][safeCol] == 9);
FoundSafePoint:
			isLast = true;
			ProcClick(safeRow, safeCol);
			output["initdata"]["firstclick"]["row"] = safeRow;
			output["initdata"]["firstclick"]["col"] = safeCol;
		}
		output["display"]["status"] = DisplayField();
		output["command"] = "request";
		output["content"]["0"]["height"] = fieldHeight;
		output["content"]["0"]["width"] = fieldWidth;
		output["content"]["0"]["minecount"] = mineCount;
		output["content"]["0"]["changed"] = DisplayField();
	}
	else
	{
		output.removeMember("initdata");
		for (int i = 1; i < input.size(); i += 2)
		{
			isLast = i == input.size() - 1;
			Json::Value content;
			Json::Value display;
			Json::Value answer = input[i]["0"]["response"].isNull() ? input[i]["0"]["content"] : input[i]["0"]["response"];
			if (((answer.isString() &&
				reader.parse(answer.asString(), content)) ||
				(answer.isObject() &&
				(content = answer, true))) &&
				content["row"].isInt() && content["col"].isInt()) // 保证输入格式正确
			{
				int currCol = content["col"].asInt();
				int currRow = content["row"].asInt();
				if (currCol >= 0 && currCol < fieldWidth && currRow >= 0 && currRow < fieldHeight && !revealed[currRow][currCol]) // 合法点击
				{
					if (!ProcClick(currRow, currCol))
					{
						nonActiveMineCount--;
					}

					if (nonActiveMineCount == unrevealedCount)
					{
						// 游戏结束
						output["display"]["msg"] = "FINISH";
						output["command"] = "finish";
						output["content"]["0"] = nonActiveMineCount * 100.0 / mineCount;
						gameEnd = true;
					}
				}
				else
				{
					output["display"]["msg"] = "INVALIDMOVE";
					output["command"] = "finish"; // 判输
					output["content"]["0"] = 0;
					gameEnd = true;
				}
			}
			else
			{
				output["display"]["msg"] = "INVALIDMOVE";
				output["command"] = "finish"; // 判输
				output["content"]["0"] = 0;
				gameEnd = true;
			}
		}
	}
	output["display"]["status"] = DisplayField();
	if (!gameEnd)
	{
		output["command"] = "request";
		output["content"]["0"]["height"] = fieldHeight;
		output["content"]["0"]["width"] = fieldWidth;
		output["content"]["0"]["minecount"] = mineCount;
		output["content"]["0"]["changed"] = DisplayField();
	}
	Json::FastWriter writer;
	cout << writer.write(output) << endl;
}
