from abc import ABCMeta, abstractmethod


class ServiceProviderInterface(metaclass=ABCMeta):

    @abstractmethod
    def register(self, container):
        pass
