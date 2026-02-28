"""
Image processing utilities for thumbnails and EXIF extraction.
"""

from PIL import Image, ImageOps
import piexif
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def generate_thumbnail(image_path: str, thumbnail_path: str, size: tuple = (200, 200)) -> bool:
    """
    Generate a thumbnail from an image.
    
    Args:
        image_path: Path to original image
        thumbnail_path: Where to save thumbnail
        size: Thumbnail size (width, height)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if needed (for PNG with transparency)
            img = ImageOps.exif_transpose(img) 
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Create thumbnail (maintains aspect ratio)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save as JPEG
            img.save(thumbnail_path, "JPEG", quality=85, optimize=True)
            
            logger.info(f"Generated thumbnail: {thumbnail_path}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to generate thumbnail: {e}")
        return False


def extract_exif_data(image_path: str) -> dict:
    """
    Extract EXIF metadata from an image.
    
    Returns dict with:
        - date_taken: datetime when photo was taken
        - camera_make: Camera manufacturer
        - camera_model: Camera model
        - gps_latitude: GPS latitude
        - gps_longitude: GPS longitude
        - width: Image width in pixels
        - height: Image height in pixels
    """
    exif_data = {
        "date_taken": None,
        "camera_make": None,
        "camera_model": None,
        "gps_latitude": None,
        "gps_longitude": None,
        "width": None,
        "height": None,
    }
    
    try:
        # Open image and get basic dimensions
        with Image.open(image_path) as img:
            exif_data["width"] = img.width
            exif_data["height"] = img.height
            
            # Try to load EXIF data
            try:
                exif_dict = piexif.load(img.info.get("exif", b""))
            except:
                # No EXIF data or couldn't parse
                logger.info(f"No EXIF data found in {image_path}")
                return exif_data
            
            # Extract date taken
            if piexif.ExifIFD.DateTimeOriginal in exif_dict.get("Exif", {}):
                date_str = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode("utf-8")
                try:
                    # Format: "2024:07:15 14:30:22"
                    exif_data["date_taken"] = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                except:
                    pass
            
            # Extract camera info
            if piexif.ImageIFD.Make in exif_dict.get("0th", {}):
                exif_data["camera_make"] = exif_dict["0th"][piexif.ImageIFD.Make].decode("utf-8").strip()
            
            if piexif.ImageIFD.Model in exif_dict.get("0th", {}):
                exif_data["camera_model"] = exif_dict["0th"][piexif.ImageIFD.Model].decode("utf-8").strip()
            
            # Extract GPS coordinates
            gps_info = exif_dict.get("GPS", {})
            if piexif.GPSIFD.GPSLatitude in gps_info and piexif.GPSIFD.GPSLongitude in gps_info:
                # Convert GPS coordinates from degrees/minutes/seconds to decimal
                lat = gps_info[piexif.GPSIFD.GPSLatitude]
                lat_ref = gps_info.get(piexif.GPSIFD.GPSLatitudeRef, b"N").decode("utf-8")
                lon = gps_info[piexif.GPSIFD.GPSLongitude]
                lon_ref = gps_info.get(piexif.GPSIFD.GPSLongitudeRef, b"E").decode("utf-8")
                
                # Convert to decimal degrees
                exif_data["gps_latitude"] = convert_to_decimal(lat, lat_ref)
                exif_data["gps_longitude"] = convert_to_decimal(lon, lon_ref)
        
        logger.info(f"Extracted EXIF: camera={exif_data['camera_model']}, GPS={exif_data['gps_latitude']},{exif_data['gps_longitude']}")
        
    except Exception as e:
        logger.error(f"Error extracting EXIF: {e}")
    
    return exif_data


def convert_to_decimal(dms: tuple, ref: str) -> float:
    """
    Convert GPS coordinates from degrees/minutes/seconds to decimal.
    
    Args:
        dms: Tuple of ((degrees_num, degrees_den), (minutes_num, minutes_den), (seconds_num, seconds_den))
        ref: Reference ('N', 'S', 'E', 'W')
    
    Returns:
        Decimal degrees
    """
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1]
    seconds = dms[2][0] / dms[2][1]
    
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    # Make negative for South/West
    if ref in ['S', 'W']:
        decimal = -decimal
    
    return round(decimal, 6)  # 6 decimal places = ~10cm accuracy