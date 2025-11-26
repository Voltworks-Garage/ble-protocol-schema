"""
C Code Generator for BLE Protocol
Generates header and implementation files from schema.json
Server-side implementation: Encodes server messages, decodes client messages

Frame format:
- First frame: [0xAA][Length][MsgID][Payload...]
- Continuation: [Payload...]
- Final frame ends with: [Checksum] (covers entire payload)

Frame buffers are managed internally in the private implementation.
"""

import json
from typing import Dict, List, Any


class CGenerator:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.protocol = schema['protocol']
        self.frame = schema['frame']
        self.server_messages = schema['messages']['server']
        self.client_messages = schema['messages']['client']
        self.types = schema['types']

    def get_c_type(self, type_name: str) -> str:
        """Convert schema type to C type"""
        type_map = {
            'uint8': 'uint8_t',
            'int8': 'int8_t',
            'uint16': 'uint16_t',
            'int16': 'int16_t',
            'uint32': 'uint32_t',
            'int32': 'int32_t',
            'uint64': 'uint64_t',
            'int64': 'int64_t',
        }
        return type_map.get(type_name, type_name)

    def calculate_struct_size(self, fields: Dict[str, str]) -> int:
        """Calculate total size of message struct in bytes"""
        total = 0
        for field_type in fields.values():
            total += self.types[field_type]['size']
        return total

    def generate_header(self) -> str:
        """Generate C header file with only function declarations"""
        lines = []
        lines.append("/**")
        lines.append(f" * BLE Telemetry Protocol v{self.protocol['version']}")
        lines.append(" * Auto-generated from schema.json")
        lines.append(" * DO NOT EDIT MANUALLY")
        lines.append(" *")
        lines.append(" * Server-side implementation:")
        lines.append(" * - Encodes server messages (for transmission)")
        lines.append(" * - Decodes client messages (for reception)")
        lines.append(" *")
        lines.append(" * Frame format:")
        lines.append(" * - First frame: [0xAA][Length][MsgID][Payload...]")
        lines.append(" * - Continuation: [Payload...]")
        lines.append(" * - Final frame ends with: [Checksum]")
        lines.append(" *")
        lines.append(" * Frame buffers are managed internally.")
        lines.append(" */")
        lines.append("")
        lines.append("#ifndef BLE_PROTOCOL_H")
        lines.append("#define BLE_PROTOCOL_H")
        lines.append("")
        lines.append("#include <stdint.h>")
        lines.append("#include <stdbool.h>")
        lines.append("")

        # Frame structure
        lines.append("// Frame structure")
        lines.append("typedef struct {")
        lines.append("    const uint8_t *data;")
        lines.append("    uint16_t length;")
        lines.append("} ble_frame_t;")
        lines.append("")

        # Message IDs
        lines.append("// Message IDs")
        for msg_name, msg_info in self.server_messages.items():
            constant_name = f"MSG_ID_{msg_name.upper()}"
            lines.append(f"#define {constant_name:<25} {msg_info['id']}")
        for msg_name, msg_info in self.client_messages.items():
            constant_name = f"MSG_ID_{msg_name.upper()}"
            lines.append(f"#define {constant_name:<25} {msg_info['id']}")
        lines.append("")

        # Server message encoding functions (server sends these)
        lines.append("// ============================================================================")
        lines.append("// Server message encoding functions")
        lines.append("// ============================================================================")
        lines.append("")

        for msg_name, msg_info in self.server_messages.items():
            lines.append(f"// Encode and get {msg_name} message")
            # Begin function - initializes internal buffer
            lines.append(f"void ble_encode_{msg_name}_begin(void);")
            # Setter functions for each field
            for field_name, field_type in msg_info['fields'].items():
                c_type = self.get_c_type(field_type)
                lines.append(f"void ble_encode_{msg_name}_set_{field_name}({c_type} value);")
            # Get frame function - returns frame struct
            lines.append(f"ble_frame_t ble_encode_{msg_name}_get_frame(void);")
            lines.append("")

        # Client message decoding functions (server receives these)
        lines.append("// ============================================================================")
        lines.append("// Client message decoding functions")
        lines.append("// ============================================================================")
        lines.append("")

        for msg_name, msg_info in self.client_messages.items():
            lines.append(f"// Decode {msg_name} message")
            # Set frame function - copies frame to internal buffer
            lines.append(f"bool ble_decode_{msg_name}_set_frame(const uint8_t *frame, uint16_t frame_len);")
            # Getter functions for each field
            for field_name, field_type in msg_info['fields'].items():
                c_type = self.get_c_type(field_type)
                lines.append(f"{c_type} ble_decode_{msg_name}_get_{field_name}(void);")
            lines.append("")

        lines.append("#endif // BLE_PROTOCOL_H")

        return '\n'.join(lines)

    def generate_implementation(self) -> str:
        """Generate C implementation file with structs and logic"""
        lines = []
        lines.append("/**")
        lines.append(f" * BLE Telemetry Protocol v{self.protocol['version']}")
        lines.append(" * Auto-generated from schema.json")
        lines.append(" * DO NOT EDIT MANUALLY")
        lines.append(" */")
        lines.append("")
        lines.append('#include "ble_protocol.h"')
        lines.append('#include <string.h>')
        lines.append("")

        # Protocol constants
        lines.append("// Protocol constants")
        first_sync = next(f['value'] for f in self.frame['first']['fields'] if f['name'] == 'sync')
        lines.append(f"#define BLE_SYNC_FIRST {first_sync}")
        lines.append("")

        # Private message structures (server messages)
        lines.append("// ============================================================================")
        lines.append("// Private message structures - Server messages")
        lines.append("// ============================================================================")
        lines.append("")

        for msg_name, msg_info in self.server_messages.items():
            lines.append(f"typedef struct {{")
            for field_name, field_type in msg_info['fields'].items():
                c_type = self.get_c_type(field_type)
                lines.append(f"    {c_type} {field_name};")
            lines.append(f"}} __attribute__((packed)) {msg_name}_t;")
            lines.append("")

        # Private message structures (client messages)
        lines.append("// ============================================================================")
        lines.append("// Private message structures - Client messages")
        lines.append("// ============================================================================")
        lines.append("")

        for msg_name, msg_info in self.client_messages.items():
            lines.append(f"typedef struct {{")
            for field_name, field_type in msg_info['fields'].items():
                c_type = self.get_c_type(field_type)
                lines.append(f"    {c_type} {field_name};")
            lines.append(f"}} __attribute__((packed)) {msg_name}_t;")
            lines.append("")

        # Private frame buffers
        lines.append("// ============================================================================")
        lines.append("// Private frame buffers")
        lines.append("// ============================================================================")
        lines.append("")

        # Server encode buffers
        for msg_name, msg_info in self.server_messages.items():
            msg_size = self.calculate_struct_size(msg_info['fields'])
            buffer_size = 3 + msg_size + 1  # Header + payload + checksum
            lines.append(f"static uint8_t {msg_name}_encode_buffer[{buffer_size}];")
            lines.append(f"static uint16_t {msg_name}_encode_len;")
        lines.append("")

        # Client decode buffers
        for msg_name, msg_info in self.client_messages.items():
            msg_size = self.calculate_struct_size(msg_info['fields'])
            buffer_size = 3 + msg_size + 1  # Header + payload + checksum
            lines.append(f"static uint8_t {msg_name}_decode_buffer[{buffer_size}];")
            lines.append(f"static bool {msg_name}_decode_valid;")
        lines.append("")

        # Checksum function
        lines.append("// ============================================================================")
        lines.append("// Private helper functions")
        lines.append("// ============================================================================")
        lines.append("")
        lines.append("// Calculate sum-mod-256 checksum")
        lines.append("static uint8_t ble_calculate_checksum(const uint8_t *data, uint16_t length) {")
        lines.append("    uint32_t sum = 0;")
        lines.append("    for (uint16_t i = 0; i < length; i++) {")
        lines.append("        sum += data[i];")
        lines.append("    }")
        lines.append("    return (uint8_t)(sum & 0xFF);")
        lines.append("}")
        lines.append("")

        # Server message encoding functions
        lines.append("// ============================================================================")
        lines.append("// Server message encoding functions (messages server sends)")
        lines.append("// ============================================================================")
        lines.append("")

        for msg_name, msg_info in self.server_messages.items():
            msg_size = self.calculate_struct_size(msg_info['fields'])

            # Begin encode function
            lines.append(f"// Begin encoding {msg_name} message")
            lines.append(f"void ble_encode_{msg_name}_begin(void) {{")
            lines.append(f"    const uint16_t payload_size = sizeof({msg_name}_t);")
            lines.append(f"    ")
            lines.append(f"    // Frame: [0xAA][Length][MsgID][Payload][Checksum]")
            lines.append(f"    {msg_name}_encode_buffer[0] = BLE_SYNC_FIRST;")
            lines.append(f"    {msg_name}_encode_buffer[1] = payload_size;")
            lines.append(f"    {msg_name}_encode_buffer[2] = {msg_info['id']};")
            lines.append(f"    ")
            lines.append(f"    // Zero out payload area")
            lines.append(f"    memset(&{msg_name}_encode_buffer[3], 0, payload_size);")
            lines.append(f"    ")
            lines.append(f"    // Frame length includes header, payload, and checksum")
            lines.append(f"    {msg_name}_encode_len = 3 + payload_size + 1;")
            lines.append(f"}}")
            lines.append("")

            # Setter functions for each field
            for field_name, field_type in msg_info['fields'].items():
                c_type = self.get_c_type(field_type)

                lines.append(f"// Set {field_name} in {msg_name} message")
                lines.append(f"void ble_encode_{msg_name}_set_{field_name}({c_type} value) {{")
                lines.append(f"    {msg_name}_t *msg = ({msg_name}_t*)&{msg_name}_encode_buffer[3];")
                lines.append(f"    msg->{field_name} = value;")
                lines.append(f"}}")
                lines.append("")

            # Get frame function
            lines.append(f"// Get encoded {msg_name} frame")
            lines.append(f"ble_frame_t ble_encode_{msg_name}_get_frame(void) {{")
            lines.append(f"    // Calculate checksum before returning frame")
            lines.append(f"    uint8_t payload_size = {msg_name}_encode_buffer[1];")
            lines.append(f"    {msg_name}_encode_buffer[3 + payload_size] = ble_calculate_checksum(&{msg_name}_encode_buffer[3], payload_size);")
            lines.append(f"    ")
            lines.append(f"    ble_frame_t frame = {{")
            lines.append(f"        .data = {msg_name}_encode_buffer,")
            lines.append(f"        .length = {msg_name}_encode_len")
            lines.append(f"    }};")
            lines.append(f"    return frame;")
            lines.append(f"}}")
            lines.append("")

        # Client message decoding functions
        lines.append("// ============================================================================")
        lines.append("// Client message decoding functions (messages server receives)")
        lines.append("// ============================================================================")
        lines.append("")

        for msg_name, msg_info in self.client_messages.items():
            msg_size = self.calculate_struct_size(msg_info['fields'])

            # Set frame function
            lines.append(f"// Set received {msg_name} frame for decoding")
            lines.append(f"bool ble_decode_{msg_name}_set_frame(const uint8_t *frame, uint16_t frame_len) {{")
            lines.append(f"    {msg_name}_decode_valid = false;")
            lines.append(f"    ")
            lines.append(f"    if (frame == NULL || frame_len < 5) return false;")
            lines.append(f"    ")
            lines.append(f"    // Verify first frame with correct message ID")
            lines.append(f"    if (frame[0] != BLE_SYNC_FIRST) return false;")
            lines.append(f"    if (frame[2] != {msg_info['id']}) return false;")
            lines.append(f"    ")
            lines.append(f"    // Verify frame length")
            lines.append(f"    uint8_t payload_size = frame[1];")
            lines.append(f"    if (payload_size != {msg_size}) return false;")
            lines.append(f"    if (frame_len < 3 + payload_size + 1) return false;")
            lines.append(f"    ")
            lines.append(f"    // Verify checksum (at end of frame)")
            lines.append(f"    uint8_t checksum = frame[3 + payload_size];")
            lines.append(f"    uint8_t calc_checksum = ble_calculate_checksum(&frame[3], payload_size);")
            lines.append(f"    if (checksum != calc_checksum) return false;")
            lines.append(f"    ")
            lines.append(f"    // Copy to internal buffer")
            lines.append(f"    memcpy({msg_name}_decode_buffer, frame, frame_len);")
            lines.append(f"    {msg_name}_decode_valid = true;")
            lines.append(f"    return true;")
            lines.append(f"}}")
            lines.append("")

            # Getter functions for each field
            for field_name, field_type in msg_info['fields'].items():
                c_type = self.get_c_type(field_type)

                lines.append(f"// Get {field_name} from {msg_name} message")
                lines.append(f"{c_type} ble_decode_{msg_name}_get_{field_name}(void) {{")
                lines.append(f"    if (!{msg_name}_decode_valid) return 0;")
                lines.append(f"    ")
                lines.append(f"    const {msg_name}_t *msg = (const {msg_name}_t*)&{msg_name}_decode_buffer[3];")
                lines.append(f"    return msg->{field_name};")
                lines.append(f"}}")
                lines.append("")

        return '\n'.join(lines)


def generate_c_code(schema_path: str, output_dir: str = '.'):
    """Main function to generate C code"""
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    generator = CGenerator(schema)

    # Generate header
    header_content = generator.generate_header()
    header_path = f"{output_dir}/ble_protocol.h"
    with open(header_path, 'w') as f:
        f.write(header_content)
    print(f"Generated: {header_path}")

    # Generate implementation
    impl_content = generator.generate_implementation()
    impl_path = f"{output_dir}/ble_protocol.c"
    with open(impl_path, 'w') as f:
        f.write(impl_content)
    print(f"Generated: {impl_path}")


if __name__ == '__main__':
    import sys
    schema_path = sys.argv[1] if len(sys.argv) > 1 else 'schema/schema.json'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'generated/c'
    generate_c_code(schema_path, output_dir)
