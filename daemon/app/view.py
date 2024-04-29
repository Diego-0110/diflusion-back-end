from recipes.view import ShareView
import consts.config as config
import os

class View(ShareView):
    def __init__(self):
        super().__init__(os.path.join(config.LOG_PATH, 'logging.log'),
                         config.HOST, config.LOG_PORT)