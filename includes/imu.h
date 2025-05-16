#include "commondefines.h"
#include <nrfx_spi.h>
#include <zephyr/drivers/spi.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>

struct imuDataRaw{
	uint8_t OUTX_L_H_G[3];
	uint8_t OUTY_L_H_G[3];
	uint8_t OUTZ_L_H_G[3];
	uint8_t OUTX_L_H_A[3];
	uint8_t OUTY_L_H_A[3];
	uint8_t OUTZ_L_H_A[3];
};

void printIMUData();
int initIMU();
int readGyro();
int readAccel();
