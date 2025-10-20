from LanguageProcessing.polish_parser.speech_parts import Nouns, Verbs, Word, Conjugation, WordType, Person


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

    def parse(self, string: str) -> Result | None:
        string = string.lstrip()
        words = string.split()
        if len(string) == 0:
            return None
        categorized_words = self.categorize_string(string)
        # do it recursively, but I am lazy
        # failed to categorized
        noun = categorized_words[0]
        word = words[0]
        length = len(words[0])
        if noun is None:  # suggest new words
            return Result(0, length, [w for w in self.nouns.get(conjugation=Conjugation.NOM) if w.word.startswith(word)], "Unrecognized word")
        elif noun.type == WordType.VERB:
            return Result(0, length, [], "First word should be a noun not a verb.")
        elif noun.type == WordType.NOUN:
            if noun.conjugation != Conjugation.NOM:
                return Result(0, length,
                              self.nouns.get(word=noun.word, conjugation=Conjugation.NOM, gender=noun.gender, number=noun.number),
                              f"Subject should be in nominative form. But is in {noun.conjugation.value}.")
        else:
            raise ValueError("Something unexpected happened.")

        if len(categorized_words) == 1:
            return None

        verb = categorized_words[1]
        position = length + 1
        word = words[1]
        length = len(words[1])
        if verb is None:
            return Result(position, length,
                          [w for w in self.verbs.get(gender=noun.gender, number=noun.number, person=Person.THIRD) if w.word.startswith(word)],
                          "Unrecognized word")
        elif verb.type == WordType.VERB:
            if verb.number != noun.number:
                return Result(position, length,
                              self.verbs.get(word=verb.word, gender=noun.gender, number=noun.number, person=Person.THIRD),
                              f"Verb should match the noun number: {noun.number.value}. But is {verb.number.value}.")
            if verb.gender != noun.gender and verb.gender is not None:
                return Result(position, length,
                              self.verbs.get(word=verb.word, gender=noun.gender, number=noun.number, person=Person.THIRD),
                              f"Verb gender should match the noun gender: {noun.gender.value}. But is {verb.gender.value}.")
            if verb.person != Person.THIRD:
                return Result(position, length,
                              self.verbs.get(word=verb.word, gender=noun.gender, number=noun.number, person=Person.THIRD),
                              f"Verb should be in 3rd person. But is {verb.person.value}.")
        elif verb.type == WordType.NOUN:
            return Result(position, length, [], "Second word should be a verb not a noun.")
        else:
            raise ValueError("Something unexpected happened.")

        if len(categorized_words) == 2:
            return None

        noun = categorized_words[2]
        position = length + 1
        word = words[2]
        length = len(words[2])
        if noun is None:  # suggest new words
            return Result(position, length,
                          [w for w in self.nouns.get(conjugation=verb.conjugation) if w.word.startswith(word)],
                          "Unrecognized word")
        elif noun.type == WordType.VERB:
            return Result(position, length, [], "Third word should be a noun not a verb.")
        elif noun.type == WordType.NOUN:
            if noun.conjugation != verb.conjugation:
                return Result(position, length,
                              self.nouns.get(word=noun.word, conjugation=verb.conjugation, gender=noun.gender,
                                             number=noun.number),
                              f"Subject should be in {verb.conjugation.value} form. But is in {noun.conjugation.value}.")
        else:
            raise ValueError("Something unexpected happened.")

    def categorize_string(self, string: str) -> list[Word | None]:
        words = string.split()
        # skip the last word is has not been finished with space
        # TODO it should know and categorize if there is only one option
        if not string.endswith(" "):
            return [self.categorize(w) for w in words[:-1]] + [None]
        else:
            return [self.categorize(w) for w in words]

    def categorize(self, word: str) -> Word | None:
        # TODO categorize verb by their base 'słuchać'
        categorized = self.nouns.get_one(word=word)
        if categorized:
            return categorized

        categorized = self.verbs.get_one(word=word)
        if categorized:
            return categorized

        return None
