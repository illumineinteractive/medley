from abc import ABC, abstractmethod


class ServiceProviderInterface(ABC):

    @abstractmethod
    def register(self, container):
        pass
