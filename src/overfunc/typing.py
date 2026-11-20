from typing import ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
RP = TypeVar("RP")
S = TypeVar("S", bound=object)

T_contra = TypeVar("T_contra", contravariant=True)
T1 = TypeVar("T1")
T2 = TypeVar("T2")


class MultiFuncError(BaseException): ...


class SupportsEqual(Protocol):
    def __eq__(self, value: object, /) -> bool: ...


class SupportsComparison(SupportsEqual, Protocol[T_contra]):
    def __le__(self, other: T_contra, /) -> bool: ...
    def __lt__(self, other: T_contra, /) -> bool: ...
    def __ge__(self, other: T_contra, /) -> bool: ...
    def __gt__(self, other: T_contra, /) -> bool: ...


V = TypeVar("V", bound=SupportsComparison)
