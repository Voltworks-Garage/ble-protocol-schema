/**
 * BLE Telemetry Protocol v1.0.0
 * Auto-generated from schema.json
 * DO NOT EDIT MANUALLY
 *
 * Client-side implementation:
 * - Encodes client messages (for transmission)
 * - Decodes server messages (for reception)
 *
 * Frame format:
 * - First frame: [0xAA][Length][MsgID][Payload...]
 * - Continuation: [Payload...]
 * - Final frame ends with: [Checksum]
 */

import 'dart:typed_data';

// Protocol constants
const int bleSyncFirst = 0xAA;

// Message IDs
const int msgIdHeartbeat = 0x01;
const int msgIdServerMessage = 0x04;
const int msgIdSensorData = 0x02;
const int msgIdMotorStatus = 0x03;
const int msgIdConfigAck = 0x11;
const int msgIdConfigSet = 0x10;

// ============================================================================
// Client message classes (messages client sends)
// ============================================================================

/// ConfigSet message - Client to Server
class ConfigSet {
  int _paramId = 0;
  int _value = 0;

  int get paramId => _paramId;
  int get value => _value;

  set paramId(int value) {
    _paramId = value;
  }
  set value(int value) {
    _value = value;
  }

  int get messageId => 0x10;

  int get payloadSize => 5;

  /// Encode message into a BLE frame
  Uint8List encodeFrame() {
    final payload = Uint8List(5);
    final data = ByteData.view(payload.buffer);
    int offset = 0;

    data.setUint8(offset, _paramId);
    offset += 1;

    data.setUint32(offset, _value, Endian.little);
    offset += 4;

    final frameSize = 3 + 5 + 1;
    final frame = Uint8List(frameSize);
    frame[0] = bleSyncFirst;
    frame[1] = 5;
    frame[2] = 0x10;
    frame.setRange(3, 3 + 5, payload);
    frame[frameSize - 1] = _calculateChecksum(payload);

    return frame;
  }

  @override
  String toString() => 'ConfigSet(param_id: ${paramId}, value: ${value})';
}

// ============================================================================
// Decoder class for server messages (multi-frame support)
// ============================================================================

/// Decoder for server messages with multi-frame reassembly support
class BleDecoder {
  final Uint8List _payloadBuffer = Uint8List(128);
  int _expectedSize = 0;
  int _bytesReceived = 0;
  int _msgId = 0;
  bool _valid = false;

  Heartbeat? _heartbeat;
  int _heartbeatTimestampMs = 0;
  bool _heartbeatUnread = false;
  ServerMessage? _serverMessage;
  int _serverMessageTimestampMs = 0;
  bool _serverMessageUnread = false;
  SensorData? _sensorData;
  int _sensorDataTimestampMs = 0;
  bool _sensorDataUnread = false;
  MotorStatus? _motorStatus;
  int _motorStatusTimestampMs = 0;
  bool _motorStatusUnread = false;
  ConfigAck? _configAck;
  int _configAckTimestampMs = 0;
  bool _configAckUnread = false;

  /// Decode a frame (supports multi-frame reassembly)
  /// Returns true when a complete message is received and validated
  /// [timeMs] Current time in milliseconds for timestamping received messages
  bool decodeFrame(Uint8List frame, int timeMs) {
    if (frame.isEmpty) return false;

    // Check if this is a first frame
    if (frame[0] == bleSyncFirst) {
      // Reset state for new message
      _valid = false;
      _bytesReceived = 0;

      // Verify minimum frame size for first frame
      if (frame.length < 4) return false;

      // Extract header
      _expectedSize = frame[1];
      _msgId = frame[2];

      // Calculate payload bytes in this frame
      final headerSize = 3;
      final payloadInFrame = frame.length - headerSize;

      // Check if this frame has checksum (complete message)
      final hasChecksum = (payloadInFrame == _expectedSize + 1);

      if (hasChecksum) {
        // Single-frame message - verify checksum
        final payloadData = frame.sublist(3, 3 + _expectedSize);
        final checksum = frame[3 + _expectedSize];
        final calcChecksum = _calculateChecksum(payloadData);
        if (checksum != calcChecksum) return false;

        // Copy payload to buffer
        _payloadBuffer.setRange(0, _expectedSize, payloadData);
        _bytesReceived = _expectedSize;
        _valid = true;
        
        // Store decoded message in per-message buffer
        _storeMessage(timeMs);
        return true;
      } else {
        // Multi-frame message - copy partial payload
        if (payloadInFrame > _expectedSize) return false;
        _payloadBuffer.setRange(0, payloadInFrame, frame.sublist(3));
        _bytesReceived = payloadInFrame;
        return false; // Need more frames
      }
    } else {
      // Continuation frame (no sync byte, just payload)
      if (_bytesReceived == 0) return false; // No first frame received

      final remaining = _expectedSize - _bytesReceived;
      final hasChecksum = (frame.length == remaining + 1);

      if (hasChecksum) {
        // Final frame - verify checksum
        _payloadBuffer.setRange(_bytesReceived, _bytesReceived + remaining, frame);
        _bytesReceived += remaining;

        final checksum = frame[remaining];
        final payloadData = _payloadBuffer.sublist(0, _expectedSize);
        final calcChecksum = _calculateChecksum(payloadData);
        if (checksum != calcChecksum) {
          _bytesReceived = 0; // Reset on checksum failure
          return false;
        }

        _valid = true;
        
        // Store decoded message in per-message buffer
        _storeMessage(timeMs);
        return true;
      } else {
        // Continuation frame - copy payload
        if (frame.length > remaining) return false;
        _payloadBuffer.setRange(_bytesReceived, _bytesReceived + frame.length, frame);
        _bytesReceived += frame.length;
        return false; // Need more frames
      }
    }
  }

