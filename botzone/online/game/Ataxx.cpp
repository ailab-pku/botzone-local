#include <iostream>
#include <sstream>
#include <string>
#include <cmath>
#include "jsoncpp/json.h"
using namespace std;


int currBotColor; // 我所执子颜色（1为黑，-1为白，棋盘状态亦同）
int gridInfo[7][7] = { 0 }; // 先x后y，记录棋盘状态
int blackPieceCount = 2, whitePieceCount = 2; 
string blackName = "", whiteName = "";
char history[801][7][7]; // ‘1’为黑，‘2’为白，‘0’为空
static int delta[24][2] = { { 1,1 },{ 0,1 },{ -1,1 },{ -1,0 },
							{ -1,-1 },{ 0,-1 },{ 1,-1 },{ 1,0 },
							{ 2,0 },{ 2,1 },{ 2,2 },{ 1,2 },
							{ 0,2 },{ -1,2 },{ -2,2 },{ -2,1 },
							{ -2,0 },{ -2,-1 },{ -2,-2 },{ -1,-2 },
							{ 0,-2 },{ 1,-2 },{ 2,-2 },{ 2,-1 } };

void savehistory(int nowgame)
{
	int row, cal;
	for (row = 0; row < 7; row++)
	{
		for (cal = 0; cal < 7; cal++)
		{
			if (gridInfo[row][cal] == 0)
				history[nowgame][row][cal] = '0';
			else
				history[nowgame][row][cal] = '2'-(gridInfo[row][cal]+1)/2;
		}
	}
}
inline int repeat(int nowgame) // 调用时，输入参数应该为input.size()-1?
{
	if (nowgame < 4)
		return false;
	int i, befgame,exist = 0;
	for (befgame = nowgame - 2; befgame >= 0; befgame--)
	{
		for (i = 0; i < befgame; i++)
		{
			int row, cal, flag = 0;
			for (row = 0; row < 7; row++)
			{
				for (cal = 0; cal < 7; cal++)
				{
					if (history[i][row][cal] != history[nowgame - 1][row][cal])
					{
						flag = 1;
						break;
					}
				}
				if (flag)
					break;
			}
			if (!flag) // 现在要找第i项和第nowgame项
			{
				flag = 0;
				for (row = 0; row < 7; row++)
				{
					for (cal = 0; cal < 7; cal++)
					{
						if (history[i+1][row][cal] != history[nowgame][row][cal])
						{
							flag = 1;
							break;
						}
					}
					if (flag)
						break;
				}
				if (!flag)
					return (-i-1);
			}
		}
	}
	return false;
}

inline bool inMap(int x, int y)
{
	if (x < 0 || x > 6 || y < 0 || y > 6)
		return false;
	return true;
}

inline bool MoveStep(int &x, int &y, int Direction)
{
	x = x + delta[Direction][0];
	y = y + delta[Direction][1];
	return inMap(x, y);
}

int ProcStep(int x0, int y0, int x1, int y1, int color, int nowgame)
{
	if (color == 0)
		return false;
	if (!inMap(x0, y0) || !inMap(x1, y1)) 
		return false;
	if (gridInfo[x0][y0] != color)
		return false;
	int dx, dy, x, y, currCount = 0, dir;
	int effectivePoints[8][2];
	dx = abs((x0 - x1)), dy = abs((y0 - y1));
	if ((dx == 0 && dy == 0) || dx > 2 || dy > 2) 
		return false;
	if (gridInfo[x1][y1] != 0) 
		return false;
	if (dx == 2 || dy == 2) 
		gridInfo[x0][y0] = 0;
	else
	{
		if (color == 1)
			blackPieceCount++;
		else
			whitePieceCount++;
	}

	gridInfo[x1][y1] = color;
	savehistory(nowgame);
	for (dir = 0; dir < 8; dir++) 
	{
		x = x1 + delta[dir][0];
		y = y1 + delta[dir][1];
		if (!inMap(x, y))
			continue;
		if (gridInfo[x][y] == -color)
		{
			effectivePoints[currCount][0] = x;
			effectivePoints[currCount][1] = y;
			currCount++;
			gridInfo[x][y] = color;
		}
	}
	if (currCount != 0)
	{
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
	}
	int number = repeat(nowgame);
	if (number == 0)
		return true;
	else
		return number;
}

