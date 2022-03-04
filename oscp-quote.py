#!/usr/bin/env python3
import sys
from typing import NoReturn


def exit_err() -> NoReturn:
    print(
        f"error: while reading line from stdin: {sys.exc_info()[0]}", file=sys.stderr)
    exit(1)


def get_line() -> str:
    try:
        line = input()
    except (EOFError, KeyboardInterrupt):
        exit(0)
    except:
        exit_err()

    return line


def quote() -> None:
    while True:
        line = get_line()
        result = ""
        for i in range(len(line)):
            if line[i] == "'":
                if i == 0:
                    result += "\"'\"'"
                elif i == len(line) - 1:
                    result += "'\"'\""
                else:
                    result += "'\"'\"'"
            else:
                result += line[i]

        if len(line) > 0 and line[0] != "'":
            result = "'" + result
        if len(line) > 0 and line[-1] != "'":
            result += "'"

        print(result)


def main() -> None:
    quote()


if __name__ == "__main__":
    main()
