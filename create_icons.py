from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Creează o iconiță simplă pentru PWA"""
    # Creează o imagine cu fundal albastru
    img = Image.new('RGB', (size, size), color='#007bff')
    draw = ImageDraw.Draw(img)
    
    # Adaugă text "AI" în centru
    try:
        # Încearcă să folosească o font mai mare
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback la font default
        font = ImageFont.load_default()
    
    text = "AI"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Salvează iconița
    img.save(f'static/{filename}')
    print(f"Creată iconița: {filename} ({size}x{size})")

def main():
    """Creează toate iconițele necesare pentru PWA"""
    # Creează directorul static dacă nu există
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Lista de iconițe necesare
    icons = [
        (16, 'icon-16.png'),
        (32, 'icon-32.png'),
        (72, 'icon-72.png'),
        (96, 'icon-96.png'),
        (128, 'icon-128.png'),
        (144, 'icon-144.png'),
        (152, 'icon-152.png'),
        (192, 'icon-192.png'),
        (384, 'icon-384.png'),
        (512, 'icon-512.png')
    ]
    
    for size, filename in icons:
        create_icon(size, filename)
    
    print("Toate iconițele au fost create cu succes!")

if __name__ == "__main__":
    main() 