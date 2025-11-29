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
const int msgIdBmsData = 0x02;
const int msgIdBmsStatus = 0x03;
const int msgIdMotorData = 0x05;
const int msgIdSafetyStatus = 0x06;
const int msgIdPerformanceData = 0x07;
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
  BmsData? _bmsData;
  int _bmsDataTimestampMs = 0;
  bool _bmsDataUnread = false;
  BmsStatus? _bmsStatus;
  int _bmsStatusTimestampMs = 0;
  bool _bmsStatusUnread = false;
  MotorData? _motorData;
  int _motorDataTimestampMs = 0;
  bool _motorDataUnread = false;
  SafetyStatus? _safetyStatus;
  int _safetyStatusTimestampMs = 0;
  bool _safetyStatusUnread = false;
  PerformanceData? _performanceData;
  int _performanceDataTimestampMs = 0;
  bool _performanceDataUnread = false;

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
        _bmsData = _decodeBmsDataFromBuffer();
        _bmsDataTimestampMs = timestampMs;
        _bmsDataUnread = true;
        break;
      case 0x03:
        _bmsStatus = _decodeBmsStatusFromBuffer();
        _bmsStatusTimestampMs = timestampMs;
        _bmsStatusUnread = true;
        break;
      case 0x05:
        _motorData = _decodeMotorDataFromBuffer();
        _motorDataTimestampMs = timestampMs;
        _motorDataUnread = true;
        break;
      case 0x06:
        _safetyStatus = _decodeSafetyStatusFromBuffer();
        _safetyStatusTimestampMs = timestampMs;
        _safetyStatusUnread = true;
        break;
      case 0x07:
        _performanceData = _decodePerformanceDataFromBuffer();
        _performanceDataTimestampMs = timestampMs;
        _performanceDataUnread = true;
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

    msg._lvBatteryMv = data.getUint32(offset, Endian.little);
    offset += 4;

    msg._vehicleState = data.getUint8(offset);
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

  /// Internal: Decode bms_data from payload buffer
  BmsData _decodeBmsDataFromBuffer() {
    final msg = BmsData._();
    final data = ByteData.view(_payloadBuffer.buffer);
    int offset = 0;

    msg._cellVoltage1Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage2Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage3Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage4Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage5Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage6Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage7Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage8Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage9Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage10Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage11Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage12Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage13Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage14Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage15Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage16Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage17Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage18Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage19Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage20Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage21Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage22Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage23Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellVoltage24Mv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._packTempC = data.getInt16(offset, Endian.little);
    offset += 2;

    return msg;
  }

  /// Internal: Decode bms_status from payload buffer
  BmsStatus _decodeBmsStatusFromBuffer() {
    final msg = BmsStatus._();
    final data = ByteData.view(_payloadBuffer.buffer);
    int offset = 0;

    msg._socPercent = data.getUint8(offset);
    offset += 1;

    msg._sohPercent = data.getUint8(offset);
    offset += 1;

    msg._packVoltageMv = data.getUint32(offset, Endian.little);
    offset += 4;

    msg._packCurrentMa = data.getInt32(offset, Endian.little);
    offset += 4;

    msg._remainingRangeKm = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._timeToEmptyMin = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._timeToFullMin = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._cellDeltaMv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._minCellVoltageMv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._maxCellVoltageMv = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._minCellIndex = data.getUint8(offset);
    offset += 1;

    msg._maxCellIndex = data.getUint8(offset);
    offset += 1;

    return msg;
  }

  /// Internal: Decode motor_data from payload buffer
  MotorData _decodeMotorDataFromBuffer() {
    final msg = MotorData._();
    final data = ByteData.view(_payloadBuffer.buffer);
    int offset = 0;

    msg._motorTempC = data.getInt16(offset, Endian.little);
    offset += 2;

    msg._controllerTempC = data.getInt16(offset, Endian.little);
    offset += 2;

    msg._motorRpm = data.getUint32(offset, Endian.little);
    offset += 4;

    msg._powerW = data.getUint32(offset, Endian.little);
    offset += 4;

    msg._torqueNm = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._throttlePercent = data.getUint8(offset);
    offset += 1;

    msg._regenLevelPercent = data.getUint8(offset);
    offset += 1;

    return msg;
  }

  /// Internal: Decode safety_status from payload buffer
  SafetyStatus _decodeSafetyStatusFromBuffer() {
    final msg = SafetyStatus._();
    final data = ByteData.view(_payloadBuffer.buffer);
    int offset = 0;

    msg._faultCodes = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._warningFlags = data.getUint32(offset, Endian.little);
    offset += 4;

    msg._chargingStatus = data.getUint8(offset);
    offset += 1;

    msg._rideMode = data.getUint8(offset);
    offset += 1;

    msg._frontBrakeEngaged = data.getUint8(offset);
    offset += 1;

    msg._rearBrakeEngaged = data.getUint8(offset);
    offset += 1;

    return msg;
  }

  /// Internal: Decode performance_data from payload buffer
  PerformanceData _decodePerformanceDataFromBuffer() {
    final msg = PerformanceData._();
    final data = ByteData.view(_payloadBuffer.buffer);
    int offset = 0;

    msg._odometerKm = data.getUint32(offset, Endian.little);
    offset += 4;

    msg._tripKm = data.getUint32(offset, Endian.little);
    offset += 4;

    msg._avgSpeedKph = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._topSpeedKph = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._energyWhPerKm = data.getUint16(offset, Endian.little);
    offset += 2;

    msg._accel060Ms = data.getUint16(offset, Endian.little);
    offset += 2;

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

  /// Get stored bms_data message (returns null if no message available)
  BmsData? getBmsData() {
    if (_bmsData != null) {
      _bmsDataUnread = false;
    }
    return _bmsData;
  }

  /// Get stored bms_status message (returns null if no message available)
  BmsStatus? getBmsStatus() {
    if (_bmsStatus != null) {
      _bmsStatusUnread = false;
    }
    return _bmsStatus;
  }

  /// Get stored motor_data message (returns null if no message available)
  MotorData? getMotorData() {
    if (_motorData != null) {
      _motorDataUnread = false;
    }
    return _motorData;
  }

  /// Get stored safety_status message (returns null if no message available)
  SafetyStatus? getSafetyStatus() {
    if (_safetyStatus != null) {
      _safetyStatusUnread = false;
    }
    return _safetyStatus;
  }

  /// Get stored performance_data message (returns null if no message available)
  PerformanceData? getPerformanceData() {
    if (_performanceData != null) {
      _performanceDataUnread = false;
    }
    return _performanceData;
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

  /// Check if bms_data message is unread
  bool bmsDataCheckIsUnread() {
    return _bmsData != null && _bmsDataUnread;
  }

  /// Check if bms_data data is stale (max age: 2000ms)
  bool bmsDataCheckDataIsStale(int timeMs) {
    if (_bmsData == null) return true;
    final ageMs = timeMs - _bmsDataTimestampMs;
    return ageMs > 2000;
  }

  /// Check if bms_status message is unread
  bool bmsStatusCheckIsUnread() {
    return _bmsStatus != null && _bmsStatusUnread;
  }

  /// Check if bms_status data is stale (max age: 2000ms)
  bool bmsStatusCheckDataIsStale(int timeMs) {
    if (_bmsStatus == null) return true;
    final ageMs = timeMs - _bmsStatusTimestampMs;
    return ageMs > 2000;
  }

  /// Check if motor_data message is unread
  bool motorDataCheckIsUnread() {
    return _motorData != null && _motorDataUnread;
  }

  /// Check if motor_data data is stale (max age: 500ms)
  bool motorDataCheckDataIsStale(int timeMs) {
    if (_motorData == null) return true;
    final ageMs = timeMs - _motorDataTimestampMs;
    return ageMs > 500;
  }

  /// Check if safety_status message is unread
  bool safetyStatusCheckIsUnread() {
    return _safetyStatus != null && _safetyStatusUnread;
  }

  /// Check if safety_status data is stale (max age: 500ms)
  bool safetyStatusCheckDataIsStale(int timeMs) {
    if (_safetyStatus == null) return true;
    final ageMs = timeMs - _safetyStatusTimestampMs;
    return ageMs > 500;
  }

  /// Check if performance_data message is unread
  bool performanceDataCheckIsUnread() {
    return _performanceData != null && _performanceDataUnread;
  }

  /// Check if performance_data data is stale (max age: 1000ms)
  bool performanceDataCheckDataIsStale(int timeMs) {
    if (_performanceData == null) return true;
    final ageMs = timeMs - _performanceDataTimestampMs;
    return ageMs > 1000;
  }

}

// ============================================================================
// Server message classes (messages client receives)
// ============================================================================

/// Heartbeat message - Server to Client
class Heartbeat {
  int _uptimeMs = 0;
  int _lvBatteryMv = 0;
  int _vehicleState = 0;

  int get uptimeMs => _uptimeMs;
  int get lvBatteryMv => _lvBatteryMv;
  int get vehicleState => _vehicleState;

  Heartbeat._();

  int get messageId => 0x01;

  @override
  String toString() => 'Heartbeat(uptime_ms: ${uptimeMs}, lvBattery_mv: ${lvBatteryMv}, vehicle_state: ${vehicleState})';
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

/// BmsData message - Server to Client
class BmsData {
  int _cellVoltage1Mv = 0;
  int _cellVoltage2Mv = 0;
  int _cellVoltage3Mv = 0;
  int _cellVoltage4Mv = 0;
  int _cellVoltage5Mv = 0;
  int _cellVoltage6Mv = 0;
  int _cellVoltage7Mv = 0;
  int _cellVoltage8Mv = 0;
  int _cellVoltage9Mv = 0;
  int _cellVoltage10Mv = 0;
  int _cellVoltage11Mv = 0;
  int _cellVoltage12Mv = 0;
  int _cellVoltage13Mv = 0;
  int _cellVoltage14Mv = 0;
  int _cellVoltage15Mv = 0;
  int _cellVoltage16Mv = 0;
  int _cellVoltage17Mv = 0;
  int _cellVoltage18Mv = 0;
  int _cellVoltage19Mv = 0;
  int _cellVoltage20Mv = 0;
  int _cellVoltage21Mv = 0;
  int _cellVoltage22Mv = 0;
  int _cellVoltage23Mv = 0;
  int _cellVoltage24Mv = 0;
  int _packTempC = 0;

  int get cellVoltage1Mv => _cellVoltage1Mv;
  int get cellVoltage2Mv => _cellVoltage2Mv;
  int get cellVoltage3Mv => _cellVoltage3Mv;
  int get cellVoltage4Mv => _cellVoltage4Mv;
  int get cellVoltage5Mv => _cellVoltage5Mv;
  int get cellVoltage6Mv => _cellVoltage6Mv;
  int get cellVoltage7Mv => _cellVoltage7Mv;
  int get cellVoltage8Mv => _cellVoltage8Mv;
  int get cellVoltage9Mv => _cellVoltage9Mv;
  int get cellVoltage10Mv => _cellVoltage10Mv;
  int get cellVoltage11Mv => _cellVoltage11Mv;
  int get cellVoltage12Mv => _cellVoltage12Mv;
  int get cellVoltage13Mv => _cellVoltage13Mv;
  int get cellVoltage14Mv => _cellVoltage14Mv;
  int get cellVoltage15Mv => _cellVoltage15Mv;
  int get cellVoltage16Mv => _cellVoltage16Mv;
  int get cellVoltage17Mv => _cellVoltage17Mv;
  int get cellVoltage18Mv => _cellVoltage18Mv;
  int get cellVoltage19Mv => _cellVoltage19Mv;
  int get cellVoltage20Mv => _cellVoltage20Mv;
  int get cellVoltage21Mv => _cellVoltage21Mv;
  int get cellVoltage22Mv => _cellVoltage22Mv;
  int get cellVoltage23Mv => _cellVoltage23Mv;
  int get cellVoltage24Mv => _cellVoltage24Mv;
  int get packTempC => _packTempC;

  BmsData._();

  int get messageId => 0x02;

  @override
  String toString() => 'BmsData(cellVoltage1_mv: ${cellVoltage1Mv}, cellVoltage2_mv: ${cellVoltage2Mv}, cellVoltage3_mv: ${cellVoltage3Mv}, cellVoltage4_mv: ${cellVoltage4Mv}, cellVoltage5_mv: ${cellVoltage5Mv}, cellVoltage6_mv: ${cellVoltage6Mv}, cellVoltage7_mv: ${cellVoltage7Mv}, cellVoltage8_mv: ${cellVoltage8Mv}, cellVoltage9_mv: ${cellVoltage9Mv}, cellVoltage10_mv: ${cellVoltage10Mv}, cellVoltage11_mv: ${cellVoltage11Mv}, cellVoltage12_mv: ${cellVoltage12Mv}, cellVoltage13_mv: ${cellVoltage13Mv}, cellVoltage14_mv: ${cellVoltage14Mv}, cellVoltage15_mv: ${cellVoltage15Mv}, cellVoltage16_mv: ${cellVoltage16Mv}, cellVoltage17_mv: ${cellVoltage17Mv}, cellVoltage18_mv: ${cellVoltage18Mv}, cellVoltage19_mv: ${cellVoltage19Mv}, cellVoltage20_mv: ${cellVoltage20Mv}, cellVoltage21_mv: ${cellVoltage21Mv}, cellVoltage22_mv: ${cellVoltage22Mv}, cellVoltage23_mv: ${cellVoltage23Mv}, cellVoltage24_mv: ${cellVoltage24Mv}, packTemp_c: ${packTempC})';
}

/// BmsStatus message - Server to Client
class BmsStatus {
  int _socPercent = 0;
  int _sohPercent = 0;
  int _packVoltageMv = 0;
  int _packCurrentMa = 0;
  int _remainingRangeKm = 0;
  int _timeToEmptyMin = 0;
  int _timeToFullMin = 0;
  int _cellDeltaMv = 0;
  int _minCellVoltageMv = 0;
  int _maxCellVoltageMv = 0;
  int _minCellIndex = 0;
  int _maxCellIndex = 0;

  int get socPercent => _socPercent;
  int get sohPercent => _sohPercent;
  int get packVoltageMv => _packVoltageMv;
  int get packCurrentMa => _packCurrentMa;
  int get remainingRangeKm => _remainingRangeKm;
  int get timeToEmptyMin => _timeToEmptyMin;
  int get timeToFullMin => _timeToFullMin;
  int get cellDeltaMv => _cellDeltaMv;
  int get minCellVoltageMv => _minCellVoltageMv;
  int get maxCellVoltageMv => _maxCellVoltageMv;
  int get minCellIndex => _minCellIndex;
  int get maxCellIndex => _maxCellIndex;

  BmsStatus._();

  int get messageId => 0x03;

  @override
  String toString() => 'BmsStatus(soc_percent: ${socPercent}, soh_percent: ${sohPercent}, packVoltage_mv: ${packVoltageMv}, packCurrent_ma: ${packCurrentMa}, remainingRange_km: ${remainingRangeKm}, timeToEmpty_min: ${timeToEmptyMin}, timeToFull_min: ${timeToFullMin}, cellDelta_mv: ${cellDeltaMv}, minCellVoltage_mv: ${minCellVoltageMv}, maxCellVoltage_mv: ${maxCellVoltageMv}, minCellIndex: ${minCellIndex}, maxCellIndex: ${maxCellIndex})';
}

/// MotorData message - Server to Client
class MotorData {
  int _motorTempC = 0;
  int _controllerTempC = 0;
  int _motorRpm = 0;
  int _powerW = 0;
  int _torqueNm = 0;
  int _throttlePercent = 0;
  int _regenLevelPercent = 0;

  int get motorTempC => _motorTempC;
  int get controllerTempC => _controllerTempC;
  int get motorRpm => _motorRpm;
  int get powerW => _powerW;
  int get torqueNm => _torqueNm;
  int get throttlePercent => _throttlePercent;
  int get regenLevelPercent => _regenLevelPercent;

  MotorData._();

  int get messageId => 0x05;

  @override
  String toString() => 'MotorData(motorTemp_c: ${motorTempC}, controllerTemp_c: ${controllerTempC}, motorRpm: ${motorRpm}, power_w: ${powerW}, torque_nm: ${torqueNm}, throttle_percent: ${throttlePercent}, regenLevel_percent: ${regenLevelPercent})';
}

/// SafetyStatus message - Server to Client
class SafetyStatus {
  int _faultCodes = 0;
  int _warningFlags = 0;
  int _chargingStatus = 0;
  int _rideMode = 0;
  int _frontBrakeEngaged = 0;
  int _rearBrakeEngaged = 0;

  int get faultCodes => _faultCodes;
  int get warningFlags => _warningFlags;
  int get chargingStatus => _chargingStatus;
  int get rideMode => _rideMode;
  int get frontBrakeEngaged => _frontBrakeEngaged;
  int get rearBrakeEngaged => _rearBrakeEngaged;

  SafetyStatus._();

  int get messageId => 0x06;

  @override
  String toString() => 'SafetyStatus(faultCodes: ${faultCodes}, warning_flags: ${warningFlags}, charging_status: ${chargingStatus}, ride_mode: ${rideMode}, frontBrake_engaged: ${frontBrakeEngaged}, rearBrake_engaged: ${rearBrakeEngaged})';
}

/// PerformanceData message - Server to Client
class PerformanceData {
  int _odometerKm = 0;
  int _tripKm = 0;
  int _avgSpeedKph = 0;
  int _topSpeedKph = 0;
  int _energyWhPerKm = 0;
  int _accel060Ms = 0;

  int get odometerKm => _odometerKm;
  int get tripKm => _tripKm;
  int get avgSpeedKph => _avgSpeedKph;
  int get topSpeedKph => _topSpeedKph;
  int get energyWhPerKm => _energyWhPerKm;
  int get accel060Ms => _accel060Ms;

  PerformanceData._();

  int get messageId => 0x07;

  @override
  String toString() => 'PerformanceData(odometer_km: ${odometerKm}, trip_km: ${tripKm}, avgSpeed_kph: ${avgSpeedKph}, topSpeed_kph: ${topSpeedKph}, energy_wh_per_km: ${energyWhPerKm}, accel_0_60_ms: ${accel060Ms})';
}

// ============================================================================
// Protocol layer helper functions
// ============================================================================

// Calculate sum-mod-256 checksum
int _calculateChecksum(Uint8List data) {
  int sum = 0;
  for (var byte in data) {
    sum += byte;
  }
  return sum & 0xFF;
}