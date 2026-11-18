from inspect import signature
from typing import Callable

from overfunc.multifunc import MultiFunc
from overfunc.typing import P, R


class TypedFunc(MultiFunc[P, R]):
    def register(
        self,
        *validators: Callable[P, bool],
        priority: float | None = None,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def wrapper(func: Callable[P, R]) -> Callable[P, R]:
            def validator(*args: P.args, **kwargs: P.kwargs) -> bool:
                try:
                    signature(func).bind(*args, **kwargs)
                except (TypeError, ValueError):
                    return False
                return True

            self._register(func, validator, *validators, priority=priority)
            return func

        return wrapper
