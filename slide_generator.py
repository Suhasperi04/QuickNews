from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import os
import random
from datetime import datetime
import requests
from io import BytesIO
import textwrap

def get_news_image(query):
    """Get a relevant image for the news headline"""
    try:
        # Using Unsplash API for demo (replace with your preferred image API)
        url = f"https://source.unsplash.com/1080x1080/?{query}"
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        # Fallback to gradient if image fetch fails
        return create_gradient_background()

def create_gradient_background():
    """Create a professional gradient background"""
    img = Image.new('RGB', (1080, 1080))
    draw = ImageDraw.Draw(img)
    
    # Professional color schemes
    color_schemes = [
        [(53, 92, 125), (108, 91, 123), (192, 108, 132)],  # Professional blue-purple
        [(40, 82, 122), (69, 123, 157), (137, 181, 175)],  # Business blue
        [(67, 76, 94), (100, 111, 135), (154, 140, 152)],  # Corporate gray
        [(44, 62, 80), (52, 73, 94), (93, 109, 126)]       # Dark professional
    ]
    
    colors = random.choice(color_schemes)
    for i in range(1080):
        # Create smooth gradient
        r = int(colors[0][0] + (i/1080) * (colors[-1][0] - colors[0][0]))
        g = int(colors[0][1] + (i/1080) * (colors[-1][1] - colors[0][1]))
        b = int(colors[0][2] + (i/1080) * (colors[-1][2] - colors[0][2]))
        draw.line([(i, 0), (i, 1080)], fill=(r, g, b))
    
    return img

def get_font(name, size):
    """Get font with fallbacks"""
    try:
        font_path = os.path.join("fonts", name)
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        # Try system fonts as fallback
        system_font = None
        if os.name == 'nt':  # Windows
            system_font = 'arial.ttf'
        else:  # Unix-like
            system_font = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        return ImageFont.truetype(system_font, size)
    except Exception as e:
        print(f"Warning: Could not load font {name}, using default. Error: {e}")
        return ImageFont.load_default()

def get_design_variant(index):
    """Get design variant based on slide index"""
    variants = [
        {
            'title_size': 60,
            'desc_size': 36,
            'title_pos': (540, 200),
            'desc_pos': (540, 600),
            'max_title_width': 900,
            'max_desc_width': 800
        },
        {
            'title_size': 55,
            'desc_size': 32,
            'title_pos': (540, 250),
            'desc_pos': (540, 650),
            'max_title_width': 850,
            'max_desc_width': 750
        }
    ]
    return random.choice(variants)

def wrap_text(text, font, max_width, max_lines=4):
    """Wrap text to fit width and line limit"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        # Try adding the word
        test_line = current_line + [word]
        width = font.getlength(' '.join(test_line))
        
        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                if len(lines) >= max_lines:
                    break
            else:
                # Word is too long, force split
                lines.append(word)
                if len(lines) >= max_lines:
                    break
    
    if current_line and len(lines) < max_lines:
        lines.append(' '.join(current_line))
    
    # If we have too many lines, add ellipsis
    if len(lines) > max_lines:
        lines = lines[:max_lines-1] + [lines[-1] + '...']
    
    return '\n'.join(lines)

def generate_slide(news_item, index, total_slides):
    """Generate a professional-looking slide"""
    # Get design variant
    design = get_design_variant(index)
    
    # Create base image
    img = create_gradient_background()
    
    # Try to get relevant image
    search_terms = news_item['title'].split()[:3]  # Use first 3 words
    try:
        news_img = get_news_image(' '.join(search_terms))
        # Ensure both images are in the same mode before blending
        if news_img.mode != img.mode:
            news_img = news_img.convert(img.mode)
        # Resize news_img to match base image size
        news_img = news_img.resize(img.size, Image.Resampling.LANCZOS)
        # Blend with gradient
        img = Image.blend(img, news_img, 0.3)
    except Exception as e:
        print(f"Warning: Could not blend image, using gradient. Error: {e}")
    
    # Add overlay for better text visibility
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 100))
    img = Image.alpha_composite(img.convert('RGBA'), overlay)
    
    # Create draw object
    draw = ImageDraw.Draw(img)
    
    # Draw title
    title_font = get_font('DejaVuSans-Bold.ttf', design['title_size'])
    title_text = wrap_text(news_item['title'], title_font, design['max_title_width'], 3)
    title_bbox = draw.textbbox(design['title_pos'], title_text, font=title_font, anchor='mm')
    draw.text(design['title_pos'], title_text, font=title_font, fill='white', anchor='mm', align='center')
    
    # Draw description if available
    if 'description' in news_item and news_item['description']:
        desc_font = get_font('DejaVuSans.ttf', design['desc_size'])
        desc_text = wrap_text(news_item['description'], desc_font, design['max_desc_width'], 4)
        draw.text(design['desc_pos'], desc_text, font=desc_font, fill='white', anchor='mm', align='center')
    
    # Add slide number
    number_font = get_font('DejaVuSans.ttf', 24)
    draw.text((1020, 1040), f'{index}/{total_slides}', font=number_font, fill='white', anchor='mm')
    
    # Convert back to RGB
    img = img.convert('RGB')
    
    return img

def generate_all_slides(news_items):
    """Generate all slides for the news items"""
    try:
        # Create slides directory if not exists
        os.makedirs('slides', exist_ok=True)
        
        # Clear existing slides
        for f in os.listdir('slides'):
            if f.endswith('.jpg'):
                os.remove(os.path.join('slides', f))
        
        # Generate slides
        slide_paths = []
        total_slides = len(news_items)
        
        for i, news in enumerate(news_items, 1):
            slide = generate_slide(news, i, total_slides)
            path = os.path.join('slides', f'slide_{i:02d}.jpg')
            slide.save(path, 'JPEG', quality=95)
            slide_paths.append(path)
            print(f"✅ Generated slide {i}/{total_slides}")
        
        return slide_paths
        
    except Exception as e:
        print(f"❌ Error generating slides: {e}")
        return []
