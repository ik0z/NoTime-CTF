import argparse,socket
import subprocess
import threading
import sys
import signal
import colorama

# Define colors
colorama.init()
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
BLUE = colorama.Fore.BLUE
YELLOW = colorama.Fore.YELLOW
RESET = colorama.Style.RESET_ALL


logo = f"""
----------------------------------------------------------
{BLUE} No T!me {RESET}
           👻 {YELLOW}Hurry up {RESET}
                        kAz 1.0 | https://github.com/ik0z/
----------------------------------------------------------
"""
# Define functions for each type of scan
def nmap_basic_scan(host):
    command = f"nmap -sV -sC {host}"
    result = subprocess.check_output(command, shell=True, universal_newlines=True)
    print(f"{YELLOW}{result}{RESET}")

def nmap_advanced_scan(host):
    command = f"nmap -sV -sC -A --script=vuln {host}"
    result = subprocess.check_output(command, shell=True, universal_newlines=True)
    print(f"{YELLOW}{result}{RESET}")


def gobuster_scan(host):
    try:
        command = f"gobuster dir -u {host} -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -q"
        result = subprocess.check_output(command, shell=True, universal_newlines=True)
        print(f"{YELLOW}{result}{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error running gobuster: {e}{RESET}")

def port_scan(host):
    # Define port numbers and corresponding services to scan for
    port_services = {
        21: "FTP",
        22: "SSH",
        25: "SMTP",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        445: "SMB",
        3306: "MYSQL",
        3389: "RDP",
        8080: "HTTP",
    }
    open_ports = []
    for port in port_services.keys():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        if result == 0:
            open_ports.append(port)
            print(f"{GREEN}[+] Port {port} ({port_services[port]}) is open{RESET}")
        sock.close()
    if len(open_ports) == 0:
        print(f"{RED}[-] No open ports found{RESET}")
    else:
        print(f"{BLUE}[+] Services detected: {', '.join([port_services[port] for port in open_ports])}{RESET}")
        if 80 in open_ports or 443 in open_ports or 8080 in open_ports:
            gobuster_scan(host)

def nmap_enum_scan(host):
    command = f"nmap -sV -A {host} --script=smb-enum-users.nse,smb-enum-shares.nse,ftp-anon.nse,ftp-proftpd-backdoor.nse"
    result = subprocess.check_output(command, shell=True, universal_newlines=True)
    print(f"{YELLOW}{result}{RESET}")

# Define function to handle Ctrl+C
def signal_handler(sig, frame):
    print(f"\n{RED}[-] User interrupted the scan. Exiting...{RESET}")
    sys.exit(0)

# Define main function
def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="CTF Autoscan tool")
    parser.add_argument("-np", action="store_true", help="Perform basic Nmap scan")
    parser.add_argument("-nad", action="store_true", help="Perform advanced Nmap scan")
    parser.add_argument("-go", action="store_true", help="Perform Gobuster scan")
    parser.add_argument("-p", action="store_true", help="Perform port/service scan via Python code")
    parser.add_argument("-host", type=str, help="Specify target host")
    parser.add_argument("-enum", action="store_true", help="Perform Nmap enumeration scan")
    parser.add_argument("-nco", action="store_true", help="Disable color output")
    parser.add_argument("-all", action="store_true", help="Perform all scans")
    parser.add_argument("-t", type=int, default=10, help="Number of threads to use (default 10)")
    args = parser.parse_args()

    # Check if host is specified
    if not args.host:
        parser.print_help()
        sys.exit(0)


    # Check if all scans are requested
    if args.all:
        args.nad = True
        args.p = True
        args.enum = True


    # Disable color output if -nco option is specified
    if args.nco:
        colorama.deinit()

    # Set number of threads
    threading_count = args.t

    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Perform requested scans
    threads = []
    if args.np:
        thread = threading.Thread(target=nmap_basic_scan, args=(args.host,))
        thread.start()
        threads.append(thread)
    if args.nad:
        thread = threading.Thread(target=nmap_advanced_scan, args=(args.host,))
        thread.start()
        threads.append(thread)
    if args.go:
        thread = threading.Thread(target=gobuster_scan, args=(args.host,))
        thread.start()
        threads.append(thread)
    if args.p:
        thread = threading.Thread(target=port_scan, args=(args.host,))
        thread.start()
        threads.append(thread)
    if args.enum:
        thread = threading.Thread(target=nmap_enum_scan, args=(args.host,))
        thread.start()
        threads.append(thread)

    # Wait for threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    print(logo)
    main()
