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
  final Uint8List _payloadBuffer = Uint8List(11);
  int _expectedSize = 0;
  int _bytesReceived = 0;
  int _msgId = 0;
  bool _valid = false;

  /// Decode a frame (supports multi-frame reassembly)
  /// Returns true when a complete message is received and validated
  bool decodeFrame(Uint8List frame) {
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

  /// Decode heartbeat message from last received frame
  Heartbeat? decodeHeartbeat() {
    if (!_valid) return null;
    if (_msgId != 0x01) return null;

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

  /// Decode sensor_data message from last received frame
  SensorData? decodeSensorData() {
    if (!_valid) return null;
    if (_msgId != 0x02) return null;

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

  /// Decode motor_status message from last received frame
  MotorStatus? decodeMotorStatus() {
    if (!_valid) return null;
    if (_msgId != 0x03) return null;

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

  /// Decode config_ack message from last received frame
  ConfigAck? decodeConfigAck() {
    if (!_valid) return null;
    if (_msgId != 0x11) return null;

    final msg = ConfigAck._();
    final data = ByteData.view(_payloadBuffer.buffer);
    int offset = 0;

    msg._paramId = data.getUint8(offset);
    offset += 1;

    msg._result = data.getUint8(offset);
    offset += 1;

    return msg;
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