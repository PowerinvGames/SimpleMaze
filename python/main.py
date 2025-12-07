# python/main.py
"""
迷宫AI游戏 - 主程序入口
"""
import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from python.app.ApplicationController import ApplicationController
from python.logger import logger


def parse_arguments():
    """解析命令行参数"""
    import argparse

    parser = argparse.ArgumentParser(description='迷宫AI游戏')
    parser.add_argument('--host', default='127.0.0.1',
                        help='HTTP服务器主机地址 (默认: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8080,
                        help='HTTP服务器端口 (默认: 8080)')
    parser.add_argument('--maze-width', type=int, default=55,
                        help='迷宫宽度 (默认: 55)')
    parser.add_argument('--maze-height', type=int, default=35,
                        help='迷宫高度 (默认: 35)')

    return parser.parse_args()


def main() -> int:
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()

        # 创建并初始化应用程序控制器
        controller = ApplicationController()
        controller.initialize(args)

        # 运行应用程序
        controller.run()

        return 0

    except Exception as e:
        logger.error(f"应用程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
