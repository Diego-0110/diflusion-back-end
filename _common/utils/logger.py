from loguru import logger
class Logger:
    def __init__(self, outputs: list) -> None:
        for output in outputs:
            logger.add(output)

    def on_action_start(self, msg):
        logger.info(msg)

    def on_success(self, msg):
        logger.success(msg)

    def on_error(self, msg):
        logger.error(msg)
