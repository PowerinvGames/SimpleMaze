# python/logger.py
"""
应用程序日志记录器
"""
import logging
import sys


class LoggerFactory:
    """日志工厂类"""

    _initialized = False

    @classmethod
    def initialize(cls):
        """初始化日志系统"""
        if not cls._initialized:
            # 创建根日志记录器
            logger = logging.getLogger('maze_game')
            logger.setLevel(logging.INFO)

            # 创建控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)

            # 创建格式化器
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)

            # 添加处理器
            logger.addHandler(console_handler)

            cls._initialized = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """获取指定名称的日志记录器"""
        if not cls._initialized:
            cls.initialize()
        return logging.getLogger(name)


# 创建默认的应用程序日志记录器
logger = LoggerFactory.get_logger('maze_game')
