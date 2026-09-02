#!/usr/bin/env python3
"""
Ubuntu System Theme - Aesthetic Desktop Widget
- 100% transparent background, floating directly on wallpaper
- Stays BEHIND all open apps and windows (on desktop background layer)
- Hidden from dock and taskbar
- Draggable when unlocked, immovable when locked
- Two explicit right-click options:
  * "🔒 Lock Position" (disables dragging so it cannot be moved accidentally)
  * "🔓 Unlock Position" (enables dragging so you can adjust position anytime)
- Remembers saved position and lock state across reboots
- Circular dial with live progress
- Bebas Neue typography and Dosis system stats
- 0% CPU overhead, zero kernel / DRM hacks
"""

import sys
import os

os.environ['GDK_BACKEND'] = 'x11'

import json
import math
import datetime
import subprocess
import psutil
import cairo

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, Pango, PangoCairo, GLib

GLib.set_prgname('ubuntu-system-theme')
GLib.set_application_name('Ubuntu System Theme')
Gtk.Window.set_default_icon_name('ubuntu-system-theme')

WIDTH = 420
HEIGHT = 560
CONFIG_DIR = os.path.expanduser("~/.config/aesthetic-widget")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
AUTOSTART_FILE = os.path.expanduser("~/.config/autostart/ubuntu-system-theme.desktop")

