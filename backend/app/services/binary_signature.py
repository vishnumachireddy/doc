import os

# Magic numbers mapping
MAGIC_NUMBERS = {
    "pdf": [b"\x25\x50\x44\x46"],                  # %PDF
    "docx": [b"\x50\x4b\x03\x04"],                 # PK.. (ZIP header used by Office Open XML)
    "png": [b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"],  # \x89PNG\r\n\x1a\n
    "jpg": [b"\xff\xd8\xff\xe0", b"\xff\xd8\xff\xe1", b"\xff\xd8\xff\xe2", b"\xff\xd8\xff\xe8", b"\xff\xd8\xff"] # JPEG markers
}

def validate_binary_signature(file_path: str) -> str | None:
    """
    Validates the binary file header against the file extension.
    Returns the detected extension (e.g. 'pdf', 'docx', 'png', 'jpg') if valid,
    or None if the file is spoofed or unsupported.
    """
    ext = os.path.splitext(file_path.lower())[1].lstrip(".")
    if ext == "jpeg":
        ext = "jpg"
        
    if ext not in MAGIC_NUMBERS:
        return None

    try:
        with open(file_path, "rb") as f:
            header = f.read(8)
            
        expected_magics = MAGIC_NUMBERS[ext]
        for magic in expected_magics:
            if header.startswith(magic):
                return ext
                
        # Also auto-detect if the extension was wrong but the content is supported
        for actual_ext, magics in MAGIC_NUMBERS.items():
            for magic in magics:
                if header.startswith(magic):
                    return actual_ext
                    
        return None
    except Exception:
        return None
