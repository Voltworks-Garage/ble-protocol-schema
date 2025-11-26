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
#define MSG_ID_SENSOR_DATA        0x02
#define MSG_ID_MOTOR_STATUS       0x03
#define MSG_ID_CONFIG_ACK         0x11
#define MSG_ID_CONFIG_SET         0x10

// ============================================================================
// Server message encoding functions
// ============================================================================

// Encode and get heartbeat message
void ble_encode_heartbeat_begin(void);
void ble_encode_heartbeat_set_uptime_ms(uint32_t value);
void ble_encode_heartbeat_set_battery_mv(uint16_t value);
void ble_encode_heartbeat_set_status_flags(uint8_t value);
ble_frame_t ble_encode_heartbeat_get_frame(void);

// Encode and get server_message message
void ble_encode_server_message_begin(void);
void ble_encode_server_message_set_data(const char* value);
ble_frame_t ble_encode_server_message_get_frame(void);

// Encode and get sensor_data message
void ble_encode_sensor_data_begin(void);
void ble_encode_sensor_data_set_timestamp_ms(uint32_t value);
void ble_encode_sensor_data_set_temperature_c(int16_t value);
void ble_encode_sensor_data_set_humidity_pct(uint8_t value);
void ble_encode_sensor_data_set_pressure_pa(uint32_t value);
ble_frame_t ble_encode_sensor_data_get_frame(void);

// Encode and get motor_status message
void ble_encode_motor_status_begin(void);
void ble_encode_motor_status_set_rpm(uint16_t value);
void ble_encode_motor_status_set_current_ma(uint16_t value);
void ble_encode_motor_status_set_temp_c(int8_t value);
void ble_encode_motor_status_set_fault_code(uint8_t value);
ble_frame_t ble_encode_motor_status_get_frame(void);

// Encode and get config_ack message
void ble_encode_config_ack_begin(void);
void ble_encode_config_ack_set_param_id(uint8_t value);
void ble_encode_config_ack_set_result(uint8_t value);
ble_frame_t ble_encode_config_ack_get_frame(void);

// ============================================================================
// Client message decoding functions
// ============================================================================

// Generic frame decoding
bool ble_decode_frame(const uint8_t *frame, uint16_t frame_len);

// Get config_set message fields
uint8_t ble_decode_config_set_get_param_id(void);
uint32_t ble_decode_config_set_get_value(void);

#endif // BLE_PROTOCOL_H