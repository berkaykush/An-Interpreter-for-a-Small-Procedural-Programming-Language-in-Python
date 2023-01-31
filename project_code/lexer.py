from .tokens import Token
from .error import LexerError


class Lexer:
    def __init__(self, text):
        self.__text = text
        self.__char_pos = 0

        if len(text) == 0:
            self.__current_char = None
        else:
            self.__current_char = self.__text[self.__char_pos]

        self.__line = 1
        self.__col = 1

    def get_next_token(self):
        while self.__current_char is not None:
            if self.__current_char.isspace():
                self.__remove_whitespace()
                continue

            if self.__current_char == "/" and self.__check_next_char() == "*":
                self.__handle_multiline_comment()
                continue

            if self.__current_char == '"':
                str_ = self.__convert_to_str()
                return Token(Token.STR, str_, self.__line, self.__col)

            if self.__current_char.isalpha():
                identifier = self.__convert_to_id()

                if identifier in Token.KEYWORDS:
                    return Token(
                        Token.KEYWORDS[identifier], identifier, self.__line, self.__col
                    )

                if identifier in ["true", "false"]:
                    return Token(Token.BOOL, identifier, self.__line, self.__col)

                return Token(Token.IDENTIFIER, identifier, self.__line, self.__col)

            if self.__current_char.isdigit():
                num = self.__convert_to_num()

                if isinstance(num, int):
                    return Token(Token.INT, num, self.__line, self.__col)

                return Token(Token.FLOAT, num, self.__line, self.__col)

            if self.__is_comparsion_operator():
                token_type, operator = self.__convert_to_comparsion_operator()
                return Token(token_type, operator, self.__line, self.__col)

            if self.__is_assignment_operator():
                token_type, operator = self.__convert_to_assignment_operator()
                return Token(token_type, operator, self.__line, self.__col)

            if self.__is_arithmetic_operator():
                token_type, operator = self.__convert_to_arithmetic_operator()
                return Token(token_type, operator, self.__line, self.__col)

            if self.__current_char == ";":
                self.__advance()
                return Token(Token.SEMI_COLON, ";", self.__line, self.__col)

            if self.__current_char == ",":
                self.__advance()
                return Token(Token.COMMA, ",", self.__line, self.__col)

            if self.__is_wrapper():
                token_type, wrapper = self.__convert_to_wrapper()
                return Token(token_type, wrapper, self.__line, self.__col)

            if self.__is_parenthesis():
                token_type, parenthesis = self.__convert_to_parenthesis()
                return Token(token_type, parenthesis, self.__line, self.__col)

            if self.__is_bracket():
                token_type, bracket = self.__convert_to_bracket()
                return Token(token_type, bracket, self.__line, self.__col)

            self.__error()

        return Token(Token.EOF, None)

    def __advance(self):
        if self.__current_char == "\n":
            self.__line += 1
            self.__col = 0

        self.__char_pos += 1

        if self.__char_pos == len(self.__text):  # End of input
            self.__current_char = None
            return

        self.__current_char = self.__text[self.__char_pos]
        self.__col += 1

    def __check_next_char(self, offset=1):
        """
        Will be useful and used for instance, differentiating between "=", and "==".
        """
        next_char_at = self.__char_pos + offset

        if next_char_at == len(self.__text):
            return None

        return self.__text[next_char_at]

    def __remove_whitespace(self):
        while self.__current_char is not None and self.__current_char.isspace():
            self.__advance()

    def __handle_multiline_comment(self):
        self.__advance()
        self.__advance()

        while self.__current_char != "*" and self.__check_next_char() != "/":
            self.__advance()

        self.__advance()
        self.__advance()

    def __is_assignment_operator(self):
        return (
            (self.__is_arithmetic_operator() and self.__check_next_char() == "=")
            or (self.__current_char == "=")
            or (
                self.__current_char == "/"
                and self.__check_next_char() == "/"
                and self.__check_next_char(offset=2) == "="
            )
        )

    def __is_arithmetic_operator(self):
        return self.__current_char in ["+", "-", "*", "/", "%"]

    def __is_comparsion_operator(self):
        return (
            (self.__current_char == "=" and self.__check_next_char() == "=")
            or (self.__current_char == "!")
            or (self.__current_char == "<")
            or (self.__current_char == ">")
        )

    def __is_wrapper(self):
        return self.__current_char in ["{", "}"]

    def __is_parenthesis(self):
        return self.__current_char in ["(", ")"]

    def __is_bracket(self):
        return self.__current_char in ["[", "]"]

    def __convert_to_str(self):
        str_ = ""
        escape_chars_map = {"n": "\n", "t": "\t", "r": "\r", "0": "\0"}
        self.__advance()

        while self.__current_char is not None and self.__current_char != '"':
            if self.__current_char == "\\":
                self.__advance()
                str_ += escape_chars_map.get(self.__current_char, self.__current_char)
            else:
                str_ += self.__current_char

            self.__advance()

        self.__advance()
        return str_

    def __convert_to_num(self):
        num = ""

        while self.__current_char is not None and self.__current_char.isdigit():
            num += self.__current_char
            self.__advance()

        if self.__current_char == ".":
            num += self.__current_char
            self.__advance()

            while self.__current_char is not None and self.__current_char.isdigit():
                num += self.__current_char
                self.__advance()

            return float(num)

        return int(num)

    def __convert_to_id(self):
        identifier = ""

        while self.__current_char is not None and self.__current_char.isalnum():
            identifier += self.__current_char
            self.__advance()

        return identifier

    def __convert_to_arithmetic_operator(self):
        operator = self.__current_char
        self.__advance()

        if operator == "+":
            token_type = Token.PLUS
        elif operator == "-":
            token_type = Token.MINUS
        elif operator == "*":
            token_type = Token.MULTIPLICATION
        elif operator == "/" and self.__current_char == "/":
            operator += self.__current_char
            self.__advance()
            token_type = Token.INT_DIVISION
        elif operator == "/":
            token_type = Token.FLOAT_DIVISION
        else:
            token_type = Token.MODULO

        return token_type, operator

    def __convert_to_assignment_operator(self):
        operator = self.__current_char
        self.__advance()

        if operator == "=":
            return Token.ASSIGN, operator

        operator += self.__current_char
        self.__advance()

        if operator == "//":
            operator += self.__current_char
            self.__advance()

            token_type = Token.INT_DIVISION_ASSIGN
        elif operator == "+=":
            token_type = Token.PLUS_ASSIGN
        elif operator == "-=":
            token_type = Token.MINUS_ASSIGN
        elif operator == "*=":
            token_type = Token.MULTIPLICATION_ASSIGN
        elif operator == "/=":
            token_type = Token.FLOAT_DIVISION_ASSIGN
        else:
            token_type = Token.MODULO_ASSIGN

        return token_type, operator

    def __convert_to_comparsion_operator(self):
        operator = self.__current_char
        self.__advance()

        match operator:
            case "=":
                operator += self.__current_char
                self.__advance()
                token_type = Token.EQUALS

            case "!":
                operator += self.__current_char
                self.__advance()
                token_type = Token.NOT_EQUALS

            case "<":
                if self.__current_char == "=":
                    operator += self.__current_char
                    self.__advance()
                    token_type = Token.LESS_THAN_OR_EQUALS
                else:
                    token_type = Token.LESS_THAN

            case _:
                if self.__current_char == "=":
                    operator += self.__current_char
                    self.__advance()

                    token_type = Token.GREATER_THAN_OR_EQUALS
                else:
                    token_type = Token.GREATER_THAN

        return token_type, operator

    def __convert_to_wrapper(self):
        wrapper = self.__current_char
        self.__advance()

        if wrapper == "{":
            token_type = Token.LEFT_CURLY_BRACKET
        else:
            token_type = Token.RIGHT_CURLY_BRACKET

        return token_type, wrapper

    def __convert_to_parenthesis(self):
        parenthesis = self.__current_char
        self.__advance()

        if parenthesis == "(":
            token_type = Token.LEFT_PARENTHESIS
        else:
            token_type = Token.RIGHT_PARENTHESIS

        return token_type, parenthesis

    def __convert_to_bracket(self):
        bracket = self.__current_char
        self.__advance()

        if bracket == "[":
            token_type = Token.LEFT_SQUARE_BRACKET
        else:
            token_type = Token.RIGHT_SQUARE_BRACKET

        return token_type, bracket

    def __error(self):
        raise LexerError(
            error_message=f'Error occured for "{self.__current_char}" on line {self.__line}, column {self.__col}'
        )
