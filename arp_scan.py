"""
This program was written by Yonatan Deri.
It follows the PEP8 guidelines.

Description:
    This file serves as a module in the network_visualizer project.

License:
    This program is under the GNU GPLv3 License.
"""

import netifaces
import scapy.all as scapy
from scapy.layers.l2 import ARP, Ether
import ipaddress


def get_active_networks() -> []:
    """
    Get active subnets inside a network of the current device.
    :return list: list, containing all active subnets inside the local network of the current device.
    """
    networks = []
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            ipv4_info = addresses[netifaces.AF_INET][0]
            ip = ipv4_info['addr']
            if "127.0.0.1" in ip:
                continue
            subnet_mask = ipv4_info['netmask']
            network = ipaddress.ip_network(f"{ip}/{subnet_mask}", strict=False)
            networks.append(network)
    return networks


def scan(ip_range) -> scapy.SndRcvList:
    """
    Scans an ip range for discovering active devices in it.
    :param ip_range:
    :return scapy.SndRcvList: list, containing all devices discovered in the network.
    """
    request = ARP(pdst=str(ip_range))
    broadcast = Ether(dst='ff:ff:ff:ff:ff:ff')
    request_broadcast = broadcast / request

    clients = scapy.srp(request_broadcast, timeout=1, verbose=False)[0]
    return clients
