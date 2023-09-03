from abc import ABC, abstractmethod

class BaseValidation(ABC):
    def _checkValue(string, predicate):
        return predicate(string)
