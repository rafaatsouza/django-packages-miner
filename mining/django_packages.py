from abc import ABC, abstractmethod

class DjangoPackagesProvider(ABC):
    
    @abstractmethod
    def get_packages(self, next=None):
        pass

    @abstractmethod
    def get_package_by_id(self, id):
        pass
