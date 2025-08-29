from dataclasses import dataclass
from typing import Literal


@dataclass
class IncludeMetadata:
    """
    Metadata describing a block in a README that should be replaced by the
    contents of an external markdown file.

    - ``readme_start`` and ``readme_end`` refer to the zero‑based line numbers
      of the opening and closing include markers in the README.
    - ``path`` is the relative or absolute path of the file whose contents
      should be injected between the markers.
    - ``required`` determines whether a missing file should raise a
      ``FileNotFoundError`` (True) or silently produce an empty block (False).
    - ``content`` is the text that will be inserted into the README; it
      is populated by the content reader.

    The ``extraction_type`` and ``extraction_part`` attributes are kept for
    possible future extensions and compatibility, but default to ``"include"``
    and ``None`` respectively.
    """

    readme_start: int
    readme_end: int
    path: str
    extraction_type: Literal["include"] = "include"
    extraction_part: str | None = None
    required: bool = True
    content: str = ""
