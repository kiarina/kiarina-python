from kiarina.agi.local_scanner import LocalPathSpec


def test_no_query_string() -> None:
    result = LocalPathSpec.from_string("src/")
    assert result == LocalPathSpec(path_pattern="src/")


def test_no_query_string_plain_file() -> None:
    result = LocalPathSpec.from_string("main.py")
    assert result == LocalPathSpec(path_pattern="main.py")


def test_include_single_pattern() -> None:
    result = LocalPathSpec.from_string("*_tests/?include=test_*.py")
    assert result == LocalPathSpec(
        path_pattern="*_tests/",
        include_patterns=["test_*.py"],
    )


def test_include_multiple_patterns_comma_separated() -> None:
    result = LocalPathSpec.from_string("nextjs/?include=*.ts,*.tsx")
    assert result == LocalPathSpec(
        path_pattern="nextjs/",
        include_patterns=["*.ts", "*.tsx"],
    )


def test_exclude_single_pattern() -> None:
    result = LocalPathSpec.from_string("src/?exclude=tests/**")
    assert result == LocalPathSpec(
        path_pattern="src/",
        exclude_patterns=["tests/**"],
    )


def test_include_and_exclude() -> None:
    result = LocalPathSpec.from_string("fastapi/?include=*.py&exclude=tests/**")
    assert result == LocalPathSpec(
        path_pattern="fastapi/",
        include_patterns=["*.py"],
        exclude_patterns=["tests/**"],
    )


def test_include_multiple_and_exclude_multiple() -> None:
    result = LocalPathSpec.from_string(
        "src/?include=*.py,*.pyi&exclude=tests/**,*_test.py"
    )
    assert result == LocalPathSpec(
        path_pattern="src/",
        include_patterns=["*.py", "*.pyi"],
        exclude_patterns=["tests/**", "*_test.py"],
    )


def test_empty_include_value() -> None:
    result = LocalPathSpec.from_string("src/?include=")
    assert result == LocalPathSpec(path_pattern="src/")


def test_empty_exclude_value() -> None:
    result = LocalPathSpec.from_string("src/?exclude=")
    assert result == LocalPathSpec(path_pattern="src/")


def test_whitespace_stripped_from_patterns() -> None:
    result = LocalPathSpec.from_string("src/?include= *.py , *.pyi ")
    assert result == LocalPathSpec(
        path_pattern="src/",
        include_patterns=["*.py", "*.pyi"],
    )


def test_question_mark_in_path_with_query() -> None:
    result = LocalPathSpec.from_string("src/foo?bar/?include=*.py")
    assert result == LocalPathSpec(
        path_pattern="src/foo?bar/",
        include_patterns=["*.py"],
    )


def test_question_mark_in_path_without_query() -> None:
    result = LocalPathSpec.from_string("src/foo?bar/baz")
    assert result == LocalPathSpec(path_pattern="src/foo?bar/baz")


def test_no_include_no_exclude_with_query() -> None:
    result = LocalPathSpec.from_string("src/?unknown=value")
    assert result == LocalPathSpec(path_pattern="src/?unknown=value")
