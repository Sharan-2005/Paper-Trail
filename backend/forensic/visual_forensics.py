"""
Visual forensics service using OpenCV and Pillow.
Implements ELA, metadata inspection, and compression analysis.
"""

import os
import io
import logging
import tempfile
from pathlib import Path
from typing import Optional

from config import UPLOAD_DIR

logger = logging.getLogger(__name__)

try:
    from PIL import Image, ImageChops, ImageEnhance, ImageFilter
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False
    logger.warning("Pillow not available – visual forensics limited")

try:
    import cv2
    import numpy as np
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False
    logger.warning("OpenCV not available – visual forensics limited")


# ─── ELA (Error Level Analysis) ───────────────────────────────────

def perform_ela(image_path: str, quality: int = 90, scale: float = 10.0) -> dict:
    """
    Perform Error Level Analysis on a JPEG image.
    Saves the ELA result image and returns analysis details.
    """
    if not _PIL_AVAILABLE:
        return {"available": False, "reason": "Pillow not installed"}

    try:
        original = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {"available": False, "reason": f"Cannot open image: {e}"}

    # Only ELA on JPEG/lossy images
    img_path = Path(image_path)
    if img_path.suffix.lower() not in (".jpg", ".jpeg"):
        return {
            "available": True,
            "performed": False,
            "reason": "ELA is most effective on JPEG images. PNG files do not use lossy compression.",
        }

    try:
        # Save at reduced quality and compare
        buffer = io.BytesIO()
        original.save(buffer, "JPEG", quality=quality)
        buffer.seek(0)
        recompressed = Image.open(buffer)

        # Compute absolute difference
        diff = ImageChops.difference(original, recompressed)
        diff_array = list(diff.getdata())

        # Scale up the difference for visibility
        ela_img = Image.new("RGB", original.size)
        scaled_pixels = []
        max_val = 0
        for pixel in diff_array:
            scaled = tuple(min(255, int(c * scale)) for c in pixel)
            scaled_pixels.append(scaled)
            max_val = max(max_val, max(pixel))

        ela_img.putdata(scaled_pixels)

        # Save ELA image
        ela_filename = f"ela_{img_path.stem}.jpg"
        ela_path = str(UPLOAD_DIR / ela_filename)
        ela_img.save(ela_path, "JPEG", quality=95)

        # Analyze variance
        import statistics
        brightness_values = [sum(p) / 3 for p in diff_array]
        mean_brightness = statistics.mean(brightness_values)
        stdev_brightness = statistics.stdev(brightness_values) if len(brightness_values) > 1 else 0

        suspicious = mean_brightness > 15 or stdev_brightness > 20

        return {
            "available": True,
            "performed": True,
            "ela_image_path": ela_path,
            "ela_image_url": f"/uploads/{ela_filename}",
            "mean_error_level": round(mean_brightness, 2),
            "std_error_level": round(stdev_brightness, 2),
            "max_pixel_error": max_val,
            "potentially_suspicious": suspicious,
            "interpretation": (
                "Elevated error levels in certain image regions may indicate re-saved or modified areas. "
                "This is a preliminary observation and requires manual verification by a certified forensic examiner."
            ) if suspicious else (
                "Error levels appear relatively uniform across the image, which is consistent with an unmodified JPEG."
            ),
            "disclaimer": (
                "ELA is a heuristic tool. Results are not conclusive evidence of manipulation. "
                "Many legitimate processing operations (scanning, compression) can produce elevated ELA values."
            ),
        }

    except Exception as e:
        logger.error(f"ELA error: {e}")
        return {"available": True, "performed": False, "reason": f"ELA failed: {e}"}


# ─── Metadata extraction ───────────────────────────────────────────

def extract_image_metadata(image_path: str) -> dict:
    """Extract EXIF and basic metadata from an image."""
    if not _PIL_AVAILABLE:
        return {"available": False}

    try:
        img = Image.open(image_path)
        meta = {
            "format": img.format,
            "mode": img.mode,
            "size": {"width": img.size[0], "height": img.size[1]},
            "dpi": img.info.get("dpi"),
        }

        # EXIF data
        exif_data = {}
        try:
            from PIL.ExifTags import TAGS
            exif_raw = img._getexif()
            if exif_raw:
                for tag_id, value in exif_raw.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if isinstance(value, (str, int, float, tuple)):
                        exif_data[str(tag)] = str(value)[:200]
        except Exception:
            pass

        meta["exif"] = exif_data
        meta["has_exif"] = bool(exif_data)
        
        # Suspicious: missing EXIF on a document image, or software tags suggesting editing
        editing_software = []
        for key, val in exif_data.items():
            if "software" in key.lower():
                editing_software.append(val)
        
        meta["editing_software_detected"] = editing_software
        meta["available"] = True
        return meta

    except Exception as e:
        return {"available": True, "error": str(e)}


# ─── Compression analysis ──────────────────────────────────────────

