import argparse
import logging
import sys
from pathlib import Path

from .vale_flagger import ValeFlagger

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_parser():
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        prog='valeflag',
        description='ValeFlagger - AsciiDoc DITA compatibility checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Check current directory
  %(prog)s --path ./docs             # Check specific directory
  %(prog)s --path file.adoc          # Check specific file
  %(prog)s --enable-rules "Headings.Capitalization,Terms.Use"
  %(prog)s --disable-rules "Style.Passive"
  %(prog)s --dry-run                 # Show issues without modifying files
        """
    )

    parser.add_argument(
        '--path', '-p',
        default='.',
        help='Target directory or file to check (default: current directory)'
    )

    parser.add_argument(
        '--enable-rules', '-e',
        help='Comma-separated list of rules to enable'
    )

    parser.add_argument(
        '--disable-rules', '-d',
        help='Comma-separated list of rules to disable'
    )

    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be flagged without modifying files'
    )

    parser.add_argument(
        '--flag-format',
        default=ValeFlagger.DEFAULT_FLAG_FORMAT,
        help='Custom flag format (default: "%(default)s")'
    )

    parser.add_argument(
        '--config', '-c',
        help='Path to configuration file (YAML format)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    return parser


def main(args=None):
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(args)

    setup_logging(args.verbose)

    try:
        # Parse rule lists
        include_rules = []
        exclude_rules = []

        if args.enable_rules:
            include_rules = [r.strip() for r in args.enable_rules.split(',')]

        if args.disable_rules:
            exclude_rules = [r.strip() for r in args.disable_rules.split(',')]

        # Create flagger instance
        flagger = ValeFlagger(
            config_path=getattr(args, 'config', None),
            flag_format=args.flag_format,
            dry_run=args.dry_run
        )

        # Run Vale
        logger.info(f"Checking {args.path}...")
        results = flagger.run(
            target_path=args.path,
            include_rules=include_rules,
            exclude_rules=exclude_rules
        )

        # Report results
        total_issues = sum(len(issues) for issues in results.values())

        if args.dry_run:
            print(f"\n{'='*60}")
            print(f"DRY RUN RESULTS: Found {total_issues} issues in {len(results)} files")
            print(f"{'='*60}")

            for file_path, issues in sorted(results.items()):
                print(f"\n📄 {file_path} ({len(issues)} issues):")
                for issue in sorted(issues, key=lambda x: x['Line']):
                    severity_icon = "❌" if issue.get('Severity') == 'error' else "⚠️"
                    rule_name = issue['Check'].replace('AsciiDocDITA.', '')
                    print(f"  {severity_icon} Line {issue['Line']}: [{rule_name}]")
                    print(f"     {issue['Message']}")
        else:
            print(f"\n✅ Flagged {total_issues} issues in {len(results)} files.")
            if total_issues > 0:
                print("Run with --dry-run to see details without modifying files.")

        return 0 if total_issues == 0 else 1

    except Exception as e:
        logger.error(f"Error: {e}")
        return 2


if __name__ == '__main__':
    sys.exit(main())
