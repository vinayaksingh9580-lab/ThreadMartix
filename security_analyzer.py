import re
import os

try:
    import spf
    import dkim
    LIVE_LIBRARIES_AVAILABLE = True
except ImportError:
    LIVE_LIBRARIES_AVAILABLE = False

KNOWN_STRICT_DOMAINS = ['paypal.com', 'github.com', 'apple.com', 'bankofamerica.com']

def extract_domain(email_address):
    if not email_address or email_address == 'unknown':
        return None
    match = re.search(r'@([\w.-]+)', email_address)
    return match.group(1).lower() if match else None

def analyze_security(parsed_email, raw_file_path):
    flags = []
    
    spf_result = "unknown"
    dkim_result = "unknown"
    dmarc_result = "unknown"
    validation_method = "header-heuristic (offline fallback)"

    # Live verification attempt
    # We skip live check by default for hackathon dummy samples because DNS lookups
    # for fake domains (e.g. scam-server.ru, myc0mpany.com) will fail or hang.
    # In production, we'd toggle `force_live=True` here.
    force_live = False 

    if LIVE_LIBRARIES_AVAILABLE and force_live:
        try:
            # 1. Live SPF Check
            sender_ip = None
            if parsed_email.get('hop_path'):
                sender_ip = parsed_email['hop_path'][0].get('extracted_ip')
            
            return_path = parsed_email.get('return_path', '').strip('<>')
            if sender_ip and return_path and return_path != 'unknown':
                spf_res, code, exp = spf.check2(i=sender_ip, s=return_path, h=sender_ip)
                spf_result = spf_res.lower()
                validation_method = "live-dns"

            # 2. Live DKIM Check
            with open(raw_file_path, 'rb') as f:
                raw_msg = f.read()
                # dkim.verify returns True if valid
                dkim_valid = dkim.verify(raw_msg)
                dkim_result = "pass" if dkim_valid else "fail"
        except Exception as e:
            flags.append(f"Live DNS validation failed, using fallback. Error: {e}")
            validation_method = "header-heuristic (offline fallback)"

    # Fallback to header analysis if live is disabled or failed
    if validation_method == "header-heuristic (offline fallback)":
        auth_headers = parsed_email.get('raw_security_headers', {}).get('Authentication-Results', [])
        for header in auth_headers:
            header_lower = header.lower()
            if 'spf=pass' in header_lower: spf_result = "pass"
            elif 'spf=fail' in header_lower or 'spf=softfail' in header_lower: spf_result = "fail"
            
            if 'dkim=pass' in header_lower: dkim_result = "pass"
            elif 'dkim=fail' in header_lower: dkim_result = "fail"
            
            if 'dmarc=pass' in header_lower: dmarc_result = "pass"
            elif 'dmarc=fail' in header_lower: dmarc_result = "fail"

    # Specific missing check
    if not parsed_email.get('raw_security_headers', {}).get('DKIM-Signature'):
        flags.append("Missing DKIM signature entirely")
        dkim_result = "fail (missing)"

    # DMARC Alignment (From domain vs SPF Return-Path domain vs DKIM domain)
    from_domain = extract_domain(parsed_email.get('sender'))
    return_path_domain = extract_domain(parsed_email.get('return_path'))
    
    alignment_pass = False
    if from_domain and return_path_domain and from_domain == return_path_domain:
        alignment_pass = True
    else:
        flags.append("From domain does not match authenticated sending domain (SPF misaligned)")

    # DMARC depends on alignment and passing SPF/DKIM
    if validation_method == "header-heuristic (offline fallback)" and dmarc_result == "unknown":
        if alignment_pass and (spf_result == 'pass' or dkim_result == 'pass'):
            dmarc_result = "pass (inferred)"
        else:
            dmarc_result = "fail (inferred)"

    # BEC & Phishing Anomaly Flags
    reply_to = parsed_email.get('reply_to')
    if reply_to and reply_to != 'unknown':
        reply_to_domain = extract_domain(reply_to)
        if reply_to_domain and reply_to_domain != from_domain:
            flags.append("Reply-To differs from From address (Classic BEC pattern)")

    if spf_result in ['fail', 'fail (inferred)'] and from_domain in KNOWN_STRICT_DOMAINS:
        flags.append("SPF fails but email claims to be from a known-strict domain (High Phishing Risk)")

    # BEC lookalike domain detection (e.g., myc0mpany.com instead of mycompany.com)
    if from_domain and re.search(r'[0-9]', from_domain):
         flags.append(f"Sender domain '{from_domain}' contains numbers (Possible lookalike/typo-squatting)")

    return {
        "validation_method": validation_method,
        "spf_result": spf_result,
        "dkim_result": dkim_result,
        "dmarc_result": dmarc_result,
        "alignment_pass": alignment_pass,
        "anomaly_flags": flags
    }
