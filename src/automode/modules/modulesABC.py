from abc import ABCMeta, abstractmethod


class ABCBehavior:
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def get_by_name(name):
        pass

    @staticmethod
    @abstractmethod
    def get_by_id(b_id):
        pass

    @staticmethod
    @abstractmethod
    def get_parameters_for_behavior(name):
        pass

    @staticmethod
    @abstractmethod
    def random_parameter(name):
        pass

    @property
    @abstractmethod
    def int(self):
        pass


class ABCCondition:
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def get_by_name(name):
        pass

    @staticmethod
    @abstractmethod
    def get_by_id(c_id):
        pass

    @staticmethod
    @abstractmethod
    def get_parameters_for_condition(name):
        pass

    @staticmethod
    @abstractmethod
    def random_parameter(name):
        pass

    @property
    @abstractmethod
    def int(self):
        pass
