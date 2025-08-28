"""
Extractor for include directives in README files.

This module provides an extractor that scans a list of markdown lines for
comment‑based include directives of the form:

    <!-- md:include start path="partials/foo.md" required=false -->
    ... existing content ...
    <!-- md:include end -->

When such a start tag is encountered, the extractor parses the ``path`` and
optional ``required`` attributes. Once a corresponding end tag is found, an
``IncludeMetadata`` instance is created to describe the region of the README to
be replaced and the file to be included.
"""

from typing import Protocol, Optional
import re

from .include_metadata import IncludeMetadata


class IncludeMetadataExtractorInterface(Protocol):
    """Interface for extracting include metadata from a README."""

    def extract(self, readme_content: list[str]) -> list[IncludeMetadata]: ...


class IncludeMetadataExtractor:
    """
    Extractor for ``IncludeMetadata`` objects from a markdown README.

    It looks for comment directives with a ``start`` and ``end`` marker to
    delineate the region of the README to replace.  The directive must specify
    a ``path`` attribute pointing to the file to include.  A ``required``
    attribute may be provided to control behavior when the file is missing; if
    omitted it defaults to ``True``.
    """

    def __init__(self) -> None:
        # Regular expressions to identify include directives.  The start tag
        # captures its attribute string for later parsing; the end tag is
        # simply matched.
        self._include_start_regex = re.compile(
            r"<!--\s*md:include\s+start\s+([^>]*)-->", re.IGNORECASE
        )
        self._include_end_regex = re.compile(
            r"<!--\s*md:include\s+end\s*-->", re.IGNORECASE
        )

    def extract(self, readme_content: list[str]) -> list[IncludeMetadata]:
        includes: list[IncludeMetadata] = []
        current: Optional[dict] = None

        for row, line in enumerate(readme_content):
            start_match = self._include_start_regex.search(line)
            end_match = self._include_end_regex.search(line)

            if start_match:
                # Parse attributes from the start tag
                attrs_str = start_match.group(1) or ""
                attrs = self._parse_attrs(attrs_str)
                path = attrs.get("path")
                if not path:
                    raise ValueError(
                        'Include directive must specify a path, e.g. path="foo.md"'
                    )
                required_str = str(attrs.get("required", "true")).strip().lower()
                required = required_str not in ("false", "0", "no")
                current = {
                    "start": row,
                    "path": path,
                    "required": required,
                }
            elif end_match and current:
                # Create metadata for the block
                includes.append(
                    IncludeMetadata(
                        readme_start=current["start"],
                        readme_end=row,
                        path=current["path"],
                        required=current.get("required", True),
                        content="",
                    )
                )
                current = None

        return includes

    @staticmethod
    def _parse_attrs(attr_str: str) -> dict:
        """
        Parse key=value pairs from an include start tag attribute string.
        Values may be quoted with single or double quotes or left unquoted.
        Returns a mapping of attribute names to values.
        """
        attrs: dict = {}
        for match in re.finditer(r"(\w+)=('([^']*)'|\"([^\"]*)\"|([^\s]+))", attr_str):
            key = match.group(1)
            value = match.group(3) or match.group(4) or match.group(5)
            attrs[key] = value
        return attrs
