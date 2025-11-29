/**
 * BLE Telemetry Protocol v1.0.0
 * Auto-generated from schema.json
 * DO NOT EDIT MANUALLY
 *
 * Server-side implementation:
 * - Encodes server messages (for transmission)
 * - Decodes client messages (for reception)
 *
 * Frame format:
 * - First frame: [0xAA][Length][MsgID][Payload...]
 * - Continuation: [Payload...]
 * - Final frame ends with: [Checksum]
 *
 * Frame buffers are managed internally.
 */

#ifndef BLE_PROTOCOL_H
#define BLE_PROTOCOL_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdbool.h>

// Frame structure
typedef struct {
    const uint8_t *data;
    uint16_t length;
} ble_frame_t;

// Message IDs
#define MSG_ID_HEARTBEAT          0x01
#define MSG_ID_SERVER_MESSAGE     0x04
#define MSG_ID_BMS_DATA           0x02
#define MSG_ID_BMS_STATUS         0x03
#define MSG_ID_MOTOR_DATA         0x05
#define MSG_ID_SAFETY_STATUS      0x06
#define MSG_ID_PERFORMANCE_DATA   0x07
#define MSG_ID_CONFIG_SET         0x10

// ============================================================================
// Server message encoding functions
// ============================================================================

// Encode and get heartbeat message
void ble_encode_heartbeat_begin(void);
void ble_encode_heartbeat_set_uptime_ms(uint32_t value);
void ble_encode_heartbeat_set_lvBattery_mv(uint32_t value);
void ble_encode_heartbeat_set_vehicle_state(uint8_t value);
ble_frame_t ble_encode_heartbeat_get_frame(void);

// Encode and get server_message message
void ble_encode_server_message_begin(void);
void ble_encode_server_message_set_data(const uint8_t* value);
ble_frame_t ble_encode_server_message_get_frame(void);

// Encode and get bms_data message
void ble_encode_bms_data_begin(void);
void ble_encode_bms_data_set_cellVoltage1_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage2_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage3_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage4_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage5_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage6_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage7_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage8_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage9_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage10_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage11_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage12_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage13_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage14_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage15_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage16_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage17_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage18_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage19_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage20_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage21_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage22_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage23_mv(uint16_t value);
void ble_encode_bms_data_set_cellVoltage24_mv(uint16_t value);
void ble_encode_bms_data_set_packTemp_c(int16_t value);
ble_frame_t ble_encode_bms_data_get_frame(void);

// Encode and get bms_status message
void ble_encode_bms_status_begin(void);
void ble_encode_bms_status_set_soc_percent(uint8_t value);
void ble_encode_bms_status_set_soh_percent(uint8_t value);
void ble_encode_bms_status_set_packVoltage_mv(uint32_t value);
void ble_encode_bms_status_set_packCurrent_ma(int32_t value);
void ble_encode_bms_status_set_remainingRange_km(uint16_t value);
void ble_encode_bms_status_set_timeToEmpty_min(uint16_t value);
void ble_encode_bms_status_set_timeToFull_min(uint16_t value);
void ble_encode_bms_status_set_cellDelta_mv(uint16_t value);
void ble_encode_bms_status_set_minCellVoltage_mv(uint16_t value);
void ble_encode_bms_status_set_maxCellVoltage_mv(uint16_t value);
void ble_encode_bms_status_set_minCellIndex(uint8_t value);
void ble_encode_bms_status_set_maxCellIndex(uint8_t value);
ble_frame_t ble_encode_bms_status_get_frame(void);

// Encode and get motor_data message
void ble_encode_motor_data_begin(void);
void ble_encode_motor_data_set_motorTemp_c(int16_t value);
void ble_encode_motor_data_set_controllerTemp_c(int16_t value);
void ble_encode_motor_data_set_motorRpm(uint32_t value);
void ble_encode_motor_data_set_power_w(uint32_t value);
void ble_encode_motor_data_set_torque_nm(uint16_t value);
void ble_encode_motor_data_set_throttle_percent(uint8_t value);
void ble_encode_motor_data_set_regenLevel_percent(uint8_t value);
ble_frame_t ble_encode_motor_data_get_frame(void);

// Encode and get safety_status message
void ble_encode_safety_status_begin(void);
void ble_encode_safety_status_set_faultCodes(uint16_t value);
void ble_encode_safety_status_set_warning_flags(uint32_t value);
void ble_encode_safety_status_set_charging_status(uint8_t value);
void ble_encode_safety_status_set_ride_mode(uint8_t value);
void ble_encode_safety_status_set_frontBrake_engaged(uint8_t value);
void ble_encode_safety_status_set_rearBrake_engaged(uint8_t value);
ble_frame_t ble_encode_safety_status_get_frame(void);

// Encode and get performance_data message
void ble_encode_performance_data_begin(void);
void ble_encode_performance_data_set_odometer_km(uint32_t value);
void ble_encode_performance_data_set_trip_km(uint32_t value);
void ble_encode_performance_data_set_avgSpeed_kph(uint16_t value);
void ble_encode_performance_data_set_topSpeed_kph(uint16_t value);
void ble_encode_performance_data_set_energy_wh_per_km(uint16_t value);
void ble_encode_performance_data_set_accel_0_60_ms(uint16_t value);
ble_frame_t ble_encode_performance_data_get_frame(void);

// ============================================================================
// Client message decoding functions
// ============================================================================

// Generic frame decoding
// time_ms: Current time in milliseconds for timestamping received messages
bool ble_decode_frame(const uint8_t *frame, uint16_t frame_len, uint32_t time_ms);

// Get config_set message fields
uint8_t ble_decode_config_set_get_param_id(void);
uint32_t ble_decode_config_set_get_value(void);

// ============================================================================
// Message status functions
// ============================================================================

// config_set message status
bool ble_decode_config_set_check_is_unread(void);
bool ble_decode_config_set_check_data_is_stale(uint32_t time_ms);

#ifdef __cplusplus
}
#endif

#endif // BLE_PROTOCOL_H