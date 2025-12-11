#!/usr/bin/env python3
"""
UV Disk Cleanup CLI Tool

A comprehensive tool for monitoring and cleaning up disk space used by uv Python packages.
"""

import sys
import os
import argparse
from pathlib import Path

# Add the directory containing this script to the Python path
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

from cli.menu import Menu


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description='UV Disk Space Manager - Monitor and clean up disk space used by uv Python packages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv-disk-clean                    # Run interactive menu
  uv-disk-clean --base-path ~/projects  # Use custom base path
  uv-disk-clean --help              # Show this help message
        """
    )
    
    parser.add_argument(
        '--base-path',
        type=str,
        default=None,
        help='Base path to search for virtual environments (default: ~/code/python)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    base_path = Path(args.base_path).expanduser() if args.base_path else None
    
    try:
        menu = Menu(base_path)
        menu.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

