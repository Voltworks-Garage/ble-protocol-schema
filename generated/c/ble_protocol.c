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
    uint32_t lvBattery_mv;
    uint8_t vehicle_state;
} __attribute__((packed)) heartbeat_t;

typedef struct {
    char data[128];
} __attribute__((packed)) server_message_t;

typedef struct {
    uint16_t cellVoltage1_mv;
    uint16_t cellVoltage2_mv;
    uint16_t cellVoltage3_mv;
    uint16_t cellVoltage4_mv;
    uint16_t cellVoltage5_mv;
    uint16_t cellVoltage6_mv;
    uint16_t cellVoltage7_mv;
    uint16_t cellVoltage8_mv;
    uint16_t cellVoltage9_mv;
    uint16_t cellVoltage10_mv;
    uint16_t cellVoltage11_mv;
    uint16_t cellVoltage12_mv;
    uint16_t cellVoltage13_mv;
    uint16_t cellVoltage14_mv;
    uint16_t cellVoltage15_mv;
    uint16_t cellVoltage16_mv;
    uint16_t cellVoltage17_mv;
    uint16_t cellVoltage18_mv;
    uint16_t cellVoltage19_mv;
    uint16_t cellVoltage20_mv;
    uint16_t cellVoltage21_mv;
    uint16_t cellVoltage22_mv;
    uint16_t cellVoltage23_mv;
    uint16_t cellVoltage24_mv;
    int16_t packTemp_c;
} __attribute__((packed)) bms_data_t;

typedef struct {
    uint8_t soc_percent;
    uint8_t soh_percent;
    uint32_t packVoltage_mv;
    int32_t packCurrent_ma;
    uint16_t remainingRange_km;
    uint16_t timeToEmpty_min;
    uint16_t timeToFull_min;
    uint16_t cellDelta_mv;
    uint16_t minCellVoltage_mv;
    uint16_t maxCellVoltage_mv;
    uint8_t minCellIndex;
    uint8_t maxCellIndex;
} __attribute__((packed)) bms_status_t;

typedef struct {
    int16_t motorTemp_c;
    int16_t controllerTemp_c;
    uint32_t motorRpm;
    uint32_t power_w;
    uint16_t torque_nm;
    uint8_t throttle_percent;
    uint8_t regenLevel_percent;
} __attribute__((packed)) motor_data_t;

typedef struct {
    uint16_t faultCodes;
    uint32_t warning_flags;
    uint8_t charging_status;
    uint8_t ride_mode;
    uint8_t frontBrake_engaged;
    uint8_t rearBrake_engaged;
} __attribute__((packed)) safety_status_t;

typedef struct {
    uint32_t odometer_km;
    uint32_t trip_km;
    uint16_t avgSpeed_kph;
    uint16_t topSpeed_kph;
    uint16_t energy_wh_per_km;
    uint16_t accel_0_60_ms;
} __attribute__((packed)) performance_data_t;

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

static uint8_t heartbeat_encode_buffer[13];
static uint16_t heartbeat_encode_len;
static uint8_t server_message_encode_buffer[132];
static uint16_t server_message_encode_len;
static uint8_t bms_data_encode_buffer[54];
static uint16_t bms_data_encode_len;
static uint8_t bms_status_encode_buffer[28];
static uint16_t bms_status_encode_len;
static uint8_t motor_data_encode_buffer[20];
static uint16_t motor_data_encode_len;
static uint8_t safety_status_encode_buffer[14];
static uint16_t safety_status_encode_len;
static uint8_t performance_data_encode_buffer[20];
static uint16_t performance_data_encode_len;

static uint8_t decode_payload_buffer[5];
static uint8_t decode_expected_size;
static uint8_t decode_bytes_received;
static uint8_t decode_msg_id;
static bool decode_valid;

static config_set_t config_set_decoded;
static bool config_set_available;
static uint32_t config_set_timestamp_ms;
static bool config_set_unread;

// ============================================================================
// Protocol layer helper functions
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

// Set lvBattery_mv in heartbeat message
void ble_encode_heartbeat_set_lvBattery_mv(uint32_t value) {
    heartbeat_t *msg = (heartbeat_t*)&heartbeat_encode_buffer[3];
    msg->lvBattery_mv = value;
}