  /// Store decoded message in per-message buffer
  void _storeMessage(int timestampMs) {
    switch (_msgId) {
      case 0x01:
        _heartbeat = _decodeHeartbeatFromBuffer();
        _heartbeatTimestampMs = timestampMs;
        _heartbeatUnread = true;
        break;
      case 0x04:
        _serverMessage = _decodeServerMessageFromBuffer();
        _serverMessageTimestampMs = timestampMs;
        _serverMessageUnread = true;
        break;
      case 0x02:
        _sensorData = _decodeSensorDataFromBuffer();
        _sensorDataTimestampMs = timestampMs;
        _sensorDataUnread = true;
        break;
      case 0x03:
        _motorStatus = _decodeMotorStatusFromBuffer();
        _motorStatusTimestampMs = timestampMs;
        _motorStatusUnread = true;
        break;
      case 0x11:
        _configAck = _decodeConfigAckFromBuffer();
        _configAckTimestampMs = timestampMs;
        _configAckUnread = true;
        break;
      default:
        break;
    }
  }

  /// Internal: Decode heartbeat from payload buffer
  Heartbeat _decodeHeartbeatFromBuffer() {
    final msg = Heartbeat._();
    final data = ByteData.view(_payloadBuffer.buffer);
    int offset = 0;

    msg._uptimeMs = data.getUint32(offset, Endian.little);
    offset += 4;

    msg._batteryMv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._statusFlags = data.getUint8(offset);
    offset += 1;

    return msg;
  }

  /// Internal: Decode server_message from payload buffer
  ServerMessage _decodeServerMessageFromBuffer() {
    final msg = ServerMessage._();
    final data = ByteData.view(_payloadBuffer.buffer);
    int offset = 0;

    // Decode string (null-terminated)
    final stringBytes = <int>[];
    for (int i = 0; i < 128; i++) {
      final byte = _payloadBuffer[offset + i];
      if (byte == 0) break; // Null terminator
      stringBytes.add(byte);
    }
    msg._data = String.fromCharCodes(stringBytes);
    offset += 128;

    return msg;
  }

  /// Internal: Decode sensor_data from payload buffer
  SensorData _decodeSensorDataFromBuffer() {
    final msg = SensorData._();
    final data = ByteData.view(_payloadBuffer.buffer);
    int offset = 0;

    msg._timestampMs = data.getUint32(offset, Endian.little);
    offset += 4;

    msg._temperatureC = data.getInt16(offset, Endian.little);
    offset += 2;

    msg._humidityPct = data.getUint8(offset);
    offset += 1;

    msg._pressurePa = data.getUint32(offset, Endian.little);
    offset += 4;

    return msg;
  }

  /// Internal: Decode motor_status from payload buffer
  MotorStatus _decodeMotorStatusFromBuffer() {
    final msg = MotorStatus._();
    final data = ByteData.view(_payloadBuffer.buffer);
    int offset = 0;

    msg._rpm = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._currentMa = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._tempC = data.getInt8(offset);
    offset += 1;

    msg._faultCode = data.getUint8(offset);
    offset += 1;

    return msg;
  }

  /// Internal: Decode config_ack from payload buffer
  ConfigAck _decodeConfigAckFromBuffer() {
    final msg = ConfigAck._();
    final data = ByteData.view(_payloadBuffer.buffer);
    int offset = 0;

    msg._paramId = data.getUint8(offset);
    offset += 1;

    msg._result = data.getUint8(offset);
    offset += 1;

    return msg;
  }

  /// Get stored heartbeat message (returns null if no message available)
  Heartbeat? getHeartbeat() {
    if (_heartbeat != null) {
      _heartbeatUnread = false;
    }
    return _heartbeat;
  }

  /// Get stored server_message message (returns null if no message available)
  ServerMessage? getServerMessage() {
    if (_serverMessage != null) {
      _serverMessageUnread = false;
    }
    return _serverMessage;
  }

  /// Get stored sensor_data message (returns null if no message available)
  SensorData? getSensorData() {
    if (_sensorData != null) {
      _sensorDataUnread = false;
    }
    return _sensorData;
  }

