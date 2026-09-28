# Photon Laser Tag

## Software needed on the Debian VM

- Python 3 with `venv` and `pip` (`python3`, `python3-venv`); a desktop session that can display a Pygame window.
- PostgreSQL already installed and configured, with database `photon`, table `players`, and local database role `student`. **Do not recreate or change the database schema.** The app currently uses `psycopg2.connect(dbname="photon", user="student")` and expects `players.id` and `players.codename`.
- Python packages pinned in `requirements.txt`: `pygame==2.6.1` and `psycopg2-binary==2.9.12`. The install script installs these into a local virtual environment.
- Git to download the project. For a Debian VM missing prerequisites: `sudo apt update && sudo apt install git python3 python3-venv`.

## Install and run

Open a terminal inside the VM's graphical desktop:

```bash
git clone https://github.com/ccaitlinc/Team4Repository.git
cd Team4Repository
bash install.sh
.venv/bin/python main.py
```

The installer requires an available Python package index to download the two packages. It does not install or modify PostgreSQL. Run the app as the VM's `student` user so its existing local PostgreSQL authentication works. If the database connection fails, verify that PostgreSQL is running and that this user can access the existing `photon` database and `players` table; use the instructor's VM setup rather than changing the schema.

To send equipment IDs to another IPv4 destination (such as the broadcast address for the selected LAN), start with:

```bash
.venv/bin/python main.py --network-address 192.168.1.255
```

The default destination is `127.0.0.1`; UDP sends to port `7500`. The option accepts an IPv4 address and rejects malformed addresses before opening the window. Select an address reachable on the VM's network; `127.0.0.1` only reaches the same machine. The app also listens for incoming UDP messages on port `7501` (accepting from any IP address). For now, anything received is printed to the terminal as `Received: <message>`; scoring and play-by-play handling will be added in a later sprint. The `--network-address` option only changes where equipment IDs are sent, not what the app listens on.

## Using the current player entry screen

1. Wait for the splash screen to finish (three seconds).
2. Click a player ID box in either team, type a numeric player ID, and press Enter.
3. The app looks up the codename. Type or edit the codename and press Enter; the app inserts a new player or updates the existing codename in the `players` table.
4. Type a numeric equipment ID in the prompt at the bottom and press Enter. The app sends that integer to the selected network address on UDP port `7500`.
5. Repeat for up to 15 players on each team. Close the window to exit. Escape cancels an active player field edit.

## Check UDP transmission

In a second terminal on the same VM, start the test receiver **before** entering an equipment ID:

```bash
.venv/bin/python tests/udp_receiver_test.py
```

With the default localhost destination, an equipment ID entered in the app should appear in this terminal. 
## Team members
| GitHub username | Real name |
|-----------------| --- |
| `ccaitlinc`     | Caitlin Condon |
| `rubyg04`       | Ruby Guerra |
| `amnaatiq`      | Amna Atiq |
| `pandanandita`  | Nandita Panda |
