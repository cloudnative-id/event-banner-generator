"""
Event Banner Generator
Generates event banners from YAML configuration files
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
from typing import Dict, List, Tuple, Optional
import textwrap


class BannerGenerator:
    """Generate event banners with customizable content"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.width = config.get('width', 1080)
        self.height = config.get('height', 1920)
        
    def create_gradient_background(self, color1: str, color2: str) -> Image.Image:
        """Create a gradient background"""
        base = Image.new('RGB', (self.width, self.height), color1)
        top = Image.new('RGB', (self.width, self.height), color2)
        mask = Image.new('L', (self.width, self.height))
        mask_data = []
        for y in range(self.height):
            for x in range(self.width):
                mask_data.append(int(255 * (y / self.height)))
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get font with fallback options"""
        font_options = [
            '/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/Arial.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        ]
        
        for font_path in font_options:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
        
        # Fallback to default font
        return ImageFont.load_default()
    
    def draw_text_with_outline(self, draw: ImageDraw.Draw, position: Tuple[int, int], 
                               text: str, font: ImageFont.FreeTypeFont, 
                               fill: str, outline: Optional[str] = None, 
                               outline_width: int = 2):
        """Draw text with optional outline"""
        x, y = position
        if outline:
            # Draw outline
            for adj_x in range(-outline_width, outline_width + 1):
                for adj_y in range(-outline_width, outline_width + 1):
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline)
        # Draw main text
        draw.text((x, y), text, font=font, fill=fill)
    
    def wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        lines = []
        words = text.split()
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def load_and_resize_image(self, image_path: str, size: Tuple[int, int], 
                              circular: bool = False) -> Optional[Image.Image]:
        """Load and resize an image, optionally make it circular"""
        if not image_path or not os.path.exists(image_path):
            return None
        
        try:
            img = Image.open(image_path).convert('RGB')
            
            # Center crop to square if making circular
            if circular:
                # Get the smallest dimension
                min_dim = min(img.size)
                # Calculate crop box to center
                left = (img.width - min_dim) // 2
                top = (img.height - min_dim) // 2
                right = left + min_dim
                bottom = top + min_dim
                img = img.crop((left, top, right, bottom))
            
            # Resize to target size
            img = img.resize(size, Image.Resampling.LANCZOS)
            
            if circular:
                # Create circular mask
                mask = Image.new('L', size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0) + size, fill=255)
                
                # Create RGBA image with circular mask
                output = Image.new('RGBA', size, (0, 0, 0, 0))
                output.paste(img, (0, 0))
                output.putalpha(mask)
                return output
            
            return img
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    
    def generate(self) -> Image.Image:
        """Generate the banner image"""
        # Create background
        bg_config = self.config.get('background', {})
        if 'gradient' in bg_config:
            gradient = bg_config['gradient']
            img = self.create_gradient_background(
                gradient.get('start', '#C2185B'),
                gradient.get('end', '#7B1FA2')
            )
        else:
            color = bg_config.get('color', '#C2185B')
            img = Image.new('RGB', (self.width, self.height), self.hex_to_rgb(color))
        
        draw = ImageDraw.Draw(img)
        
        # Draw logos
        self._draw_logos(img, draw)
        
        # Draw title
        self._draw_title(draw)
        
        # Draw event details
        self._draw_event_details(draw)
        
        # Draw location (if specified separately)
        self._draw_location(draw)
        
        # Draw speakers
        self._draw_speakers(img, draw)
        
        # Draw organized by
        self._draw_footer(img, draw)
        
        return img
    
    def _draw_logos(self, img: Image.Image, draw: ImageDraw.Draw):
        """Draw logos at the top"""
        logos_config = self.config.get('logos', [])
        if not logos_config:
            return
        
        x_offset = 40
        y_offset = 40
        
        for logo_config in logos_config:
            logo_path = logo_config.get('path')
            logo_size = logo_config.get('size', [120, 120])
            
            logo_img = self.load_and_resize_image(logo_path, tuple(logo_size))
            if logo_img:
                if logo_img.mode == 'RGBA':
                    img.paste(logo_img, (x_offset, y_offset), logo_img)
                else:
                    img.paste(logo_img, (x_offset, y_offset))
                x_offset += logo_size[0] + 40
    
    def _draw_title(self, draw: ImageDraw.Draw):
        """Draw event title"""
        title_config = self.config.get('title', {})
        title_text = title_config.get('text', '')
        title_color = title_config.get('color', '#FFFFFF')
        title_size = title_config.get('size', 70)
        title_y = title_config.get('y_position', 200)
        
        font = self.get_font(title_size, bold=True)
        
        # Wrap title if needed
        lines = self.wrap_text(title_text, font, self.width - 80)
        
        y = title_y
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y), line, font=font, fill=title_color)
            y += bbox[3] - bbox[1] + 10
    
    def _draw_event_details(self, draw: ImageDraw.Draw):
        """Draw event date, time, and location"""
        details_config = self.config.get('details', {})
        details_text = details_config.get('text', '')
        details_color = details_config.get('color', '#FFFFFF')
        details_size = details_config.get('size', 40)
        details_y = details_config.get('y_position', 400)
        
        font = self.get_font(details_size)
        
        # Wrap details if needed
        lines = self.wrap_text(details_text, font, self.width - 80)
        
        y = details_y
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y), line, font=font, fill=details_color)
            y += bbox[3] - bbox[1] + 5
    
    def _draw_location(self, draw: ImageDraw.Draw):
        """Draw event location if specified separately"""
        location_config = self.config.get('location', {})
        if not location_config:
            return
        
        location_text = location_config.get('text', '')
        if not location_text:
            return
            
        location_color = location_config.get('color', '#FFFFFF')
        location_size = location_config.get('size', 32)
        location_y = location_config.get('y_position', 420)
        
        font = self.get_font(location_size)
        
        # Wrap location if needed
        lines = self.wrap_text(location_text, font, self.width - 80)
        
        y = location_y
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y), line, font=font, fill=location_color)
            y += bbox[3] - bbox[1] + 5
    
    def _draw_speakers(self, img: Image.Image, draw: ImageDraw.Draw):
        """Draw speakers section"""
        speakers = self.config.get('speakers', [])
        if not speakers:
            return
        
        speakers_y_start = self.config.get('speakers_y_start', 550)
        speaker_spacing = self.config.get('speaker_spacing', 250)
        
        y_position = speakers_y_start
        
        for speaker in speakers:
            self._draw_speaker(img, draw, speaker, y_position)
            y_position += speaker_spacing
    
    def _draw_speaker(self, img: Image.Image, draw: ImageDraw.Draw, 
                     speaker: Dict, y_position: int):
        """Draw a single speaker"""
        # Load and draw photo
        photo_path = speaker.get('photo')
        photo_size = speaker.get('photo_size', [200, 200])
        photo_x = speaker.get('photo_x', 40)
        circular = speaker.get('circular_photo', True)  # Default to circular
        
        if photo_path:
            photo = self.load_and_resize_image(photo_path, tuple(photo_size), circular=circular)
            if photo:
                if photo.mode == 'RGBA':
                    img.paste(photo, (photo_x, y_position), photo)
                else:
                    img.paste(photo, (photo_x, y_position))
        
        # Draw speaker name
        name = speaker.get('name', '')
        name_color = speaker.get('name_color', '#FFFFFF')
        name_size = speaker.get('name_size', 48)
        name_x = photo_x + photo_size[0] + 30
        
        font_name = self.get_font(name_size, bold=True)
        draw.text((name_x, y_position), name, font=font_name, fill=name_color)
        
        # Draw speaker title/role
        role = speaker.get('role', '')
        role_color = speaker.get('role_color', '#E0E0E0')
        role_size = speaker.get('role_size', 32)
        
        font_role = self.get_font(role_size)
        draw.text((name_x, y_position + 60), role, font=font_role, fill=role_color)
        
        # Draw talk title
        talk_title = speaker.get('talk_title', '')
        talk_color = speaker.get('talk_color', '#FFFFFF')
        talk_size = speaker.get('talk_size', 36)
        
        font_talk = self.get_font(talk_size)
        
        # Wrap talk title
        max_width = self.width - name_x - 40
        talk_lines = self.wrap_text(talk_title, font_talk, max_width)
        
        talk_y = y_position + 110
        for line in talk_lines:
            draw.text((name_x, talk_y), line, font=font_talk, fill=talk_color)
            talk_y += 45
    
    def _draw_footer(self, img: Image.Image, draw: ImageDraw.Draw):
        """Draw footer with organized by section"""
        footer_config = self.config.get('footer', {})
        footer_text = footer_config.get('text', 'Organized By')
        footer_color = footer_config.get('color', '#FFFFFF')
        footer_size = footer_config.get('size', 36)
        footer_y = footer_config.get('y_position', self.height - 250)
        
        font = self.get_font(footer_size)
        
        bbox = draw.textbbox((0, 0), footer_text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, footer_y), footer_text, font=font, fill=footer_color)
        
        # Draw footer logo
        logo_path = footer_config.get('logo')
        if logo_path:
            logo_size = footer_config.get('logo_size', [100, 100])
            logo_y = footer_y + 60
            
            logo_img = self.load_and_resize_image(logo_path, tuple(logo_size))
            if logo_img:
                logo_x = (self.width - logo_size[0]) // 2
                if logo_img.mode == 'RGBA':
                    img.paste(logo_img, (logo_x, logo_y), logo_img)
                else:
                    img.paste(logo_img, (logo_x, logo_y))
    
    def save(self, img: Image.Image, output_path: str, formats: List[str] = ['jpg', 'webp']):
        """Save the image in multiple formats"""
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        base_path = os.path.splitext(output_path)[0]
        
        saved_files = []
        for fmt in formats:
            if fmt.lower() in ['jpg', 'jpeg']:
                # Convert RGBA to RGB for JPEG
                if img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
                    rgb_img.save(f"{base_path}.jpg", 'JPEG', quality=95)
                else:
                    img.save(f"{base_path}.jpg", 'JPEG', quality=95)
                saved_files.append(f"{base_path}.jpg")
            elif fmt.lower() == 'webp':
                img.save(f"{base_path}.webp", 'WEBP', quality=95)
                saved_files.append(f"{base_path}.webp")
            elif fmt.lower() == 'png':
                img.save(f"{base_path}.png", 'PNG')
                saved_files.append(f"{base_path}.png")
        
        return saved_files
