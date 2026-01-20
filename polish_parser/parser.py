from itertools import chain

from .speech_parts import Nouns, Verbs, Word, Conjugation, WordType, Person, Adjectives, Pronouns
import Levenshtein

class ResultMultiple:
    row: int
    position: int
    length: int
    expected: list[Word]
    reason: str

    def __init__(self, row: int, position: int, length: int, expected: list[Word], reason: str):
        self.row = row
        self.position = position
        self.length = length
        self.expected = expected
        self.reason = reason

    def __str__(self):
        return (f"Row: {self.row}\n"
                f"Position: {self.position}\n"
                f"Length: {self.length}\n"
                f"Expecting: {self.expected}\n"
                f"Reason: {self.reason}")

    def __repr__(self):
        return self.__str__()


class Result:
    position: int
    length: int
    expected: list[Word]
    reason: str

    def __init__(self, position: int, length: int, expected: list[Word], reason: str):
        self.position = position
        self.length = length
        self.expected = expected
        self.reason = reason

    def __str__(self):
        return (f"Position: {self.position}\n"
                f"Length: {self.length}\n"
                f"Expecting: {self.expected}\n"
                f"Reason: {self.reason}")

    def __repr__(self):
        return self.__str__()


class Parser:
    nouns = Nouns.from_file()
    verbs = Verbs.from_file()
    pronouns = Pronouns.from_file()
    adjectives = Adjectives.from_file()
    index: int = 0
    position: int = 0
    categorized_words: list[Word | None] = list()
    words: list[str] = list()

    previous_genders: list = list()
    previous_numbers: list = list()
    previous_conjugations: list = list()

    def parse_subject(self) -> Result | None:
        self.previous_genders = list()
        self.previous_numbers = list()
        self.previous_conjugations = list()
        # first word
        category = self.categorized_words[self.index]
        word = self.words[self.index]
        length = len(word)
        possible = None
        if category is None:  # suggest new words
            return Result(self.position, length,
                          [w for w in chain(self.nouns.get(conjugation=Conjugation.NOM),
                                            self.adjectives.get(conjugation=Conjugation.NOM),
                                            self.pronouns.get(conjugation=Conjugation.NOM)) if w.word.startswith(word)],
                          "Unrecognized word")
        elif category.type == WordType.VERB:
            return Result(self.position, length, [], "First word should be a noun, adjective or pronoun not a verb.")
        elif category.type == WordType.NOUN:
            possible = self.nouns.get_all(category.word)
            if Conjugation.NOM not in [p.conjugation for p in possible]:
                return Result(self.position, length,
                              self.nouns.get(word=category.word, conjugation=Conjugation.NOM, gender=category.gender,
                                             number=category.number),
                              f"Subject should be in nominative form. But is in {category.conjugation.value}.")
        elif category.type == WordType.ADJECTIVE:
            possible = self.adjectives.get_all(category.word)
            if Conjugation.NOM not in [p.conjugation for p in possible]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=Conjugation.NOM, gender=category.gender,
                                                  number=category.number),
                              f"Subject's adjective should be in nominative form. But is in {category.conjugation.value}.")
        elif category.type == WordType.PRONOUN:
            possible = self.pronouns.get_all(category.word)
            if Conjugation.NOM not in [p.conjugation for p in possible]:
                return Result(self.position, length,
                              self.pronouns.get(word=category.word, conjugation=Conjugation.NOM, gender=category.gender,
                                                number=category.number),
                              f"Subject's pronoun should be in nominative form. But is in {category.conjugation.value}.")
        else:
            raise ValueError("Something unexpected happened.")

        # second word
        self.index += 1
        self.position += length + 1
        self.previous_genders = list({p.gender for p in possible})
        self.previous_numbers = list({p.number for p in possible})
        self.previous_conjugations = list({p.conjugation for p in possible})
        if self.index == len(self.categorized_words) or category.type == WordType.NOUN:
            return None
        previous = category
        possible = None
        category = self.categorized_words[self.index]
        word = self.words[self.index]
        length = len(word)

        if category is None:  # suggest new words
            return Result(self.position, length,
                          [w for w in chain(self.nouns.get(conjugation=Conjugation.NOM, gender=self.previous_genders, number=self.previous_numbers),
                                            self.adjectives.get(conjugation=Conjugation.NOM, gender=self.previous_genders, number=self.previous_numbers)) if w.word.startswith(word)],
                          "Unrecognized word")
        elif category.type == WordType.VERB:
            return Result(self.position, length, [], "Second word should be a noun or adjective not a verb.")
        elif category.type == WordType.NOUN:
            possible = self.nouns.get_all(category.word)
            if Conjugation.NOM not in [p.conjugation for p in possible]:
                return Result(self.position, length,
                              self.nouns.get(word=category.word, conjugation=Conjugation.NOM, gender=self.previous_genders,
                                             number=self.previous_numbers),
                              f"Subject should be in nominative form. But is in {category.conjugation.value}.")
            elif not [p.gender for p in possible if p.gender not in self.previous_genders]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=Conjugation.NOM,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Subject should match the gender of the previous word: {[p.value for p in self.previous_genders]}. But is in {category.gender.value}.")
            elif not [p.number for p in possible if p.number not in self.previous_numbers]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=Conjugation.NOM,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Subject should match the number of the previous word: {[p.value for p in self.previous_numbers]}. But is in {category.number.value}.")
        elif category.type == WordType.ADJECTIVE:
            possible = self.adjectives.get_all(category.word)
            if previous.type == WordType.ADJECTIVE:
                return Result(self.position, length,[], "Two adjectives are not allowed.")
            elif Conjugation.NOM not in [p.conjugation for p in possible]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=Conjugation.NOM, gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Subject's adjective should be in nominative form. But is in {category.conjugation.value}.")
            elif not [p.gender for p in possible if p.gender not in self.previous_genders]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=Conjugation.NOM,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Subject's adjective should match the gender of the previous word: {[p.value for p in self.previous_genders]}. But is in {category.gender.value}.")
            elif not [p.number for p in possible if p.number not in self.previous_numbers]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=Conjugation.NOM,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Subject's adjective should match the number of the previous word: {[p.value for p in self.previous_numbers]}. But is in {category.number.value}.")
        elif category.type == WordType.PRONOUN:
            return Result(self.position, length, [], f"Subject's pronoun should always be first.")
        else:
            raise ValueError("Something unexpected happened.")

        # third word
        self.index += 1
        self.position += length + 1
        self.previous_genders = list({p.gender for p in possible}.intersection(self.previous_genders))
        self.previous_numbers = list({p.number for p in possible}.intersection(self.previous_numbers))
        self.previous_conjugations = list({p.conjugation for p in possible}.intersection(self.previous_conjugations))
        if self.index == len(self.categorized_words) or category.type == WordType.NOUN:
            return None
        previous = category
        possible = None
        category = self.categorized_words[self.index]
        word = self.words[self.index]
        length = len(word)

        if category is None:  # suggest new words
            return Result(self.position, length,
                          [w for w in chain(self.nouns.get(conjugation=Conjugation.NOM, gender=self.previous_genders, number=self.previous_numbers)) if
                           w.word.startswith(word)],
                          "Unrecognized word")
        elif category.type == WordType.VERB:
            return Result(self.position, length, [], "Third word should be a noun not a verb.")
        elif category.type == WordType.NOUN:
            possible = self.nouns.get_all(category.word)
            if Conjugation.NOM not in [p.conjugation for p in possible]:
                return Result(self.position, length,
                              self.nouns.get(word=category.word, conjugation=Conjugation.NOM, gender=self.previous_genders,
                                             number=self.previous_numbers),
                              f"Subject should be in nominative form. But is in {category.conjugation.value}.")
            elif not [p.gender for p in possible if p.gender not in self.previous_genders]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=Conjugation.NOM,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Subject should match the gender of the previous word: {[p.value for p in self.previous_genders]}. But is in {category.gender.value}.")
            elif not [p.number for p in possible if p.number not in self.previous_numbers]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=Conjugation.NOM,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Subject should match the number of the previous word: {[p.value for p in self.previous_numbers]}. But is in {category.number.value}.")
        elif category.type == WordType.ADJECTIVE:
            return Result(self.position, length, [], "Two adjectives are not allowed.")
        elif category.type == WordType.PRONOUN:
            return Result(self.position, length, [], f"Subject's pronoun should always be first.")
        else:
            raise ValueError("Something unexpected happened.")

        self.index += 1
        self.position += length + 1

        return None

    def parse_verb(self):
        # one verb only
        category = self.categorized_words[self.index]
        word = self.words[self.index]
        length = len(word)
        if category is None:  # suggest new words
            return Result(self.position, length,
                          [w for w in self.verbs.get(gender=self.previous_genders, number=self.previous_numbers, person=Person.THIRD) if
                           Levenshtein.distance(w.word, word) <= 2 or w.word.startswith(word)],
                          "Unrecognized word")
        elif category.type == WordType.VERB:
            if category.number is None:  # it's just the base
                return Result(self.position, length,
                              self.verbs.get(base=category.word, gender=self.previous_genders, number=self.previous_numbers,
                                             person=Person.THIRD),
                              f"Verb should match the noun number: {[p.value for p in self.previous_numbers]}. But is the verb is not conjugated.")
            if category.number not in self.previous_numbers:
                return Result(self.position, length,
                              self.verbs.get(word=category.word, gender=self.previous_genders, number=self.previous_numbers,
                                             person=Person.THIRD),
                              f"Verb should match the noun number: {[p.value for p in self.previous_numbers]}. But is {category.number.value}.")
            if category.gender not in self.previous_genders and category.gender is not None:
                return Result(self.position, length,
                              self.verbs.get(word=category.word, gender=self.previous_genders, number=self.previous_numbers,
                                             person=Person.THIRD),
                              f"Verb gender should match the noun gender: {[p.value for p in self.previous_genders]}. But is {category.gender.value}.")
            if category.person != Person.THIRD:
                return Result(self.position, length,
                              self.verbs.get(word=category.word, gender=self.previous_genders, number=self.previous_numbers,
                                             person=Person.THIRD),
                              f"Verb should be in 3rd person. But is {category.person.value}.")
        elif category.type == WordType.NOUN:
            return Result(self.position, length, [], "Subject should be followed be a verb not a noun.")
        elif category.type == WordType.ADJECTIVE:
            return Result(self.position, length, [], "Subject should be followed be a verb not an adjective.")
        elif category.type == WordType.PRONOUN:
            return Result(self.position, length, [], "Subject should be followed be a verb not a pronoun.")
        else:
            raise ValueError("Something unexpected happened.")

        self.index += 1
        self.position += length + 1

        return None

    def parse_object(self):
        self.previous_genders = list()
        self.previous_numbers = list()
        self.previous_conjugations = list()
        # first word
        verb = self.categorized_words[self.index - 1]
        category = self.categorized_words[self.index]
        word = self.words[self.index]
        length = len(word)
        possible = None
        if category is None:  # suggest new words
            return Result(self.position, length,
                          [w for w in chain(self.nouns.get(conjugation=verb.conjugation),
                                            self.adjectives.get(conjugation=verb.conjugation),
                                            self.pronouns.get(conjugation=verb.conjugation)) if w.word.startswith(word)],
                          "Unrecognized word")
        elif category.type == WordType.VERB:
            return Result(self.position, length, [], "Verb should be followed by a noun, adjective or pronoun not a verb.")
        elif category.type == WordType.NOUN:
            possible = self.nouns.get_all(category.word)
            if verb.conjugation not in [p.conjugation for p in possible]:
                return Result(self.position, length,
                              self.nouns.get(word=category.word, conjugation=verb.conjugation, gender=category.gender,
                                             number=category.number),
                              f"Object should be in {verb.conjugation.value} form. But is in {category.conjugation.value}.")
        elif category.type == WordType.ADJECTIVE:
            possible = self.adjectives.get_all(category.word)
            if verb.conjugation not in [p.conjugation for p in possible]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=verb.conjugation,
                                                  gender=category.gender,
                                                  number=category.number),
                              f"Object's adjective should be in {verb.conjugation.value} form. But is in {category.conjugation.value}.")
        elif category.type == WordType.PRONOUN:
            possible = self.adjectives.get_all(category.word)
            if verb.conjugation not in [p.conjugation for p in possible]:
                return Result(self.position, length,
                              self.pronouns.get(word=category.word, conjugation=verb.conjugation, gender=category.gender,
                                                number=category.number),
                              f"Object's pronoun should be in {verb.conjugation.value} form. But is in {category.conjugation.value}.")
        else:
            raise ValueError("Something unexpected happened.")

        # second word
        self.index += 1
        self.position += length + 1
        self.previous_genders = list({p.gender for p in possible})
        self.previous_numbers = list({p.number for p in possible})
        self.previous_conjugations = list({p.conjugation for p in possible})
        if self.index == len(self.categorized_words) or category.type == WordType.NOUN:
            return None
        previous = category
        possible = None
        category = self.categorized_words[self.index]
        word = self.words[self.index]
        length = len(word)

        if category is None:  # suggest new words
            return Result(self.position, length,
                          [w for w in chain(self.nouns.get(conjugation=verb.conjugation, gender=self.previous_genders, number=self.previous_numbers),
                                            self.adjectives.get(conjugation=verb.conjugation, gender=self.previous_genders, number=self.previous_numbers)) if
                           w.word.startswith(word)],
                          "Unrecognized word")
        elif category.type == WordType.VERB:
            return Result(self.position, length, [], "There is only one verb allowed per sentence.")
        elif category.type == WordType.NOUN:
            possible = self.nouns.get_all(category.word)
            if verb.conjugation not in [p.conjugation for p in possible]:
                return Result(self.position, length,
                              self.nouns.get(word=category.word, conjugation=verb.conjugation, gender=self.previous_genders,
                                             number=self.previous_numbers),
                              f"Object should be in {verb.conjugation} form. But is in {category.conjugation.value}.")
            elif not [p.gender for p in possible if p.gender not in self.previous_genders]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=verb.conjugation,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Object should match the gender of the previous word: {[p.value for p in self.previous_genders]}. But is in {category.gender.value}.")
            elif not [p.number for p in possible if p.number not in self.previous_numbers]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=verb.conjugation,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Object should match the number of the previous word: {[p.value for p in self.previous_numbers]}. But is in {category.number.value}.")
        elif category.type == WordType.ADJECTIVE:
            possible = self.adjectives.get_all(category.word)
            if previous.type == WordType.ADJECTIVE:
                return Result(self.position, length, [], "Two adjectives are not allowed.")
            elif verb.conjugation not in [p.conjugation for p in possible]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=verb.conjugation,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Object's adjective should be in nominative form. But is in {category.conjugation.value}.")
            elif not [p.gender for p in possible if p.gender not in self.previous_genders]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=verb.conjugation,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Object's adjective should match the gender of the previous word: {[p.value for p in self.previous_genders]}. But is in {category.gender.value}.")
            elif not [p.number for p in possible if p.number not in self.previous_numbers]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=verb.conjugation,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Object's adjective should match the number of the previous word: {[p.value for p in self.previous_numbers]}. But is in {category.number.value}.")
            possible = self.adjectives.get_all(category.word)
        elif category.type == WordType.PRONOUN:
            return Result(self.position, length, [], f"Object's pronoun should always be first after the verb.")
        else:
            raise ValueError("Something unexpected happened.")

        # third word
        self.index += 1
        self.position += length + 1
        self.previous_genders = list({p.gender for p in possible}.intersection(self.previous_genders))
        self.previous_numbers = list({p.number for p in possible}.intersection(self.previous_numbers))
        self.previous_conjugations = list({p.conjugation for p in possible}.intersection(self.previous_conjugations))
        if self.index == len(self.categorized_words) or category.type == WordType.NOUN:
            return None
        previous = category
        possible = None
        category = self.categorized_words[self.index]
        word = self.words[self.index]
        length = len(word)

        if category is None:  # suggest new words
            return Result(self.position, length,
                          [w for w in chain(self.nouns.get(conjugation=verb.conjugation, gender=self.previous_genders, number=self.previous_numbers)) if
                           w.word.startswith(word)],
                          "Unrecognized word")
        elif category.type == WordType.VERB:
            return Result(self.position, length, [], "There is only one verb allowed per sentence.")
        elif category.type == WordType.NOUN:
            possible = self.nouns.get_all(category.word)
            if verb.conjugation not in [p.conjugation for p in possible]:
                return Result(self.position, length,
                              self.nouns.get(word=category.word, conjugation=verb.conjugation, gender=self.previous_genders,
                                             number=self.previous_numbers),
                              f"Object should be in nominative form. But is in {category.conjugation.value}.")
            elif not [p.gender for p in possible if p.gender not in self.previous_genders]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=verb.conjugation,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Object should match the gender of the previous word: {[p.value for p in self.previous_genders]}. But is in {category.gender.value}.")
            elif not [p.number for p in possible if p.number not in self.previous_numbers]:
                return Result(self.position, length,
                              self.adjectives.get(word=category.word, conjugation=verb.conjugation,
                                                  gender=self.previous_genders,
                                                  number=self.previous_numbers),
                              f"Object should match the number of the previous word: {[p.value for p in self.previous_numbers]}. But is in {category.number.value}.")
        elif category.type == WordType.ADJECTIVE:
            return Result(self.position, length, [], "Two adjectives are not allowed.")
        elif category.type == WordType.PRONOUN:
            return Result(self.position, length, [], f"Subject's pronoun should always be first after a verb.")
        else:
            raise ValueError("Something unexpected happened.")

        self.index += 1
        self.position += length + 1

        return None

    def parse(self, string: str) -> Result | None:
        string = string.lstrip()
        self.words = string.split()
        if len(string) == 0:
            return None
        self.categorized_words = self.categorize_string(string)
        # failed to categorized
        self.index = 0
        self.position = 0
        result = self.parse_subject()
        if result:
            return result

        if self.index == len(self.categorized_words):
            return None

        result = self.parse_verb()
        if result:
            return result

        if self.index == len(self.categorized_words):
            return None

        result = self.parse_object()
        if result:
            return result

        if self.index == len(self.categorized_words):
            return None

        return None

    def categorize_string(self, string: str) -> list[Word | None]:
        words = string.split()
        # skip the last word is has not been finished with space
        # TODO it should know and categorize if there is only one option
        if not string.endswith(" ") and not string.endswith("\n"):
            return [self.categorize(w) for w in words[:-1]] + [None]
        else:
            return [self.categorize(w) for w in words]

    def categorize(self, word: str) -> Word | None:
        # TODO categorize verb by their base 'słuchać'
        for attr in [self.nouns, self.verbs, self.adjectives, self.pronouns]:
            categorized = attr.get_one(word=word)
            if categorized:
                return categorized

        return None

    def parse_multiple(self, string: str) -> ResultMultiple | None:
        strings: list[str] = string.split("\n")
        for i in range(len(strings) - 1):
            strings[i].rstrip()
            strings[i] += "\n"

        for i, s in enumerate(strings):
            result = self.parse(s)
            if result:
                return ResultMultiple(i, result.position, result.length, result.expected, result.reason)

        return None


if __name__ == "__main__":
    my_parser = Parser()
    print(my_parser.parse_multiple("jego pan miał dobrego psa     \n"))
