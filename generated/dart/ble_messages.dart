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

  /// Decode heartbeat from frame
  static Heartbeat? decode(Uint8List frame) {
    if (frame.length < 5) return null;

    // Verify first frame with correct message ID
    if (frame[0] != bleSyncFirst) return null;
    if (frame[2] != 0x01) return null;

    // Verify frame length
    final payloadSize = frame[1];
    if (payloadSize != 7) return null;
    if (frame.length < 3 + payloadSize + 1) return null;

    // Extract and verify checksum (at end of frame)
    final payloadData = frame.sublist(3, 3 + payloadSize);
    final checksum = frame[3 + payloadSize];
    final calcChecksum = _calculateChecksum(payloadData);
    if (checksum != calcChecksum) return null;

    // Decode message
    final msg = Heartbeat._();
    final data = ByteData.view(payloadData.buffer);
    int offset = 0;

    msg._uptimeMs = data.getUint32(offset, Endian.little);
    offset += 4;

    msg._batteryMv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._statusFlags = data.getUint8(offset);
    offset += 1;

    return msg;
  }

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

  /// Decode sensor_data from frame
  static SensorData? decode(Uint8List frame) {
    if (frame.length < 5) return null;

    // Verify first frame with correct message ID
    if (frame[0] != bleSyncFirst) return null;
    if (frame[2] != 0x02) return null;

    // Verify frame length
    final payloadSize = frame[1];
    if (payloadSize != 11) return null;
    if (frame.length < 3 + payloadSize + 1) return null;

    // Extract and verify checksum (at end of frame)
    final payloadData = frame.sublist(3, 3 + payloadSize);
    final checksum = frame[3 + payloadSize];
    final calcChecksum = _calculateChecksum(payloadData);
    if (checksum != calcChecksum) return null;

    // Decode message
    final msg = SensorData._();
    final data = ByteData.view(payloadData.buffer);
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

  /// Decode motor_status from frame
  static MotorStatus? decode(Uint8List frame) {
    if (frame.length < 5) return null;

    // Verify first frame with correct message ID
    if (frame[0] != bleSyncFirst) return null;
    if (frame[2] != 0x03) return null;

    // Verify frame length
    final payloadSize = frame[1];
    if (payloadSize != 6) return null;
    if (frame.length < 3 + payloadSize + 1) return null;

    // Extract and verify checksum (at end of frame)
    final payloadData = frame.sublist(3, 3 + payloadSize);
    final checksum = frame[3 + payloadSize];
    final calcChecksum = _calculateChecksum(payloadData);
    if (checksum != calcChecksum) return null;

    // Decode message
    final msg = MotorStatus._();
    final data = ByteData.view(payloadData.buffer);
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

  /// Decode config_ack from frame
  static ConfigAck? decode(Uint8List frame) {
    if (frame.length < 5) return null;

    // Verify first frame with correct message ID
    if (frame[0] != bleSyncFirst) return null;
    if (frame[2] != 0x11) return null;

    // Verify frame length
    final payloadSize = frame[1];
    if (payloadSize != 2) return null;
    if (frame.length < 3 + payloadSize + 1) return null;

    // Extract and verify checksum (at end of frame)
    final payloadData = frame.sublist(3, 3 + payloadSize);
    final checksum = frame[3 + payloadSize];
    final calcChecksum = _calculateChecksum(payloadData);
    if (checksum != calcChecksum) return null;

    // Decode message
    final msg = ConfigAck._();
    final data = ByteData.view(payloadData.buffer);
    int offset = 0;

    msg._paramId = data.getUint8(offset);
    offset += 1;

    msg._result = data.getUint8(offset);
    offset += 1;

    return msg;
  }

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