class AestheticWidget(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Ubuntu System Theme")
        self.set_icon_name("ubuntu-system-theme")
        self.set_default_size(WIDTH, HEIGHT)
        self.set_decorated(False)
        self.set_app_paintable(True)
        
        # Keep window in background behind all apps and out of taskbar/dock
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_focus_on_map(False)
        self.set_keep_below(True)
        self.set_keep_above(False)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.STRUCTURE_MASK
        )

        self.pinned = False
        self.position_locked = False
        self.save_timeout_id = 0
        self.last_x = None
        self.last_y = None

        self.load_config_or_center()

        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_button_press)
        self.connect("configure-event", self.on_configure_event)
        self.connect("destroy", Gtk.main_quit)

        GLib.timeout_add_seconds(1, self.on_timer_tick)

    def get_center_coords(self):
        screen = Gdk.Screen.get_default()
        display = screen.get_display() if screen else None
        if display:
            monitor = display.get_primary_monitor() or display.get_monitor(0)
            if monitor:
                geom = monitor.get_geometry()
                return ((geom.width - WIDTH) // 2, 70)
        return (558, 70)

    def load_config_or_center(self):
        loaded = False
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    pos_x = data.get("x")
                    pos_y = data.get("y")
                    if pos_x is not None and pos_y is not None:
                        self.move(int(pos_x), int(pos_y))
                        self.last_x = int(pos_x)
                        self.last_y = int(pos_y)
                        loaded = True
                    self.position_locked = bool(data.get("locked", False))
                    if data.get("pinned", False):
                        self.pinned = True
                        self.set_keep_above(True)
                        self.set_keep_below(False)
                    else:
                        self.pinned = False
                        self.set_keep_above(False)
                        self.set_keep_below(True)
            except Exception:
                pass
        
        if not loaded:
            cx, cy = self.get_center_coords()
            self.move(cx, cy)
            self.last_x = cx
            self.last_y = cy
            self.set_keep_below(True)
            self.set_keep_above(False)

    def on_configure_event(self, widget, event):
        self.last_x = event.x
        self.last_y = event.y
        if not self.pinned:
            self.set_keep_below(True)
        if self.save_timeout_id:
            GLib.source_remove(self.save_timeout_id)
        self.save_timeout_id = GLib.timeout_add(1000, self.save_config_callback)
        return False

    def save_config_callback(self):
        self.save_config()
        self.save_timeout_id = 0
        return GLib.SOURCE_REMOVE

    def save_config(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        try:
            x = self.last_x if self.last_x is not None else self.get_position()[0]
            y = self.last_y if self.last_y is not None else self.get_position()[1]
            data = {
                "x": x,
                "y": y,
                "locked": self.position_locked,
                "pinned": self.pinned,
                "always_on": self.is_autostart_enabled()
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def is_autostart_enabled(self):
        if not os.path.exists(AUTOSTART_FILE):
            return False
        try:
            with open(AUTOSTART_FILE, "r") as f:
                content = f.read()
                return "X-GNOME-Autostart-enabled=true" in content
        except Exception:
            return False

    def set_autostart(self, enable):
        os.makedirs(os.path.dirname(AUTOSTART_FILE), exist_ok=True)
        if enable:
            content = f"""[Desktop Entry]
Type=Application
Name=Ubuntu System Theme
Comment=Autostart aesthetic desktop widget on login
Exec={os.path.expanduser('~/.local/bin/conky-desktop')}
Icon=ubuntu-system-theme
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
"""
            with open(AUTOSTART_FILE, "w") as f:
                f.write(content)
            self.send_notify("Always On Enabled", "Widget will start automatically whenever you reboot or log in.")
        else:
            if os.path.exists(AUTOSTART_FILE):
                try:
                    os.remove(AUTOSTART_FILE)
                except Exception:
                    pass
            self.send_notify("Always On Disabled", "Widget will not start automatically on reboot.")
        self.save_config()

    def send_notify(self, title, msg):
        try:
            subprocess.Popen(["notify-send", "-a", "Ubuntu System Theme", "-i", "ubuntu-system-theme", title, msg], stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def on_timer_tick(self):
        self.queue_draw()
        return True

    def on_button_press(self, widget, event):
        if event.button == 1:
            if not self.position_locked:
                self.begin_move_drag(
                    event.button,
                    int(event.x_root),
                    int(event.y_root),
                    event.time
                )
                return True
            else:
                return False
        elif event.button == 3:
            self.show_context_menu(event)
            return True
        return False

    def set_lock_state(self, locked):
        self.position_locked = locked
        self.save_config()
        if locked:
            self.send_notify("Position Locked 🔒", "Widget position is locked. Dragging is disabled.")
        else:
            self.send_notify("Position Unlocked 🔓", "Widget is unlocked. You can click and drag to adjust position.")

    def reset_position(self, _):
        cx, cy = self.get_center_coords()
        self.move(cx, cy)
        self.last_x = cx
        self.last_y = cy
        if not self.pinned:
            self.set_keep_below(True)
        self.save_config()
        self.send_notify("Position Reset", "Widget centered on desktop.")

    def show_context_menu(self, event):
        menu = Gtk.Menu()
        
        lock_item = Gtk.RadioMenuItem(label="🔒 Lock Position (Disable Dragging)")
        unlock_item = Gtk.RadioMenuItem.new_with_label_from_widget(lock_item, "🔓 Unlock Position (Enable Dragging)")
        
        if self.position_locked:
            lock_item.set_active(True)
        else:
            unlock_item.set_active(True)

        lock_item.connect("toggled", lambda item: self.set_lock_state(True) if item.get_active() else None)
        unlock_item.connect("toggled", lambda item: self.set_lock_state(False) if item.get_active() else None)

        menu.append(lock_item)
        menu.append(unlock_item)

        menu.append(Gtk.SeparatorMenuItem())

        autostart_active = self.is_autostart_enabled()
        autostart_item = Gtk.CheckMenuItem(label="⚡ Always on (Start on Reboot)")
        autostart_item.set_active(autostart_active)
        autostart_item.connect("toggled", lambda item: self.set_autostart(item.get_active()))
        menu.append(autostart_item)

        pin_item = Gtk.CheckMenuItem(label="📌 Float on Top of Other Apps")
        pin_item.set_active(self.pinned)
        pin_item.connect("toggled", self.toggle_pin)
        menu.append(pin_item)

        reset_item = Gtk.MenuItem(label="🎯 Reset to Center")
        reset_item.connect("activate", self.reset_position)
        menu.append(reset_item)

        menu.append(Gtk.SeparatorMenuItem())

        close_item = Gtk.MenuItem(label="❌ Close Widget")
        close_item.connect("activate", lambda _: self.destroy())
        menu.append(close_item)

        menu.show_all()
        menu.popup_at_pointer(event)

    def toggle_pin(self, item):
        self.pinned = item.get_active()
        if self.pinned:
            self.set_keep_above(True)
            self.set_keep_below(False)
            self.send_notify("Floating on Top", "Widget will display over other apps.")
        else:
            self.set_keep_above(False)
            self.set_keep_below(True)
            self.send_notify("Desktop Background Mode", "Widget stays behind other apps on desktop wallpaper.")
        self.save_config()

    def draw_text_shadow(self, cr, layout, x, y, r, g, b, a=1.0):
        cr.save()
        cr.move_to(x + 1.5, y + 1.5)
        cr.set_source_rgba(0, 0, 0, 0.65)
        PangoCairo.show_layout(cr, layout)
        cr.restore()

        cr.save()
        cr.move_to(x, y)
        cr.set_source_rgba(r, g, b, a)
        PangoCairo.show_layout(cr, layout)
        cr.restore()

    def on_draw(self, widget, cr):
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        now = datetime.datetime.now()
        cx, cy, r = WIDTH // 2, 110, 75

        # 1. Hatysa Circular Dial
        cr.set_line_width(3.5)
        cr.set_source_rgba(1, 1, 1, 0.25)
        cr.arc(cx, cy, r, 0, 2 * math.pi)
        cr.stroke()

        # Dynamic seconds arc
        sec = now.second
        sec_angle = (sec / 60.0) * 2 * math.pi - (math.pi / 2)
        cr.set_line_width(4.5)
        cr.set_source_rgba(1, 1, 1, 0.95)
        cr.arc(cx, cy, r, -math.pi / 2, sec_angle)
        cr.stroke()

        # 2. Large Time
        layout = PangoCairo.create_layout(cr)
        desc_time = Pango.FontDescription('Bebas Neue 60')
        layout.set_font_description(desc_time)

        # Hours
        layout.set_text(now.strftime('%I'), -1)
        w, h = layout.get_pixel_size()
        self.draw_text_shadow(cr, layout, cx - w - 2, cy - h / 2 + 5, 1, 1, 1, 1.0)

        # Minutes (Lavender Accent)
        layout.set_text(now.strftime('%M'), -1)
        self.draw_text_shadow(cr, layout, cx + 4, cy - h / 2 + 5, 0.73, 0.60, 0.97, 1.0)

        # AM / PM
        desc_ampm = Pango.FontDescription('Bebas Neue 16')
        layout.set_font_description(desc_ampm)
        layout.set_text(now.strftime('%p'), -1)
        self.draw_text_shadow(cr, layout, cx - 52, cy + 22, 0.49, 0.80, 1.0, 1.0)

        # 3. Date
        desc_date = Pango.FontDescription('Bebas Neue 20')
        layout.set_font_description(desc_date)
        date_str = now.strftime('%d %B %Y').upper()
        layout.set_text(date_str, -1)
        w, h = layout.get_pixel_size()
        self.draw_text_shadow(cr, layout, cx - w / 2, cy + 105, 1, 1, 1, 0.95)

        # 4. Weekday Strip
        desc_day = Pango.FontDescription('Bebas Neue 14')
        layout.set_font_description(desc_day)
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        cur_day = now.weekday()
        start_x = cx - (len(days) * 44) / 2 + 5

        for i, d in enumerate(days):
            layout.set_text(d, -1)
            w, h = layout.get_pixel_size()
            dx = start_x + i * 44
            dy = cy + 138
            if i == cur_day:
                self.draw_text_shadow(cr, layout, dx, dy, 1, 1, 1, 1.0)
                cr.set_source_rgba(1, 1, 1, 0.9)
                cr.rectangle(dx - 1, dy + h + 2, w + 2, 2)
                cr.fill()
            else:
                self.draw_text_shadow(cr, layout, dx, dy, 0.60, 0.56, 0.64, 0.65)

        # 5. System Info (Botein Minimalist Style)
        stat_y = cy + 195
        desc_title = Pango.FontDescription('Dosis Bold 15')
        desc_body = Pango.FontDescription('Dosis 13')

        # Green accent bar
        cr.set_source_rgba(0.55, 0.91, 0.55, 0.95)
        cr.rectangle(cx - 130, stat_y - 8, 4, 46)
        cr.fill()

        layout.set_font_description(desc_title)
        layout.set_text('SYSTEM INFO', -1)
        self.draw_text_shadow(cr, layout, cx - 118, stat_y - 8, 1, 1, 1, 1.0)

        layout.set_font_description(desc_body)
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        layout.set_text(f'CPU : {cpu:.0f}%  //  RAM : {mem:.0f}%', -1)
        self.draw_text_shadow(cr, layout, cx - 118, stat_y + 12, 0.9, 0.9, 0.95, 0.9)

        bat = psutil.sensors_battery()
        if bat:
            chg = ' (CHARGING)' if bat.power_plugged else ''
            layout.set_text(f'BATTERY : {bat.percent:.0f}%{chg}', -1)
            self.draw_text_shadow(cr, layout, cx - 118, stat_y + 28, 0.9, 0.9, 0.95, 0.9)

        # 6. Now Playing / Uptime
        stat2_y = stat_y + 64
        cr.set_source_rgba(0.73, 0.60, 0.97, 0.95)
        cr.rectangle(cx - 130, stat2_y - 8, 4, 46)
        cr.fill()

        layout.set_font_description(desc_title)
        layout.set_text('NOW PLAYING', -1)
        self.draw_text_shadow(cr, layout, cx - 118, stat2_y - 8, 1, 1, 1, 1.0)

        layout.set_font_description(desc_body)
        media_text = "NO ACTIVE MEDIA"
        try:
            status = subprocess.check_output(["playerctl", "status"], stderr=subprocess.DEVNULL).decode().strip()
            if status in ["Playing", "Paused"]:
                track = subprocess.check_output(["playerctl", "metadata", "title"], stderr=subprocess.DEVNULL).decode().strip()
                artist = subprocess.check_output(["playerctl", "metadata", "artist"], stderr=subprocess.DEVNULL).decode().strip()
                if track:
                    media_text = f"{track} - {artist}" if artist else track
                    if len(media_text) > 32:
                        media_text = media_text[:30] + "..."
        except Exception:
            pass

        layout.set_text(media_text.upper(), -1)
        self.draw_text_shadow(cr, layout, cx - 118, stat2_y + 12, 0.9, 0.9, 0.95, 0.9)

        boot = datetime.datetime.fromtimestamp(psutil.boot_time())
        delta = now - boot
        hrs, rem = divmod(int(delta.total_seconds()), 3600)
        mins, _ = divmod(rem, 60)
        layout.set_text(f'UPTIME : {hrs}H {mins}M', -1)
        self.draw_text_shadow(cr, layout, cx - 118, stat2_y + 28, 0.9, 0.9, 0.95, 0.9)

        return True

def main():
    if "--check" in sys.argv:
        print("Syntax and imports OK")
        sys.exit(0)

    win = AestheticWidget()
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
