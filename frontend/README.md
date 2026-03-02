# Lantern Frontend

A web interface for discovering and controlling Yongnuo lights over your local network.

## Setup

### Bluetooth permissions

To run without `sudo`, add your user to the `bluetooth` group:

```bash
sudo usermod -aG bluetooth $USER
```

Then log out and back in, or apply it to your current shell:

```bash
newgrp bluetooth
```

### Install dependencies

From the repo root, install the lantern library:

```bash
venv/bin/pip install -e .
```

Then install the frontend server dependencies:

```bash
venv/bin/pip install -r frontend/requirements.txt
```

## Running

```bash
venv/bin/python3 frontend/main.py
```

Then open `http://localhost:8000` in your browser (or replace `localhost` with your machine's LAN IP to access it from other devices on the network).

## Features

- **Discover** lights in range
- **Connect / disconnect** individual lights
- **White mode** — color temperature slider (1,000–10,000 K)
- **RGB mode** — color wheel
- **Intensity** slider (0–100%)
- **Power off**

## OSC

An OSC UDP server starts automatically on port `9000`. Lights are auto-connected on the first incoming message.

Address scheme:

```
/light/{mac}/intensity    f      (0.0 – 1.0)
/light/{mac}/temperature  i      (kelvin, e.g. 4800)
/light/{mac}/color        iii    (r g b, 0–255)
/light/{mac}/power_off
```

### Examples

Set intensity to 50%:

```bash
oscsend 127.0.0.1 9000 /light/AA:BB:CC:DD:EE:FF/intensity f 0.5
```

Set color temperature to 4800K:

```bash
oscsend 127.0.0.1 9000 /light/AA:BB:CC:DD:EE:FF/temperature i 4800
```

Set color to red:

```bash
oscsend 127.0.0.1 9000 /light/AA:BB:CC:DD:EE:FF/color iii 255 0 0
```

Set color to warm orange at 70% intensity:

```bash
oscsend 127.0.0.1 9000 /light/AA:BB:CC:DD:EE:FF/color iii 255 80 0
oscsend 127.0.0.1 9000 /light/AA:BB:CC:DD:EE:FF/intensity f 0.7
```

Power off:

```bash
oscsend 127.0.0.1 9000 /light/AA:BB:CC:DD:EE:FF/power_off
```
