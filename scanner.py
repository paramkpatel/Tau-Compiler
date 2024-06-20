# THIS IS A STUB FILE FOR THE SCANNER
# STUDENTS WILL BE FILLING IN THE DETAILS


from tau.tokens import Token, Span, Coord, punctuation, keywords
from typing import Iterator
import string


class Scanner:
    tokens: list[Token]

    def __init__(self, input: str):
        self.input = input
        self.tokens = []
        self.token_line = 1
        self.token_start = 0
        self.token_col = 0
        self.tokens = self.get_token()

    def __iter__(self) -> Iterator[Token]:
        return iter(self.tokens)

    def get_token(self) -> list[Token]:
        # counter keeps track of character for new line
        char_counter = 1
        # loop through input
        while self.token_col < len(self.input):
            self.token_start = self.token_col
            start_coord = Coord(self.token_line, char_counter)
            if self.input[self.token_col] == "\n":
                self.token_line += 1
                char_counter = 1
                self.token_col += 1
            # for : case
            elif self.input[self.token_col] == ":":
                end_coord = Coord(self.token_line, char_counter + 1)
                token = Token(":", ":", Span(start_coord, end_coord))
                self.tokens.append(token)
                self.token_col += 1
                char_counter += 1
            # check if whitespace
            elif self.input[self.token_col] in string.whitespace:
                self.token_col += 1
                char_counter += 1
            # check if number
            elif self.input[self.token_col] in string.digits:
                # loop until not a digit
                while (
                    self.token_col < len(self.input)
                    and self.input[self.token_col] in string.digits
                ):
                    self.token_col += 1
                    char_counter += 1
                end_coord = Coord(self.token_line, char_counter)
                # create token
                token = Token(
                    "INT",
                    self.input[self.token_start : self.token_col],
                    Span(start_coord, end_coord),
                )
                self.tokens.append((token))
            # check if identifier
            elif self.input[self.token_col] in string.ascii_letters:
                # loop until not a letter or digit
                while (
                    self.token_col < len(self.input)
                    and self.input[self.token_col]
                    in string.ascii_letters + string.digits
                ):
                    self.token_col += 1
                    char_counter += 1
                end_coord = Coord(self.token_line, char_counter)
                if self.input[self.token_start : self.token_col] in keywords:
                    token = Token(
                        self.input[self.token_start : self.token_col],
                        self.input[self.token_start : self.token_col],
                        Span(start_coord, end_coord),
                    )
                else:
                    token = Token(
                        "ID",
                        self.input[self.token_start : self.token_col],
                        Span(start_coord, end_coord),
                    )
                self.tokens.append((token))
            # check if comment
            elif self.input[self.token_col : self.token_col + 2] == "//":
                while (
                    self.token_col < len(self.input)
                    and self.input[self.token_col] != "\n"
                ):
                    self.token_col += 1
                    char_counter += 1
            elif (
                self.input[self.token_col : self.token_col + 2] in punctuation
                or self.input[self.token_col] in punctuation
            ):
                next_two_chars = self.input[self.token_col : self.token_col + 2]

                if next_two_chars in punctuation and self.token_col + 2 < len(
                    self.input
                ):  # Two-character punctuation
                    end = Coord(self.token_line, char_counter + 2)
                    token = Token(
                        next_two_chars, next_two_chars, Span(start_coord, end)
                    )

                    self.tokens.append(token)
                    self.token_col += 2
                    char_counter += 2
                elif (
                    self.input[self.token_col] in punctuation
                ):  # Single-character punctuation
                    end = Coord(self.token_line, char_counter + 1)
                    token = Token(
                        self.input[self.token_col],
                        self.input[self.token_col],
                        Span(start_coord, end),
                    )
                    self.tokens.append(token)
                    self.token_col += 1
                    char_counter += 1
            else:
                self.token_col += 1
                char_counter += 1
        # create EOF token
        self.tokens.append(
            Token(
                "EOF",
                "",
                Span(
                    Coord(self.token_line, char_counter),
                    Coord(self.token_line, char_counter),
                ),
            )
        )
        return self.tokens
