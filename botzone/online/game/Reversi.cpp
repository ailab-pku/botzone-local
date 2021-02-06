#include <iostream>
#include <sstream>
#include <string>
#include "jsoncpp/json.h"
using namespace std;


// 注意黑方为0号玩家
int currBotColor; // 正在等待输出结果的BOT
int gridInfo[8][8] = { 0 }; // 先x后y
int blackPieceCount = 2, whitePieceCount = 2;
string blackName = "", whiteName = "";

static bool MoveStep(int &x, int &y, int Direction)
{
	if (Direction == 0 || Direction == 6 || Direction == 7)
		x++;
	if (Direction == 0 || Direction == 1 || Direction == 2)
		y++;
	if (Direction == 2 || Direction == 3 || Direction == 4)
		x--;
	if (Direction == 4 || Direction == 5 || Direction == 6)
		y--;
	if (x < 0 || x > 7 || y < 0 || y > 7)
		return false;
	return true;
}

bool ProcStep(int xPos, int yPos, int color, bool checkOnly = false)
{
	if (xPos == -1)
		return true;
	if (xPos < 0 || xPos > 7 || yPos < 0 || yPos > 7)
		return false;
	int effectivePoints[8][2];
	int dir, x, y, currCount;
	bool isValidMove = false;
	if (gridInfo[xPos][yPos] != 0)
		return false;
	for (dir = 0; dir < 8; dir++)
	{
		x = xPos;
		y = yPos;
		currCount = 0;
		while (1)
		{
			if (!MoveStep(x, y, dir))
			{
				currCount = 0;
				break;
			}
			if (gridInfo[x][y] == -color)
			{
				currCount++;
				effectivePoints[currCount][0] = x;
				effectivePoints[currCount][1] = y;
			}
			else if (gridInfo[x][y] == 0)
			{
				currCount = 0;
				break;
			}
			else
			{
				break;
			}
		}
		if (currCount != 0)
		{
			isValidMove = true;
			if (checkOnly)
				return true;
			if (color == 1)
			{
				blackPieceCount += currCount;
				whitePieceCount -= currCount;
			}
			else
			{
				whitePieceCount += currCount;
				blackPieceCount -= currCount;
			}
			while (currCount > 0)
			{
				x = effectivePoints[currCount][0];
				y = effectivePoints[currCount][1];
				gridInfo[x][y] *= -1;
				currCount--;
			}
		}
	}
	if (isValidMove)
	{
		gridInfo[xPos][yPos] = color;
		if (color == 1)
			blackPieceCount++;
		else
			whitePieceCount++;
		return true;
	}
	else
		return false;
}

bool CheckIfHasValidMove(int color)
{
	int x, y;
	for (y = 0; y < 8; y++)
		for (x = 0; x < 8; x++)
			if (ProcStep(x, y, color, true))
				return true;
	return false;
}

