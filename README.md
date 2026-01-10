# Event Banner Generator

A Python-based tool to generate event banners for Kubernetes Community meetups and other events.

## Features

- 📝 Define event content in YAML files
- 🎨 Customizable colors, fonts, and layouts
- 👥 Support for multiple speakers/presenters
- 🖼️ Multiple output formats (JPG, WEBP)
- 🎯 Flexible positioning and styling

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Create or edit a YAML file in the `events` directory (see examples)
2. Run the generator:

```bash
python generate_banner.py events/your-event.yaml
```

Or generate all events:

```bash
python generate_banner.py --all
```

The generated banners will be saved in the `output` directory.

## YAML Configuration

See the example files in the `events` directory for configuration options:
- Event title and details
- Date, time, and location
- Speakers with photos and descriptions
- Colors and branding
- Logo images

## Directory Structure

```
event-banner-generator/
├── generate_banner.py      # Main generator script
├── banner_generator.py     # Banner generation logic
├── requirements.txt        # Python dependencies
├── events/                 # YAML event configurations
│   ├── example-march-2024.yaml
│   └── example-june-2024.yaml
├── assets/                 # Logos and default images
│   └── logos/
└── output/                 # Generated banners
```

## Customization

You can customize:
- Background colors and gradients
- Font sizes and colors
- Logo placement
- Speaker photo sizes and positions
- Layout spacing

See the YAML examples for all available options.
