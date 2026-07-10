import threading
import time
import subprocess
from flask import Flask, render_template, jsonify
from scapy.all import sniff, IP
from core.model import initialize_parameters, gru_forward_sequence
from core.extractor import PacketFeatureExtractor

app = Flask(__name__)


state_lock = threading.Lock()
recent_logs = []
blocked_ips = set()
current_metrics = {"status": "Initializing", "last_score": 0.0, "active_window_count": 0}


MODEL_PARAMS = initialize_parameters(d=4, h=16)
INTERFACE = "eth0"  # Adjust based on your VM/Linux interface

def execute_mitigation(ip_address):
    global blocked_ips
    with state_lock:
        if ip_address in blocked_ips or ip_address in ["127.0.0.1", "0.0.0.0"]:
            return
        blocked_ips.add(ip_address)
        log_msg = f"CRITICAL: Low-Rate DDoS pattern detected from {ip_address}. Executing firewall ban."
        recent_logs.append(f"[{time.strftime('%H:%M:%S')}] {log_msg}")
        
    try:
        subprocess.call(f"sudo iptables -A INPUT -s {ip_address} -j DROP", shell=True)
    except Exception as e:
        print(f"Error executing iptables: {e}")

def sniffing_backend_worker():
    global current_metrics, recent_logs
    extractor = PacketFeatureExtractor(window_duration=1.0, sequence_length=30)
    
    with state_lock:
        current_metrics["status"] = "Active"
        recent_logs.append(f"[{time.strftime('%H:%M:%S')}] Sniffing thread attached to interface: {INTERFACE}")

    def network_callback(packet):
        extractor.process_packet(packet)
        matrix = extractor.get_current_sequence()
        
        with state_lock:
            current_metrics["active_window_count"] = len(extractor.sequence_buffer)
        
        if matrix is not None:
            # Run model prediction
            y_pred, _, _ = gru_forward_sequence(matrix, MODEL_PARAMS)
            score = float(y_pred[0, 0])
            
            with state_lock:
                current_metrics["last_score"] = score
                
            if score >= 0.85 and packet.haslayer(IP):
                execute_mitigation(packet[IP].src)

    sniff(iface=INTERFACE, prn=network_callback, store=0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    with state_lock:
        return jsonify({
            "metrics": current_metrics,
            "logs": recent_logs[-15:], 
            "blocked": list(blocked_ips)
        })

if __name__ == '__main__':

    bg_thread = threading.Thread(target=sniffing_backend_worker, daemon=True)
    bg_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)