import os
import json
from email_parser import parse_email, reconstruct_hop_path
from security_analyzer import analyze_security
from content_classifier import classify_email, calculate_fraud_score
from geolocator import get_originating_ip, geolocate_ip

def main():
    sample_dir = 'samples'
    samples = ['1_legit.eml', '2_phishing.eml', '3_bec.eml']
    
    for sample in samples:
        filepath = os.path.join(sample_dir, sample)
        print(f"\n{'='*60}\nParsing: {sample}\n{'='*60}")
        
        parsed_data = parse_email(filepath)
        
        if "error" in parsed_data:
            print(f"Error parsing file: {parsed_data['error']}")
            continue
            
        # Phase 1: Hops
        hops = reconstruct_hop_path(parsed_data.get('received_headers', []))
        parsed_data['hop_path'] = hops
        parsed_data.pop('received_headers', None)
        
        # Phase 4: Geolocation & Infrastructure Intel
        origin_ip = get_originating_ip(hops)
        geo_data = geolocate_ip(origin_ip)
        parsed_data['geo_assessment'] = geo_data
        
        # Phase 2: Security Validation
        security_results = analyze_security(parsed_data, filepath)
        parsed_data['security_analysis'] = security_results
        
        # Phase 3: Content Classification & Fraud Score
        text_to_classify = parsed_data.get('body_text') or parsed_data.get('subject') or ""
        ml_result = classify_email(text_to_classify)
        
        # Add VPN/Tor penalties if found by Phase 4
        anomaly_flags = security_results.get('anomaly_flags', [])
        if geo_data.get('is_tor'):
            anomaly_flags.append("Origin IP is a known Tor exit node")
        elif geo_data.get('is_vpn_or_hosting'):
            anomaly_flags.append("Origin IP is from a VPN/Hosting provider (Non-residential)")
            
        fraud_score_details = calculate_fraud_score(
            ml_result, 
            anomaly_flags
        )
        
        parsed_data['fraud_assessment'] = fraud_score_details
        
        print(json.dumps(parsed_data, indent=2))

if __name__ == '__main__':
    main()
