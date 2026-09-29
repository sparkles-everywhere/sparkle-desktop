# Desktop Sparkles

A beautiful animated sparkle overlay for your Linux X11 desktop using GTK3 and Cairo.

## Features

- **Multiple sparkle shapes**: diamond, hollow diamond, soft star, six-point star, and eight-point star
- **Smooth animations**: fade in/out, gentle drifting motion, rotation, and pulsing size effects
- **Soft glow effect**: layered rendering for a luminous appearance
- **Click-through**: sparkles don't block mouse input to windows below
- **Full-screen overlay**: covers the entire desktop
- **High performance**: runs at ~60 FPS
- **Automatic respawning**: sparkles continuously regenerate
- **Configurable**: easily adjust sparkle count, size, lifetime, colors, and animation parameters

## Dependencies

- Python 3
- GTK3 (`python3-gi` or `gobject-introspection`)
- Cairo (`pycairo`)
- X11 (required for window management)

On Debian/Ubuntu:
```bash
sudo apt install python3-gi python3-cairo gir1.2-gtk-3.0
```

On Fedora:
```bash
sudo dnf install python3-gobject python3-cairo gtk3
```

On Arch:
```bash
sudo pacman -S python-gobject python-cairo gtk3
```

## Installation

1. Clone or download this repository
2. Make the script executable:
```bash
chmod +x desktop-sparkles.py
```

3. Run manually to test:
```bash
./desktop-sparkles.py
```

## Systemd Service Installation

To automatically start desktop sparkles when you log in:

1. Edit the `desktop-sparkles.service` file and update the `ExecStart` path:
```ini
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/path/to/desktop-sparkles.py
```
Replace `/home/YOUR_USERNAME/path/to/` with your actual home directory and path.

2. Install the service to your user systemd directory:
```bash
cp desktop-sparkles.service ~/.config/systemd/user/
```

3. Reload systemd:
```bash
systemctl --user daemon-reload
```

4. Enable the service:
```bash
systemctl --user enable desktop-sparkles.service
```

5. Start the service:
```bash
systemctl --user start desktop-sparkles.service
```

### Managing the Service

- Check status: `systemctl --user status desktop-sparkles.service`
- Stop: `systemctl --user stop desktop-sparkles.service`
- Restart: `systemctl --user restart desktop-sparkles.service`
- Disable: `systemctl --user disable desktop-sparkles.service`

## Configuration

Edit the configuration section at the top of `desktop-sparkles.py`:

- `SPARKLE_COUNT`: Number of sparkles on screen (default: 10)
- `MIN_SIZE` / `MAX_SIZE`: Size range in pixels (default: 2.0-4.0)
- `MIN_LIFETIME` / `MAX_LIFETIME`: How long sparkles live in seconds (default: 1.5-3.0)
- `SPAWN_INTERVAL`: Time between spawn checks (default: 0.05)
- `FRAME_INTERVAL`: Animation frame interval in ms (default: 16 for ~60 FPS)
- `SPARKLE_COLOR`: RGB color tuple (default: white)
- `WIGGLE_DISTANCE`: How far sparkles drift (default: 4.0)
- `MAX_ROTATION`: Maximum rotation in degrees (default: 10.0)

## How It Works

The script creates a transparent, full-screen GTK window that sits above other windows but allows clicks to pass through. It uses Cairo to draw animated sparkles with various shapes and effects. Each sparkle has randomized properties for position, size, lifetime, rotation speed, and wiggle behavior to create a natural, varied appearance.
