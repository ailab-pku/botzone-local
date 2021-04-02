# Botzone本地环境

本项目旨在构建通用的多智能体游戏环境，同时能够对接botzone上已有的游戏和bot。

## 背景

[Botzone](https://botzone.org)是一个在线的程序对战平台，提供了一系列游戏。用户可以提交自己的程序（被称为Bot），开启游戏桌与他人的Bot进行自动对战。一些课程或者比赛小组中可以用比赛的形式进行批量对局。

然而，由于该平台的对局均在线上进行，在下列场景中会带来一些不便之处：

- 用户写了两个Bot版本，想要多次运行对局来比较两个Bot的水平高低，而在网站上只能多次手动开启游戏桌进行对局
- 用户Bot正在开发中，存在一些bug需要反复修改，而在网站上需要反复上传Bot新版本并运行对局
- 用户想要训练基于学习算法的Bot，目前的在线对战方式无法支持接入基于函数调用的智能体，也无法做到高效收集数据，用户通常需要自己实现本地游戏环境进行智能体训练

因此本库的目的在于提供一套本地化的、可离线运行对局的Botzone环境。

本库与之前的[Botzone本地调试工具](https://github.com/zhouhaoyu/botzone-local-runner)的区别：
- **Botzone本地调试工具**中虽然本地程序是在本地运行的，但每回合都需要向服务器发起请求以调用服务器上的游戏裁判程序，没有真正做到完全在本地运行对局，并且效率较低
- **Botzone本地环境**中将游戏裁判程序和用户Bot都下载到本地，因此能够做到在用户主机上运行完整的对局，并且效率很高

## 介绍

本项目的最初目的是为了支持在本地运行botzone形式的对局，但在具体实现中为了可扩展性考虑，我们将其实现成了一个通用的多智能体游戏环境库。具体来说：

- 定义了多智能体博弈场景下**游戏环境**（Env）以及**智能体**（Agent）的通用接口规范，使得可以用非常简洁的代码运行对局
- 用户可以自己开发符合接口规范的新环境，也可以实现自定义的智能体（如用于算法研究）
- 通过在轻量级沙盒（Docker）中运行游戏裁判程序和Bot程序，本库直接对线上已有的游戏和Bot进行了支持，并将其包装成符合上述通用接口规范的组件
- 为了游戏环境的运行效率，本库中使用Python重新实现了线上各游戏的裁判程序，用户可以用它们来代替包装的线上游戏环境，可以大幅提升本地对局效率

## 开始使用

### 安装

本库需要Python 3.5+的Python环境。目前由于本库仍然在完善中，暂时不支持pip安装，未来会以Python库的形式发布。

在下载本库后，你需要安装相应的Python依赖：
```
git clone https://github.com/ailab-pku/botzone-local.git
cd botzone-local
pip install -r requirements.txt
```

### 使用线上游戏和Bot

为了支持线上Bot，你需要先安装docker（用于创建本地沙箱运行代码）以及NodeJS（用于支持简单交互）。

用户很容易可以使用线上已有的游戏和Bot运行对局。下面给出了一个简洁的例子：
```
try:
	# 创建名叫NoGo的游戏环境
	from botzone.online.game import Game, GameConfig
	env = Game(GameConfig.fromName('NoGo'))
	# 创建两个Bot实例，ID均为5fede20fd9383f7579afff06（这是样例Bot）
	from botzone.online.bot import Bot, BotConfig
	bots = [Bot(BotConfig.fromID('5fede20fd9383f7579afff06')) for i in range(env.player_num)]
	# 指定对局玩家
	env.init(bots)
	# 运行对局并渲染画面
	score = env.reset()
	env.render()
	while score is None:
		score = env.step() # 对局结束时，step会以tuple的形式返回各玩家得分
		env.render()
	print(score)
finally:
	# 对于包装的游戏和Bot，必须保证程序结束前调用close以释放沙盒资源，将该代码放在finally块中可以保证在程序出错退出前仍然能够执行。如果不释放沙盒资源，一段时间后你的电脑中会运行着许多docker容器实例，需要手动杀死。
	# 对于自定义的Env和Agent也建议在结束前调用close，因为它们可能需要释放资源
	env.close()
	for bot in bots: bot.close()
```

一些注意点：

- 第一次使用沙盒运行游戏或Bot时，本库会提示下载docker镜像文件。我们对于每种语言的运行环境预编译了一个镜像，以及一个可以支持所有语言的镜像，该镜像与服务器评测环境几乎一致。你可以选择只下载常用语言的镜像（比较小），也可以选择下载通用镜像（10G左右）。
- 在试图创建Bot时，本库会尝试从botzone网站下载Bot代码并缓存到默认路径（botzone/online/bot/)下，你可以通过向BotConfig传递参数```path```以改变缓存路径。
- 有的Bot运行时需要读写用户空间中的文件。你可以通过向BotConfig中传递参数```userfile```以开启这一行为，本库会尝试从botzone网站下载用户空间的数据并缓存到默认路径（botzone/online/bot/user_id/)下，你可以通过向BotConfig传递参数```userfile_path```以改变缓存路径。
- 下载非公开bot以及用户空间的文件时需要用户权限，在这种情况下本库会自动提示输入你的邮箱和密码来登录账号。

### 环境

本库使用唯一ID来标识不同的游戏环境。可以直接用以下代码来获取环境实例：
```
import botzone
env = botzone.make('Ataxx-v0') # Ataxx的Python环境
```
与以下代码的效果是相同的：
```
from botzone.envs.botzone.ataxx import AtaxxEnv
env = AtaxxEnv()
```

所有沙盒包装的游戏环境均采用GameName-wrap的ID形式，当前本库支持的完整环境列表可以用```botzone.all()```获取，[这里](https://github.com/ailab-pku/botzone-local/tree/master/botzone/envs)提供了对各环境的简单描述。

### 自定义环境和智能体

本库中实现了统一的[环境接口](https://github.com/ailab-pku/botzone-local/blob/master/botzone/env.py)和[Agent接口](https://github.com/ailab-pku/botzone-local/blob/master/botzone/agent.py)。
用户只需要继承```botzone.Env```和```botzone.Agent```即可实现自定义的环境和智能体，并且在统一的接口下自由交互。

在另一种应用场景中，用户在本地创建了打算上传到botzone的Bot程序或者游戏裁判程序，但想要先在本地进行调试。这种场景中用户可以自己构造BotConfig或GameConfig对象，并用它们创建只存在于本地的Bot或者Game。详细信息可以查看相关类的文档注释：[Bot](https://github.com/ailab-pku/botzone-local/blob/master/botzone/online/bot.py), [Game](https://github.com/ailab-pku/botzone-local/blob/master/botzone/online/game.py)
