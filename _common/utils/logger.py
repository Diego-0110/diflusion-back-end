from types import FunctionType
class Logger:
    def __init__(self, hierarchy: int, handle_event: FunctionType,
                 handle_success: FunctionType, handle_error: FunctionType):
        self.hierarchy = hierarchy
        self.handle_event = handle_event
        self.handle_success = handle_success
        self.handle_error = handle_error

    def on_event(self, msg: str):
        self.handle_event(msg)

    def on_success(self, msg: str):
        self.handle_success(msg)

    def on_error(self, msg: str):
        self.handle_error(msg)

class HierarchicLogger:
    def __init__(self, loggers: list[Logger]):
        self.loggers = loggers
    
    def on_event(self, hierarchy: int, msg: str):
        for logger in self.loggers:
            if logger.hierarchy <= hierarchy:
                logger.on_event(msg)

    def on_success(self, hierarchy: int, msg: str):
        for logger in self.loggers:
            if logger.hierarchy <= hierarchy:
                logger.on_success(msg)

    def on_error(self, hierarchy: int, msg: str):
        for logger in self.loggers:
            if logger.hierarchy <= hierarchy:
                logger.on_error(msg)

from loguru import logger
class Logger2:
    def __init__(self, outputs: list) -> None:
        logger.remove(0) # Remove default handler
        for output in outputs:
            logger.add(output)
    
    def add_output(self, output) -> int:
        return logger.add(output)
    
    def rm_output(self, output_id):
        logger.remove(output_id)

    def on_event(self, msg):
        logger.info(msg)

    def on_success(self, msg):
        logger.success(msg)

    def on_error(self, msg):
        logger.error(msg)