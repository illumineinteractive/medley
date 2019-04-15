from abc import ABCMeta, abstractmethod
import six


@six.add_metaclass(ABCMeta)
class ServiceProviderInterface(object):

    @abstractmethod
    def register(self, container):
        pass
