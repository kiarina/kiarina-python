from typing import TypeAlias

FileBundleFilePath: TypeAlias = str
"""
A relative path of an entry stored inside a :class:`FileBundle` archive.

This is NOT a filesystem path. It is the name used as the zip member name and
referenced from manifest entries (e.g. ``"audio.mp3"``).
"""
