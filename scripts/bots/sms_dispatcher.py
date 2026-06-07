import json
import sys

def format_student_score_sms(student_name, score, percentage, topic_summary):
    """Compiles a highly concise text block optimized for parent SMS updates."""
    # Enforce strict capitalization for name references
    clean_name = student_name.strip().upper()
    
    sms_body = (
        f"ZANNIE ACADEMIC REPORT\n"
        f"Student: {clean_name}\n"
        f"Score: {score}/10 ({percentage}%)\n"
        f"Breakdown:\n"
    )
    
    # Append localized mastery indicators
    for topic, info in topic_summary.items():
        pass_rate = int((info['correct'] / info['total']) * 100)
        status = "Pass" if pass_rate >= 70 else "Review"
        sms_body += f"▪️ {topic}: {info['correct']}/{info['total']} ({status})\n"
        
    sms_body += "Log in to your portal terminal node to review the complete analytical dashboard chart."
    
    # Calculate SMS character segment bounds (160 characters per SMS unit)
    char_count = len(sms_body)
    segments = (char_count // 160) + 1
    
    return {
        "text": sms_body,
        "metrics": {
            "character_count": char_count,
            "sms_segments_required": segments
        }
    }

def format_system_alert_sms(service_name, alert_type, diagnostic_details):
    """Compiles immediate, character-bounded technical emergency templates for the administrator."""
    alert_body = (
        f"⚠️ CRITICAL SYSTEM ALERT\n"
        f"Node: UserLAnd Mobile Workspace\n"
        f"Service: {service_name}\n"
        f"Type: {alert_type.upper()}\n"
        f"Details: {diagnostic_details}\n"
        f"Action: Check ./log_monitor.sh logs immediately."
    )
    return {
        "text": alert_body,
        "metrics": {
            "character_count": len(alert_body),
            "sms_segments_required": (len(alert_body) // 160) + 1
        }
    }

if __name__ == "__main__":
    # Test Data Simulation Block
    print("============================================================")
    print("📱 ZANNIE AUTOMATED COMMUNICATION GATEWAY — OUTPUT TEMPLATES")
    print("============================================================")
    
    # Simulate a mockup score dataset for a student evaluation report
    sample_topics = {
        "Dimensions": {"correct": 3, "total": 3},
        "Mechanics": {"correct": 3, "total": 4},
        "Circular Motion": {"correct": 1, "total": 3}
    }
    
    student_sms = format_student_score_sms("TOOKI", 7, 70, sample_topics)
    print(f"👉 STUDENT REPORT OUTBOUND BLOCK:\n{student_sms['text']}")
    print(f"📊 [SMS Segment Weight: {student_sms['metrics']['character_count']} chars, {student_sms['metrics']['sms_segments_required']} segment]\n")
    
    print("------------------------------------------------------------")
    
    # Simulate an automated technical alert block
    alert_sms = format_system_alert_sms("Paystack Gateway Port 5001", "Rate Limit Flood Detected", "IP 127.0.0.1 triggered 429 status response blocks.")
    print(f"👉 ADMINISTRATIVE OUTBOUND ALERT:\n{alert_sms['text']}")
    print(f"📊 [SMS Segment Weight: {alert_sms['metrics']['character_count']} chars, {alert_sms['metrics']['sms_segments_required']} segment]")
    print("============================================================\n")