int main()
{
	string str;
	getline(cin, str);
	Json::Reader reader;
	Json::Value input, output;
	reader.parse(str, input);
	input = input["log"];


	gridInfo[3][4] = gridInfo[4][3] = 1;  //|白|黑|
	gridInfo[3][3] = gridInfo[4][4] = -1; //|黑|白|
	currBotColor = 1; // 先手为黑
	if (input.size() == 0)
	{
		output["display"] = "";
		output["command"] = "request";
		output["content"]["0"]["x"] = -1;
		output["content"]["0"]["y"] = -1;
	}
	else
	{
		for (int i = 1; i < input.size(); i += 2)
		{
			bool isLast = i == input.size() - 1;
			Json::Value content;
			Json::Value display;
			if (currBotColor == 1) // 0号玩家 / 黑方
			{
				Json::Value answer = input[i]["0"]["response"].isNull() ? input[i]["0"]["content"] : input[i]["0"]["response"];
				if (((answer.isString() &&
					reader.parse(answer.asString(), content)) ||
					(answer.isObject() &&
						(content = answer, true))) &&
					content["x"].isInt() && content["y"].isInt()) // 保证输入格式正确
				{
					int currX = content["x"].asInt();
					int currY = content["y"].asInt();
					if (currX == -1 && isLast) // bot选择PASS
					{
						if (!CheckIfHasValidMove(currBotColor)) // 他应该PASS
						{
							output["display"]["x"] = -1;
							output["display"]["y"] = -1;
							output["command"] = "request";
							output["content"]["1"]["x"] = -1;
							output["content"]["1"]["y"] = -1;
						}
						else // 他不应该PASS
						{
							// Todo: Bug here--
							output["display"]["err"] = "HE_THOUGHT_THAT_HE_COULDNOT_MOVE_BUT_IN_FACT_HE_CAN";
							output["display"]["winner"] = 1;
							output["command"] = "finish"; // 判输
							output["content"]["0"] = 0;
							output["content"]["1"] = 2;
						}
					}
					else if (!ProcStep(currX, currY, currBotColor) && isLast) // 不合法棋步！
					{
						output["display"]["err"] = "INVALID_MOVE";
						output["display"]["winner"] = 1;
						output["command"] = "finish"; // 判输
						output["content"]["0"] = 0;
						output["content"]["1"] = 2;
					}
					else if (isLast) // 正常棋步
					{
						output["display"]["x"] = currX;
						output["display"]["y"] = currY;
						if (!CheckIfHasValidMove(currBotColor) && !CheckIfHasValidMove(-currBotColor)) // 游戏结束
						{
							if (blackPieceCount > whitePieceCount)
							{
								output["display"]["winner"] = 0;
								output["command"] = "finish";
								output["content"]["0"] = 2;
								output["content"]["1"] = 0;
							}
							else if (blackPieceCount < whitePieceCount)
							{
								output["display"]["winner"] = 1;
								output["command"] = "finish";
								output["content"]["0"] = 0;
								output["content"]["1"] = 2;
							}
							else
							{
								output["command"] = "finish";
								output["content"]["0"] = 1;
								output["content"]["1"] = 1;
							}
						}
						else
						{

							output["display"]["x"] = currX;
							output["display"]["y"] = currY;
							output["command"] = "request";
							output["content"]["1"]["x"] = currX;
							output["content"]["1"]["y"] = currY;
						}
					}
				}
				else if (isLast)
				{
					output["display"]["err"] = "INVALID_INPUT_VERDICT_" + input[i]["0"]["verdict"].asString();
					output["display"]["winner"] = 1;
					output["command"] = "finish"; // 判输
					output["content"]["0"] = 0;
					output["content"]["1"] = 2;
				}
			}
			else
			{
				Json::Value answer = input[i]["1"]["response"].isNull() ? input[i]["1"]["content"] : input[i]["1"]["response"];
				if (((answer.isString() &&
					reader.parse(answer.asString(), content)) ||
					(answer.isObject() &&
						(content = answer, true))) &&
					content["x"].isInt() && content["y"].isInt()) // 保证输入格式正确
				{
					int currX = content["x"].asInt();
					int currY = content["y"].asInt();
					if (currX == -1 && isLast) // bot选择PASS
					{
						if (!CheckIfHasValidMove(currBotColor)) // 他应该PASS
						{
							output["display"]["x"] = -1;
							output["display"]["y"] = -1;
							output["command"] = "request";
							output["content"]["0"]["x"] = -1;
							output["content"]["0"]["y"] = -1;
						}
						else // 他不应该PASS
						{
							output["display"]["err"] = "HE_THOUGHT_THAT_HE_COULDNOT_MOVE_BUT_IN_FACT_HE_CAN";
							output["display"]["winner"] = 0;
							output["command"] = "finish"; // 判输
							output["content"]["0"] = 2;
							output["content"]["1"] = 0;
						}
					}
					else if (!ProcStep(currX, currY, currBotColor) && isLast) // 不合法棋步！
					{
						output["display"]["err"] = "INVALID_MOVE";
						output["display"]["winner"] = 0;
						output["command"] = "finish"; // 判输
						output["content"]["0"] = 2;
						output["content"]["1"] = 0;
					}
					else if (isLast) // 正常棋步
					{
						output["display"]["x"] = currX;
						output["display"]["y"] = currY;
						if (!CheckIfHasValidMove(currBotColor) && !CheckIfHasValidMove(-currBotColor)) // 游戏结束
						{
							if (blackPieceCount > whitePieceCount)
							{
								output["display"]["winner"] = 0;
								output["command"] = "finish";
								output["content"]["0"] = 2;
								output["content"]["1"] = 0;
							}
							else if (blackPieceCount < whitePieceCount)
							{
								output["display"]["winner"] = 1;
								output["command"] = "finish";
								output["content"]["0"] = 0;
								output["content"]["1"] = 2;
							}
							else
							{
								output["command"] = "finish";
								output["content"]["0"] = 1;
								output["content"]["1"] = 1;
							}
						}
						else
						{
							output["command"] = "request";
							output["content"]["0"]["x"] = currX;
							output["content"]["0"]["y"] = currY;
						}
					}
				}
				else if (isLast)
				{
					output["display"]["err"] = "INVALID_INPUT_VERDICT_" + input[i]["1"]["verdict"].asString();
					output["display"]["winner"] = 0;
					output["command"] = "finish"; // 判输
					output["content"]["0"] = 2;
					output["content"]["1"] = 0;
				}
			}
			currBotColor *= -1;
		}
	}
	Json::FastWriter writer;
	cout << writer.write(output) << endl;
}
