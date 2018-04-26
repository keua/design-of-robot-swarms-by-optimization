from automode.controller.AutoMoDeControllerABC import AutoMoDeControllerABC


class BT(AutoMoDeControllerABC):

    def __init__(self):
        super().__init__()

    def draw(self):
        pass

    @staticmethod
    def parse_from_commandline_args(cmd_args):
        pass

    def convert_to_commandline_args(self):
        pass

    def evaluate_single_run(self, seed):
        pass

    def mutate(self):
        pass