// Set vehicle_state in heartbeat message
void ble_encode_heartbeat_set_vehicle_state(uint8_t value) {
    heartbeat_t *msg = (heartbeat_t*)&heartbeat_encode_buffer[3];
    msg->vehicle_state = value;
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

// Begin encoding server_message message
void ble_encode_server_message_begin(void) {
    const uint16_t payload_size = sizeof(server_message_t);
    
    // Frame: [0xAA][Length][MsgID][Payload][Checksum]
    server_message_encode_buffer[0] = BLE_SYNC_FIRST;
    server_message_encode_buffer[1] = payload_size;
    server_message_encode_buffer[2] = 0x04;
    
    // Zero out payload area
    memset(&server_message_encode_buffer[3], 0, payload_size);
    
    // Frame length includes header, payload, and checksum
    server_message_encode_len = 3 + payload_size + 1;
}

// Set data in server_message message
void ble_encode_server_message_set_data(const uint8_t* value) {
    server_message_t *msg = (server_message_t*)&server_message_encode_buffer[3];
    if (value != NULL) {
        strncpy(msg->data, (const char*)value, sizeof(msg->data) - 1);
        msg->data[sizeof(msg->data) - 1] = '\0';
    } else {
        msg->data[0] = '\0';
    }
}

// Get encoded server_message frame
ble_frame_t ble_encode_server_message_get_frame(void) {
    // Calculate checksum before returning frame
    uint8_t payload_size = server_message_encode_buffer[1];
    server_message_encode_buffer[3 + payload_size] = ble_calculate_checksum(&server_message_encode_buffer[3], payload_size);
    
    ble_frame_t frame = {
        .data = server_message_encode_buffer,
        .length = server_message_encode_len
    };
    return frame;
}

// Begin encoding bms_data message
void ble_encode_bms_data_begin(void) {
    const uint16_t payload_size = sizeof(bms_data_t);
    
    // Frame: [0xAA][Length][MsgID][Payload][Checksum]
    bms_data_encode_buffer[0] = BLE_SYNC_FIRST;
    bms_data_encode_buffer[1] = payload_size;
    bms_data_encode_buffer[2] = 0x02;
    
    // Zero out payload area
    memset(&bms_data_encode_buffer[3], 0, payload_size);
    
    // Frame length includes header, payload, and checksum
    bms_data_encode_len = 3 + payload_size + 1;
}

// Set cellVoltage1_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage1_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage1_mv = value;
}

// Set cellVoltage2_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage2_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage2_mv = value;
}

// Set cellVoltage3_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage3_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage3_mv = value;
}

// Set cellVoltage4_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage4_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage4_mv = value;
}

// Set cellVoltage5_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage5_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage5_mv = value;
}

// Set cellVoltage6_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage6_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage6_mv = value;
}

// Set cellVoltage7_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage7_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage7_mv = value;
}

// Set cellVoltage8_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage8_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage8_mv = value;
}

// Set cellVoltage9_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage9_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage9_mv = value;
}

// Set cellVoltage10_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage10_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage10_mv = value;
}

// Set cellVoltage11_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage11_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage11_mv = value;
}

// Set cellVoltage12_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage12_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage12_mv = value;
}

// Set cellVoltage13_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage13_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage13_mv = value;
}

// Set cellVoltage14_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage14_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage14_mv = value;
}

// Set cellVoltage15_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage15_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage15_mv = value;
}

// Set cellVoltage16_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage16_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage16_mv = value;
}

// Set cellVoltage17_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage17_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage17_mv = value;
}

// Set cellVoltage18_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage18_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage18_mv = value;
}

// Set cellVoltage19_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage19_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage19_mv = value;
}

// Set cellVoltage20_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage20_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage20_mv = value;
}

// Set cellVoltage21_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage21_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage21_mv = value;
}

// Set cellVoltage22_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage22_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage22_mv = value;
}

// Set cellVoltage23_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage23_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage23_mv = value;
}

// Set cellVoltage24_mv in bms_data message
void ble_encode_bms_data_set_cellVoltage24_mv(uint16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->cellVoltage24_mv = value;
}

// Set packTemp_c in bms_data message
void ble_encode_bms_data_set_packTemp_c(int16_t value) {
    bms_data_t *msg = (bms_data_t*)&bms_data_encode_buffer[3];
    msg->packTemp_c = value;
}

