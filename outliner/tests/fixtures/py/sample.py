#!/usr/bin/env python3
"""Module docstring."""

__version__ = "1.0.0"
__all__ = [
    "Animal",
    "make_animal",
]

MAX_SIZE: int = 100


# Represents any animal
class Animal:
    """Base animal class."""

    kind = "unknown"

    def __init__(self, name: str, kind: str = "unknown") -> None:
        self.name = name
        self.kind = kind

    def speak(self) -> str:
        return f"{self.name} says hello"

    @property
    def display_name(self) -> str:
        return self.name.title()

    @staticmethod
    def species() -> str:
        return "Animalia"

    @classmethod
    def from_dict(cls, data: dict) -> "Animal":
        return cls(data["name"], data.get("kind", "unknown"))


class Dog(Animal):
    """A dog."""

    def speak(self) -> str:
        return f"{self.name} says woof"

    def fetch(
        self,
        item: str,
        distance: float = 1.0,
    ) -> bool:
        return True


def make_animal(
    name: str,
    kind: str = "unknown",
) -> "Animal":
    """Create an animal."""
    return Animal(name, kind)


async def fetch_animal(url: str) -> dict:
    """Fetch animal data."""
    pass


def complex_factory(
    name: str,
    size: int = 0,
    verbose: bool = False,
) -> "Animal":
    return Animal(name)


def _helper(x: int) -> int:
    return x * 2
