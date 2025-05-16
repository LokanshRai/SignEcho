#include "commondefines.h"
#include "packetBuilder.h"
#include "imu.h"
#include "ble.h"
#include <zephyr/logging/log.h>
#include "emg.h"

LOG_MODULE_REGISTER(PKTB_LOG); //Logging

extern struct imuDataRaw IMU_DATA_RAW;
static int8_t payload[payloadSizeInBytes] = {0};


int updatePayloadWithGyroData(int index){
    int error = 0;
    error = readGyro();
    if(error < 0){
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to read Gyro Values: err: %d", __FILE__, __func__, __LINE__, error);
		return error;
    }
    payload[0+(12*index)] = IMU_DATA_RAW.OUTX_L_H_G[2];
    payload[1+(12*index)] = IMU_DATA_RAW.OUTX_L_H_G[1];
    payload[2+(12*index)] = IMU_DATA_RAW.OUTY_L_H_G[2];
    payload[3+(12*index)] = IMU_DATA_RAW.OUTY_L_H_G[1];
    payload[4+(12*index)] = IMU_DATA_RAW.OUTZ_L_H_G[2];
    payload[5+(12*index)] = IMU_DATA_RAW.OUTZ_L_H_G[1];
    return error;
}

int updatePayloadWithAccelData(int index){
    int error = 0;
    error = readAccel();
    if(error < 0){
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to read Accel Values: err: %d", __FILE__, __func__, __LINE__, error);
		return error;
    }
    payload[6+(12*index)]  = IMU_DATA_RAW.OUTX_L_H_A[2];
    payload[7+(12*index)]  = IMU_DATA_RAW.OUTX_L_H_A[1];
    payload[8+(12*index)]  = IMU_DATA_RAW.OUTY_L_H_A[2];
    payload[9+(12*index)]  = IMU_DATA_RAW.OUTY_L_H_A[1];
    payload[10+(12*index)] = IMU_DATA_RAW.OUTZ_L_H_A[2];
    payload[11+(12*index)] = IMU_DATA_RAW.OUTZ_L_H_A[1];
    return error;
}

void sendPacket(){
    send_sensor_notification(payload, sizeof(payload));
}

int updatePayloadWithEMGData(int index){
    int error = 0;
    readEMG();

    int payloadEMGDataStart8 = 0;
    for(int i = 0; i < ARRAY_SIZE(emgData); i++){
        int8_t upper8Bits = emgData[i] >> BIT_SHIFT;
        int8_t lower8Bits = emgData[i];
        payload[payloadEMGDataStart8+(12*index)] = upper8Bits;
        payload[payloadEMGDataStart8+1+(12*index)] = lower8Bits;
        payloadEMGDataStart8+=2; 
    }
    return error;
}

void printPayload(){
    LOG_INF("INFO@ Printing Payload 8 Bytes");
    for(int i = 0; i < ARRAY_SIZE(payload); i++){
        LOG_INF("INDEX: %d DECIMAL VALUE: %hhx", i, payload[i]);
    }
}