// Get encoded bms_data frame
ble_frame_t ble_encode_bms_data_get_frame(void) {
    // Calculate checksum before returning frame
    uint8_t payload_size = bms_data_encode_buffer[1];
    bms_data_encode_buffer[3 + payload_size] = ble_calculate_checksum(&bms_data_encode_buffer[3], payload_size);
    
    ble_frame_t frame = {
        .data = bms_data_encode_buffer,
        .length = bms_data_encode_len
    };
    return frame;
}

// Begin encoding bms_status message
void ble_encode_bms_status_begin(void) {
    const uint16_t payload_size = sizeof(bms_status_t);
    
    // Frame: [0xAA][Length][MsgID][Payload][Checksum]
    bms_status_encode_buffer[0] = BLE_SYNC_FIRST;
    bms_status_encode_buffer[1] = payload_size;
    bms_status_encode_buffer[2] = 0x03;
    
    // Zero out payload area
    memset(&bms_status_encode_buffer[3], 0, payload_size);
    
    // Frame length includes header, payload, and checksum
    bms_status_encode_len = 3 + payload_size + 1;
}

// Set soc_percent in bms_status message
void ble_encode_bms_status_set_soc_percent(uint8_t value) {
    bms_status_t *msg = (bms_status_t*)&bms_status_encode_buffer[3];
    msg->soc_percent = value;
}

// Set soh_percent in bms_status message
void ble_encode_bms_status_set_soh_percent(uint8_t value) {
    bms_status_t *msg = (bms_status_t*)&bms_status_encode_buffer[3];
    msg->soh_percent = value;
}

// Set packVoltage_mv in bms_status message
void ble_encode_bms_status_set_packVoltage_mv(uint32_t value) {
    bms_status_t *msg = (bms_status_t*)&bms_status_encode_buffer[3];
    msg->packVoltage_mv = value;
}

// Set packCurrent_ma in bms_status message
void ble_encode_bms_status_set_packCurrent_ma(int32_t value) {
    bms_status_t *msg = (bms_status_t*)&bms_status_encode_buffer[3];
    msg->packCurrent_ma = value;
}

// Set remainingRange_km in bms_status message
void ble_encode_bms_status_set_remainingRange_km(uint16_t value) {
    bms_status_t *msg = (bms_status_t*)&bms_status_encode_buffer[3];
    msg->remainingRange_km = value;
}

// Set timeToEmpty_min in bms_status message
void ble_encode_bms_status_set_timeToEmpty_min(uint16_t value) {
    bms_status_t *msg = (bms_status_t*)&bms_status_encode_buffer[3];
    msg->timeToEmpty_min = value;
}

// Set timeToFull_min in bms_status message
void ble_encode_bms_status_set_timeToFull_min(uint16_t value) {
    bms_status_t *msg = (bms_status_t*)&bms_status_encode_buffer[3];
    msg->timeToFull_min = value;
}

// Set cellDelta_mv in bms_status message
void ble_encode_bms_status_set_cellDelta_mv(uint16_t value) {
    bms_status_t *msg = (bms_status_t*)&bms_status_encode_buffer[3];
    msg->cellDelta_mv = value;
}

// Set minCellVoltage_mv in bms_status message
void ble_encode_bms_status_set_minCellVoltage_mv(uint16_t value) {
    bms_status_t *msg = (bms_status_t*)&bms_status_encode_buffer[3];
    msg->minCellVoltage_mv = value;
}

// Set maxCellVoltage_mv in bms_status message
void ble_encode_bms_status_set_maxCellVoltage_mv(uint16_t value) {
    bms_status_t *msg = (bms_status_t*)&bms_status_encode_buffer[3];
    msg->maxCellVoltage_mv = value;
}

// Set minCellIndex in bms_status message
void ble_encode_bms_status_set_minCellIndex(uint8_t value) {
    bms_status_t *msg = (bms_status_t*)&bms_status_encode_buffer[3];
    msg->minCellIndex = value;
}

// Set maxCellIndex in bms_status message
void ble_encode_bms_status_set_maxCellIndex(uint8_t value) {
    bms_status_t *msg = (bms_status_t*)&bms_status_encode_buffer[3];
    msg->maxCellIndex = value;
}

