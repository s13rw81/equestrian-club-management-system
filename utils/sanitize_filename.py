import re


def secure_filename(filename):
    """
    Sanitizes a filename to ensure it's safe and compatible with most file systems.
    """
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')

    # Remove any characters that are not alphanumeric, underscores, or dots
    filename = re.sub(r'[^\w\.\-]', '', filename)

    # Limit the filename length
    max_filename_length = 255  # Example maximum length
    filename = filename[:max_filename_length]

    return filename
