# BLE Protocol Schema

## Overview

This repository implements a schema-driven code generation system for BLE (Bluetooth Low Energy) UART communication protocols. It enables defining a communication protocol once in JSON format and automatically generating type-safe, encapsulated, stateless implementations in multiple programming languages.

## Purpose

The primary purpose is to facilitate reliable communication between:
- **Server (Embedded systems)** - C/C++ code on microcontrollers with BLE capabilities
- **Client (Mobile applications)** - Dart/Flutter code on phones that connect to BLE devices

By using a single schema definition with client/server separation, both sides of the communication are guaranteed to use the same message formats while maintaining clear boundaries about which messages flow in which direction.

## Architecture

### Client-Server Model

The protocol uses a **strictly unidirectional** message flow:

- **Server Messages**: Sent FROM embedded device TO mobile app
  - Server side (C): Encodes these messages for transmission
  - Client side (Dart): Decodes these messages upon reception

- **Client Messages**: Sent FROM mobile app TO embedded device
  - Client side (Dart): Encodes these messages for transmission
  - Server side (C): Decodes these messages upon reception

There is **no overlap** - each message type exists only in one direction.

### Schema Definition

The protocol is defined in [schema/schema.json](schema/schema.json), which specifies:

1. **Protocol metadata**: Name and version information
2. **Frame structure**: How data is packaged for transmission
3. **Message definitions**: Separate `server` and `client` message categories
4. **Type system**: Primitive data types and their binary representation

### Code Generators

Two specialized generators produce language-specific implementations:

- **[generators/c_generator.py](generators/c_generator.py)**: Generates C code for embedded systems (server side)
  - Encodes server messages
  - Decodes client messages
  - All structs are private
  - Only accessor functions are exposed
  - Stateless decoding - no context object needed

- **[generators/dart_generator.py](generators/dart_generator.py)**: Generates Dart code for Flutter (client side)
  - Encodes client messages
  - Decodes server messages
  - All fields are private with getters/setters
  - Client messages are mutable, server messages are read-only
  - Stateless decoding - static methods on message classes

### Generated Code

Running the generator produces:

**C Output** ([generated/c/](generated/c/)) - Server Side:
- `ble_protocol.h` - Public API with function declarations only
- `ble_protocol.c` - Private structs and implementation

**Dart Output** ([generated/dart/](generated/dart/)) - Client Side:
- `ble_messages.dart` - Message class definitions with encapsulation
- `ble_codec.dart` - Compatibility file (no longer needed)

## Protocol Specification

### Frame Format

The protocol uses a framing system designed for BLE's MTU (Maximum Transmission Unit) constraints, supporting multi-frame messages when data exceeds the BLE packet size.

**First Frame Structure:**
```
Byte 0:    Sync byte (0xAA)
Byte 1:    Total payload length across all frames
Byte 2:    Message ID
Bytes 3-N: Payload data
Byte N+1:  Checksum
```

**Continuation Frame Structure:**
```
Byte 0:    Sync byte (0x55)
Bytes 1-N: Payload data (continued)
Byte N+1:  Checksum
```

### Key Features

- **Little-endian byte order**: Multi-byte values are encoded with least significant byte first
- **Sum-mod-256 checksum**: Simple but effective error detection on payload data
- **Sync bytes**: Distinguish between first frame (0xAA) and continuation frames (0x55)
- **Length field**: Specifies total payload size across all frames, not including headers/checksums
- **Multi-frame support**: Automatically handles messages larger than BLE MTU

### Type System

Supported primitive types:
- `uint8`, `int8` - 1-byte unsigned/signed integers
- `uint16`, `int16` - 2-byte unsigned/signed integers
- `uint32`, `int32` - 4-byte unsigned/signed integers
- `uint64`, `int64` - 8-byte unsigned/signed integers

## Usage Workflow

1. **Define or modify protocol** in [schema/schema.json](schema/schema.json)
2. **Categorize messages** as either `server` or `client` based on sender
3. **Generate code** by running `python generate.py`
4. **Integrate generated code** into embedded and mobile projects
5. **Use accessor functions** to encode/decode messages

## Code Generation

The [generate.py](generate.py) script provides flexible code generation:

```bash
# Generate both C and Dart
python generate.py

# Generate only C code
python generate.py --lang c

# Generate only Dart code
python generate.py --lang dart

# Custom schema and output paths
python generate.py --schema custom.json --output build/
```

## Technical Details

### C Implementation (Server Side)

**Encapsulation:**
- All message structs are defined in `.c` file only
- Header file exposes only function declarations
- No opaque pointers or context objects needed
- Completely stateless

