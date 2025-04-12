# slide_generator.py

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
    img = Image.new("RGB", (1080, 1080))
    draw = ImageDraw.Draw(img)
    
    colors = [
        [(20, 30, 48), (36, 59, 85)],      # Deep Blue
        [(48, 25, 52), (95, 44, 130)],     # Royal Purple
        [(20, 36, 50), (71, 120, 140)],    # Ocean Blue
        [(40, 30, 50), (70, 50, 90)]       # Night Purple
    ]
    
    color1, color2 = random.choice(colors)
    
    for y in range(1080):
        r = int(color1[0] + (color2[0] - color1[0]) * y / 1080)
        g = int(color1[1] + (color2[1] - color1[1]) * y / 1080)
        b = int(color1[2] + (color2[2] - color1[2]) * y / 1080)
        draw.line([(0, y), (1080, y)], fill=(r, g, b))
    
    return img

def get_font(name, size):
    """Get font with fallbacks"""
    try:
        font_paths = {
            'title': "C:\\Windows\\Fonts\\SEGOEUI.TTF",
            'bold': "C:\\Windows\\Fonts\\SEGOEUIB.TTF",
            'number': "C:\\Windows\\Fonts\\SEGUIBL.TTF"
        }
        return ImageFont.truetype(font_paths.get(name, font_paths['title']), size)
    except:
        return ImageFont.load_default()

def get_design_variant(index):
    """Get design variant based on slide index"""
    variants = [
        {
            'overlay_color': (0, 0, 0, 180),  # Dark overlay
            'headline_color': (255, 255, 255),  # White
            'link_color': (29, 161, 242),  # Twitter Blue
            'accent_color': (200, 200, 200)  # Light Gray
        },
        {
            'overlay_color': (20, 23, 26, 200),  # Dark blue overlay
            'headline_color': (255, 255, 255),  # White
            'link_color': (255, 122, 0),  # Orange
            'accent_color': (180, 180, 180)  # Light Gray
        },
        {
            'overlay_color': (26, 20, 26, 200),  # Dark purple overlay
            'headline_color': (255, 255, 255),  # White
            'link_color': (0, 255, 153),  # Mint Green
            'accent_color': (180, 180, 180)  # Light Gray
        },
        {
            'overlay_color': (26, 20, 20, 200),  # Dark red overlay
            'headline_color': (255, 255, 255),  # White
            'link_color': (255, 204, 0),  # Gold
            'accent_color': (180, 180, 180)  # Light Gray
        }
    ]
    return variants[index % len(variants)]

def add_overlay(img, color):
    """Add a semi-transparent overlay"""
    overlay = Image.new('RGBA', img.size, color)
    img_rgba = img.convert('RGBA')
    composite = Image.alpha_composite(img_rgba, overlay)
    return composite.convert('RGB')  # Convert back to RGB for JPEG saving