  /// Get stored motor_status message (returns null if no message available)
  MotorStatus? getMotorStatus() {
    if (_motorStatus != null) {
      _motorStatusUnread = false;
    }
    return _motorStatus;
  }

  /// Get stored config_ack message (returns null if no message available)
  ConfigAck? getConfigAck() {
    if (_configAck != null) {
      _configAckUnread = false;
    }
    return _configAck;
  }

  /// Check if heartbeat message is unread
  bool heartbeatCheckIsUnread() {
    return _heartbeat != null && _heartbeatUnread;
  }

  /// Check if heartbeat data is stale (max age: 5000ms)
  bool heartbeatCheckDataIsStale(int timeMs) {
    if (_heartbeat == null) return true;
    final ageMs = timeMs - _heartbeatTimestampMs;
    return ageMs > 5000;
  }

  /// Check if server_message message is unread
  bool serverMessageCheckIsUnread() {
    return _serverMessage != null && _serverMessageUnread;
  }

  /// Check if server_message data is stale (max age: 1000ms)
  bool serverMessageCheckDataIsStale(int timeMs) {
    if (_serverMessage == null) return true;
    final ageMs = timeMs - _serverMessageTimestampMs;
    return ageMs > 1000;
  }

  /// Check if sensor_data message is unread
  bool sensorDataCheckIsUnread() {
    return _sensorData != null && _sensorDataUnread;
  }

  /// Check if sensor_data data is stale (max age: 2000ms)
  bool sensorDataCheckDataIsStale(int timeMs) {
    if (_sensorData == null) return true;
    final ageMs = timeMs - _sensorDataTimestampMs;
    return ageMs > 2000;
  }

  /// Check if motor_status message is unread
  bool motorStatusCheckIsUnread() {
    return _motorStatus != null && _motorStatusUnread;
  }

  /// Check if motor_status data is stale (max age: 1000ms)
  bool motorStatusCheckDataIsStale(int timeMs) {
    if (_motorStatus == null) return true;
    final ageMs = timeMs - _motorStatusTimestampMs;
    return ageMs > 1000;
  }

  /// Check if config_ack message is unread
  bool configAckCheckIsUnread() {
    return _configAck != null && _configAckUnread;
  }

  /// Check if config_ack data is stale (max age: 1000ms)
  bool configAckCheckDataIsStale(int timeMs) {
    if (_configAck == null) return true;
    final ageMs = timeMs - _configAckTimestampMs;
    return ageMs > 1000;
  }

}

// ============================================================================
// Server message classes (messages client receives)
// ============================================================================

/// Heartbeat message - Server to Client
class Heartbeat {
  int _uptimeMs = 0;
  int _batteryMv = 0;
  int _statusFlags = 0;

  int get uptimeMs => _uptimeMs;
  int get batteryMv => _batteryMv;
  int get statusFlags => _statusFlags;

  Heartbeat._();

  int get messageId => 0x01;

  @override
  String toString() => 'Heartbeat(uptime_ms: ${uptimeMs}, battery_mv: ${batteryMv}, status_flags: ${statusFlags})';
}

/// ServerMessage message - Server to Client
class ServerMessage {
  String _data = '';

  String get data => _data;

  ServerMessage._();

  int get messageId => 0x04;

  @override
  String toString() => 'ServerMessage(data: ${data})';
}

/// SensorData message - Server to Client
class SensorData {
  int _timestampMs = 0;
  int _temperatureC = 0;
  int _humidityPct = 0;
  int _pressurePa = 0;

  int get timestampMs => _timestampMs;
  int get temperatureC => _temperatureC;
  int get humidityPct => _humidityPct;
  int get pressurePa => _pressurePa;

  SensorData._();

  int get messageId => 0x02;

  @override
  String toString() => 'SensorData(timestamp_ms: ${timestampMs}, temperature_c: ${temperatureC}, humidity_pct: ${humidityPct}, pressure_pa: ${pressurePa})';
}

/// MotorStatus message - Server to Client
class MotorStatus {
  int _rpm = 0;
  int _currentMa = 0;
  int _tempC = 0;
  int _faultCode = 0;

  int get rpm => _rpm;
  int get currentMa => _currentMa;
  int get tempC => _tempC;
  int get faultCode => _faultCode;

  MotorStatus._();

  int get messageId => 0x03;

  @override
  String toString() => 'MotorStatus(rpm: ${rpm}, current_ma: ${currentMa}, temp_c: ${tempC}, fault_code: ${faultCode})';
}

/// ConfigAck message - Server to Client
class ConfigAck {
  int _paramId = 0;
  int _result = 0;

  int get paramId => _paramId;
  int get result => _result;

  ConfigAck._();

  int get messageId => 0x11;

  @override
  String toString() => 'ConfigAck(param_id: ${paramId}, result: ${result})';
}

// ============================================================================
// Private helper functions
// ============================================================================

// Calculate sum-mod-256 checksum
int _calculateChecksum(Uint8List data) {
  int sum = 0;
  for (var byte in data) {
    sum += byte;
  }
  return sum & 0xFF;
}