def analyze_compression(image_path: str) -> dict:
    """Analyze image compression characteristics."""
    if not _CV2_AVAILABLE:
        return {"available": False}

    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"available": True, "error": "Could not read image"}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Check for block artifacts (JPEG compression blocks)
        h, w = gray.shape
        block_variance = []
        for y in range(0, h - 8, 8):
            for x in range(0, w - 8, 8):
                block = gray[y:y+8, x:x+8]
                block_variance.append(float(np.var(block)))

        mean_bv = float(np.mean(block_variance)) if block_variance else 0
        std_bv = float(np.std(block_variance)) if block_variance else 0

        # High variance in block artifacts may suggest inconsistency
        suspicious = std_bv > mean_bv * 2 and mean_bv > 10

        # Noise analysis
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        return {
            "available": True,
            "mean_block_variance": round(mean_bv, 2),
            "std_block_variance": round(std_bv, 2),
            "laplacian_variance": round(laplacian_var, 2),
            "potentially_suspicious": suspicious,
            "interpretation": (
                "Significant variation in compression block characteristics detected. "
                "This may warrant further examination."
            ) if suspicious else (
                "Compression characteristics appear consistent across the image."
            ),
        }

    except Exception as e:
        return {"available": True, "error": str(e)}


# ─── Brightness/contrast analysis ─────────────────────────────────

def analyze_brightness_consistency(image_path: str) -> dict:
    """Check for brightness and contrast inconsistencies across image regions."""
    if not _CV2_AVAILABLE:
        return {"available": False}

    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"available": True, "error": "Could not read image"}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # Divide into 4 quadrants and compare brightness
        regions = {
            "top_left": gray[:h//2, :w//2],
            "top_right": gray[:h//2, w//2:],
            "bottom_left": gray[h//2:, :w//2],
            "bottom_right": gray[h//2:, w//2:],
        }

        region_stats = {}
        means = []
        for name, region in regions.items():
            m = float(np.mean(region))
            s = float(np.std(region))
            region_stats[name] = {"mean": round(m, 1), "std": round(s, 1)}
            means.append(m)

        overall_variance = float(np.var(means))
        suspicious = overall_variance > 400  # Empirical threshold

        return {
            "available": True,
            "region_stats": region_stats,
            "overall_brightness_variance": round(overall_variance, 2),
            "potentially_suspicious": suspicious,
            "interpretation": (
                "Significant brightness inconsistency detected across image regions. "
                "This may indicate image compositing or selective editing."
            ) if suspicious else (
                "Brightness distribution appears consistent across image regions."
            ),
        }

    except Exception as e:
        return {"available": True, "error": str(e)}


# ─── Main forensics runner ─────────────────────────────────────────

def run_visual_forensics(file_path: str, file_type: str) -> dict:
    """
    Run all visual forensic checks on a document image.
    Returns combined results.
    """
    results = {
        "file_path": file_path,
        "file_type": file_type,
        "checks": {},
        "summary": {
            "total_checks": 0,
            "suspicious_findings": 0,
            "overall_assessment": "normal",
        },
        "disclaimer": (
            "Visual forensic analysis provides preliminary observations only. "
            "Findings are not conclusive evidence of document manipulation. "
            "All observations require manual verification by qualified forensic examiners."
        ),
    }

    # Only run on image files
    if file_type.lower() not in ("jpg", "jpeg", "png", "image"):
        results["checks"]["note"] = "Visual forensics available for image files only. For PDFs, individual page images are analyzed."
        return results

    # Run checks
    checks_run = 0
    suspicious_count = 0

    ela = perform_ela(file_path)
    results["checks"]["ela"] = ela
    if ela.get("performed"):
        checks_run += 1
        if ela.get("potentially_suspicious"):
            suspicious_count += 1

    metadata = extract_image_metadata(file_path)
    results["checks"]["metadata"] = metadata
    if metadata.get("available"):
        checks_run += 1
        if metadata.get("editing_software_detected"):
            suspicious_count += 1

    compression = analyze_compression(file_path)
    results["checks"]["compression"] = compression
    if compression.get("available") and not compression.get("error"):
        checks_run += 1
        if compression.get("potentially_suspicious"):
            suspicious_count += 1

    brightness = analyze_brightness_consistency(file_path)
    results["checks"]["brightness"] = brightness
    if brightness.get("available") and not brightness.get("error"):
        checks_run += 1
        if brightness.get("potentially_suspicious"):
            suspicious_count += 1

    results["summary"]["total_checks"] = checks_run
    results["summary"]["suspicious_findings"] = suspicious_count

    if suspicious_count == 0:
        results["summary"]["overall_assessment"] = "normal"
    elif suspicious_count == 1:
        results["summary"]["overall_assessment"] = "minor_anomaly"
    elif suspicious_count == 2:
        results["summary"]["overall_assessment"] = "moderate_anomaly"
    else:
        results["summary"]["overall_assessment"] = "significant_anomaly"

    return results

