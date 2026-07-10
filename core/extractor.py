import time
import numpy as np
from scapy.all import IP, TCP

class PacketFeatureExtractor:
    def __init__(self, window_duration=1.0, sequence_length=30):
        self.window_duration = window_duration
        self.sequence_length = sequence_length
        self.current_window_start = time.time()
        
        self.packet_count = 0
        self.byte_count = 0
        self.syn_count = 0
        self.last_packet_time = None
        self.inter_arrival_times = []
        self.sequence_buffer = []

    def process_packet(self, packet):
        current_time = time.time()
        
        if current_time - self.current_window_start >= self.window_duration:
            self._finalize_window()
            self.current_window_start = current_time

        self.packet_count += 1
        if packet.haslayer(IP):
            self.byte_count += len(packet[IP])
        if packet.haslayer(TCP) and (packet[TCP].flags & 0x02):
            self.syn_count += 1

        if self.last_packet_time is not None:
            self.inter_arrival_times.append(current_time - self.last_packet_time)
        self.last_packet_time = current_time

    def _finalize_window(self):
        avg_iat = np.mean(self.inter_arrival_times) if self.inter_arrival_times else 0.0
        syn_ratio = self.syn_count / self.packet_count if self.packet_count > 0 else 0.0
        
        features = np.array([avg_iat, float(self.packet_count), float(self.byte_count), syn_ratio])
        self.sequence_buffer.append(features)
        
        if len(self.sequence_buffer) > self.sequence_length:
            self.sequence_buffer.pop(0)
            
        self.packet_count = 0
        self.byte_count = 0
        self.syn_count = 0
        self.inter_arrival_times = []

    def get_current_sequence(self):
        if len(self.sequence_buffer) == self.sequence_length:
            return np.array(self.sequence_buffer)
        return None