#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "✨ Installing Ubuntu System Theme..."

mkdir -p ~/.local/bin
mkdir -p ~/.local/share/fonts
mkdir -p ~/.local/share/icons/hicolor/scalable/apps
mkdir -p ~/.local/share/icons/hicolor/128x128/apps
mkdir -p ~/.local/share/applications
mkdir -p ~/.config/autostart
mkdir -p ~/.config/systemd/user

echo "📦 Installing executable to ~/.local/bin/ubuntu-system-theme..."
cp "$DIR/src/ubuntu_system_theme.py" ~/.local/bin/ubuntu-system-theme
chmod +x ~/.local/bin/ubuntu-system-theme

echo "🔤 Installing typography (Bebas Neue & Dosis)..."
if [ -d "$DIR/assets/fonts" ] && [ -f "$DIR/assets/fonts/BebasNeue-Regular.ttf" ]; then
    cp "$DIR/assets/fonts/"* ~/.local/share/fonts/ 2>/dev/null || true
else
    curl -sL "https://raw.githubusercontent.com/google/fonts/main/ofl/bebasneue/BebasNeue-Regular.ttf" -o ~/.local/share/fonts/BebasNeue-Regular.ttf
    curl -sL "https://raw.githubusercontent.com/google/fonts/main/ofl/dosis/Dosis%5Bwght%5D.ttf" -o ~/.local/share/fonts/Dosis-VariableFont_wght.ttf
fi
fc-cache -fv ~/.local/share/fonts >/dev/null 2>&1 || true

echo "🎨 Installing application icons..."
cp "$DIR/assets/icons/ubuntu-system-theme.svg" ~/.local/share/icons/hicolor/scalable/apps/ 2>/dev/null || true
cp "$DIR/assets/icons/ubuntu-system-theme.png" ~/.local/share/icons/hicolor/128x128/apps/ 2>/dev/null || true
gtk-update-icon-cache -f ~/.local/share/icons/hicolor 2>/dev/null || true

echo "🖥️  Installing desktop entry..."
cat << 'DESK' > ~/.local/share/applications/ubuntu-system-theme.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=Ubuntu System Theme
GenericName=Desktop System Theme & Widget
Comment=Aesthetic desktop clock and live system monitor
Exec=/home/hafeed/.local/bin/ubuntu-system-theme
Icon=ubuntu-system-theme
Terminal=false
Categories=Utility;
StartupWMClass=ubuntu-system-theme
StartupNotify=false
DESK
chmod +x ~/.local/share/applications/ubuntu-system-theme.desktop
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

cat << 'AUTO' > ~/.config/autostart/ubuntu-system-theme.desktop
[Desktop Entry]
Type=Application
Name=Ubuntu System Theme
Comment=Autostart aesthetic desktop widget on login
Exec=/home/hafeed/.local/bin/ubuntu-system-theme
Icon=ubuntu-system-theme
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
AUTO
chmod +x ~/.config/autostart/ubuntu-system-theme.desktop

cat << 'SERV' > ~/.config/systemd/user/ubuntu-system-theme.service
[Unit]
Description=Ubuntu System Theme Desktop Widget
After=graphical-session.target

[Service]
Type=simple
Environment=DISPLAY=:0
ExecStart=/home/hafeed/.local/bin/ubuntu-system-theme
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
SERV

systemctl --user daemon-reload 2>/dev/null || true
systemctl --user enable ubuntu-system-theme 2>/dev/null || true
systemctl --user restart ubuntu-system-theme 2>/dev/null || nohup ~/.local/bin/ubuntu-system-theme >/dev/null 2>&1 &

echo "========================================================"
echo "🎉 Ubuntu System Theme installed and running successfully!"
echo "Right-click the widget on your desktop to lock position or configure."
echo "========================================================"
