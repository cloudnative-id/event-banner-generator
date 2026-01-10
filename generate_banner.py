#!/usr/bin/env python3
"""
Event Banner Generator - Main Script
Usage: python generate_banner.py <yaml_file> [--output <output_path>]
       python generate_banner.py --all
"""

import argparse
import yaml
import os
import sys
from pathlib import Path
from banner_generator import BannerGenerator


def load_yaml_config(yaml_file: str) -> dict:
    """Load YAML configuration file"""
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading YAML file {yaml_file}: {e}")
        sys.exit(1)


def generate_banner(yaml_file: str, output_path: str = None):
    """Generate banner from YAML configuration"""
    print(f"Loading configuration from: {yaml_file}")
    config = load_yaml_config(yaml_file)
    
    # Determine output path
    if not output_path:
        yaml_filename = Path(yaml_file).stem
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{yaml_filename}.jpg")
    
    # Create generator
    generator = BannerGenerator(config)
    
    print("Generating banner...")
    img = generator.generate()
    
    # Save in multiple formats
    output_formats = config.get('output_formats', ['jpg', 'webp'])
    print(f"Saving banner in formats: {', '.join(output_formats)}")
    saved_files = generator.save(img, output_path, output_formats)
    
    print("Banner generated successfully!")
    for file in saved_files:
        print(f"  ✓ {file}")
    
    return saved_files


def generate_all_banners():
    """Generate banners for all YAML files in events directory"""
    events_dir = 'events'
    
    if not os.path.exists(events_dir):
        print(f"Events directory '{events_dir}' not found!")
        sys.exit(1)
    
    yaml_files = list(Path(events_dir).glob('*.yaml')) + list(Path(events_dir).glob('*.yml'))
    
    if not yaml_files:
        print(f"No YAML files found in '{events_dir}' directory!")
        sys.exit(1)
    
    print(f"Found {len(yaml_files)} event(s) to generate\n")
    
    for yaml_file in yaml_files:
        print(f"\n{'='*60}")
        generate_banner(str(yaml_file))
    
    print(f"\n{'='*60}")
    print(f"All {len(yaml_files)} banner(s) generated successfully!")


def main():
    parser = argparse.ArgumentParser(
        description='Generate event banners from YAML configuration files'
    )
    parser.add_argument(
        'yaml_file',
        nargs='?',
        help='Path to YAML configuration file'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output path for the generated banner'
    )
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Generate banners for all YAML files in events directory'
    )
    
    args = parser.parse_args()
    
    if args.all:
        generate_all_banners()
    elif args.yaml_file:
        generate_banner(args.yaml_file, args.output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
