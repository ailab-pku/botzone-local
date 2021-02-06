#include<cstdio>
#include<cstdlib>
#include<cstring>
#include<iostream>
#include<string>
#include<list>
#include<ctime>
#include"jsoncpp/json.h"
using namespace std;
int n;
int m;
int obstacle;
const int maxn=25;
const int dx[4]={-1,0,1,0};
const int dy[4]={0,1,0,-1};
bool vis[maxn][maxn];
bool grid[maxn][maxn];
int lose[2],reason[2];
int tot,width,height;

Json::Value obs;

struct point
{
	int x,y;
	point(int _x,int _y)
	{
		x=_x;
		y=_y;
	}
};

list<point> snake[2];

bool isInBody(int x,int y)
{
	for (int id=0;id<=1;id++)
		for (list<point>::iterator iter=snake[id].begin();iter!=snake[id].end();++iter)
			if (x==iter->x && y==iter->y)
				return true;
	return false;
}

bool whetherGrow(int num)
{
	if (num<=9) return true;
	if ((num-9)%3==0) return true;
	return false;
}

bool validDirection(int id,int k)
{
	if (k<0 || k>3) return false;
	point p=*(snake[id].begin());
	int x=p.x+dx[k];
	int y=p.y+dy[k];

	//printf(" get 0\n");
	if (x>n || y>m || x<1 || y<1) return false;
	//printf(" get 1\n");
	//iprintf(" $$ %d %d %d\n",x,y,grid[x][y]);
	if (grid[x][y]) return false;
	//printf(" get 2\n");
	if (isInBody(x,y)) return false;
	//printf(" get 3\n");
	return true;
}

void move(int id,int dire,int num)
{
	point p=*(snake[id].begin());
	int x=p.x+dx[dire];
	int y=p.y+dy[dire];
	snake[id].push_front(point(x,y));
}

int otherPlayerID(int id)
{
	return 1-id;
}

string playerString(int id)
{
	if (id==0) return "0";
	return "1";
}

void deleteEnd(int id)
{
	snake[id].pop_back();
}

void outputSnakeBody(int id)
{
	cout<<"Snake No."<<id<<endl;
	for (list<point>::iterator iter=snake[id].begin();iter!=snake[id].end();++iter)
		cout<<iter->x<<" "<<iter->y<<endl;
	cout<<endl;
}

int Rand(int n)
{
	return (rand()*rand()*rand()%n+n)%n+1;
}

void dfs(int x,int y)
{
	vis[x][y]=true;
	for (int k=0;k<4;k++)
	{
		int xx=x+dx[k];
		int yy=y+dy[k];
		if (xx>0 && yy>0 && xx<=n && yy<=m)
			if (vis[xx][yy]==false && grid[xx][yy]==false)
				dfs(xx,yy);
	}
}