// Get encoded bms_status frame
ble_frame_t ble_encode_bms_status_get_frame(void) {
    // Calculate checksum before returning frame
    uint8_t payload_size = bms_status_encode_buffer[1];
    bms_status_encode_buffer[3 + payload_size] = ble_calculate_checksum(&bms_status_encode_buffer[3], payload_size);
    
    ble_frame_t frame = {
        .data = bms_status_encode_buffer,
        .length = bms_status_encode_len
    };
    return frame;
}

// Begin encoding motor_data message
void ble_encode_motor_data_begin(void) {
    const uint16_t payload_size = sizeof(motor_data_t);
    
    // Frame: [0xAA][Length][MsgID][Payload][Checksum]
    motor_data_encode_buffer[0] = BLE_SYNC_FIRST;
    motor_data_encode_buffer[1] = payload_size;
    motor_data_encode_buffer[2] = 0x05;
    
    // Zero out payload area
    memset(&motor_data_encode_buffer[3], 0, payload_size);
    
    // Frame length includes header, payload, and checksum
    motor_data_encode_len = 3 + payload_size + 1;
}

// Set motorTemp_c in motor_data message
void ble_encode_motor_data_set_motorTemp_c(int16_t value) {
    motor_data_t *msg = (motor_data_t*)&motor_data_encode_buffer[3];
    msg->motorTemp_c = value;
}

// Set controllerTemp_c in motor_data message
void ble_encode_motor_data_set_controllerTemp_c(int16_t value) {
    motor_data_t *msg = (motor_data_t*)&motor_data_encode_buffer[3];
    msg->controllerTemp_c = value;
}

// Set motorRpm in motor_data message
void ble_encode_motor_data_set_motorRpm(uint32_t value) {
    motor_data_t *msg = (motor_data_t*)&motor_data_encode_buffer[3];
    msg->motorRpm = value;
}

// Set power_w in motor_data message
void ble_encode_motor_data_set_power_w(uint32_t value) {
    motor_data_t *msg = (motor_data_t*)&motor_data_encode_buffer[3];
    msg->power_w = value;
}

// Set torque_nm in motor_data message
void ble_encode_motor_data_set_torque_nm(uint16_t value) {
    motor_data_t *msg = (motor_data_t*)&motor_data_encode_buffer[3];
    msg->torque_nm = value;
}

// Set throttle_percent in motor_data message
void ble_encode_motor_data_set_throttle_percent(uint8_t value) {
    motor_data_t *msg = (motor_data_t*)&motor_data_encode_buffer[3];
    msg->throttle_percent = value;
}

// Set regenLevel_percent in motor_data message
void ble_encode_motor_data_set_regenLevel_percent(uint8_t value) {
    motor_data_t *msg = (motor_data_t*)&motor_data_encode_buffer[3];
    msg->regenLevel_percent = value;
}

// Get encoded motor_data frame
ble_frame_t ble_encode_motor_data_get_frame(void) {
    // Calculate checksum before returning frame
    uint8_t payload_size = motor_data_encode_buffer[1];
    motor_data_encode_buffer[3 + payload_size] = ble_calculate_checksum(&motor_data_encode_buffer[3], payload_size);
    
    ble_frame_t frame = {
        .data = motor_data_encode_buffer,
        .length = motor_data_encode_len
    };
    return frame;
}

// Begin encoding safety_status message
void ble_encode_safety_status_begin(void) {
    const uint16_t payload_size = sizeof(safety_status_t);
    
    // Frame: [0xAA][Length][MsgID][Payload][Checksum]
    safety_status_encode_buffer[0] = BLE_SYNC_FIRST;
    safety_status_encode_buffer[1] = payload_size;
    safety_status_encode_buffer[2] = 0x06;
    
    // Zero out payload area
    memset(&safety_status_encode_buffer[3], 0, payload_size);
    
    // Frame length includes header, payload, and checksum
    safety_status_encode_len = 3 + payload_size + 1;
}

// Set faultCodes in safety_status message
void ble_encode_safety_status_set_faultCodes(uint16_t value) {
    safety_status_t *msg = (safety_status_t*)&safety_status_encode_buffer[3];
    msg->faultCodes = value;
}

