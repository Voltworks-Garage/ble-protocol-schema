"""
Dart/Flutter Code Generator for BLE Protocol
Generates Dart classes and codec from schema.json
Client-side implementation: Encodes client messages, decodes server messages

Frame format:
- First frame: [0xAA][Length][MsgID][Payload...]
- Continuation: [Payload...]
- Final frame ends with: [Checksum] (covers entire payload)
"""

import json
from typing import Dict, List, Any, Tuple


class DartGenerator:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.protocol = schema['protocol']
        self.frame = schema['frame']
        self.server_messages = schema['messages']['server']
        self.client_messages = schema['messages']['client']
        self.types = schema['types']

    def get_dart_type(self, type_name: str) -> str:
        """Convert schema type to Dart type"""
        type_map = {
            'uint8': 'int',
            'int8': 'int',
            'uint16': 'int',
            'int16': 'int',
            'uint32': 'int',
            'int32': 'int',
            'uint64': 'int',
            'int64': 'int',
        }
        return type_map.get(type_name, type_name)

    def get_byte_data_method(self, type_name: str) -> Tuple[str, str]:
        """Get ByteData read/write method for a type"""
        methods = {
            'uint8': ('getUint8', 'setUint8'),
            'int8': ('getInt8', 'setInt8'),
            'uint16': ('getUint16', 'setUint16'),
            'int16': ('getInt16', 'setInt16'),
            'uint32': ('getUint32', 'setUint32'),
            'int32': ('getInt32', 'setInt32'),
            'uint64': ('getUint64', 'setUint64'),
            'int64': ('getInt64', 'setInt64'),
        }
        return methods.get(type_name, ('getUint8', 'setUint8'))

    def calculate_struct_size(self, fields: Dict[str, str]) -> int:
        """Calculate total size of message in bytes"""
        total = 0
        for field_type in fields.values():
            total += self.types[field_type]['size']
        return total

    def to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase"""
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    def to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase"""
        return ''.join(x.title() for x in snake_str.split('_'))

    def generate_messages(self) -> str:
        """Generate Dart message classes with encapsulation"""
        lines = []
        lines.append("/**")
        lines.append(f" * BLE Telemetry Protocol v{self.protocol['version']}")
        lines.append(" * Auto-generated from schema.json")
        lines.append(" * DO NOT EDIT MANUALLY")
        lines.append(" *")
        lines.append(" * Client-side implementation:")
        lines.append(" * - Encodes client messages (for transmission)")
        lines.append(" * - Decodes server messages (for reception)")
        lines.append(" *")
        lines.append(" * Frame format:")
        lines.append(" * - First frame: [0xAA][Length][MsgID][Payload...]")
        lines.append(" * - Continuation: [Payload...]")
        lines.append(" * - Final frame ends with: [Checksum]")
        lines.append(" */")
        lines.append("")
        lines.append("import 'dart:typed_data';")
        lines.append("")

        # Constants
        lines.append("// Protocol constants")
        first_sync = next(f['value'] for f in self.frame['first']['fields'] if f['name'] == 'sync')
        lines.append(f"const int bleSyncFirst = {first_sync};")
        lines.append("")

        # Message IDs
        lines.append("// Message IDs")
        for msg_name, msg_info in self.server_messages.items():
            constant_name = f"msgId{self.to_pascal_case(msg_name)}"
            lines.append(f"const int {constant_name} = {msg_info['id']};")
        for msg_name, msg_info in self.client_messages.items():
            constant_name = f"msgId{self.to_pascal_case(msg_name)}"
            lines.append(f"const int {constant_name} = {msg_info['id']};")
        lines.append("")

        # Client message classes (client sends these)
        lines.append("// ============================================================================")
        lines.append("// Client message classes (messages client sends)")
        lines.append("// ============================================================================")
        lines.append("")

        for msg_name, msg_info in self.client_messages.items():
            class_name = self.to_pascal_case(msg_name)
            msg_size = self.calculate_struct_size(msg_info['fields'])

            lines.append(f"/// {class_name} message - Client to Server")
            lines.append(f"class {class_name} {{")

            # Private fields
            for field_name, field_type in msg_info['fields'].items():
                dart_type = self.get_dart_type(field_type)
                camel_name = self.to_camel_case(field_name)
                lines.append(f"  {dart_type} _{camel_name} = 0;")
            lines.append("")

            # Getters
            for field_name, field_type in msg_info['fields'].items():
                dart_type = self.get_dart_type(field_type)
                camel_name = self.to_camel_case(field_name)
                lines.append(f"  {dart_type} get {camel_name} => _{camel_name};")
            lines.append("")

            # Setters
            for field_name, field_type in msg_info['fields'].items():
                dart_type = self.get_dart_type(field_type)
                camel_name = self.to_camel_case(field_name)
                lines.append(f"  set {camel_name}({dart_type} value) {{")
                lines.append(f"    _{camel_name} = value;")
                lines.append(f"  }}")
            lines.append("")

            # Message ID getter
            lines.append(f"  int get messageId => {msg_info['id']};")
            lines.append("")

            # Payload size getter
            lines.append(f"  int get payloadSize => {msg_size};")
            lines.append("")

            # Encode method
            lines.append("  /// Encode message into a BLE frame")
            lines.append("  Uint8List encodeFrame() {")
            lines.append(f"    final payload = Uint8List({msg_size});")
            lines.append("    final data = ByteData.view(payload.buffer);")
            lines.append("    int offset = 0;")
            lines.append("")

            for field_name, field_type in msg_info['fields'].items():
                read_method, write_method = self.get_byte_data_method(field_type)
                camel_name = self.to_camel_case(field_name)
                field_size = self.types[field_type]['size']

                if field_size == 1:
                    lines.append(f"    data.{write_method}(offset, _{camel_name});")
                else:
                    lines.append(f"    data.{write_method}(offset, _{camel_name}, Endian.little);")
                lines.append(f"    offset += {field_size};")
                lines.append("")

            # Create frame: [0xAA][Length][MsgID][Payload][Checksum]
            lines.append(f"    final frameSize = 3 + {msg_size} + 1;")
            lines.append("    final frame = Uint8List(frameSize);")
            lines.append("    frame[0] = bleSyncFirst;")
            lines.append(f"    frame[1] = {msg_size};")
            lines.append(f"    frame[2] = {msg_info['id']};")
            lines.append(f"    frame.setRange(3, 3 + {msg_size}, payload);")
            lines.append(f"    frame[frameSize - 1] = _calculateChecksum(payload);")
            lines.append("")
            lines.append("    return frame;")
            lines.append("  }")
            lines.append("")

            # toString
            to_string_fields = ', '.join([
                f"{name}: ${{{self.to_camel_case(name)}}}"
                for name in msg_info['fields'].keys()
            ])
            lines.append("  @override")
            lines.append(f"  String toString() => '{class_name}({to_string_fields})';")

            lines.append("}")
            lines.append("")

        # Server message classes (client receives these)
        lines.append("// ============================================================================")
        lines.append("// Server message classes (messages client receives)")
        lines.append("// ============================================================================")
        lines.append("")

        for msg_name, msg_info in self.server_messages.items():
            class_name = self.to_pascal_case(msg_name)
            msg_size = self.calculate_struct_size(msg_info['fields'])

            lines.append(f"/// {class_name} message - Server to Client")
            lines.append(f"class {class_name} {{")

            # Private fields
            for field_name, field_type in msg_info['fields'].items():
                dart_type = self.get_dart_type(field_type)
                camel_name = self.to_camel_case(field_name)
                lines.append(f"  {dart_type} _{camel_name} = 0;")
            lines.append("")

            # Getters (read-only for received messages)
            for field_name, field_type in msg_info['fields'].items():
                dart_type = self.get_dart_type(field_type)
                camel_name = self.to_camel_case(field_name)
                lines.append(f"  {dart_type} get {camel_name} => _{camel_name};")
            lines.append("")

            # Private constructor
            lines.append(f"  {class_name}._();")
            lines.append("")

            # Message ID getter
            lines.append(f"  int get messageId => {msg_info['id']};")
            lines.append("")

            # Static decode method (stateless)
            lines.append(f"  /// Decode {msg_name} from frame")
            lines.append(f"  static {class_name}? decode(Uint8List frame) {{")
            lines.append("    if (frame.length < 5) return null;")
            lines.append("")
            lines.append("    // Verify first frame with correct message ID")
            lines.append("    if (frame[0] != bleSyncFirst) return null;")
            lines.append(f"    if (frame[2] != {msg_info['id']}) return null;")
            lines.append("")
            lines.append("    // Verify frame length")
            lines.append("    final payloadSize = frame[1];")
            lines.append(f"    if (payloadSize != {msg_size}) return null;")
            lines.append("    if (frame.length < 3 + payloadSize + 1) return null;")
            lines.append("")
            lines.append("    // Extract and verify checksum (at end of frame)")
            lines.append("    final payloadData = frame.sublist(3, 3 + payloadSize);")
            lines.append("    final checksum = frame[3 + payloadSize];")
            lines.append("    final calcChecksum = _calculateChecksum(payloadData);")
            lines.append("    if (checksum != calcChecksum) return null;")
            lines.append("")
            lines.append(f"    // Decode message")
            lines.append(f"    final msg = {class_name}._();")
            lines.append("    final data = ByteData.view(payloadData.buffer);")
            lines.append("    int offset = 0;")
            lines.append("")

            for field_name, field_type in msg_info['fields'].items():
                read_method, write_method = self.get_byte_data_method(field_type)
                camel_name = self.to_camel_case(field_name)
                field_size = self.types[field_type]['size']

                if field_size == 1:
                    lines.append(f"    msg._{camel_name} = data.{read_method}(offset);")
                else:
                    lines.append(f"    msg._{camel_name} = data.{read_method}(offset, Endian.little);")
                lines.append(f"    offset += {field_size};")
                lines.append("")

            lines.append("    return msg;")
            lines.append("  }")
            lines.append("")

            # toString
            to_string_fields = ', '.join([
                f"{name}: ${{{self.to_camel_case(name)}}}"
                for name in msg_info['fields'].keys()
            ])
            lines.append("  @override")
            lines.append(f"  String toString() => '{class_name}({to_string_fields})';")

            lines.append("}")
            lines.append("")

        # Checksum helper
        lines.append("// ============================================================================")
        lines.append("// Private helper functions")
        lines.append("// ============================================================================")
        lines.append("")
        lines.append("// Calculate sum-mod-256 checksum")
        lines.append("int _calculateChecksum(Uint8List data) {")
        lines.append("  int sum = 0;")
        lines.append("  for (var byte in data) {")
        lines.append("    sum += byte;")
        lines.append("  }")
        lines.append("  return sum & 0xFF;")
        lines.append("}")

        return '\n'.join(lines)

    def generate_codec(self) -> str:
        """Generate empty codec file for compatibility"""
        lines = []
        lines.append("/**")
        lines.append(f" * BLE Protocol Codec v{self.protocol['version']}")
        lines.append(" * Auto-generated from schema.json")
        lines.append(" * DO NOT EDIT MANUALLY")
        lines.append(" *")
        lines.append(" * Note: This file is generated for compatibility but is no longer needed.")
        lines.append(" * All encoding/decoding is done directly on message classes.")
        lines.append(" */")
        lines.append("")
        lines.append("// Decoder functionality is now built into message classes")
        lines.append("// - Client messages: Use encodeFrame() method")
        lines.append("// - Server messages: Use static decode() method")

        return '\n'.join(lines)


def generate_dart_code(schema_path: str, output_dir: str = '.'):
    """Main function to generate Dart code"""
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    generator = DartGenerator(schema)

    # Generate messages
    messages_content = generator.generate_messages()
    messages_path = f"{output_dir}/ble_messages.dart"
    with open(messages_path, 'w') as f:
        f.write(messages_content)
    print(f"Generated: {messages_path}")

    # Generate codec (now minimal)
    codec_content = generator.generate_codec()
    codec_path = f"{output_dir}/ble_codec.dart"
    with open(codec_path, 'w') as f:
        f.write(codec_content)
    print(f"Generated: {codec_path}")


if __name__ == '__main__':
    import sys
    schema_path = sys.argv[1] if len(sys.argv) > 1 else 'schema/schema.json'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'generated/dart'
    generate_dart_code(schema_path, output_dir)
