from enum import Enum
from itertools import product
from typing import Any, Type
import os

import pandas as pd

_Unset = None


module_dir = os.path.dirname(os.path.abspath(__file__))


class Number(Enum):
    SG = "singular"
    PL = "plural"


class Conjugation(Enum):
    NOM = "nominative"
    ACC = "accusative"
    DAT = "dative"
    GEN = "genitive"
    VOC = "vocative"
    LOC = "locative"
    INS = "instrumental"


class Gender(Enum):
    M = "male"
    F = "female"
    N = "neutral"


class Person(Enum):
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"

    @staticmethod
    def from_number(number: int) -> "Person":
        if 1 <= number <= 3:
            return [Person.FIRST, Person.SECOND, Person.THIRD][number - 1]
        raise ValueError(f"Person must be between 1 and 3 inclusive. You provided: {number}")

    @staticmethod
    def to_number(person: "Person") -> int:
        return [Person.FIRST, Person.SECOND, Person.THIRD].index(person) + 1


class Tense(Enum):
    PRES = "present"
    PAST = "past"
    # FUTU = "futu"


class Mood(Enum):
    IND = "indicative"  # orzekający
    PRE = "conditional"  # przypuszczający


class WordType(Enum):
    NOUN = "noun"
    VERB = "verb"


class Word:
    def __init__(
            self,
            word: str,
            number: Number | None,
            conjugation: Conjugation | None,
            gender: Gender | None,
            person: Person | None,
            tense: Tense | None,
            mood: Mood | None,
            type: WordType
    ):
        self.word: str = word
        self.number: Number | None = number
        self.conjugation: Conjugation | None = conjugation
        self.gender: Gender | None = gender
        self.person: Person | None = person
        self.tense: Tense | None = tense
        self.mood: Mood | None = mood
        self.type: WordType = type

    def __str__(self):
        return f"{self.word}"

    def __repr__(self):
        return f"{self.word}"  # , {self.type}, {self.number}, {self.conjugation}, {self.gender})"

    @classmethod
    def from_str(cls, word: str, column_name: str, type: WordType):
        number = None
        conjugation = None
        gender = None
        person = None
        tense = None
        mood = None
        if type == WordType.NOUN:
            number, conjugation, gender = column_name.split("_")
            number, conjugation, gender = Number[number], Conjugation[conjugation], Gender[gender]
        elif type == WordType.VERB:
            number, conjugation, gender, person, tense, mood = column_name.split("_")
            number, conjugation, gender, person, tense, mood = (Number[number],
                                                                Conjugation[conjugation],
                                                                Gender[gender] if gender != "-" else None,
                                                                Person.from_number(int(person)),
                                                                Tense[tense] if tense != "-" else None,
                                                                Mood[mood])
        else:
            raise ValueError(f"Unrecognized type: {type}. Use 'WordType.NOUN' or 'WordType.VERB'.")
        return cls(word, number, conjugation, gender, person, tense, mood, type)


def get_possibilities(variable: Any, enum: Type[Enum]):
    if isinstance(variable, list):
        return variable
    elif variable is None:
        return list(enum)
    else:
        return [variable]


class Nouns:
    nouns: pd.DataFrame

    @classmethod
    def from_file(cls):
        instance = cls()
        instance.nouns = pd.read_csv(f"{module_dir}/nouns.csv")
        return instance

    def get_one(self, word: str) -> Word | None:
        columns_with_word = next(iter(self.nouns.columns[(self.nouns == word).any()].tolist()),
                                 None)  # TODO it can match multiple columns
        return Word.from_str(word, columns_with_word, WordType.NOUN) if columns_with_word is not None else None

    def get(
            self,
            *,
            word: str | _Unset = _Unset,
            number: Number | list[Number] | _Unset = _Unset,
            conjugation: Conjugation | _Unset = _Unset,
            gender: Gender | _Unset = _Unset
    ) -> list[Word] | None:
        number = get_possibilities(number, Number)
        conjugation = get_possibilities(conjugation, Conjugation)
        gender = get_possibilities(gender, Gender)

        columns: list[str] = list()
        for n, c, g in product(number, conjugation, gender):
            columns.append(f"{n.name}_{c.name}_{g.name}")

        if word is not None:  # used in suggesting fixes
            # FIXME might not work long term, cause matching multiple rows
            rows_with_word = self.nouns[(self.nouns == word).any(axis=1)]
            return [Word.from_str(v, k, WordType.NOUN) for k, col in rows_with_word[columns].items() for v in col]

        return [Word.from_str(v, k, WordType.NOUN) for k, col in self.nouns[columns].items() for v in col]


class Verbs:
    verbs: pd.DataFrame

    @classmethod
    def from_file(cls):
        # TODO data format is wrong, it's always genitive
        instance = cls()
        instance.verbs = pd.read_csv(f"{module_dir}/verbs.csv")
        instance.verbs.index = instance.verbs["VERB"]
        return instance

    def get_one(self, word: str) -> Word | None:
        columns_with_word = next(iter(self.verbs.columns[(self.verbs == word).any()].tolist()),
                                 None)  # TODO it can match multiple columns
        return Word.from_str(word, columns_with_word, WordType.VERB) if columns_with_word is not None else None

    def get(
            self,
            *,
            word: str | _Unset = _Unset,
            base: str | list[str] | _Unset = _Unset,
            number: Number | list[Number] | _Unset = _Unset,
            conjugation: Conjugation | _Unset = _Unset,
            gender: Gender | _Unset = _Unset,
            person: Person | list[Person] | _Unset = _Unset,
            tense: Tense | list[Tense] | _Unset = _Unset,
            mood: Mood | list[Mood] | _Unset = _Unset
    ) -> list[Word] | None:
        number = get_possibilities(number, Number)
        conjugation = get_possibilities(conjugation, Conjugation)
        gender = get_possibilities(gender, Gender) + ["-"]
        person = get_possibilities(person, Person)
        tense = get_possibilities(tense, Tense) + ["-"]
        mood = get_possibilities(mood, Mood)

        columns: set[str] = set()
        for n, c, g, p, t, m in product(number, conjugation, gender, person, tense, mood):
            columns.add(
                f"{n.name}_{c.name}_{g.name if not isinstance(g, str) else g}_{Person.to_number(p)}_{t.name if not isinstance(t, str) else t}_{m.name}")

        if word is not None:  # used in suggesting fixes
            # FIXME might not work long term, cause matching multiple rows
            rows_with_word = self.verbs[(self.verbs == word).any(axis=1)]
            return [Word.from_str(v, k, WordType.VERB) for k, col in rows_with_word[columns].items() for v in col]

        columns.intersection_update(self.verbs.columns)

        if base is not _Unset:
            return [Word.from_str(v, k, WordType.VERB) for k, v in self.verbs.loc[base][list(columns)].items()]
        else:
            return [Word.from_str(v, k, WordType.VERB) for k, col in self.verbs[list(columns)].items() for v in col]

# nouns = Nouns.from_file()
#
# print(nouns.get(conjugation=Conjugation.NOM, gender=Gender.M))

# verbs = Verbs.from_file()
#
# print(verbs.get(word="słucham"))