// Set warning_flags in safety_status message
void ble_encode_safety_status_set_warning_flags(uint32_t value) {
    safety_status_t *msg = (safety_status_t*)&safety_status_encode_buffer[3];
    msg->warning_flags = value;
}

// Set charging_status in safety_status message
void ble_encode_safety_status_set_charging_status(uint8_t value) {
    safety_status_t *msg = (safety_status_t*)&safety_status_encode_buffer[3];
    msg->charging_status = value;
}

// Set ride_mode in safety_status message
void ble_encode_safety_status_set_ride_mode(uint8_t value) {
    safety_status_t *msg = (safety_status_t*)&safety_status_encode_buffer[3];
    msg->ride_mode = value;
}

// Set frontBrake_engaged in safety_status message
void ble_encode_safety_status_set_frontBrake_engaged(uint8_t value) {
    safety_status_t *msg = (safety_status_t*)&safety_status_encode_buffer[3];
    msg->frontBrake_engaged = value;
}

// Set rearBrake_engaged in safety_status message
void ble_encode_safety_status_set_rearBrake_engaged(uint8_t value) {
    safety_status_t *msg = (safety_status_t*)&safety_status_encode_buffer[3];
    msg->rearBrake_engaged = value;
}

// Get encoded safety_status frame
ble_frame_t ble_encode_safety_status_get_frame(void) {
    // Calculate checksum before returning frame
    uint8_t payload_size = safety_status_encode_buffer[1];
    safety_status_encode_buffer[3 + payload_size] = ble_calculate_checksum(&safety_status_encode_buffer[3], payload_size);
    
    ble_frame_t frame = {
        .data = safety_status_encode_buffer,
        .length = safety_status_encode_len
    };
    return frame;
}

// Begin encoding performance_data message
void ble_encode_performance_data_begin(void) {
    const uint16_t payload_size = sizeof(performance_data_t);
    
    // Frame: [0xAA][Length][MsgID][Payload][Checksum]
    performance_data_encode_buffer[0] = BLE_SYNC_FIRST;
    performance_data_encode_buffer[1] = payload_size;
    performance_data_encode_buffer[2] = 0x07;
    
    // Zero out payload area
    memset(&performance_data_encode_buffer[3], 0, payload_size);
    
    // Frame length includes header, payload, and checksum
    performance_data_encode_len = 3 + payload_size + 1;
}

// Set odometer_km in performance_data message
void ble_encode_performance_data_set_odometer_km(uint32_t value) {
    performance_data_t *msg = (performance_data_t*)&performance_data_encode_buffer[3];
    msg->odometer_km = value;
}

// Set trip_km in performance_data message
void ble_encode_performance_data_set_trip_km(uint32_t value) {
    performance_data_t *msg = (performance_data_t*)&performance_data_encode_buffer[3];
    msg->trip_km = value;
}

// Set avgSpeed_kph in performance_data message
void ble_encode_performance_data_set_avgSpeed_kph(uint16_t value) {
    performance_data_t *msg = (performance_data_t*)&performance_data_encode_buffer[3];
    msg->avgSpeed_kph = value;
}

// Set topSpeed_kph in performance_data message
void ble_encode_performance_data_set_topSpeed_kph(uint16_t value) {
    performance_data_t *msg = (performance_data_t*)&performance_data_encode_buffer[3];
    msg->topSpeed_kph = value;
}

// Set energy_wh_per_km in performance_data message
void ble_encode_performance_data_set_energy_wh_per_km(uint16_t value) {
    performance_data_t *msg = (performance_data_t*)&performance_data_encode_buffer[3];
    msg->energy_wh_per_km = value;
}

// Set accel_0_60_ms in performance_data message
void ble_encode_performance_data_set_accel_0_60_ms(uint16_t value) {
    performance_data_t *msg = (performance_data_t*)&performance_data_encode_buffer[3];
    msg->accel_0_60_ms = value;
}

// Get encoded performance_data frame
ble_frame_t ble_encode_performance_data_get_frame(void) {
    // Calculate checksum before returning frame
    uint8_t payload_size = performance_data_encode_buffer[1];
    performance_data_encode_buffer[3 + payload_size] = ble_calculate_checksum(&performance_data_encode_buffer[3], payload_size);
    
    ble_frame_t frame = {
        .data = performance_data_encode_buffer,
        .length = performance_data_encode_len
    };
    return frame;
}

