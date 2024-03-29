import os
import sys

from project_code.error import (
    LexerError,
    ParserError,
    SemanticError,
    InterpreterError,
)
from project_code.interpreter import Interpreter
from project_code.lexer import Lexer
from project_code.parser_ import Parser
from project_code.semantic_analysis import SemanticAnalyzer


def open_program_file():
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename>.co")
        sys.exit(1)

    filename = sys.argv[1]

    if os.path.splitext(filename)[1] != ".co":
        print("Error: File must be a .co file.")
        sys.exit(1)

    text = ""

    try:
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()
    except IOError:
        print(f"Error: File '{filename}' not found or could not be opened.")
        sys.exit(1)

    return text


def main():
    text = open_program_file()

    if not text:
        return

    lexer = Lexer(text)

    try:
        parser = Parser(lexer)
        tree = parser.parse()
    except (LexerError, ParserError) as l_p_error:
        print(l_p_error.message)
        sys.exit(1)

    try:
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.visit(tree)
    except SemanticError as s_error:
        print(s_error.message)
        sys.exit(1)
    except NotImplementedError as n_error:
        print(n_error)
        sys.exit(1)

    interpreter = Interpreter(tree)

    try:
        interpreter.interpret()
    except InterpreterError as i_error:
        print(i_error.message)
        sys.exit(1)


if __name__ == "__main__":
    main()
