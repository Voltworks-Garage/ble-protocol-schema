/**
 * BLE Telemetry Protocol v1.0.0
 * Auto-generated from schema.json
 * DO NOT EDIT MANUALLY
 */

#include "ble_protocol.h"
#include <string.h>

// Protocol constants
#define BLE_SYNC_FIRST 0xAA

// ============================================================================
// Private message structures - Server messages
// ============================================================================

typedef struct {
    uint32_t uptime_ms;
    uint16_t battery_mv;
    uint8_t status_flags;
} __attribute__((packed)) heartbeat_t;

typedef struct {
    uint32_t timestamp_ms;
    int16_t temperature_c;
    uint8_t humidity_pct;
    uint32_t pressure_pa;
} __attribute__((packed)) sensor_data_t;

typedef struct {
    uint16_t rpm;
    uint16_t current_ma;
    int8_t temp_c;
    uint8_t fault_code;
} __attribute__((packed)) motor_status_t;

typedef struct {
    uint8_t param_id;
    uint8_t result;
} __attribute__((packed)) config_ack_t;

// ============================================================================
// Private message structures - Client messages
// ============================================================================

typedef struct {
    uint8_t param_id;
    uint32_t value;
} __attribute__((packed)) config_set_t;

// ============================================================================
// Private frame buffers
// ============================================================================

static uint8_t heartbeat_encode_buffer[11];
static uint16_t heartbeat_encode_len;
static uint8_t sensor_data_encode_buffer[15];
static uint16_t sensor_data_encode_len;
static uint8_t motor_status_encode_buffer[10];
static uint16_t motor_status_encode_len;
static uint8_t config_ack_encode_buffer[6];
static uint16_t config_ack_encode_len;

static uint8_t config_set_decode_buffer[9];
static bool config_set_decode_valid;

// ============================================================================
// Private helper functions
// ============================================================================

// Calculate sum-mod-256 checksum
static uint8_t ble_calculate_checksum(const uint8_t *data, uint16_t length) {
    uint32_t sum = 0;
    for (uint16_t i = 0; i < length; i++) {
        sum += data[i];
    }
    return (uint8_t)(sum & 0xFF);
}

// ============================================================================
// Server message encoding functions (messages server sends)
// ============================================================================

// Begin encoding heartbeat message
void ble_encode_heartbeat_begin(void) {
    const uint16_t payload_size = sizeof(heartbeat_t);
    
    // Frame: [0xAA][Length][MsgID][Payload][Checksum]
    heartbeat_encode_buffer[0] = BLE_SYNC_FIRST;
    heartbeat_encode_buffer[1] = payload_size;
    heartbeat_encode_buffer[2] = 0x01;
    
    // Zero out payload area
    memset(&heartbeat_encode_buffer[3], 0, payload_size);
    
    // Frame length includes header, payload, and checksum
    heartbeat_encode_len = 3 + payload_size + 1;
}

// Set uptime_ms in heartbeat message
void ble_encode_heartbeat_set_uptime_ms(uint32_t value) {
    heartbeat_t *msg = (heartbeat_t*)&heartbeat_encode_buffer[3];
    msg->uptime_ms = value;
}

// Set battery_mv in heartbeat message
void ble_encode_heartbeat_set_battery_mv(uint16_t value) {
    heartbeat_t *msg = (heartbeat_t*)&heartbeat_encode_buffer[3];
    msg->battery_mv = value;
}

// Set status_flags in heartbeat message
void ble_encode_heartbeat_set_status_flags(uint8_t value) {
    heartbeat_t *msg = (heartbeat_t*)&heartbeat_encode_buffer[3];
    msg->status_flags = value;
}

// Get encoded heartbeat frame
ble_frame_t ble_encode_heartbeat_get_frame(void) {
    // Calculate checksum before returning frame
    uint8_t payload_size = heartbeat_encode_buffer[1];
    heartbeat_encode_buffer[3 + payload_size] = ble_calculate_checksum(&heartbeat_encode_buffer[3], payload_size);
    
    ble_frame_t frame = {
        .data = heartbeat_encode_buffer,
        .length = heartbeat_encode_len
    };
    return frame;
}

// Begin encoding sensor_data message
void ble_encode_sensor_data_begin(void) {
    const uint16_t payload_size = sizeof(sensor_data_t);
    
    // Frame: [0xAA][Length][MsgID][Payload][Checksum]
    sensor_data_encode_buffer[0] = BLE_SYNC_FIRST;
    sensor_data_encode_buffer[1] = payload_size;
    sensor_data_encode_buffer[2] = 0x02;
    
    // Zero out payload area
    memset(&sensor_data_encode_buffer[3], 0, payload_size);
    
    // Frame length includes header, payload, and checksum
    sensor_data_encode_len = 3 + payload_size + 1;
}

// Set timestamp_ms in sensor_data message
void ble_encode_sensor_data_set_timestamp_ms(uint32_t value) {
    sensor_data_t *msg = (sensor_data_t*)&sensor_data_encode_buffer[3];
    msg->timestamp_ms = value;
}

// Set temperature_c in sensor_data message
void ble_encode_sensor_data_set_temperature_c(int16_t value) {
    sensor_data_t *msg = (sensor_data_t*)&sensor_data_encode_buffer[3];
    msg->temperature_c = value;
}

// Set humidity_pct in sensor_data message
void ble_encode_sensor_data_set_humidity_pct(uint8_t value) {
    sensor_data_t *msg = (sensor_data_t*)&sensor_data_encode_buffer[3];
    msg->humidity_pct = value;
}

// Set pressure_pa in sensor_data message
void ble_encode_sensor_data_set_pressure_pa(uint32_t value) {
    sensor_data_t *msg = (sensor_data_t*)&sensor_data_encode_buffer[3];
    msg->pressure_pa = value;
}