// ============================================================================
// Client message decoding functions (messages server receives)
// ============================================================================

// Copy decoded payload to appropriate message buffer
static void ble_decode_store_message(uint32_t timestamp_ms) {
    switch (decode_msg_id) {
        case 0x10:
            memcpy(&config_set_decoded, decode_payload_buffer, sizeof(config_set_t));
            config_set_available = true;
            config_set_timestamp_ms = timestamp_ms;
            config_set_unread = true;
            break;
        default:
            break;
    }
}

// Decode client message frame (supports multi-frame reassembly)
// Returns true when complete message is received and validated
// time_ms: Current time in milliseconds for timestamping received messages
bool ble_decode_frame(const uint8_t *frame, uint16_t frame_len, uint32_t time_ms) {
    if (frame == NULL || frame_len < 1) return false;
    
    // Check if this is a first frame
    if (frame[0] == BLE_SYNC_FIRST) {
        // Reset state for new message
        decode_valid = false;
        decode_bytes_received = 0;
        
        // Verify minimum frame size for first frame
        if (frame_len < 4) return false;
        
        // Extract header
        decode_expected_size = frame[1];
        decode_msg_id = frame[2];
        
        // Calculate payload bytes in this frame
        uint16_t header_size = 3;
        uint16_t payload_in_frame = frame_len - header_size;
        
        // Check if this frame has checksum (complete message)
        bool has_checksum = (payload_in_frame == decode_expected_size + 1);
        
        if (has_checksum) {
            // Single-frame message - verify checksum
            uint8_t checksum = frame[3 + decode_expected_size];
            uint8_t calc_checksum = ble_calculate_checksum(&frame[3], decode_expected_size);
            if (checksum != calc_checksum) return false;
            
            // Copy payload to buffer
            memcpy(decode_payload_buffer, &frame[3], decode_expected_size);
            decode_bytes_received = decode_expected_size;
            decode_valid = true;
            
            // Store in per-message buffer
            ble_decode_store_message(time_ms);
            return true;
        } else {
            // Multi-frame message - copy partial payload
            if (payload_in_frame > decode_expected_size) return false;
            memcpy(decode_payload_buffer, &frame[3], payload_in_frame);
            decode_bytes_received = payload_in_frame;
            return false; // Need more frames
        }
    } else {
        // Continuation frame (no sync byte, just payload)
        if (decode_bytes_received == 0) return false; // No first frame received
        
        uint16_t remaining = decode_expected_size - decode_bytes_received;
        bool has_checksum = (frame_len == remaining + 1);
        
        if (has_checksum) {
            // Final frame - verify checksum
            memcpy(&decode_payload_buffer[decode_bytes_received], frame, remaining);
            decode_bytes_received += remaining;
            
            uint8_t checksum = frame[remaining];
            uint8_t calc_checksum = ble_calculate_checksum(decode_payload_buffer, decode_expected_size);
            if (checksum != calc_checksum) {
                decode_bytes_received = 0; // Reset on checksum failure
                return false;
            }
            
            decode_valid = true;
            
            // Store in per-message buffer
            ble_decode_store_message(time_ms);
            return true;
        } else {
            // Continuation frame - copy payload
            if (frame_len > remaining) return false;
            memcpy(&decode_payload_buffer[decode_bytes_received], frame, frame_len);
            decode_bytes_received += frame_len;
            return false; // Need more frames
        }
    }
}

// Get param_id from config_set message
uint8_t ble_decode_config_set_get_param_id(void) {
    if (!config_set_available) return 0;
    config_set_unread = false;
    return config_set_decoded.param_id;
}

// Get value from config_set message
uint32_t ble_decode_config_set_get_value(void) {
    if (!config_set_available) return 0;
    config_set_unread = false;
    return config_set_decoded.value;
}

// ============================================================================
// Message status functions
// ============================================================================

// Check if config_set message is unread
bool ble_decode_config_set_check_is_unread(void) {
    return config_set_available && config_set_unread;
}

// Check if config_set data is stale (max age: 1000ms)
bool ble_decode_config_set_check_data_is_stale(uint32_t time_ms) {
    if (!config_set_available) return true;
    uint32_t age_ms = time_ms - config_set_timestamp_ms;
    return age_ms > 1000;
}
