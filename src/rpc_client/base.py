# Abstract Base Classes (ABCs)
from abc import ABC, abstractmethod

class RPCClientBase(ABC):
    @abstractmethod
    def get_native_balance(self, network: str, address: str) -> str:
        ...

    @abstractmethod
    def is_eoa(self, network: str, address: str) -> bool | None:
        ...
