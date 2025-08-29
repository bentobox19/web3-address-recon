# Abstract Base Classes (ABCs)
from abc import ABC, abstractmethod

class RPCClientBase(ABC):
    @abstractmethod
    def get_native_balance(self, network: str, address: str) -> str:
        ...

    @abstractmethod
    def is_eoa(self, network: str, address: str) -> bool | None:
        ...

    @abstractmethod
    def is_safe(self, network: str, address: str) -> bool | None:
        ...

    @abstractmethod
    def get_safe_owners(self, network: str, address: str) -> list[str] | None:
        ...

    @abstractmethod
    def get_safe_threshold(self, network: str, address: str) -> int | None:
        ...
