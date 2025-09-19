import logging
import logging.handlers
import multiprocessing
import sys

class MPLogger:
    """多进程安全日志封装，支持轮转"""
    _queue = None
    _listener = None

    @staticmethod
    def init_logger(
        log_file="mp_log.log",
        level=logging.INFO,
        console=True,
        max_bytes=None,
        backup_count=5,
        when=None,
        interval=1
    ):
        """
        初始化多进程日志系统
        :param log_file: 日志文件路径
        :param level: 日志级别
        :param console: 是否输出到控制台
        :param max_bytes: 文件最大字节数（按大小轮转） None 表示不启用
        :param backup_count: 保留的旧日志文件个数
        :param when: 按时间轮转，'S','M','H','D','midnight','W0'-'W6'，None 表示不启用
        :param interval: 时间轮转间隔
        """
        if MPLogger._queue is None:
            MPLogger._queue = multiprocessing.Queue(-1)

            handlers = []

            # 根据参数选择轮转类型
            if max_bytes is not None:
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
                )
            elif when is not None:
                file_handler = logging.handlers.TimedRotatingFileHandler(
                    log_file, when=when, interval=interval, backupCount=backup_count, encoding='utf-8'
                )
            else:
                file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')

            file_formatter = logging.Formatter(
                '%(asctime)s - %(processName)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)

            if console:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(file_formatter)
                handlers.append(console_handler)

            MPLogger._listener = logging.handlers.QueueListener(MPLogger._queue, *handlers)
            MPLogger._listener.start()

        return MPLogger.get_logger("root", level)

    @staticmethod
    def get_logger(name, level=logging.INFO):
        """获取多进程安全 logger"""
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(level)
            qh = logging.handlers.QueueHandler(MPLogger._queue)
            logger.addHandler(qh)
            logger.propagate = False
        return logger

    @staticmethod
    def stop():
        """停止日志监听器"""
        if MPLogger._listener:
            MPLogger._listener.stop()
            MPLogger._listener = None
        if MPLogger._queue:
            MPLogger._queue.close()
            MPLogger._queue = None


# ------------------- 使用示例 -------------------

if __name__ == "__main__":
    import time

    # 初始化日志系统，按文件大小轮转，每10KB一个文件，保留3个备份
    MPLogger.init_logger(log_file="test_mp_rotating.log", max_bytes=10*1024, backup_count=3)

    def worker(idx):
        logger = MPLogger.get_logger(f"worker-{idx}")
        for i in range(20):
            logger.info(f"Process {idx} logging message {i}")
            time.sleep(0.1)

    processes = [multiprocessing.Process(target=worker, args=(i,)) for i in range(3)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    MPLogger.stop()
