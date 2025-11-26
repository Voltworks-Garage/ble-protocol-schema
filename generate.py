#!/usr/bin/env python3
"""
BLE Protocol Code Generator
Generates C and Dart code from schema.json
"""

import argparse
import os
import sys
from pathlib import Path

# Add generators directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generators'))

from c_generator import generate_c_code
from dart_generator import generate_dart_code


def main():
    parser = argparse.ArgumentParser(
        description='Generate C and Dart code from BLE protocol schema',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all code with default paths
  python generate.py

  # Generate only C code
  python generate.py --lang c

  # Generate only Dart code
  python generate.py --lang dart

  # Use custom schema and output directory
  python generate.py --schema custom_schema.json --output my_output
        """
    )

    parser.add_argument(
        '--schema',
        default='schema/schema.json',
        help='Path to schema.json file (default: schema/schema.json)'
    )

    parser.add_argument(
        '--output',
        default='generated',
        help='Output directory (default: generated)'
    )

    parser.add_argument(
        '--lang',
        choices=['c', 'dart', 'all'],
        default='all',
        help='Language to generate (default: all)'
    )

    args = parser.parse_args()

    # Verify schema exists
    if not os.path.exists(args.schema):
        print(f"Error: Schema file not found: {args.schema}")
        sys.exit(1)

    # Create output directories
    c_output = os.path.join(args.output, 'c')
    dart_output = os.path.join(args.output, 'dart')

    if args.lang in ['c', 'all']:
        os.makedirs(c_output, exist_ok=True)

    if args.lang in ['dart', 'all']:
        os.makedirs(dart_output, exist_ok=True)

    # Generate code
    print(f"Reading schema from: {args.schema}")
    print()

    if args.lang in ['c', 'all']:
        print("Generating C code...")
        generate_c_code(args.schema, c_output)
        print()

    if args.lang in ['dart', 'all']:
        print("Generating Dart code...")
        generate_dart_code(args.schema, dart_output)
        print()

    print("Code generation complete!")


if __name__ == '__main__':
    main()
