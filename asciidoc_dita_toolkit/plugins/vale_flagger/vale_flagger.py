import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import ValeFlaggerConfig

logger = logging.getLogger(__name__)


class ValeFlagger:
    """Integrates Vale linter with AsciiDoc files for DITA compatibility checking."""

    DEFAULT_FLAG_FORMAT = "// ADT-FLAG [{rule}]: {message}"

    def __init__(self, config_path: str = None, flag_format: str = None, dry_run: bool = False):
        """
        Initialize ValeFlagger with configuration.

        Args:
            config_path: Path to configuration file
            flag_format: Custom flag format string
            dry_run: If True, don't modify files
        """
        self.config = ValeFlaggerConfig(config_path)
        self.flag_format = flag_format or self.config.flag_format
        self.dry_run = dry_run
        self._check_docker()

    def _check_docker(self):
        """Verify Docker is available."""
        try:
            subprocess.run(["docker", "--version"],
                         capture_output=True,
                         check=True,
                         timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise RuntimeError(
                "Docker is not installed or not running. "
                "Please install Docker and ensure it's running."
            )

    def run(self,
            target_path: str = ".",
            include_rules: List[str] = None,
            exclude_rules: List[str] = None) -> Dict[str, List[dict]]:
        """
        Run Vale with configuration-based rules.

        Args:
            target_path: Directory or file to check
            include_rules: List of rules to enable
            exclude_rules: List of rules to disable

        Returns:
            Dictionary of file paths to issues found
        """
        # Merge CLI rules with config rules
        include_rules = include_rules or self.config.enabled_rules
        exclude_rules = exclude_rules or self.config.disabled_rules

        target_path = Path(target_path).resolve()

        # Run Vale via Docker
        vale_output = self._run_vale(target_path, include_rules, exclude_rules)

        # Process results
        if not self.dry_run and vale_output:
            self._insert_flags(vale_output)

        return vale_output

    def _run_vale(self,
                  target_path: Path,
                  include_rules: List[str] = None,
                  exclude_rules: List[str] = None) -> Dict[str, List[dict]]:
        """Execute Vale via Docker and parse JSON output."""
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{target_path.parent}:/docs",
            self.config.docker_image,
            "--output=JSON"
        ]

        # Build dynamic .vale.ini content if rules specified OR no local config exists
        local_vale_config = target_path.parent / ".vale.ini"
        if include_rules or exclude_rules or not local_vale_config.exists():
            config_content = self._build_vale_config(include_rules, exclude_rules)
            cmd.extend(["--config=/dev/stdin"])
            input_text = config_content
        else:
            input_text = None

        # Add target (relative to mounted volume)
        relative_target = target_path.name if target_path.is_file() else "."
        cmd.append(relative_target)

        logger.debug(f"Running Vale command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                input=input_text,
                timeout=self.config.timeout_seconds
            )

            if result.returncode not in (0, 1):  # Vale returns 1 if issues found
                logger.error(f"Vale error output: {result.stderr}")
                raise RuntimeError(f"Vale failed with return code {result.returncode}")

            if not result.stdout.strip():
                return {}

            return json.loads(result.stdout)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Vale output: {result.stdout}")
            raise ValueError(f"Invalid JSON from Vale: {e}")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Vale execution timed out after {self.config.timeout_seconds} seconds")

    def _build_vale_config(self,
                          include_rules: List[str] = None,
                          exclude_rules: List[str] = None) -> str:
        """Build dynamic Vale configuration."""
        config = [
            "StylesPath = /root/.local/share/vale/styles",
            "MinAlertLevel = suggestion",
            "",
            "[*.adoc]",
            "BasedOnStyles = AsciiDocDITA"
        ]

        if include_rules:
            for rule in include_rules:
                config.append(f"AsciiDocDITA.{rule} = YES")

        if exclude_rules:
            for rule in exclude_rules:
                config.append(f"AsciiDocDITA.{rule} = NO")

        return "\n".join(config)

    def _insert_flags(self, vale_output: Dict[str, List[dict]]):
        """Insert flags into files based on Vale output."""
        for file_path, issues in vale_output.items():
            if issues:
                self._flag_file(file_path, issues)

    def _flag_file(self, file_path: str, issues: List[dict]):
        """Insert flags into a single file."""
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return

        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines(keepends=True)

            # Group issues by line number
            issues_by_line = {}
            for issue in issues:
                line_num = issue['Line']
                if line_num not in issues_by_line:
                    issues_by_line[line_num] = []
                issues_by_line[line_num].append(issue)

            # Insert flags in reverse order to maintain line numbers
            for line_num in sorted(issues_by_line.keys(), reverse=True):
                flag = self._format_flag(issues_by_line[line_num])
                # Adjust for 0-based indexing
                insert_pos = max(0, line_num - 1)
                lines.insert(insert_pos, flag + '\n')

            # Write back to file
            file_path.write_text(''.join(lines), encoding='utf-8')
            logger.info(f"Flagged {len(issues_by_line)} issues in {file_path}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

    def _format_flag(self, issues: List[dict]) -> str:
        """Format multiple issues on the same line into a single flag."""
        if len(issues) == 1:
            return self.flag_format.format(
                rule=issues[0]['Check'].replace('AsciiDocDITA.', ''),
                message=issues[0]['Message']
            )
        else:
            # Multiple issues on same line
            rules = [i['Check'].replace('AsciiDocDITA.', '') for i in issues]
            messages = [i['Message'] for i in issues]
            return self.flag_format.format(
                rule=', '.join(rules),
                message=' | '.join(messages)
            )
