# 迷宫AI游戏项目

---

# 🎮 项目概述

一个基于Python的迷宫游戏，集成了本地GUI界面和HTTP API服务，支持多种交互方式控制游戏进程。项目采用模块化设计，实现了游戏逻辑、UI展示和API服务的清晰分离。

# 🚀 快速开始

## 环境要求

- Python 3.7+
- 依赖包：参见 requirements.txt

## 安装步骤

```bash
# 克隆项目
git clone <repository-url>
cd maze_game

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 运行游戏

```bash
python python/main.py
```

启动后，游戏窗口将自动打开，同时HTTP API服务将在 http://127.0.0.1:8080 启动。

# 📁 项目结构

```text
SimpleMaze/
├── python/                           # 主要源代码目录
│   ├── main.py                       # 程序入口
│   ├── constants.py                  # 常量配置
│   ├── logger.py                     # 日志配置
│   ├── app/                          # 应用层
│   │   ├── ApplicationController.py
│   │   └── GameEventBus.py
│   ├── core/                         # 核心游戏逻辑
│   │   ├── models/                   # 数据模型
│   │   │   ├── GameModels.py
│   │   │   └── MazeModels.py
│   │   ├── game/                     # 游戏服务
│   │   │   └── MazeGameService.py
│   │   ├── maze/                     # 迷宫生成
│   │   │   └── MazeGenerator.py
│   ├── ui/                           # 用户界面
│   │   ├── GameWindow.py             # 主窗口
│   │   ├── MazeRenderer.py           # 迷宫渲染器
│   │   └── components/               # UI组件
│   │       ├── GameInfoPanel.py
│   │       ├── ControlPanel.py
│   │       ├── FunctionPanel.py
│   │       └── MazePanel.py
│   ├── server/                       # HTTP服务器
│   │   └── HttpGameServer.py
│   └── utils/                        # 工具类
│       └── FontManager.py
├── resources/                        # 资源文件
│   ├── HarmonyOS_SansSC_Regular.ttf  # 中文字体
├── requirements.txt                  # 项目依赖
└── README.md                         # 项目说明
└── LICENSE                           # 许可证
```

# 🎯 游戏特性

## 三种控制方式

1. 本地GUI界面：可视化操作，支持按钮和键盘控制
2. 键盘快捷键：
   - 方向键/WASD：控制移动
   - 空格键：等待
   - R键：重置当前关卡
   - N键：生成新关卡
3. HTTP API：支持程序化控制，便于AI集成

## 游戏机制

- 随机生成迷宫（55×35大小）
- 玩家从左下角出发，目标到达右上角出口
- 实时显示移动次数和位置信息
- 到达终点时显示胜利界面

# 🌐 HTTP API接口

## 基础信息

- 服务器地址：http://127.0.0.1:8080
- 请求格式：JSON
- 响应格式：JSON

## 可用接口

```text
GET    /api/health     # 健康检查
GET    /api/state      # 获取游戏状态
POST   /api/move       # 移动玩家
POST   /api/reset      # 重置当前关卡
POST   /api/new-level  # 生成新关卡
```

## 游戏状态数据结构

```json
{
  "maze_size": {"width": 55, "height": 35},
  "player_position": {"col": 1, "row": 33},
  "exit_position": {"col": 53, "row": 1},
  "move_count": 0,
  "is_completed": false
}
```

## 移动方向

- `up`：向上移动
- `down`：向下移动
- `left`：向左移动
- `right`：向右移动
- `wait`：等待（不移动）

## API调用示例

```python
import requests

# 移动玩家
response = requests.post(
    "http://127.0.0.1:8080/api/move",
    json={"direction": "up"}
)

# 获取游戏状态
state = requests.get("http://127.0.0.1:8080/api/state").json()

# 重置关卡
requests.post("http://127.0.0.1:8080/api/reset")
```

# 🛠️ 开发说明

## 设计模式

- **事件驱动架构**：使用事件总线解耦UI与游戏逻辑
- **模块化组件**：UI元素封装为独立组件
- **MVC分离**：模型、视图、控制器清晰分离

## 字体配置

项目中包含中文字体文件（HarmonyOS Sans SC），确保中文正常显示。如需更换字体，请：

1. 将新字体文件放入 resources/ 目录
2. 在 python/constants.py 中更新 ResourcePaths.FONT_FILE 路径

## 日志系统

- 使用Python标准logging模块
- 日志级别：INFO
- 输出到控制台

# 📋 命令行参数

```bash
python python/main.py --help
```

可用参数：

- --host：HTTP服务器主机地址（默认：127.0.0.1）
- --port：HTTP服务器端口（默认：8080）
- --maze-width：迷宫宽度（默认：55）
- --maze-height：迷宫高度（默认：35）

# 🔧 故障排除

## 常见问题

1. **中文显示乱码**
   - 确保 resources/HarmonyOS_SansSC_Regular.ttf 文件存在
   - 检查字体文件路径是否正确
2. **端口占用**
   - 默认使用8080端口，如被占用会自动尝试其他端口
   - 可通过 --port 参数指定其他端口
3. **依赖安装失败**
   - 确保使用Python 3.7+
   - 尝试升级pip：pip install --upgrade pip

## 调试模式

如需更详细的日志，可修改 python/logger.py 中的日志级别：

```python
logger.setLevel(logging.DEBUG)  # 改为DEBUG级别
```

# 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。

# 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支：git checkout -b feature/新功能
3. 提交更改：git commit -m '添加新功能'
4. 推送到分支：git push origin feature/新功能
5. 提交 Pull Request

# 📞 联系方式

如有问题或建议，请提交GitHub Issue。

---

开始你的迷宫冒险吧！ 🚶‍♂️➡️🎯
