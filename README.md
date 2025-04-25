# **Airsmack**

_Airsmack is a tool designed for wireless network monitoring and attack automation using Airodump-ng and related utilities._

## Overview
Airsmack streamlines **wireless security assessments** by automating data collection, deauthentication attacks, and handshake captures. It integrates **multiprocessing**, **subprocess management**, and **custom scripting** for efficient execution.

## **⚙ System Dependencies**
Ensure your system meets the following requirements:

- **Operating System**: Kali Linux (`latest`)
- **Networking Tools**:
  - `aircrack-ng`
  - `airodump-ng`
  - `cowpatty`
- **Python**: `>= 3.12`
- **Required Packages** (Install via `apt` or package manager):
  - `kmod`

### Python Dependencies
Install the required Python packages via `pip`:

```bash
pip install -r requirements.txt
```

### Usage

1️Clone the Repository

```bash
git clone https://github.com/B34MR/airsmack.git
cd airsmack
```

2️ Set Up Environment
```bash
pip install -r requirements.txt
```

3️ Run Airsmack

```bash
python airsmack.py
```

## **⚖ Legal Disclaimer**
This project is intended for educational and security research purposes only. Unauthorized use of network monitoring tools may violate laws and regulations. The developers assume no responsibility for misuse. Always ensure you have explicit permission before testing on any network.
