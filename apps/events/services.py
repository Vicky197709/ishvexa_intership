import hashlib


def generate_fingerprint(message: str, stack_trace: str = "") -> str:
    """
    Generate a fingerprint for an event based on message and top stack frame.
    
    Args:
        message: The error message
        stack_trace: The full stack trace (optional)
    
    Returns:
        SHA256 hash of the normalized message and top stack frame
    """
    # Normalize message
    normalized_message = message.strip().lower()
    
    # Extract top stack frame (first line if stack_trace exists)
    if stack_trace:
        lines = stack_trace.strip().split('\n')
        top_frame = lines[0] if lines else ""
    else:
        top_frame = ""
    
    # Create fingerprint
    fingerprint_data = f"{normalized_message}|{top_frame}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()
