#!/usr/bin/env python3
"""
BLE Protocol Code Generator
Generates C and Dart code from protocol and message schemas
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
        description='Generate C and Dart code from BLE protocol schemas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all code with default paths
  python generate.py

  # Generate only C code
  python generate.py --lang c

  # Generate only Dart code
  python generate.py --lang dart

  # Use custom schemas and output directory
  python generate.py --protocol custom_protocol.json --messages custom_messages.json --output my_output
        """
    )

    parser.add_argument(
        '--protocol',
        default='schema/protocol.json',
        help='Path to protocol.json file (default: schema/protocol.json)'
    )

    parser.add_argument(
        '--messages',
        default='schema/messages.json',
        help='Path to messages.json file (default: schema/messages.json)'
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

    # Verify schemas exist
    if not os.path.exists(args.protocol):
        print(f"Error: Protocol schema file not found: {args.protocol}")
        sys.exit(1)

    if not os.path.exists(args.messages):
        print(f"Error: Messages schema file not found: {args.messages}")
        sys.exit(1)

    # Create output directories
    c_output = os.path.join(args.output, 'c')
    dart_output = os.path.join(args.output, 'dart')

    if args.lang in ['c', 'all']:
        os.makedirs(c_output, exist_ok=True)

    if args.lang in ['dart', 'all']:
        os.makedirs(dart_output, exist_ok=True)

    # Generate code
    print(f"Reading schemas:")
    print(f"  Protocol: {args.protocol}")
    print(f"  Messages: {args.messages}")
    print()

    if args.lang in ['c', 'all']:
        print("Generating C code...")
        generate_c_code(args.protocol, args.messages, c_output)
        print()

    if args.lang in ['dart', 'all']:
        print("Generating Dart code...")
        generate_dart_code(args.protocol, args.messages, dart_output)
        print()

    print("Code generation complete!")


if __name__ == '__main__':
    main()
