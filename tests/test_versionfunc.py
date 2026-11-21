from __future__ import annotations

import pytest

from overfunc.typing import MultiFuncError
from overfunc.version import __version__
from overfunc.versionfunc import (
    VersionDecorator,
    VersionFunc,
)


def test_dispatches_by_version_interval_and_tag() -> None:
    def version(value: tuple[str, str]) -> tuple[str, str]:
        return value

    @VersionDecorator(
        version=version,
        channel=lambda value: "stable",
    )
    def convert(value: tuple[str, str]) -> str: ...

    @convert.register().for_version(initial=("1", "0"), final=("2", "0"))
    def v1(value: tuple[str, str]) -> str:
        return "v1"

    @convert.register().for_tag(channel="stable")
    def stable(value: tuple[str, str]) -> str:
        return "stable"

    assert convert(("1", "5")) == "v1"
    assert __version__ == "0.0.1"


def test_version_decorator_configures_getters() -> None:
    class Release:
        def __init__(self, version: int, channel: str) -> None:
            self.version = version
            self.channel = channel

    @VersionDecorator().with_version_from_attr("version").with_tag_from_attr("channel")
    def dispatcher(release: Release) -> str: ...

    @dispatcher.register().for_version(initial=2)
    def current(release: Release) -> str:
        return "current"

    @dispatcher.register().for_tag(channel="beta")
    def beta(release: Release) -> str:
        return "beta"

    assert isinstance(dispatcher, VersionFunc)
    assert dispatcher(Release(2, "stable")) == "current"
    assert dispatcher(Release(1, "beta")) == "beta"
    with pytest.raises(MultiFuncError):
        assert dispatcher(Release(0, "?"))


def test_version_class_decorator_configures_getters() -> None:
    class Release:
        def __init__(self, version: int, channel: str) -> None:
            self.version = version
            self.channel = channel

        @(
            VersionDecorator()
            .with_version_from_attr("version")
            .with_tag_from_attr("channel")
        )
        def dispatcher(release: Release) -> str: ...

        @dispatcher.register().for_version(initial=2)
        def current(release: Release) -> str:
            return "current"

        @dispatcher.register().for_tag(channel="beta")
        def beta(release: Release) -> str:
            return "beta"

    assert isinstance(Release.dispatcher, VersionFunc)
    assert Release(2, "stable").dispatcher() == "current"
    assert Release(1, "beta").dispatcher() == "beta"
    with pytest.raises(MultiFuncError):
        assert Release(0, "?").dispatcher()


def test_version_tag_getters_can_be_added_directly() -> None:
    @VersionDecorator().with_tag_getter(channel=lambda release: "stable")
    def choose(release: object) -> str: ...

    @choose.register().for_tag(channel="stable")
    def stable(release: object) -> str:
        return "stable"

    assert choose(object()) == "stable"


def test_version_dispatch_raises_when_no_rule_matches() -> None:
    @VersionDecorator(version=lambda value: value)
    def dispatcher(value: int) -> str: ...

    @dispatcher.register().for_version(initial=2)
    def current(value: int) -> str:
        return "current"

    assert dispatcher(3) == "current"
    with pytest.raises(MultiFuncError):
        dispatcher(1)


def test_version_class_decorator_segments():
    class Number:
        def __init__(self, value: int) -> None:
            self.value = value

        @VersionDecorator().with_version_from_attr("value")
        def what(self) -> str: ...

        @what.register().for_version(final=0)
        def _(self) -> str:
            return "Negative"

        @what.register().for_version(initial=0, final=10)
        def _(self) -> str:
            return "One digit"

        @what.register().for_version(initial=10)
        def _(self) -> str:
            return "Large"

    assert Number(-20).what() == "Negative"
    assert Number(2).what() == "One digit"
    assert Number(20).what() == "Large"
