"""Shared type variables, protocols, and exceptions used by overfunc."""

from typing import ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
RP = TypeVar("RP")
S = TypeVar("S", bound=object)

T_contra = TypeVar("T_contra", contravariant=True)
T1 = TypeVar("T1")
T2 = TypeVar("T2")


class MultiFuncError(BaseException):
    """Raised when no registered implementation accepts a call."""


class SupportsEqual(Protocol):
    """Protocol for values that support equality comparison."""

    def __eq__(self, value: object, /) -> bool:
        """Return whether this value equals another object."""
        ...


class SupportsComparison(SupportsEqual, Protocol[T_contra]):
    """Protocol for values supporting ordering comparisons with another type."""

    def __le__(self, other: T_contra, /) -> bool:
        """Return whether this value is less than or equal to another."""
        ...

    def __lt__(self, other: T_contra, /) -> bool:
        """Return whether this value is less than another."""
        ...

    def __ge__(self, other: T_contra, /) -> bool:
        """Return whether this value is greater than or equal to another."""
        ...

    def __gt__(self, other: T_contra, /) -> bool:
        """Return whether this value is greater than another."""
        ...


V = TypeVar("V", bound=SupportsComparison)