int main()
{
	//srand(time(0));

	string str;
	string temps;
	getline(cin,temps);
	str+=temps;

	Json::Reader reader;
	Json::Value input, output, initdata, obstacles,temp;
	reader.parse(str, input);

	initdata=input["initdata"];

	if (initdata.isString())
		reader.parse(initdata.asString(), initdata);
	if (initdata.isString())
		reader.parse("{}", initdata);

	temp=initdata["seed"];
	if (temp.isInt())
		srand(temp.asInt());
	else
		srand(time(0));

	temp=initdata["width"];
	width=9+Rand(3);
	if (temp.isInt())
	{
		width=temp.asInt();
		if (width>12 || width<10)
			width=12;
	}
	output["initdata"]["width"]=width;

	temp=initdata["height"];
	height=10+Rand(6);
	if ((width+height)%2==0)
		height--;
	if (temp.isInt())
	{
		height=temp.asInt();
		if (height>16 || height<10)
			height=12;
	}
	output["initdata"]["height"]=height;

	obs=initdata["obstacle"];
	output["initdata"]["obstacle"]=obs;

	int obsCount=obs.size();
	for (int i=0;i<obsCount;i++)
	{
		int ox=obs[(Json::Value::UInt) i]["x"].asInt();
		int oy=obs[(Json::Value::UInt) i]["y"].asInt();
		grid[ox][oy]=true;
	}

	n=height;
	m=width;

	input = input["log"];

	Json::FastWriter writer;

	if (input.size()==0)
	{
		output["initdata"]["height"]=n;	
		output["initdata"]["width"]=m;
		output["initdata"]["0"]["x"]=1;
		output["initdata"]["0"]["y"]=1;
		output["initdata"]["1"]["x"]=n;
		output["initdata"]["1"]["y"]=m;

		obstacle=width*height/10;

		while (true)
		{
			int countObs=0;
			for (int i=0;i<obstacle/2;i++)
			{
				int x=Rand(n);
				int y=Rand(m);
				while (grid[x][y] || (x==1 && y==1) || (x==n && y==m))
				{
					x=Rand(n);
					y=Rand(m);
				}
				countObs++;
				output["initdata"]["obstacle"][tot]["x"]=x;	
				output["initdata"]["obstacle"][tot++]["y"]=y;
				grid[x][y]=true;
				if (x!=n-x+1 || y!=m-y+1)
				{
					countObs++;
					output["initdata"]["obstacle"][tot]["x"]=n-x+1;
					output["initdata"]["obstacle"][tot++]["y"]=m-y+1;
					grid[n-x+1][m-y+1]=true;
				}
			}
			dfs(1,1);
			int countVis=0;
			for (int i=1;i<=n;i++)
				for (int j=1;j<=m;j++)
					if (vis[i][j]) countVis++;
			if (countVis+countObs==width*height)
				break;
			else
			{
				tot=0;
				output["initdata"]["obstacle"].clear();
				memset(grid,0,sizeof(grid));
				memset(vis,0,sizeof(vis));
			}
		}
		obs=output["initdata"]["obstacle"];

		output["command"]="request";
		output["content"]["0"]["x"]=1;
		output["content"]["0"]["y"]=1;
		output["content"]["1"]["x"]=n;
		output["content"]["1"]["y"]=m;

		output["content"]["0"]["height"]=height;
		output["content"]["1"]["height"]=height;
		output["content"]["0"]["width"]=width;
		output["content"]["1"]["width"]=width;
		output["content"]["0"]["obstacle"]=obs;
		output["content"]["1"]["obstacle"]=obs;

		initdata=output["initdata"];
		output["display"]=initdata;

		cout<<writer.write(output)<<endl;
		return 0;
	}

	snake[0].push_front(point(1,1));
	snake[1].push_front(point(n,m));


	for (int i=1;i<input.size();i+=2)
	{
		bool isLast = i==input.size()-1;
		bool isOver = false;
		int num=i/2;
		Json::Value content;

		for (int id=0;id<=1;id++)
		{
			if (!whetherGrow(num)) // do not grow this time
			{
				output["display"]["grow"]="false";
				deleteEnd(id);
			}
			else
				output["display"]["grow"]="true";
		}

		for (int id=0;id<=1;id++)
		{
			Json::Value answer=input[i][playerString(id)]["response"];
			if (answer.isObject() && (content=answer, true) && content["direction"].isInt()) // valid input
			{
				int dire=content["direction"].asInt();
				if (isLast) output["display"][playerString(id)]=dire;

				if (dire>=0 && dire<=3 && id==1 && snake[0].begin()->x==snake[1].begin()->x+dx[dire] && snake[0].begin()->y==snake[1].begin()->y+dy[dire])
				{
					isOver=true;
					lose[0]=lose[1]=1;
					continue;
				}
				if (validDirection(id,dire))
				{
					move(id,dire,num);
					if (isLast && !isOver)
					{
						output["command"]="request";
						output["content"][playerString(otherPlayerID(id))]["direction"]=dire;
					}
				}
				else // invalid direction
				{
					isOver=true;
					reason[id]=0;
					lose[id]=1;
				}
			}
			else // invalid input
			{
				isOver=true;
				reason[id]=1;
				lose[id]=1;
			}
		}

		if (lose[0] || lose[1])
		{
			if (lose[0]+lose[1]==1)
			{
				if (reason[0]+reason[1]==0)
					output["display"]["err"]="INVALIDMOVE";
				else
					output["display"]["err"] = "INVALID_INPUT_VERDICT_" + input[i][playerString(lose[1])]["verdict"].asString();

				int winner=lose[0]?1:0;
				output["display"]["winner"]=playerString(winner);
				output["command"]="finish";
				output["content"].clear();
				output["content"][playerString(winner)]=2;
				output["content"][playerString(otherPlayerID(winner))]=0;
			}
			if (lose[0]+lose[1]==2)
			{
				output["command"]="finish";
				output["content"].clear();
				output["display"]["err"]="BothSnakeDie";
				output["content"]["0"]=1;
				output["content"]["1"]=1;	
			}
			break;
		}

		//outputSnakeBody(0);
		//outputSnakeBody(1);
	}


	cout<<writer.write(output)<<endl;
	return 0;
}
