# BLE Protocol Schema

BLE UART protocol schema for phone app communication with the BLE dashboard module.

This repository contains a schema-driven code generator that produces both C (embedded) and Dart (Flutter) implementations from a single JSON schema definition.

## Features

- **Schema-driven**: Define your protocol once in `schema/schema.json`
- **Multi-language**: Generates C code for embedded systems and Dart code for Flutter apps
- **BLE-optimized**: Handles multi-frame messages for BLE MTU constraints
- **Type-safe**: Strongly typed message structures in both languages
- **Checksummed**: Built-in sum-mod-256 checksum validation
- **Encapsulated**: Messages use accessor functions, not public structs
- **Client/Server separation**: Clear distinction between messages sent and received
- **Stateless**: Simple function-based API without decoder objects

## Architecture

The protocol uses a **client-server** model:

- **Server** = Embedded device (C code)
  - Encodes server messages (to send to client)
  - Decodes client messages (received from client)

- **Client** = Mobile app (Dart code)
  - Encodes client messages (to send to server)
  - Decodes server messages (received from server)

Messages are strictly unidirectional - each message type is either sent by server OR client, never both.

## Quick Start

### Generate Code

```bash
# Generate both C and Dart code
python3 generate.py

# Generate only C code
python3 generate.py --lang c

# Generate only Dart code
python3 generate.py --lang dart
```

Generated files will be in:
- `generated/c/ble_protocol.h` - C header file
- `generated/c/ble_protocol.c` - C implementation
- `generated/dart/ble_messages.dart` - Dart message classes

### C Usage (Server/Embedded)

```c
#include "ble_protocol.h"

// Encoding a server message (server sends heartbeat to client)
uint8_t frame[256];
uint16_t frame_len;

ble_encode_heartbeat_begin(frame, &frame_len);
ble_encode_heartbeat_set_uptime_ms(frame, 12345);
ble_encode_heartbeat_set_battery_mv(frame, 3700);
ble_encode_heartbeat_set_status_flags(frame, 0x01);
// Send frame via BLE UART

// Decoding a client message (server receives config_set from client)
// Simply pass the received frame directly to getters
uint8_t param_id = ble_decode_config_set_get_param_id(received_frame, frame_len);
uint32_t value = ble_decode_config_set_get_value(received_frame, frame_len);
// Process configuration...
```

### Dart Usage (Client/Flutter)

```dart
import 'package:your_app/generated/ble_messages.dart';

// Encoding a client message (client sends config_set to server)
final configSet = ConfigSet();
configSet.paramId = 5;
configSet.value = 1000;

final frame = configSet.encodeFrame();
// Send frame via BLE characteristic

// Decoding a server message (client receives heartbeat from server)
// Simply pass the received frame directly to static decode method
final heartbeat = Heartbeat.decode(receivedFrame);

if (heartbeat != null) {
  print('Uptime: ${heartbeat.uptimeMs}ms');
  print('Battery: ${heartbeat.batteryMv}mV');
}
```

## Schema Format

The protocol is defined in `schema/schema.json`:

```json
{
  "protocol": {
    "name": "ble_telemetry",
    "version": "1.0.0"
  },
  "messages": {
    "server": {
      "heartbeat": {
        "id": "0x01",
        "fields": {
          "uptime_ms": "uint32",
          "battery_mv": "uint16",
          "status_flags": "uint8"
        }
      }
    },
    "client": {
      "config_set": {
        "id": "0x10",
        "fields": {
          "param_id": "uint8",
          "value": "uint32"
        }
      }
    }
  }
}
```

### Message Categories

- **`messages.server`**: Messages sent FROM server TO client
  - Server encodes these (C code)
  - Client decodes these (Dart code)

- **`messages.client`**: Messages sent FROM client TO server
  - Client encodes these (Dart code)
  - Server decodes these (C code)

### Adding a New Message

1. Edit `schema/schema.json`
2. Add your message under `messages.server` or `messages.client`
3. Run `python3 generate.py`
4. Use the generated accessor functions in your code

## Protocol Details

### Frame Structure

**First Frame:**
```
[0xAA][Length][MsgID][Payload...][Checksum]
```

**Continuation Frame:**
```
[0x55][Payload...][Checksum]
```

- Little-endian byte order
- Sum-mod-256 checksum on payload only
- Length field specifies total payload across all frames

### Current Message IDs

**Server Messages** (server → client):
- `0x01` - Heartbeat (device status)
- `0x02` - Sensor Data (temperature, humidity, pressure)
- `0x03` - Motor Status (RPM, current, temperature, faults)
- `0x11` - Config Ack (configuration acknowledgment)

**Client Messages** (client → server):
- `0x10` - Config Set (configuration write)

## Project Structure

```
ble-protocol-schema/
├── schema/
│   └── schema.json           # Protocol definition
├── generators/
│   ├── c_generator.py        # C code generator
│   └── dart_generator.py     # Dart code generator
├── generate.py               # Main generator script
├── generated/                # Generated code output
│   ├── c/
│   │   ├── ble_protocol.h
│   │   └── ble_protocol.c
│   └── dart/
│       └── ble_messages.dart
└── README.md
```

## Implementation Details

### C Implementation (Server)

**Encapsulation:**
- All structs are private in `.c` file
- Header only exposes function declarations
- No decoder context object needed

**Server Message Encoding:**
```c
// 1. Begin encoding - initializes frame
int ble_encode_<message>_begin(uint8_t *frame_out, uint16_t *frame_len);

// 2. Set fields - automatically updates checksum after each set
void ble_encode_<message>_set_<field>(uint8_t *frame, <type> value);
```

**Client Message Decoding:**
```c
// Get field directly from frame - stateless
<type> ble_decode_<message>_get_<field>(const uint8_t *frame, uint16_t frame_len);
```

Each getter function:
- Validates frame structure
- Verifies sync byte and message ID
- Checks checksum
- Extracts the field value
- Returns 0 on any error

### Dart Implementation (Client)

**Encapsulation:**
- All fields are private with `_` prefix
- Public getters for all fields
- Public setters only on client messages

**Client Messages** (mutable, for sending):
```dart
final msg = ConfigSet();
msg.paramId = 5;      // Setters available
msg.value = 1000;
final frame = msg.encodeFrame();  // Encode to Uint8List
```

**Server Messages** (immutable, for receiving):
```dart
final msg = Heartbeat.decode(frame);  // Static method
if (msg != null) {
  print(msg.uptimeMs);  // Getters only (read-only)
}
```

Each `decode()` method:
- Validates frame structure
- Verifies sync byte and message ID
- Checks checksum
- Returns message object or null on error

## Requirements

- **Python 3.6+** for running code generators
- **Standard C compiler** (GCC, Clang, etc.) for C code
- **Flutter SDK** for Dart code
- No external dependencies for the generators themselves

## License

See LICENSE file for details.
