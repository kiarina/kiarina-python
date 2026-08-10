import re
import sys


class StreamPrinter:
    def __init__(self) -> None:
        self._check_escape = False
        self._partial_unicode = ""
        self._first = True
        self._unicode_escape_pattern = re.compile(r"\\u[0-9a-fA-F]{4}")
        self._partial_unicode_escape_pattern = re.compile(r"\\u[0-9a-fA-F]{0,3}$")

    def __call__(self, t: str) -> None:
        # If this is the first string
        if self._first:
            if t.strip():
                self._first = False

        # If the previous string ended with an escape character
        if self._check_escape:
            self._check_escape = False

            # Handle newline that spans across chunks
            if t.startswith("n"):
                print(file=sys.stderr)
                t = t[1:]

            # Detect partial Unicode escape sequence
            elif t.startswith("u"):
                self._partial_unicode = "\\u"
                t = t[1:]

        # Concatenate if there's a partial Unicode escape string
        if self._partial_unicode:
            t = self._partial_unicode + t
            self._partial_unicode = ""

        # Decode Unicode escapes
        t = self._unicode_escape_pattern.sub(
            lambda match: chr(int(match.group(0)[2:], 16)), t
        )

        # Handle newline characters
        t = t.replace("\\\\n", "\n")
        t = t.replace("\\n", "\n")

        # Only newline character
        if t == "\\n":
            print(file=sys.stderr)

        # Last character is a newline
        elif t.endswith("\\n"):
            print(t[:-2], file=sys.stderr)

        # Last character is an escape character
        elif t.endswith("\\"):
            self._check_escape = True
            print(t[:-1], end="", file=sys.stderr)

        # Last character is a partial Unicode escape
        elif match := self._partial_unicode_escape_pattern.search(t):
            self._partial_unicode = match.group(0)
            t = self._partial_unicode_escape_pattern.sub("", t)
            print(t, end="", file=sys.stderr)

        # Normal string
        else:
            print(t, end="", file=sys.stderr)
