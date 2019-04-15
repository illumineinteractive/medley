from abc import ABCMeta, abstractmethod


class ServiceProviderInterface(object, metaclass=ABCMeta):

    @abstractmethod
    def register(self, container):
        pass
