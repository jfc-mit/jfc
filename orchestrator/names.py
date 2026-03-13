"""Session name pool — random human first names, no repeats within a run."""

import random

NAMES = [
    "Ada", "Alfred", "Amara", "Boris", "Celeste", "Claude", "Dagmar",
    "Edmund", "Eloise", "Felix", "Gertrude", "Gerald", "Hana", "Ingrid",
    "Jasper", "Kenji", "Lena", "Magnus", "Margaret", "Nadia", "Oscar",
    "Petra", "Quentin", "Rosa", "Sven", "Tomoko", "Ulrich", "Vera",
    "Wolfgang", "Xena", "Yuki", "Zelda", "Agnes", "Basil", "Cosima",
    "Dmitri", "Estelle", "Fabian", "Greta", "Hugo", "Isolde", "Jules",
    "Katya", "Leopold", "Mireille", "Nikolai", "Odette", "Pavel", "Renata",
    "Sigrid", "Tomas", "Ursula", "Viktor", "Wanda", "Yvette", "Zoran",
    "Anselm", "Brigitte", "Casimir", "Dorothea", "Emeric", "Fiona",
    "Gunnar", "Hedwig", "Ivan", "Johanna", "Klaus", "Ludmila", "Marcel",
    "Nora", "Otto", "Philippa", "Rainer", "Sabine", "Theo", "Valentina",
]


class NamePool:
    def __init__(self, seed: int | None = None):
        self._remaining = list(NAMES)
        rng = random.Random(seed)
        rng.shuffle(self._remaining)
        self._used: list[str] = []

    def pick(self) -> str:
        if not self._remaining:
            raise RuntimeError("Name pool exhausted — too many sessions")
        name = self._remaining.pop()
        self._used.append(name)
        return name

    @property
    def used(self) -> list[str]:
        return list(self._used)
