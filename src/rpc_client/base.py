from abc import ABC, abstractmethod

class RPCClientBase(ABC):
    @abstractmethod
    async def get_native_balance(self, network: str, address: str) -> str:
        ...

    @abstractmethod
    async def is_eoa(self, network: str, address: str) -> bool | None:
        ...

    @abstractmethod
    async def is_safe(self, network: str, address: str) -> bool | None:
        ...

    @abstractmethod
    async def get_safe_threshold(self, network: str, address: str) -> int | None:
        ...

    @abstractmethod
    async def get_safe_nonce(self, network: str, address: str) -> int | None:
        ...

    @abstractmethod
    async def get_safe_owners(self, network: str, address: str) -> list[str] | None:
        ...

