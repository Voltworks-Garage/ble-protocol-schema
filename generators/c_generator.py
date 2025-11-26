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

    def get_c_type(self, type_name: str, for_struct_decl: bool = False, max_string_length: int = 64) -> str:
        """Convert schema type to C type

        Args:
            type_name: The schema type name
            for_struct_decl: If True, returns type suitable for struct field declaration
            max_string_length: Maximum string length for string types
        """
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
        if type_name == 'string':
            # For struct declarations, we need the array size in the field declaration
            return 'char' if for_struct_decl else 'const char*'
        return type_map.get(type_name, type_name)

    def is_variable_size(self, type_name: str) -> bool:
        """Check if a type has variable size"""
        return self.types.get(type_name, {}).get('size') == 'variable'

    def get_field_type_name(self, field_value) -> str:
        """Extract type name from field value (handles both string and dict formats)"""
        if isinstance(field_value, dict):
            return field_value.get('type', field_value)
        return field_value

    def get_field_max_length(self, field_value, default: int = 64) -> int:
        """Get max_length for a string field"""
        if isinstance(field_value, dict):
            return field_value.get('max_length', default)
        return default

    def get_field_size(self, field_value, max_string_length: int = 64) -> int:
        """Get size of a field in bytes"""
        field_type = self.get_field_type_name(field_value)
        if self.is_variable_size(field_type):
            # For null-terminated strings, use max length from field or default
            return self.get_field_max_length(field_value, max_string_length)
        return self.types[field_type]['size']

    def calculate_struct_size(self, fields: Dict, max_string_length: int = 64) -> int:
        """Calculate total size of message struct in bytes"""
        total = 0
        for field_value in fields.values():
            total += self.get_field_size(field_value, max_string_length)
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
        lines.append("#ifdef __cplusplus")
        lines.append("extern \"C\" {")
        lines.append("#endif")
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
            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
                if self.is_variable_size(field_type):
                    lines.append(f"void ble_encode_{msg_name}_set_{field_name}(const char* value);")
                else:
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

        lines.append("// Generic frame decoding")
        lines.append("bool ble_decode_frame(const uint8_t *frame, uint16_t frame_len);")
        lines.append("")

        for msg_name, msg_info in self.client_messages.items():
            lines.append(f"// Get {msg_name} message fields")
            # Getter functions for each field
            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
                if self.is_variable_size(field_type):
                    lines.append(f"const char* ble_decode_{msg_name}_get_{field_name}(void);")
                else:
                    c_type = self.get_c_type(field_type)
                    lines.append(f"{c_type} ble_decode_{msg_name}_get_{field_name}(void);")
            lines.append("")

        lines.append("#ifdef __cplusplus")
        lines.append("}")
        lines.append("#endif")
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
            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
                if self.is_variable_size(field_type):
                    field_size = self.get_field_size(field_value)
                    lines.append(f"    char {field_name}[{field_size}];")
                else:
                    c_type = self.get_c_type(field_type, for_struct_decl=True)
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
            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
                if self.is_variable_size(field_type):
                    field_size = self.get_field_size(field_value)
                    lines.append(f"    char {field_name}[{field_size}];")
                else:
                    c_type = self.get_c_type(field_type, for_struct_decl=True)
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

        # Shared decode state for multi-frame reassembly
        max_client_size = max(self.calculate_struct_size(msg['fields']) for msg in self.client_messages.values())
        lines.append(f"static uint8_t decode_payload_buffer[{max_client_size}];")
        lines.append(f"static uint8_t decode_expected_size;")
        lines.append(f"static uint8_t decode_bytes_received;")
        lines.append(f"static uint8_t decode_msg_id;")
        lines.append(f"static bool decode_valid;")
        lines.append("")

        # Per-message decoded buffers (for storing complete messages)
        for msg_name, msg_info in self.client_messages.items():
            msg_size = self.calculate_struct_size(msg_info['fields'])
            lines.append(f"static {msg_name}_t {msg_name}_decoded;")
            lines.append(f"static bool {msg_name}_available;")
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
            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
                lines.append(f"// Set {field_name} in {msg_name} message")

                if self.is_variable_size(field_type):
                    # String setter
                    lines.append(f"void ble_encode_{msg_name}_set_{field_name}(const char* value) {{")
                    lines.append(f"    {msg_name}_t *msg = ({msg_name}_t*)&{msg_name}_encode_buffer[3];")
                    lines.append(f"    if (value != NULL) {{")
                    lines.append(f"        strncpy(msg->{field_name}, value, sizeof(msg->{field_name}) - 1);")
                    lines.append(f"        msg->{field_name}[sizeof(msg->{field_name}) - 1] = '\\0';")
                    lines.append(f"    }} else {{")
                    lines.append(f"        msg->{field_name}[0] = '\\0';")
                    lines.append(f"    }}")
                    lines.append(f"}}")
                else:
                    # Numeric setter
                    c_type = self.get_c_type(field_type)
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

        # Helper function to copy decoded message to per-message buffer
        lines.append("// Copy decoded payload to appropriate message buffer")
        lines.append("static void ble_decode_store_message(void) {")
        lines.append("    switch (decode_msg_id) {")
        for msg_name, msg_info in self.client_messages.items():
            lines.append(f"        case {msg_info['id']}:")
            lines.append(f"            memcpy(&{msg_name}_decoded, decode_payload_buffer, sizeof({msg_name}_t));")
            lines.append(f"            {msg_name}_available = true;")
            lines.append(f"            break;")
        lines.append("        default:")
        lines.append("            break;")
        lines.append("    }")
        lines.append("}")
        lines.append("")

        # Generic frame decoder with multi-frame support
        lines.append("// Decode client message frame (supports multi-frame reassembly)")
        lines.append("// Returns true when complete message is received and validated")
        lines.append("bool ble_decode_frame(const uint8_t *frame, uint16_t frame_len) {")
        lines.append("    if (frame == NULL || frame_len < 1) return false;")
        lines.append("    ")
        lines.append("    // Check if this is a first frame")
        lines.append("    if (frame[0] == BLE_SYNC_FIRST) {")
        lines.append("        // Reset state for new message")
        lines.append("        decode_valid = false;")
        lines.append("        decode_bytes_received = 0;")
        lines.append("        ")
        lines.append("        // Verify minimum frame size for first frame")
        lines.append("        if (frame_len < 4) return false;")
        lines.append("        ")
        lines.append("        // Extract header")
        lines.append("        decode_expected_size = frame[1];")
        lines.append("        decode_msg_id = frame[2];")
        lines.append("        ")
        lines.append("        // Calculate payload bytes in this frame")
        lines.append("        uint16_t header_size = 3;")
        lines.append("        uint16_t payload_in_frame = frame_len - header_size;")
        lines.append("        ")
        lines.append("        // Check if this frame has checksum (complete message)")
        lines.append("        bool has_checksum = (payload_in_frame == decode_expected_size + 1);")
        lines.append("        ")
        lines.append("        if (has_checksum) {")
        lines.append("            // Single-frame message - verify checksum")
        lines.append("            uint8_t checksum = frame[3 + decode_expected_size];")
        lines.append("            uint8_t calc_checksum = ble_calculate_checksum(&frame[3], decode_expected_size);")
        lines.append("            if (checksum != calc_checksum) return false;")
        lines.append("            ")
        lines.append("            // Copy payload to buffer")
        lines.append("            memcpy(decode_payload_buffer, &frame[3], decode_expected_size);")
        lines.append("            decode_bytes_received = decode_expected_size;")
        lines.append("            decode_valid = true;")
        lines.append("            ")
        lines.append("            // Store in per-message buffer")
        lines.append("            ble_decode_store_message();")
        lines.append("            return true;")
        lines.append("        } else {")
        lines.append("            // Multi-frame message - copy partial payload")
        lines.append("            if (payload_in_frame > decode_expected_size) return false;")
        lines.append("            memcpy(decode_payload_buffer, &frame[3], payload_in_frame);")
        lines.append("            decode_bytes_received = payload_in_frame;")
        lines.append("            return false; // Need more frames")
        lines.append("        }")
        lines.append("    } else {")
        lines.append("        // Continuation frame (no sync byte, just payload)")
        lines.append("        if (decode_bytes_received == 0) return false; // No first frame received")
        lines.append("        ")
        lines.append("        uint16_t remaining = decode_expected_size - decode_bytes_received;")
        lines.append("        bool has_checksum = (frame_len == remaining + 1);")
        lines.append("        ")
        lines.append("        if (has_checksum) {")
        lines.append("            // Final frame - verify checksum")
        lines.append("            memcpy(&decode_payload_buffer[decode_bytes_received], frame, remaining);")
        lines.append("            decode_bytes_received += remaining;")
        lines.append("            ")
        lines.append("            uint8_t checksum = frame[remaining];")
        lines.append("            uint8_t calc_checksum = ble_calculate_checksum(decode_payload_buffer, decode_expected_size);")
        lines.append("            if (checksum != calc_checksum) {")
        lines.append("                decode_bytes_received = 0; // Reset on checksum failure")
        lines.append("                return false;")
        lines.append("            }")
        lines.append("            ")
        lines.append("            decode_valid = true;")
        lines.append("            ")
        lines.append("            // Store in per-message buffer")
        lines.append("            ble_decode_store_message();")
        lines.append("            return true;")
        lines.append("        } else {")
        lines.append("            // Continuation frame - copy payload")
        lines.append("            if (frame_len > remaining) return false;")
        lines.append("            memcpy(&decode_payload_buffer[decode_bytes_received], frame, frame_len);")
        lines.append("            decode_bytes_received += frame_len;")
        lines.append("            return false; // Need more frames")
        lines.append("        }")
        lines.append("    }")
        lines.append("}")
        lines.append("")

        # Field getters for each message type
        for msg_name, msg_info in self.client_messages.items():
            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
                lines.append(f"// Get {field_name} from {msg_name} message")

                if self.is_variable_size(field_type):
                    # String getter
                    lines.append(f"const char* ble_decode_{msg_name}_get_{field_name}(void) {{")
                    lines.append(f"    if (!{msg_name}_available) return \"\";")
                    lines.append(f"    return {msg_name}_decoded.{field_name};")
                    lines.append(f"}}")
                else:
                    # Numeric getter
                    c_type = self.get_c_type(field_type)
                    lines.append(f"{c_type} ble_decode_{msg_name}_get_{field_name}(void) {{")
                    lines.append(f"    if (!{msg_name}_available) return 0;")
                    lines.append(f"    return {msg_name}_decoded.{field_name};")
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
