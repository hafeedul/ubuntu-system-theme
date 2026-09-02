#!/usr/bin/env bash
set -e

echo "Removing Ubuntu System Theme..."
systemctl --user stop ubuntu-system-theme 2>/dev/null || true
systemctl --user disable ubuntu-system-theme 2>/dev/null || true
pkill -f "ubuntu_system_theme" 2>/dev/null || true
pkill -f "ubuntu-system-theme" 2>/dev/null || true

rm -f ~/.local/bin/ubuntu-system-theme
rm -f ~/.local/share/applications/ubuntu-system-theme.desktop
rm -f ~/.config/autostart/ubuntu-system-theme.desktop
rm -f ~/.config/systemd/user/ubuntu-system-theme.service
rm -f ~/.local/share/icons/hicolor/scalable/apps/ubuntu-system-theme.svg
rm -f ~/.local/share/icons/hicolor/128x128/apps/ubuntu-system-theme.png
rm -rf ~/.config/aesthetic-widget

systemctl --user daemon-reload 2>/dev/null || true
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo "Uninstallation complete."
