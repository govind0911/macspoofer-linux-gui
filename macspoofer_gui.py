#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import random
import re


def get_interfaces():
    interfaces = []

    try:
        output = subprocess.check_output(
            ["ip", "-o", "link", "show"],
            text=True
        )

        for line in output.splitlines():
            match = re.match(r"^\d+:\s+([^:]+):", line)

            if match:
                iface = match.group(1)

                if iface != "lo":
                    interfaces.append(iface)

    except Exception as e:
        messagebox.showerror("Error", str(e))

    return interfaces


def get_current_mac(interface):
    try:
        output = subprocess.check_output(
            ["ip", "link", "show", interface],
            text=True
        )

        match = re.search(
            r"link/ether\s+([0-9a-f:]{17})",
            output,
            re.IGNORECASE
        )

        return match.group(1) if match else "Unknown"

    except Exception:
        return "Unknown"


def generate_random_mac():
    first = (random.randint(0, 255) & 0xFC) | 0x02

    mac = [first] + [
        random.randint(0, 255)
        for _ in range(5)
    ]

    return ":".join(f"{x:02x}" for x in mac)


def refresh_mac():
    iface = interface_var.get()

    if iface:
        current_mac_var.set(
            get_current_mac(iface)
        )


def random_mac():
    mac_var.set(
        generate_random_mac()
    )


def apply_mac():
    iface = interface_var.get()
    mac = mac_var.get().strip()

    if not iface:
        messagebox.showerror(
            "Error",
            "Select an interface"
        )
        return

    if not re.match(
        r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$",
        mac
    ):
        messagebox.showerror(
            "Error",
            "Invalid MAC format"
        )
        return

    try:
        subprocess.run(
            ["sudo", "ip", "link", "set", iface, "down"],
            check=True
        )

        subprocess.run(
            ["sudo", "ip", "link", "set", iface,
             "address", mac],
            check=True
        )

        subprocess.run(
            ["sudo", "ip", "link", "set", iface, "up"],
            check=True
        )

        current_mac_var.set(
            get_current_mac(iface)
        )

        messagebox.showinfo(
            "Success",
            f"MAC changed to:\n{mac}"
        )

    except subprocess.CalledProcessError as e:
        messagebox.showerror(
            "Error",
            str(e)
        )


root = tk.Tk()
root.title("Linux MAC Spoofer")
root.geometry("500x250")
root.resizable(False, False)

interface_var = tk.StringVar()
current_mac_var = tk.StringVar()
mac_var = tk.StringVar()

tk.Label(
    root,
    text="Network Interface"
).pack(pady=5)

interfaces = get_interfaces()

iface_combo = ttk.Combobox(
    root,
    textvariable=interface_var,
    values=interfaces,
    state="readonly"
)

iface_combo.pack()

if interfaces:
    interface_var.set(interfaces[0])
    refresh_mac()

tk.Button(
    root,
    text="Refresh Current MAC",
    command=refresh_mac
).pack(pady=5)

tk.Label(
    root,
    text="Current MAC"
).pack()

tk.Label(
    root,
    textvariable=current_mac_var,
    font=("Courier", 11)
).pack()

tk.Label(
    root,
    text="New MAC"
).pack(pady=5)

tk.Entry(
    root,
    textvariable=mac_var,
    width=25
).pack()

tk.Button(
    root,
    text="Generate Random MAC",
    command=random_mac
).pack(pady=5)

tk.Button(
    root,
    text="Apply MAC Address",
    command=apply_mac
).pack(pady=10)

root.mainloop()

