<div align="center">

# 🌟 Ubuntu System Theme
### Minimalist, Transparent Desktop Clock & Live System Monitor for Linux

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux%20(Universal)-blue.svg)](#-one-command-installation-per-distro)
[![Language](https://img.shields.io/badge/Python-3.8+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Toolkit](https://img.shields.io/badge/GUI-GTK%203%20%2B%20Cairo-4A90E2.svg)](https://www.gtk.org/)
[![Stability](https://img.shields.io/badge/Stability-100%25%20Crash--Proof-brightgreen.svg)](#-why-this-instead-of-traditional-conky)

A lightweight, hardware-accelerated desktop widget that recreates the iconic **Hatysa** clock and **Botein** system ricing aesthetics directly on your desktop wallpaper with **100% transparent canvas**.

</div>

---

## 📸 Preview

```
                 ╭─────────────────────────╮
                 │        ╭───────╮        │
                 │       │  04:23  │       │
                 │        ╰───────╯        │
                 │     02 SEPTEMBER 2026   │
                 │   MON TUE [WED] THU FRI │
                 │                         │
                 │ ▎ SYSTEM INFO           │
                 │   CPU : 18% // RAM : 24%│
                 │   BATTERY : 85%         │
                 │                         │
                 │ ▎ NOW PLAYING           │
                 │   Linkin Park - Numb    │
                 │   UPTIME : 2H 15M       │
                 ╰─────────────────────────╯
```

---

## 🚀 One-Command Installation (Per Distro)

Copy and paste the single command corresponding to your Linux distribution into your terminal. It will automatically install all dependencies, download the widget, configure fonts and icons, and start it on your desktop immediately:

### 🟠 Ubuntu / Linux Mint / Debian / Pop!_OS / Zorin OS
```bash
sudo apt update && sudo apt install -y git python3-gi python3-psutil gir1.2-gtk-3.0 gir1.2-pango-1.0 playerctl curl && git clone https://github.com/hafeedul/ubuntu-system-theme.git && cd ubuntu-system-theme && ./install.sh
```

### 🔵 Fedora / RHEL / AlmaLinux / Rocky Linux
```bash
sudo dnf install -y git python3-gobject python3-psutil gtk3 playerctl curl && git clone https://github.com/hafeedul/ubuntu-system-theme.git && cd ubuntu-system-theme && ./install.sh
```

### 🏹 Arch Linux / Manjaro / EndeavourOS / Garuda
```bash
sudo pacman -S --noconfirm git python-gobject python-psutil gtk3 playerctl curl && git clone https://github.com/hafeedul/ubuntu-system-theme.git && cd ubuntu-system-theme && ./install.sh
```

### 🦎 openSUSE (Tumbleweed & Leap)
```bash
sudo zypper install -y git python3-gobject python3-psutil typelib-1_0-Gtk-3_0 playerctl curl && git clone https://github.com/hafeedul/ubuntu-system-theme.git && cd ubuntu-system-theme && ./install.sh
```

---

## ✨ Features

- **100% Seamless Transparency**: Blends directly into your wallpaper. No gray cards, no borders, no window titles.
- **Hatysa Typography & Dial**:
  - Fine circular gauge with real-time seconds progress arc.
  - Dual-tone bold numerals (`Bebas Neue` font): Hours in pure white, Minutes in soft lavender (`#bb9af7`), and AM/PM in cyan.
  - Formatted date and weekday indicator strip (`MON TUE WED THU FRI SAT SUN`) with active day underline.
- **Botein Live Monitoring**:
  - Real-time **CPU%**, **RAM%**, and **Battery%** with charging state.
  - Real-time **Now Playing** track and artist detection via `playerctl` (works with Spotify, VLC, Firefox, Chrome, etc.).
  - System **Uptime** clock.
- **True Desktop Layer Integration**:
  - Positioned on the desktop background layer beneath all open windows.
  - Automatically hidden from the dock, dash, and taskbar (`skip-taskbar`).
- **Interactive Positioning & Pin Controls**:
  - **Click & Drag**: Drag the widget anywhere across multiple monitors when unlocked.
  - **🔒 Lock Position**: Prevents accidental movement.
  - **🔓 Unlock Position**: Re-enables dragging whenever you want to adjust placement.
  - **🎯 Reset to Center**: Instantly snaps the widget back to the top-middle of your screen.
  - **⚡ Always on (Start on Reboot)**: Registers autostart so it launches whenever your PC boots.

---

## 🛡️ Why This Instead of Traditional Conky?

Traditional Conky setups with transparent overlays often rely on X11 root-window rendering hacks and heavy OpenGL visualizers (`Glava`) that cause:
1. **Intel GPU DRM Pipe Failures**: Repeated `*ERROR* Atomic update failure on pipe A` crashes.
2. **Wayland Incompatibility**: Screen freezes, lock screen kickouts, and high CPU usage.

**Ubuntu System Theme** is built from scratch using **native GTK 3, Cairo, and Pango**:
- Zero root-window hacks.
- Pure event-driven updates (uses `<0.1%` CPU at idle).
- 100% stable on Wayland and X11 across all Intel, AMD, and NVIDIA hardware.

---

## 🖱️ Right-Click Controls

Right-click anywhere on the widget to access the context menu:

| Option | Description |
|---|---|
| **🔒 Lock Position** | Locks the widget firmly so it cannot be dragged accidentally. |
| **🔓 Unlock Position** | Unlocks the widget so you can click and drag it to adjust placement. |
| **⚡ Always on (Start on Reboot)** | Automatically starts the widget on login / reboot. |
| **📌 Float on Top of Other Apps** | Toggles whether the widget stays behind or floats above windows. |
| **🎯 Reset to Center** | Resets coordinates back to the upper-center of your screen. |
| **❌ Close Widget** | Safely exits the widget. |

---

## ⚙️ Service Commands

The widget runs under a lightweight systemd user service:

```bash
# Check status
systemctl --user status ubuntu-system-theme

# Start widget
systemctl --user start ubuntu-system-theme

# Stop widget
systemctl --user stop ubuntu-system-theme

# Restart widget
systemctl --user restart ubuntu-system-theme
```

---

## 🗑️ Uninstallation

To cleanly remove the widget, fonts, service, and settings from your system:

```bash
cd ubuntu-system-theme
./uninstall.sh
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - feel free to use, modify, and distribute!
