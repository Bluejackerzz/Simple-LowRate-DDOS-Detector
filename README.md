# Simple-LowRate-DDOS-Detector
An simple LowRate DDOS Detector using GRU as an Model to determine the packet pattern to detect Lowrate-like DDOS to an host

basicaly its an Intrusion Detection System(IDS) to identify and mitigate low-rate, DDOS attacks as an example like Slowloris.

Currently how it works its still dependant on the GRU Models to track the connection patterns between packets, so expect false positive or vice versa

---
## UI

![Screenshot](https://i.postimg.cc/cHkQJWQM/imagehehehddosyey.png)
Condition where the detector sucessfully detect and block the ip of the attacker


## Folders

```text
ids-gru-project/
│
├── core/
│   ├── __init__.py
│   ├── model.py            
│   └── extractor.py        
│
├── templates/
│   └── index.html          
│
├── app.py                  
└── attack_low_rate.py      # Use/put this in another VM/PC to act as an attacker
```
## Dependencies
its only works on Linux type OS, so as long the VM or hypervisor using linux its a okay

its using libcap and iptables
```text
sudo apt-get install libpcap-dev iptables -y
```

Python Dependencies
```text
pip install numpy scapy flask requests
```

##Network Interface
Before running the app, check your system Network Interfaces thats gonna be used by detector to detect the packets, leave it default if it using eth0

its shows on app.py

```text
INTERFACE = "eth0"
```
## Run

to run the detector just use
```text
sudo python3 app.py
```

## Others 

you can also use the attack_low_rate.py to test to attack the VM wheres the detector is placed 

before that dont forget to config the parameter
based on the ip of the detector or target VM
```text
TARGET_IP = "x.x.x.x"
TARGET_PORT = 5000
```

to execute  

```text
python3 attack_low_rate.py
```

## OTHERS ++
IS IT THEORITICALLY CAN HANDLE SYN FLOOD?

YES, but it will gonna bottlenect the scapy
