from app.view import View
from app.model import Model
from app.controller import Controller
if __name__ == '__main__':
    view = View()
    model = Model(view)
    ctrl = Controller(model, view)
    ctrl.run()