// Get encoded sensor_data frame
ble_frame_t ble_encode_sensor_data_get_frame(void) {
    // Calculate checksum before returning frame
    uint8_t payload_size = sensor_data_encode_buffer[1];
    sensor_data_encode_buffer[3 + payload_size] = ble_calculate_checksum(&sensor_data_encode_buffer[3], payload_size);
    
    ble_frame_t frame = {
        .data = sensor_data_encode_buffer,
        .length = sensor_data_encode_len
    };
    return frame;
}

// Begin encoding motor_status message
void ble_encode_motor_status_begin(void) {
    const uint16_t payload_size = sizeof(motor_status_t);
    
    // Frame: [0xAA][Length][MsgID][Payload][Checksum]
    motor_status_encode_buffer[0] = BLE_SYNC_FIRST;
    motor_status_encode_buffer[1] = payload_size;
    motor_status_encode_buffer[2] = 0x03;
    
    // Zero out payload area
    memset(&motor_status_encode_buffer[3], 0, payload_size);
    
    // Frame length includes header, payload, and checksum
    motor_status_encode_len = 3 + payload_size + 1;
}

// Set rpm in motor_status message
void ble_encode_motor_status_set_rpm(uint16_t value) {
    motor_status_t *msg = (motor_status_t*)&motor_status_encode_buffer[3];
    msg->rpm = value;
}

// Set current_ma in motor_status message
void ble_encode_motor_status_set_current_ma(uint16_t value) {
    motor_status_t *msg = (motor_status_t*)&motor_status_encode_buffer[3];
    msg->current_ma = value;
}

// Set temp_c in motor_status message
void ble_encode_motor_status_set_temp_c(int8_t value) {
    motor_status_t *msg = (motor_status_t*)&motor_status_encode_buffer[3];
    msg->temp_c = value;
}

// Set fault_code in motor_status message
void ble_encode_motor_status_set_fault_code(uint8_t value) {
    motor_status_t *msg = (motor_status_t*)&motor_status_encode_buffer[3];
    msg->fault_code = value;
}

// Get encoded motor_status frame
ble_frame_t ble_encode_motor_status_get_frame(void) {
    // Calculate checksum before returning frame
    uint8_t payload_size = motor_status_encode_buffer[1];
    motor_status_encode_buffer[3 + payload_size] = ble_calculate_checksum(&motor_status_encode_buffer[3], payload_size);
    
    ble_frame_t frame = {
        .data = motor_status_encode_buffer,
        .length = motor_status_encode_len
    };
    return frame;
}

// Begin encoding config_ack message
void ble_encode_config_ack_begin(void) {
    const uint16_t payload_size = sizeof(config_ack_t);
    
    // Frame: [0xAA][Length][MsgID][Payload][Checksum]
    config_ack_encode_buffer[0] = BLE_SYNC_FIRST;
    config_ack_encode_buffer[1] = payload_size;
    config_ack_encode_buffer[2] = 0x11;
    
    // Zero out payload area
    memset(&config_ack_encode_buffer[3], 0, payload_size);
    
    // Frame length includes header, payload, and checksum
    config_ack_encode_len = 3 + payload_size + 1;
}

// Set param_id in config_ack message
void ble_encode_config_ack_set_param_id(uint8_t value) {
    config_ack_t *msg = (config_ack_t*)&config_ack_encode_buffer[3];
    msg->param_id = value;
}

// Set result in config_ack message
void ble_encode_config_ack_set_result(uint8_t value) {
    config_ack_t *msg = (config_ack_t*)&config_ack_encode_buffer[3];
    msg->result = value;
}

// Get encoded config_ack frame
ble_frame_t ble_encode_config_ack_get_frame(void) {
    // Calculate checksum before returning frame
    uint8_t payload_size = config_ack_encode_buffer[1];
    config_ack_encode_buffer[3 + payload_size] = ble_calculate_checksum(&config_ack_encode_buffer[3], payload_size);
    
    ble_frame_t frame = {
        .data = config_ack_encode_buffer,
        .length = config_ack_encode_len
    };
    return frame;
}

// ============================================================================
// Client message decoding functions (messages server receives)
// ============================================================================

// Set received config_set frame for decoding
bool ble_decode_config_set_set_frame(const uint8_t *frame, uint16_t frame_len) {
    config_set_decode_valid = false;
    
    if (frame == NULL || frame_len < 5) return false;
    
    // Verify first frame with correct message ID
    if (frame[0] != BLE_SYNC_FIRST) return false;
    if (frame[2] != 0x10) return false;
    
    // Verify frame length
    uint8_t payload_size = frame[1];
    if (payload_size != 5) return false;
    if (frame_len < 3 + payload_size + 1) return false;
    
    // Verify checksum (at end of frame)
    uint8_t checksum = frame[3 + payload_size];
    uint8_t calc_checksum = ble_calculate_checksum(&frame[3], payload_size);
    if (checksum != calc_checksum) return false;
    
    // Copy to internal buffer
    memcpy(config_set_decode_buffer, frame, frame_len);
    config_set_decode_valid = true;
    return true;
}

// Get param_id from config_set message
uint8_t ble_decode_config_set_get_param_id(void) {
    if (!config_set_decode_valid) return 0;
    
    const config_set_t *msg = (const config_set_t*)&config_set_decode_buffer[3];
    return msg->param_id;
}

// Get value from config_set message
uint32_t ble_decode_config_set_get_value(void) {
    if (!config_set_decode_valid) return 0;
    
    const config_set_t *msg = (const config_set_t*)&config_set_decode_buffer[3];
    return msg->value;
}
