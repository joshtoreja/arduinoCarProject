# arduinoCarProject

Dijkstra Path-Following Arduino Car

What: An Elegoo/Arduino robot car that follows a shortest path computed with Dijkstra.
How: Press “9” on the IR remote to enter Path Mode, then stream commands over Serial: S, moves like R3 / U2, then E. The car executes the route using time-based motion.

Repository layout
arduinocarProject/
├─ arduino/
│  ├─ DijkstraPathCar/
│  │  └─ DijkstraPathCar.ino
│  └─ extras/
│     └─ PathMode/
│        └─ PathMode.ino        # optional helper for factory sketches
└─ python/
   ├─ grid_generator.py
   ├─ dijkstra.py
   └─ bridge_send_path.py

Hardware

Arduino UNO (Elegoo UNO R3 compatible)

Motor driver: TB67H450 / TB6612 family (IN1/IN2 + PWM)

IR receiver (default pin 12)

Two DC motors with battery pack

Default motor pins in DijkstraPathCar.ino: Left PWM 5, IN1 2, IN2 4; Right PWM 6, IN1 7, IN2 8.

Software requirements

Arduino IDE (2.x recommended)

Library: IRremote by Armin Joachimsmeyer

Sketch uses #include <IRremote.hpp> (v3+). If using v2, change to #include <IRremote.h> and adjust API if needed.

Python 3.9+

Packages: matplotlib, pyserial

Install Python packages:

python3 -m pip install matplotlib pyserial

Arduino: upload the sketch

Open arduino/DijkstraPathCar/DijkstraPathCar.ino in Arduino IDE.

Tools → Board: Arduino Uno. Tools → Port: your /dev/cu.* (macOS) or COMx (Windows).

Install IRremote if prompted.

Upload. Open Serial Monitor at 115200; on reset you should see RDY.

IR key setup: Press 9 on the remote. If the sketch prints PATH:ENTER, you’re done. If not, read the RAW hex value printed for your “9” key and set it in the sketch:

#define IR_CODE_9  0xYOUR_HEX_CODE


Re-upload.

Python: generate a grid and plan a path

From the python/ directory:

# Unweighted grid (all steps cost 1)
python3 grid_generator.py --max 10 --k 10 --weighted none --json grid.json

# Or weighted grid (random 1..4)
# python3 grid_generator.py --max 10 --k 10 --seed 1 --weighted random --wmin 1 --wmax 4 --json grid.json

# Compute path to the closest 'R' point and export results
python3 dijkstra.py --grid grid.json --color R \
  --save-path path.json \
  --save-moves moves.json \
  --save-moves-txt moves.txt


Outputs:

path.json — waypoints ({"path":[[x0,y0],...]})

moves.json — "moves": "URRDL..."

moves.txt — the exact lines the car expects:

S
U1
R3
...
E

Send the path to the car

Find your serial port (macOS example):

ls /dev/cu.*
PORT="/dev/cu.usbmodemXXXX"   # replace with yours


Put the car’s battery on. Press 9 on the remote to enter Path Mode. Then:

python3 bridge_send_path.py path.json --port "$PORT" --baud 115200 --handshake

Configuration (in DijkstraPathCar.ino)
// IR
#define IR_RECV_PIN 12
#define IR_CODE_9   0xFF52AD      // replace with your remote’s RAW code for "9"
#define IR_CODE_EXIT 0xFF9867     // optional exit key

// Motors
#define L_PWM 5
#define L_IN1 2
#define L_IN2 4
#define R_PWM 6
#define R_IN1 7
#define R_IN2 8

// Timing (tune for your surface/grid)
int DRIVE_SPEED  = 180;          // 0..255
int TURN_SPEED   = 170;          // 0..255
unsigned long CELL_MS   = 600;   // ms per grid cell
unsigned long TURN90_MS = 350;   // ms per ~90° turn

Calibration tips
printf "S\nU1\nR1\nE\n" > tiny_moves.txt
python3 bridge_send_path.py tiny_moves.txt --port "$PORT" --baud 115200


If distance per cell is off → adjust CELL_MS.

If turns aren’t square → adjust TURN90_MS.

If a side runs backward → swap that motor’s IN1/IN2 or reverse wiring.

Troubleshooting

No serial port → try another USB cable/port; CH340-based boards may need the CH340 driver (macOS).

Pressing 9 does nothing → print IR values in Serial Monitor, set IR_CODE_9, re-upload.

“Port busy” → close Serial Monitor before running the Python sender.

No movement on USB → motors require the battery pack.

License

Add your preferred license (MIT/Apache-2.0/etc.).
