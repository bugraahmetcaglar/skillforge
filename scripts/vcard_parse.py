from __future__ import annotations

from apps.contact.utils.vcard_parser import VCardParser



def parse_vcard_file(file_path: str | Path | TextIO) -> list[dict[str, Any]]:
    """Quick function to parse a vCard file and return all contacts"""
    with VCardParser() as parser:
        return list(parser.parse_file(file_path))


def parse_vcard_content(content: str) -> list[dict[str, Any]]:
    """Quick function to parse vCard content string"""
    with VCardParser() as parser:
        return list(parser.parse_content(content))