bool CheckIfHasValidMove(int color, int nowgame) 
{
	int x0, y0, x, y, dir;
	for (y0 = 0; y0 < 7; y0++)
		for (x0 = 0; x0 < 7; x0++)
		{
			if (gridInfo[x0][y0] != color)
				continue;
			for (dir = 0; dir < 24; dir++)
			{
				x = x0 + delta[dir][0];
				y = y0 + delta[dir][1];
				if (!inMap(x, y))
					continue;
				if (gridInfo[x][y] == 0)
				{
					history[nowgame][x][y] = '2' - (color + 1) / 2;
					if (repeat(nowgame))
					{
						history[nowgame][x][y] = '0';
						continue;
					}
					else
					{
						history[nowgame][x][y] = '0';
						return true;
					}
				}
			}
		}
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

	gridInfo[0][0] = gridInfo[6][6] = 1;  
	gridInfo[6][0] = gridInfo[0][6] = -1; 
	savehistory(0);
	currBotColor = 1; 
	if (input.size() == 0)
	{
		output["display"] = "";
		output["command"] = "request";
		output["content"]["0"]["x0"] = -1;
		output["content"]["0"]["y0"] = -1;
		output["content"]["0"]["x1"] = -1;
		output["content"]["0"]["y1"] = -1;
	}
	else
	{
		for (int i = 1; i < input.size(); i += 2)
		{
			bool isLast = i == input.size() - 1;
			// bool isLast = true;

			Json::Value content;
			Json::Value display;
			if (currBotColor == 1)
			{
				savehistory((i + 1) / 2);
				Json::Value answer = input[i]["0"]["response"].isNull() ? input[i]["0"]["content"] : input[i]["0"]["response"];
				if (((answer.isString() &&
					reader.parse(answer.asString(), content)) ||
					(answer.isObject() &&
					(content = answer, true))) &&
					content["x0"].isInt() && content["y0"].isInt() &&
					content["x1"].isInt() && content["y1"].isInt()) 
				{
					int befX = content["x0"].asInt();
					int befY = content["y0"].asInt();
					int currX = content["x1"].asInt();
					int currY = content["y1"].asInt();
					int procresult = ProcStep(befX, befY, currX, currY, currBotColor, (i + 1) / 2);

					if (!procresult && isLast)
					{
						output["display"]["err"] = "INVALIDMOVE";
						output["display"]["winner"] = 1;
						output["command"] = "finish"; 
						output["content"]["0"] = 0;
						output["content"]["1"] = 2;
					}
					else if (procresult < 0 && isLast)
					{
						output["display"]["err"] = "CIRCULAR_MOVE";
						output["display"]["errorturn"] = -procresult;
						output["display"]["winner"] = 1;
						output["command"] = "finish";
						output["content"]["0"] = 0;
						output["content"]["1"] = 2;
					}
					else if (isLast) 
					{
						output["display"]["x0"] = befX;
						output["display"]["y0"] = befY;
						output["display"]["x1"] = currX;
						output["display"]["y1"] = currY;
						if (whitePieceCount == 0)
						{
							output["display"]["winner"] = 0;
							output["command"] = "finish";
							output["content"]["0"] = 2;
							output["content"]["1"] = 0;
						}
						else
						{
							bool blackHasMove = CheckIfHasValidMove(currBotColor, i),
								whiteHasMove = CheckIfHasValidMove(-currBotColor, i);
							if (!blackHasMove || !whiteHasMove || input.size() > 800) 
							{
								if (blackHasMove && !whiteHasMove)
									blackPieceCount = 49 - whitePieceCount;
								if (!blackHasMove && whiteHasMove)
									whitePieceCount = 49 - blackPieceCount;

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
									output["display"]["winner"] = -1;
									output["command"] = "finish";
									output["content"]["0"] = 1;
									output["content"]["1"] = 1;
								}
							}
							else
							{
								output["command"] = "request";
								output["content"]["1"]["x0"] = befX;
								output["content"]["1"]["y0"] = befY;
								output["content"]["1"]["x1"] = currX;
								output["content"]["1"]["y1"] = currY;
							}
						}
					}
				}
				else if (isLast) 
				{
					output["display"]["err"] = "INVALID_INPUT_VERDICT_" + input[i]["0"]["verdict"].asString();
					output["display"]["winner"] = 1;
					output["command"] = "finish"; 
					output["content"]["0"] = 0;
					output["content"]["1"] = 2;
				}
			}
			else
			{
				Json::Value answer = input[i]["1"]["response"].isNull() ? input[i]["1"]["content"] : input[i]["1"]["response"];
				if (((answer.isString() &&
					reader.parse(answer.asString(), content)) ||
					(answer.isObject()) &&
					(content = answer, true)) &&
					content["x0"].isInt() && content["y0"].isInt() &&
					content["x1"].isInt() && content["y1"].isInt()) 
				{
					int befX = content["x0"].asInt();
					int befY = content["y0"].asInt();
					int currX = content["x1"].asInt();
					int currY = content["y1"].asInt();
					int procresult = ProcStep(befX, befY, currX, currY, currBotColor, (i + 1) / 2);

					if (!procresult && isLast)
					{
						output["display"]["err"] = "INVALIDMOVE";
						output["display"]["winner"] = 0;
						output["command"] = "finish"; 
						output["content"]["0"] = 2;
						output["content"]["1"] = 0;
					}
					else if (procresult < 0 && isLast)
					{
						output["display"]["err"] = "CIRCULAR_MOVE";
						output["display"]["errorturn"] = -procresult;
						output["display"]["winner"] = 0;
						output["command"] = "finish";
						output["content"]["0"] = 2;
						output["content"]["1"] = 0;
					}
					else if (isLast) 
					{
						output["display"]["x0"] = befX;
						output["display"]["y0"] = befY;
						output["display"]["x1"] = currX;
						output["display"]["y1"] = currY;
						if (blackPieceCount == 0)
						{
							output["display"]["winner"] = 1;
							output["command"] = "finish";
							output["content"]["0"] = 0;
							output["content"]["1"] = 2;
						}
						else
						{
							bool blackHasMove = CheckIfHasValidMove(-currBotColor,i+1),
								whiteHasMove = CheckIfHasValidMove(currBotColor,i+1);
							if (!blackHasMove || !whiteHasMove || input.size() > 800) 
							{
								if (blackHasMove && !whiteHasMove)
									blackPieceCount = 49 - whitePieceCount;
								if (!blackHasMove && whiteHasMove)
									whitePieceCount = 49 - blackPieceCount;

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
									output["display"]["winner"] = -1;
									output["command"] = "finish";
									output["content"]["0"] = 1;
									output["content"]["1"] = 1;
								}
							}
							else
							{
								output["command"] = "request";
								output["content"]["0"]["x0"] = befX;
								output["content"]["0"]["y0"] = befY;
								output["content"]["0"]["x1"] = currX;
								output["content"]["0"]["y1"] = currY;
							}
						}
					}
				}
				else if (isLast)
				{
					output["display"]["err"] = "INVALID_INPUT_VERDICT_" + input[i]["1"]["verdict"].asString();
					output["display"]["winner"] = 0;
					output["command"] = "finish"; 
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
