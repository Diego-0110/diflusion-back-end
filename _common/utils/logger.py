from loguru import logger
class Logger:
    def __init__(self, outputs: list) -> None:
        logger.remove(0) # Remove default handler
        for output in outputs:
            logger.add(output)
    
    def add_output(self, output) -> int:
        return logger.add(output)
    
    def rm_output(self, output_id):
        logger.remove(output_id)

    def on_action_start(self, msg):
        logger.info(msg)

    def on_success(self, msg):
        logger.success(msg)

    def on_error(self, msg):
        logger.error(msg)