**Server Message Encoding** (messages server sends):
```c
// Begin encoding - initializes frame with header
int ble_encode_<message>_begin(uint8_t *frame_out, uint16_t *frame_len);

// Set each field - automatically updates checksum
void ble_encode_<message>_set_<field>(uint8_t *frame, <type> value);
```

Example:
```c
uint8_t frame[256];
uint16_t frame_len;

ble_encode_heartbeat_begin(frame, &frame_len);
ble_encode_heartbeat_set_uptime_ms(frame, 12345);
ble_encode_heartbeat_set_battery_mv(frame, 3700);
```

**Client Message Decoding** (messages server receives):
```c
// Get each field directly from frame - stateless
<type> ble_decode_<message>_get_<field>(const uint8_t *frame, uint16_t frame_len);
```

Example:
```c
uint8_t param = ble_decode_config_set_get_param_id(frame, frame_len);
uint32_t value = ble_decode_config_set_get_value(frame, frame_len);
```

**Validation:**
Each decode getter performs complete validation:
- Checks frame length
- Verifies sync byte (0xAA)
- Verifies message ID
- Validates checksum
- Returns 0 on any error

**Features:**
- Uses packed structs (`__attribute__((packed))`) for binary layout
- Stateless - no context to manage
- Memory-safe with explicit buffer size tracking
- No dynamic allocation
- No public struct exposure

### Dart Implementation (Client Side)

**Encapsulation:**
- All fields are private (`_fieldName`)
- Public getters for all fields
- Public setters only for client messages (outgoing)
- Private constructors for server messages (incoming)
- Completely stateless

**Client Message Encoding** (messages client sends):
```dart
final msg = ConfigSet();
msg.paramId = 5;          // Use setters
msg.value = 1000;
final frame = msg.encodeFrame();  // Returns Uint8List
```

**Server Message Decoding** (messages client receives):
```dart
final msg = Heartbeat.decode(receivedFrame);  // Static method
if (msg != null) {
  print(msg.uptimeMs);  // Use getters (read-only)
}
```

**Validation:**
Each static `decode()` method performs complete validation:
- Checks frame length
- Verifies sync byte (0xAA)
- Verifies message ID
- Validates checksum
- Returns null on any error

**Features:**
- Object-oriented with separate classes per message type
- Type-safe with Dart's null safety
- Stateless - no decoder object needed
- Server message classes are immutable (read-only)
- Client message classes are mutable (read-write)
- Uses `ByteData` and `Uint8List` for binary operations

### Checksum Algorithm

Both implementations use sum-mod-256 checksum:
1. Sum all payload bytes (as unsigned integers)
2. Take result modulo 256 (or mask with 0xFF)
3. Checksum validates payload only, not headers

The checksum is automatically:
- Calculated on encode
- Verified on decode
- Rejected if mismatch

## Design Principles

### Single Instance per Side

The protocol is designed such that there will only ever be **one instance** on each side:
- One embedded device (server)
- One mobile app connection (client)

This design assumption allows:
- Stateless function-based API
- No need for multi-instance support
- Simplified implementation
- Reduced memory footprint

### Strict Encapsulation

Message data is **never** exposed as public structs or fields:
- **C**: Only functions in header, structs in implementation
- **Dart**: Only getters/setters, fields are private

Benefits:
- Implementation details can change without breaking API
- Type safety is enforced
- Clear separation between interface and implementation
- Easier to evolve protocol over time

### Stateless Design

No decoder objects or contexts are needed:
- **C**: Functions take `(frame, frame_len)` directly
- **Dart**: Static `decode()` methods on message classes

Benefits:
- Simpler API - no lifecycle management
- No memory allocation for decoding
- Thread-safe by default
- Easier to use and harder to misuse

### Unidirectional Messages

Each message flows in **exactly one direction**:
- Server messages: Server → Client only
- Client messages: Client → Server only

Benefits:
- Clear protocol semantics
- Reduced code size (only encode OR decode per message)
- Easier testing and validation
- No ambiguity about message origin
- Compile-time enforcement of direction

## Requirements

- **Python 3.6+** for running code generators
- **Standard C compiler** (GCC, Clang, etc.) for C code
- **Flutter SDK** for Dart code
- No external dependencies for the generators themselves

## License

GNU General Public License v3.0 (GPL-3.0) - See [LICENSE](LICENSE) for details.

## Development Notes

- Generated code should **not** be manually edited (changes will be overwritten)
- Schema changes automatically propagate to all generated code
- Both generators are self-contained Python modules
- Message IDs should be unique across both server and client categories
- The `.gitignore` excludes `generated/` by default (though committed in this repo for reference)
- Stateless design means no memory leaks or cleanup issues
- Each decode operation is independent and self-validating
