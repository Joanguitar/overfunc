"""Dispatch function implementations by version ranges and tags."""

from typing import Callable, Generic, Self

from overfunc.comparefunc import CompareFunc, CompareFuncRegister, CompareDecorator
from overfunc.typing import P, R, V, SupportsEqual
from overfunc.util import compose, get_self, attr_getter


class VersionFuncRegister(CompareFuncRegister[P, R], Generic[P, R, V]):
    """Add version-range and tag constraints to a function registration."""

    def for_version(self, initial: V | None = None, final: V | None = None) -> Self:
        """Restrict matching to the half-open interval [initial, final)."""
        new = self
        if initial is not None:
            new = new.ge(version=initial)
        if final is not None:
            new = new.lt(version=final)
        return new

    def for_tag(self, **tags):
        """Add equality constraints for the supplied tag values."""
        return self.eq(**tags)


class VersionDecorator(CompareDecorator[P], Generic[P, V]):
    """Configure version and tag getters for a version dispatcher."""

    def __init__(
        self,
        version: Callable[P, V] | None = None,
        **getters: Callable[P, SupportsEqual],
    ) -> None:
        """Initialize version and tag getters."""
        if version is None:
            super().__init__(**getters)  # type: ignore
        else:
            super().__init__(version=version, **getters)  # type: ignore

    def with_version_getter(self, getter: Callable[P, V]):
        """Return a clone using the supplied version getter."""
        return self.with_getter(version=getter)

    def with_version_from_attr(self, attr_name: str):
        """Configure the version getter to read the named argument attribute."""
        return self.with_version_getter(compose(get_self, attr_getter(attr_name)))

    def with_tag_getter(self, **getters: Callable[P, SupportsEqual]):
        """Add getters used to extract tag values."""
        return self.with_getter(**getters)  # type: ignore

    def with_tag_from_attr(self, *tag: str):
        """Configure tag getters to read the named argument attributes."""
        return self.with_attr(*tag)

    def __call__(self, func: Callable[P, R]) -> VersionFunc[P, R, V]:
        """Wrap a function in a version dispatcher using the configured getters."""
        return VersionFunc(func, **self._getters)  # type: ignore


class VersionFunc(CompareFunc[P, R], VersionDecorator[P, V], Generic[P, R, V]):
    """Dispatch implementations by version intervals and optional tag values."""

    def __init__(
        self,
        func: Callable[P, R],
        version: Callable[P, V] | None = None,
        **getters: Callable[P, SupportsEqual],
    ) -> None:
        """Initialize a dispatcher with a version getter and optional tag getters."""
        if version is None:
            super().__init__(func, **getters)  # type: ignore
        else:
            super().__init__(func, version=version, **getters)  # type: ignore

    def register(self, *validators: Callable[P, bool], priority: float | None = None):
        """Create a builder for registering version- and tag-guarded implementations."""
        return VersionFuncRegister(self, *validators, priority=priority)
