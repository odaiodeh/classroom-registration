import qrcode
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import os
import socket
import platform

def reshape_arabic_text(text):
    """Reshape Arabic text for proper display"""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def generate_qr_code(data: str, size: int = 300) -> Image:
    """Generate a QR code image"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Connect to an external server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def get_public_ip():
    """Get the public IP address (for cloud deployment)"""
    try:
        import requests
        # Try AWS EC2 metadata service first
        try:
            response = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4', timeout=2)
            if response.status_code == 200:
                return response.text.strip()
        except:
            pass
        
        # Fallback to external service
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except:
            pass
            
        # Last fallback to another service
        try:
            response = requests.get('https://checkip.amazonaws.com', timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except:
            pass
            
    except Exception:
        pass
    
    return None

def get_registration_url(port=5002, base_url=None):
    """Generate the registration URL for QR code"""
    if base_url:
        # Use provided base URL (for cloud deployment)
        return f"{base_url}/register"
    
    # Try to get public IP first (for cloud)
    public_ip = get_public_ip()
    if public_ip:
        return f"http://{public_ip}:{port}/register"
    
    # Fallback to local IP
    local_ip = get_local_ip()
    return f"http://{local_ip}:{port}/register"

# Define all classes
CLASSES = [
    "الرابع أ",
    "الرابع ب", 
    "الرابع ج",
    "الرابع د",
    "الرابع هـ",
    "الخامس أ",
    "الخامس ب",
    "الخامس ج", 
    "الخامس د",
    "السادس أ",
    "السادس ب",
    "السادس ج",
    "السادس د",
    "السادس هـ"
]

# Color scheme for modern UI
COLORS = {
    'primary': '#2E86AB',      # Blue
    'secondary': '#A23B72',    # Purple-pink
    'success': '#4CAF50',      # Green
    'danger': '#F44336',       # Red
    'warning': '#FF9800',      # Orange
    'info': '#00BCD4',         # Cyan
    'background': '#F5F5F5',   # Light gray
    'card_bg': '#FFFFFF',      # White
    'text_primary': '#212121', # Dark gray
    'text_secondary': '#757575' # Medium gray
}

# Grade colors
GRADE_COLORS = {
    'الرابع': '#3498db',   # Blue
    'الخامس': '#e74c3c',  # Red
    'السادس': '#2ecc71'   # Green
}
