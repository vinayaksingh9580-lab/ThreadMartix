import email
from email import policy
import re

def extract_ip(text):
    """
    Extracts the first IPv4 address found in a string.
    Useful for pulling the sender's IP from a 'Received' header.
    """
    match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text)
    return match.group(0) if match else None

def parse_email(file_path):
    """
    Reads an .eml file and returns a structured dictionary of its contents.
    Designed to degrade gracefully on missing or malformed headers.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            # policy.default parses headers cleanly and handles decoding
            msg = email.message_from_file(f, policy=policy.default)
    except Exception as e:
        return {"error": f"Failed to open or parse email: {e}"}

    # 1. Basic Metadata
    # We use 'unknown' as a fallback to ensure we never crash on missing fields
    sender = str(msg.get('From', 'unknown'))
    
    display_name = 'unknown'
    if sender != 'unknown':
        # Simple extraction: "Display Name" <user@domain> -> Display Name
        match = re.match(r'(.*?)<.*>', sender)
        if match:
            display_name = match.group(1).strip(' "\'')

    subject = str(msg.get('Subject', 'unknown'))
    
    # 2. Body Extraction
    # Emails can be multipart (HTML + Text) or single part. We extract both if available.
    body_text = None
    body_html = None
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition'))
            # Ignore attachments
            if 'attachment' not in content_disposition:
                if content_type == 'text/plain':
                    try:
                        body_text = part.get_content()
                    except:
                        pass
                elif content_type == 'text/html':
                    try:
                        body_html = part.get_content()
                    except:
                        pass
    else:
        content_type = msg.get_content_type()
        if content_type == 'text/plain':
            try:
                body_text = msg.get_content()
            except:
                pass
        elif content_type == 'text/html':
            try:
                body_html = msg.get_content()
            except:
                pass

    # 3. Routing & Forensic Headers
    # get_all returns a list of all instances of a header, preserving order
    received_headers = msg.get_all('Received', [])
    msg_id = str(msg.get('Message-ID', 'unknown'))
    reply_to = str(msg.get('Reply-To', 'unknown'))
    return_path = str(msg.get('Return-Path', 'unknown'))

    # 4. Security Assessment Headers
    # We just extract them here. Validation/parsing happens in a later phase.
    auth_results = msg.get_all('Authentication-Results', [])
    received_spf = msg.get_all('Received-SPF', [])
    dkim_signatures = msg.get_all('DKIM-Signature', [])

    return {
        "sender": sender.strip(),
        "display_name": display_name,
        "subject": subject,
        "body_text": body_text.strip() if body_text else None,
        "body_html": body_html.strip() if body_html else None,
        "received_headers": received_headers,
        "message_id": msg_id,
        "reply_to": reply_to,
        "return_path": return_path,
        "raw_security_headers": {
            "Authentication-Results": auth_results,
            "Received-SPF": received_spf,
            "DKIM-Signature": dkim_signatures
        }
    }

def reconstruct_hop_path(received_headers):
    """
    Parses 'Received' headers to reconstruct the SMTP relay chain.
    Headers are added at the top by each receiving MTA, so we process 
    them in reverse order (bottom-to-top) to get chronological hops.
    """
    hops = []
    # Process in reverse to reflect the actual flow of the email
    for i, header in enumerate(reversed(received_headers)):
        # Normalize whitespace (newlines and tabs to spaces)
        header_clean = re.sub(r'\s+', ' ', str(header))
        
        from_host = "unknown"
        by_host = "unknown"
        timestamp = "unknown"

        # Regex parsing for messy headers. We use non-greedy matching.
        # Typical format: from [sender] by [receiver] with [protocol] id [id] ; [date]
        from_match = re.search(r'from\s+([^;]+?)(?=\s+by|\s+with|\s+id|;|$)', header_clean, re.IGNORECASE)
        by_match = re.search(r'by\s+([^;]+?)(?=\s+with|\s+id|\s+for|;|$)', header_clean, re.IGNORECASE)
        
        # Date is almost always appended after the final semicolon
        parts = header_clean.rsplit(';', 1)
        if len(parts) == 2:
            timestamp = parts[1].strip()

        if from_match:
            from_host = from_match.group(1).strip()
        if by_match:
            by_host = by_match.group(1).strip()

        extracted_ip = extract_ip(header_clean)

        hops.append({
            "hop_number": i + 1,
            "from_host": from_host,
            "by_host": by_host,
            "timestamp": timestamp,
            "extracted_ip": extracted_ip
        })
    return hops
