from abc import ABC, abstractmethod

class AbstractModel(ABC):
    @abstractmethod
    def predict(self, features: list) -> float:
        """Must return a float between 0 and 1 representing fraud probability."""
        pass