def wrap_text(text, font, max_width, max_lines=4):
    """Wrap text to fit width and line limit"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        # Try adding the word
        test_line = current_line + [word]
        test_width = font.getlength(' '.join(test_line))
        
        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(' '.join(current_line))
                if len(lines) >= max_lines:
                    # Add ellipsis to last line if truncated
                    lines[-1] = lines[-1].rstrip() + "..."
                    break
                current_line = [word]
            else:
                # Word is too long, split it
                lines.append(word)
                if len(lines) >= max_lines:
                    break
                current_line = []
    
    if current_line and len(lines) < max_lines:
        lines.append(' '.join(current_line))
    
    return lines

def shorten_url(url):
    """Shorten URL to fit in the slide"""
    if len(url) > 40:
        return url[:37] + "..."
    return url

def get_search_terms(title, category):
    """Get better search terms from news title and category"""
    # Remove common words that don't help in image search
    common_words = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    
    # Extract key terms from title
    words = title.lower().split()
    key_terms = [word for word in words if word not in common_words]
    
    # Get the most relevant 2-3 terms
    if len(key_terms) > 3:
        # For longer titles, take first and last important words
        search_terms = key_terms[:2] + [key_terms[-1]]
    else:
        search_terms = key_terms
    
    # Add category-specific terms
    category_terms = {
        'sports': ['sports', 'game', 'match'],
        'business': ['business', 'finance', 'corporate'],
        'technology': ['tech', 'technology', 'digital'],
        'entertainment': ['entertainment', 'movie', 'cinema'],
        'india': ['india', 'indian'],
        'world': ['world', 'global', 'international']
    }
    
    # Add relevant category term
    if category.lower() in category_terms:
        search_terms.append(category_terms[category.lower()][0])
    
    # Clean and join terms
    clean_terms = []
    for term in search_terms:
        # Remove special characters
        term = ''.join(c for c in term if c.isalnum() or c.isspace())
        if term and len(term) > 2:  # Only keep meaningful terms
            clean_terms.append(term)
    
    # Create search query
    search_query = '+'.join(clean_terms[:3])  # Limit to 3 terms for best results
    print(f"🔍 Image search terms: {search_query}")
    return search_query

def generate_slide(news_item, index, total_slides):
    """Generate a professional-looking slide"""
    try:
        # Create base image with news-related background
        if index == 0:
            # Title slide with news-related background
            base_img = get_news_image("newspaper+headlines+press")
            design = {
                'overlay_color': (0, 0, 0, 180),
                'headline_color': (255, 255, 255),
                'link_color': (29, 161, 242),
                'accent_color': (200, 200, 200)
            }
        else:
            # Get relevant image for the headline
            search_terms = get_search_terms(news_item['title'], news_item['category'])
            base_img = get_news_image(search_terms)
            design = get_design_variant(index)
        
        # Ensure correct size and convert to RGB
        base_img = ImageOps.fit(base_img, (1080, 1080))
        
        # Add dark overlay for readability
        img = add_overlay(base_img, design['overlay_color'])
        draw = ImageDraw.Draw(img)
        
        if index == 0:
            # Title slide
            title_font = get_font('bold', 100)
            subtitle_font = get_font('title', 50)
            date_font = get_font('title', 40)
            
            # Main title
            draw.text((540, 400), "TODAY'S", font=title_font, fill=design['headline_color'], anchor="mm")
            draw.text((540, 500), "HEADLINES", font=title_font, fill=design['headline_color'], anchor="mm")
            
            # Date
            current_date = datetime.now().strftime("%d %B %Y")
            draw.text((540, 600), current_date, font=date_font, fill=design['accent_color'], anchor="mm")
            
            # Bottom text
            draw.text((540, 950), "Swipe right →", font=subtitle_font, fill=design['accent_color'], anchor="mm")
        else:
            # News slides
            number_font = get_font('number', 120)
            headline_font = get_font('bold', 60)
            note_font = get_font('title', 35)
            
            # Slide number
            number_text = f"{index}/{total_slides-1}"
            draw.text((100, 100), number_text, font=number_font, fill=design['headline_color'])
            
            # Headline - limit to 4 lines
            lines = wrap_text(news_item['title'], headline_font, 900, max_lines=4)
            y = 380  # Start slightly higher for 4 lines
            line_height = 70
            for line in lines:
                draw.text((540, y), line, font=headline_font, fill=design['headline_color'], anchor="mm")
                y += line_height
            
            # Note at bottom
            note_text = "Find details in caption ↓"
            draw.text((540, 950), note_text, font=note_font, fill=design['accent_color'], anchor="mm")
        
        return img
    except Exception as e:
        print(f"Error generating slide {index}: {e}")
        # Fallback to simple gradient background
        return create_gradient_background()

def generate_all_slides(news_items):
    """Generate all slides with proper numbering"""
    folder = "slides"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Clean old slides
    for filename in os.listdir(folder):
        if filename.endswith(".jpg"):
            os.remove(os.path.join(folder, filename))
    
    total_slides = len(news_items) + 1  # Including title slide
    
    try:
        # Generate title slide
        print("🎨 Generating title slide...")
        title_slide = generate_slide({"title": "Title"}, 0, total_slides)
        title_slide.save(os.path.join(folder, "01_title.jpg"), 
                        format='JPEG', quality=95, optimize=True)
        
        # Generate news slides
        for i, news_item in enumerate(news_items, 1):
            print(f"🎨 Generating slide {i}/{len(news_items)}...")
            slide_num = str(i + 1).zfill(2)  # Ensures proper sorting: 01, 02, etc.
            img = generate_slide(news_item, i, total_slides)
            img.save(os.path.join(folder, f"{slide_num}_news.jpg"), 
                    format='JPEG', quality=95, optimize=True)
            print(f"✅ Generated slide {i}: {news_item['title'][:50]}...")
    except Exception as e:
        print(f"❌ Error generating slides: {e}")
        raise  # Re-raise the exception for proper error handling
