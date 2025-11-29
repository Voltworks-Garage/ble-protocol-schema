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
    def __init__(self, protocol_schema: Dict[str, Any], messages_schema: Dict[str, Any]):
        """
        Initialize generator with separate protocol and message schemas

        Args:
            protocol_schema: Contains protocol, frame, and types definitions
            messages_schema: Contains message definitions (server and client)
        """
        self.protocol = protocol_schema['protocol']
        self.frame = protocol_schema['frame']
        self.types = protocol_schema['types']
        self.server_messages = messages_schema['messages']['server']
        self.client_messages = messages_schema['messages']['client']

    # ========================================================================
    # Protocol Layer - Frame format and encoding/decoding logic
    # ========================================================================

    def _get_protocol_constants(self) -> List[str]:
        """Generate protocol-level constants (sync bytes, etc.)"""
        lines = []
        lines.append("// Protocol constants")
        first_sync = next(f['value'] for f in self.frame['first']['fields'] if f['name'] == 'sync')
        lines.append(f"const int bleSyncFirst = {first_sync};")
        lines.append("")
        return lines

    def _generate_checksum_function(self) -> List[str]:
        """Generate checksum calculation function"""
        lines = []
        lines.append("// Calculate sum-mod-256 checksum")
        lines.append("int _calculateChecksum(Uint8List data) {")
        lines.append("  int sum = 0;")
        lines.append("  for (var byte in data) {")
        lines.append("    sum += byte;")
        lines.append("  }")
        lines.append("  return sum & 0xFF;")
        lines.append("}")
        return lines

    def _generate_decode_frame_method(self) -> List[str]:
        """Generate frame decoding method with multi-frame support"""
        lines = []
        lines.append("  /// Decode a frame (supports multi-frame reassembly)")
        lines.append("  /// Returns true when a complete message is received and validated")
        lines.append("  /// [timeMs] Current time in milliseconds for timestamping received messages")
        lines.append("  bool decodeFrame(Uint8List frame, int timeMs) {")
        lines.append("    if (frame.isEmpty) return false;")
        lines.append("")
        lines.append("    // Check if this is a first frame")
        lines.append("    if (frame[0] == bleSyncFirst) {")
        lines.append("      // Reset state for new message")
        lines.append("      _valid = false;")
        lines.append("      _bytesReceived = 0;")
        lines.append("")
        lines.append("      // Verify minimum frame size for first frame")
        lines.append("      if (frame.length < 4) return false;")
        lines.append("")
        lines.append("      // Extract header")
        lines.append("      _expectedSize = frame[1];")
        lines.append("      _msgId = frame[2];")
        lines.append("")
        lines.append("      // Calculate payload bytes in this frame")
        lines.append("      final headerSize = 3;")
        lines.append("      final payloadInFrame = frame.length - headerSize;")
        lines.append("")
        lines.append("      // Check if this frame has checksum (complete message)")
        lines.append("      final hasChecksum = (payloadInFrame == _expectedSize + 1);")
        lines.append("")
        lines.append("      if (hasChecksum) {")
        lines.append("        // Single-frame message - verify checksum")
        lines.append("        final payloadData = frame.sublist(3, 3 + _expectedSize);")
        lines.append("        final checksum = frame[3 + _expectedSize];")
        lines.append("        final calcChecksum = _calculateChecksum(payloadData);")
        lines.append("        if (checksum != calcChecksum) return false;")
        lines.append("")
        lines.append("        // Copy payload to buffer")
        lines.append("        _payloadBuffer.setRange(0, _expectedSize, payloadData);")
        lines.append("        _bytesReceived = _expectedSize;")
        lines.append("        _valid = true;")
        lines.append("        ")
        lines.append("        // Store decoded message in per-message buffer")
        lines.append("        _storeMessage(timeMs);")
        lines.append("        return true;")
        lines.append("      } else {")
        lines.append("        // Multi-frame message - copy partial payload")
        lines.append("        if (payloadInFrame > _expectedSize) return false;")
        lines.append("        _payloadBuffer.setRange(0, payloadInFrame, frame.sublist(3));")
        lines.append("        _bytesReceived = payloadInFrame;")
        lines.append("        return false; // Need more frames")
        lines.append("      }")
        lines.append("    } else {")
        lines.append("      // Continuation frame (no sync byte, just payload)")
        lines.append("      if (_bytesReceived == 0) return false; // No first frame received")
        lines.append("")
        lines.append("      final remaining = _expectedSize - _bytesReceived;")
        lines.append("      final hasChecksum = (frame.length == remaining + 1);")
        lines.append("")
        lines.append("      if (hasChecksum) {")
        lines.append("        // Final frame - verify checksum")
        lines.append("        _payloadBuffer.setRange(_bytesReceived, _bytesReceived + remaining, frame);")
        lines.append("        _bytesReceived += remaining;")
        lines.append("")
        lines.append("        final checksum = frame[remaining];")
        lines.append("        final payloadData = _payloadBuffer.sublist(0, _expectedSize);")
        lines.append("        final calcChecksum = _calculateChecksum(payloadData);")
        lines.append("        if (checksum != calcChecksum) {")
        lines.append("          _bytesReceived = 0; // Reset on checksum failure")
        lines.append("          return false;")
        lines.append("        }")
        lines.append("")
        lines.append("        _valid = true;")
        lines.append("        ")
        lines.append("        // Store decoded message in per-message buffer")
        lines.append("        _storeMessage(timeMs);")
        lines.append("        return true;")
        lines.append("      } else {")
        lines.append("        // Continuation frame - copy payload")
        lines.append("        if (frame.length > remaining) return false;")
        lines.append("        _payloadBuffer.setRange(_bytesReceived, _bytesReceived + frame.length, frame);")
        lines.append("        _bytesReceived += frame.length;")
        lines.append("        return false; // Need more frames")
        lines.append("      }")
        lines.append("    }")
        lines.append("  }")
        lines.append("")
        return lines

    def _generate_store_message_method(self) -> List[str]:
        """Generate helper method to store decoded message in per-message buffer"""
        lines = []
        lines.append("  /// Store decoded message in per-message buffer")
        lines.append("  void _storeMessage(int timestampMs) {")
        lines.append("    switch (_msgId) {")
        for msg_name, msg_info in self.server_messages.items():
            class_name = self.to_pascal_case(msg_name)
            camel_name = self.to_camel_case(msg_name)
            lines.append(f"      case {msg_info['id']}:")
            lines.append(f"        _{camel_name} = _decode{class_name}FromBuffer();")
            lines.append(f"        _{camel_name}TimestampMs = timestampMs;")
            lines.append(f"        _{camel_name}Unread = true;")
            lines.append(f"        break;")
        lines.append("      default:")
        lines.append("        break;")
        lines.append("    }")
        lines.append("  }")
        lines.append("")
        return lines

    # ========================================================================
    # Message Layer - Type handling and message-specific logic
    # ========================================================================

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
            'string': 'String',
        }
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

    def calculate_struct_size(self, fields: Dict, max_string_length: int = 64) -> int:
        """Calculate total size of message in bytes"""
        total = 0
        for field_value in fields.values():
            total += self.get_field_size(field_value, max_string_length)
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

        # Protocol constants (from protocol layer)
        lines.extend(self._get_protocol_constants())

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
            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
                dart_type = self.get_dart_type(field_type)
                camel_name = self.to_camel_case(field_name)
                if self.is_variable_size(field_type):
                    lines.append(f"  {dart_type} _{camel_name} = '';")
                else:
                    lines.append(f"  {dart_type} _{camel_name} = 0;")
            lines.append("")

            # Getters
            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
                dart_type = self.get_dart_type(field_type)
                camel_name = self.to_camel_case(field_name)
                lines.append(f"  {dart_type} get {camel_name} => _{camel_name};")
            lines.append("")

            # Setters
            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
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

            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
                camel_name = self.to_camel_case(field_name)

                if self.is_variable_size(field_type):
                    # String encoding - null-terminated
                    field_size = self.get_field_size(field_value)
                    lines.append(f"    // Encode string (null-terminated)")
                    lines.append(f"    final stringBytes = _{camel_name}.codeUnits;")
                    lines.append(f"    final bytesToCopy = stringBytes.length < {field_size} - 1 ? stringBytes.length : {field_size} - 1;")
                    lines.append(f"    for (int i = 0; i < bytesToCopy; i++) {{")
                    lines.append(f"      payload[offset + i] = stringBytes[i];")
                    lines.append(f"    }}")
                    lines.append(f"    payload[offset + bytesToCopy] = 0; // Null terminator")
                    lines.append(f"    offset += {field_size};")
                    lines.append("")
                else:
                    # Numeric encoding
                    read_method, write_method = self.get_byte_data_method(field_type)
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

        # Decoder class for multi-frame reassembly
        lines.append("// ============================================================================")
        lines.append("// Decoder class for server messages (multi-frame support)")
        lines.append("// ============================================================================")
        lines.append("")

        max_server_size = max(self.calculate_struct_size(msg['fields']) for msg in self.server_messages.values())

        lines.append("/// Decoder for server messages with multi-frame reassembly support")
        lines.append("class BleDecoder {")
        lines.append(f"  final Uint8List _payloadBuffer = Uint8List({max_server_size});")
        lines.append("  int _expectedSize = 0;")
        lines.append("  int _bytesReceived = 0;")
        lines.append("  int _msgId = 0;")
        lines.append("  bool _valid = false;")
        lines.append("")

        # Per-message storage
        for msg_name, msg_info in self.server_messages.items():
            class_name = self.to_pascal_case(msg_name)
            camel_name = self.to_camel_case(msg_name)
            lines.append(f"  {class_name}? _{camel_name};")
            lines.append(f"  int _{camel_name}TimestampMs = 0;")
            lines.append(f"  bool _{camel_name}Unread = false;")
        lines.append("")

        # Protocol layer decode methods
        lines.extend(self._generate_decode_frame_method())
        lines.extend(self._generate_store_message_method())

        # Add internal decode methods (from buffer)
        for msg_name, msg_info in self.server_messages.items():
            class_name = self.to_pascal_case(msg_name)
            lines.append(f"  /// Internal: Decode {msg_name} from payload buffer")
            lines.append(f"  {class_name} _decode{class_name}FromBuffer() {{")
            lines.append(f"    final msg = {class_name}._();")
            lines.append("    final data = ByteData.view(_payloadBuffer.buffer);")
            lines.append("    int offset = 0;")
            lines.append("")

            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
                camel_name = self.to_camel_case(field_name)

                if self.is_variable_size(field_type):
                    # String decoding - null-terminated
                    field_size = self.get_field_size(field_value)
                    lines.append(f"    // Decode string (null-terminated)")
                    lines.append(f"    final stringBytes = <int>[];")
                    lines.append(f"    for (int i = 0; i < {field_size}; i++) {{")
                    lines.append(f"      final byte = _payloadBuffer[offset + i];")
                    lines.append(f"      if (byte == 0) break; // Null terminator")
                    lines.append(f"      stringBytes.add(byte);")
                    lines.append(f"    }}")
                    lines.append(f"    msg._{camel_name} = String.fromCharCodes(stringBytes);")
                    lines.append(f"    offset += {field_size};")
                    lines.append("")
                else:
                    # Numeric decoding
                    read_method, write_method = self.get_byte_data_method(field_type)
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

        # Add public getter methods for stored messages
        for msg_name, msg_info in self.server_messages.items():
            class_name = self.to_pascal_case(msg_name)
            camel_name = self.to_camel_case(msg_name)
            lines.append(f"  /// Get stored {msg_name} message (returns null if no message available)")
            lines.append(f"  {class_name}? get{class_name}() {{")
            lines.append(f"    if (_{camel_name} != null) {{")
            lines.append(f"      _{camel_name}Unread = false;")
            lines.append(f"    }}")
            lines.append(f"    return _{camel_name};")
            lines.append("  }")
            lines.append("")

        # Status methods
        for msg_name, msg_info in self.server_messages.items():
            class_name = self.to_pascal_case(msg_name)
            camel_name = self.to_camel_case(msg_name)
            max_age = msg_info.get('maxAge', 1000)

            # Check is unread
            lines.append(f"  /// Check if {msg_name} message is unread")
            lines.append(f"  bool {camel_name}CheckIsUnread() {{")
            lines.append(f"    return _{camel_name} != null && _{camel_name}Unread;")
            lines.append("  }")
            lines.append("")

            # Check data is stale
            lines.append(f"  /// Check if {msg_name} data is stale (max age: {max_age}ms)")
            lines.append(f"  bool {camel_name}CheckDataIsStale(int timeMs) {{")
            lines.append(f"    if (_{camel_name} == null) return true;")
            lines.append(f"    final ageMs = timeMs - _{camel_name}TimestampMs;")
            lines.append(f"    return ageMs > {max_age};")
            lines.append("  }")
            lines.append("")

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
            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
                dart_type = self.get_dart_type(field_type)
                camel_name = self.to_camel_case(field_name)
                if self.is_variable_size(field_type):
                    lines.append(f"  {dart_type} _{camel_name} = '';")
                else:
                    lines.append(f"  {dart_type} _{camel_name} = 0;")
            lines.append("")

            # Getters (read-only for received messages)
            for field_name, field_value in msg_info['fields'].items():
                field_type = self.get_field_type_name(field_value)
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

            # toString
            to_string_fields = ', '.join([
                f"{name}: ${{{self.to_camel_case(name)}}}"
                for name in msg_info['fields'].keys()
            ])
            lines.append("  @override")
            lines.append(f"  String toString() => '{class_name}({to_string_fields})';")

            lines.append("}")
            lines.append("")

        # Protocol layer helper functions
        lines.append("// ============================================================================")
        lines.append("// Protocol layer helper functions")
        lines.append("// ============================================================================")
        lines.append("")
        lines.extend(self._generate_checksum_function())

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


def generate_dart_code(protocol_schema_path: str, messages_schema_path: str, output_dir: str = '.'):
    """Main function to generate Dart code

    Args:
        protocol_schema_path: Path to protocol.json (frame format, types)
        messages_schema_path: Path to messages.json (message definitions)
        output_dir: Output directory for generated files
    """
    with open(protocol_schema_path, 'r') as f:
        protocol_schema = json.load(f)

    with open(messages_schema_path, 'r') as f:
        messages_schema = json.load(f)

    generator = DartGenerator(protocol_schema, messages_schema)

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
    protocol_path = sys.argv[1] if len(sys.argv) > 1 else 'schema/protocol.json'
    messages_path = sys.argv[2] if len(sys.argv) > 2 else 'schema/messages.json'
    output_dir = sys.argv[3] if len(sys.argv) > 3 else 'generated/dart'
    generate_dart_code(protocol_path, messages_path, output_dir)
