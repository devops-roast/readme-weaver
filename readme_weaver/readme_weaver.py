from typing import Optional

from loguru import logger

from readme_weaver.include_content_reader import IncludeContentReaderInterface
from readme_weaver.include_metadata import IncludeMetadata
from readme_weaver.include_metadata_extractor import IncludeMetadataExtractorInterface


class ReadmeWeaver:
    def __init__(
        self,
        readme_paths: list[str],
        changed_files: Optional[list[str]],
        include_metadata_extractor: IncludeMetadataExtractorInterface,
        include_content_reader: IncludeContentReaderInterface,
    ) -> None:
        self._readme_paths = readme_paths
        self._changed_files = changed_files
        self._include_metadata_extractor = include_metadata_extractor
        self._include_content_reader = include_content_reader

    def __call__(self) -> None:
        for readme_path in self._readme_paths:
            self._process_readme(readme_path=readme_path)

    def _process_readme(self, readme_path: str) -> None:
        readme_content = self._read_readme(readme_path)
        if not readme_content:
            logger.info(f"Empty markdown file {readme_path}. Skipping.")
            return

        includes = self._extract_includes(
            readme_content=readme_content, readme_path=readme_path
        )

        if not includes:
            return

        if self._changed_files:
            if readme_path not in self._changed_files:
                includes = [inc for inc in includes if inc.path in self._changed_files]

        include_contents = self._include_content_reader.read(includes=includes)

        self._update_readme(
            include_contents=include_contents,
            readme_content=readme_content,
            readme_path=readme_path,
        )

    def _read_readme(self, readme_path: str) -> list[str]:
        if not readme_path.endswith(".md"):
            raise ValueError("README path must end with .md")

        with open(readme_path, encoding="utf-8") as readme_file:
            return readme_file.readlines()

    def _extract_includes(
        self, readme_content: list[str], readme_path: str
    ) -> Optional[list[IncludeMetadata]]:
        includes = self._include_metadata_extractor.extract(readme_content=readme_content)
        if not includes:
            logger.debug(
                f"No include directives found in README at path {readme_path}. Skipping."
            )
            return None
        logger.info(
            f"""Found include paths in {readme_path}:
            {set(inc.path for inc in includes)}"""
        )
        return includes

    def _update_readme(
        self,
        include_contents: list[IncludeMetadata],
        readme_content: list[str],
        readme_path: str,
    ) -> None:
        updated_readme = []
        readme_content_cursor = 0

        for include in sorted(include_contents, key=lambda x: x.readme_start):
            updated_readme += readme_content[readme_content_cursor : include.readme_start + 1]
            updated_readme += include.content + "\n"

            readme_content_cursor = include.readme_end

        updated_readme += readme_content[readme_content_cursor:]

        with open(readme_path, "w", encoding="utf-8") as readme_file:
            readme_file.writelines(updated_readme)
