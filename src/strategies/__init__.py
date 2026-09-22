from .base import Strategy
from .ma_cross import MACross
from .momentum import Momentum

REGISTRY = {
    "ma_cross": MACross,
    "momentum": Momentum,
}


def get_strategy(name: str, **kwargs) -> Strategy:
    if name not in REGISTRY:
        raise ValueError(f"Unknown strategy: {name}. Available: {list(REGISTRY)}")
    return REGISTRY[name](**kwargs)
