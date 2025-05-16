#include "imu.h"
#include "commondefines.h"
#include <zephyr/drivers/spi.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(IMU_LOG); //Logging
struct spi_dt_spec spispec = SPI_DT_SPEC_GET(DT_NODELABEL(imu), SPIOP, 0);

struct imuDataRaw IMU_DATA_RAW;

int imu_read_reg(uint8_t reg, uint8_t* data, uint8_t size)
{
	uint8_t tx_buffer 					= reg | READ_BIT;
	struct spi_buf tx_spi_buf			= {.buf = (void *)&tx_buffer, .len = 1};
	struct spi_buf_set tx_spi_buf_set 	= {.buffers = &tx_spi_buf, .count = 1};
	struct spi_buf rx_spi_bufs 			= {.buf = data, .len = size};
	struct spi_buf_set rx_spi_buf_set	= {.buffers = &rx_spi_bufs, .count = 1};

	//transceieve reads and writes at the same time - so while it writes it alsos also reading data
	//in which case the first 8bits of data recieved will always be 0 so the var/struct we are using to
	//store the data has to be sized appropiatley ex it has to be sized up by 1 to accomadate for the 
	//first read to always be 0
	int error = spi_transceive_dt(&spispec, &tx_spi_buf_set, &rx_spi_buf_set);
	if (error < 0) {
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to read reg: %d, err: %d", __FILE__, __func__, __LINE__, reg, error);
		return error;
	}

	return 0;
}

int imu_write_reg(uint8_t reg, uint8_t value)
{
	uint8_t tx_buf[] 					= {(reg & 0x7F), value};	
	struct spi_buf 		tx_spi_buf 		= {.buf = tx_buf, .len = sizeof(tx_buf)};
	struct spi_buf_set 	tx_spi_buf_set	= {.buffers = &tx_spi_buf, .count = 1};

	int error = spi_write_dt(&spispec, &tx_spi_buf_set);
	if (error < 0) {
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to write reg: %d with value: %d, err: %d", __FILE__, __func__, __LINE__, reg, value, error);
		return error;
	}

	return 0;
}

int initIMU(){
    int error = 0;
	error = !spi_is_ready_dt(&spispec);
    if (error) {
        LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to initalize SPI bus or CS GPIO", __FILE__, __func__, __LINE__);
		return error;
	}
    //LOG_INF("Continuously read sensor samples, and display");
	//bit 0 MUST be set to 0 for correct operation
	//before reading values of gyroscope we have to turn it on 
	//current mode 10100010 - 1010 sets it to 6.66 kHz high performance
	//0100 sets it to a full scale range of +-500 degrees per second (angular rates the gyroscope can accuratley measure)
	error = imu_write_reg(CTRL2_G, 0xA4);
	if(error < 0){
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to write initalization register for Gyro", __FILE__, __func__, __LINE__);
		return error;
	}
    //bit 0 MUST be set to 0 for correct operation
	//before reading values of accelerometer we have to turn it on 
	//current mode 10101100 - 1010 sets it to 6.66 kHz high performance
	//1000 sets it to a +- 4g for measurements (max), bit1 set to 0 selects the first stage digital filtering
	error = imu_write_reg(CTRL1_XL, 0xA8);
	if(error < 0){
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to write initalization register for Accel", __FILE__, __func__, __LINE__);
		return error;
	}
    return error;
}

int readGyro(){
	int error = 0;
	imu_read_reg(OUTX_L_G, IMU_DATA_RAW.OUTX_L_H_G, READ_SIZE_MULTIPLE);
	if(error < 0){
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to write read register for Gyro", __FILE__, __func__, __LINE__);
		return error;
	}
	imu_read_reg(OUTY_L_G, IMU_DATA_RAW.OUTY_L_H_G, READ_SIZE_MULTIPLE);
	if(error < 0){
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to write read register for Gyro", __FILE__, __func__, __LINE__);
		return error;
	}
	imu_read_reg(OUTZ_L_G, IMU_DATA_RAW.OUTZ_L_H_G, READ_SIZE_MULTIPLE);
	if(error < 0){
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to write read register for Gyro", __FILE__, __func__, __LINE__);
		return error;
	}
	
    return error;
}

int readAccel(){
	int error = 0;
	imu_read_reg(OUTX_L_A, IMU_DATA_RAW.OUTX_L_H_A, READ_SIZE_MULTIPLE);
	if(error < 0){
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to read register for Accel", __FILE__, __func__, __LINE__);
		return error;
	}
	imu_read_reg(OUTY_L_A, IMU_DATA_RAW.OUTY_L_H_A, READ_SIZE_MULTIPLE);
	if(error < 0){
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to read register for Accel", __FILE__, __func__, __LINE__);
		return error;
	}
	imu_read_reg(OUTZ_L_A, IMU_DATA_RAW.OUTZ_L_H_A, READ_SIZE_MULTIPLE);
	if(error < 0){
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to read register for Accel", __FILE__, __func__, __LINE__);
		return error;
	}
    return error;
}

void printIMUData(){
	int16_t outx_g = (int16_t)(((uint16_t)IMU_DATA_RAW.OUTX_L_H_G[2]) << BIT_SHIFT | IMU_DATA_RAW.OUTX_L_H_G[1]);
	int16_t outy_g = (int16_t)(((uint16_t)IMU_DATA_RAW.OUTY_L_H_G[2]) << BIT_SHIFT | IMU_DATA_RAW.OUTY_L_H_G[1]);
	int16_t outz_g = (int16_t)(((uint16_t)IMU_DATA_RAW.OUTZ_L_H_G[2]) << BIT_SHIFT | IMU_DATA_RAW.OUTZ_L_H_G[1]);
	int16_t outx_a = (int16_t)(((uint16_t)IMU_DATA_RAW.OUTX_L_H_A[2]) << BIT_SHIFT | IMU_DATA_RAW.OUTX_L_H_A[1]);
	int16_t outy_a = (int16_t)(((uint16_t)IMU_DATA_RAW.OUTY_L_H_A[2]) << BIT_SHIFT | IMU_DATA_RAW.OUTY_L_H_A[1]);
	int16_t outz_a = (int16_t)(((uint16_t)IMU_DATA_RAW.OUTZ_L_H_A[2]) << BIT_SHIFT | IMU_DATA_RAW.OUTZ_L_H_A[1]);
    LOG_INF("INFO@ IMU DATA Hexadecimal Values - GYRO X: %hx GYRO Y: %hx GYRO Z: %hx ACCEL X: %hx ACCEL Y: %hx ACCEL Z: %hx", outx_g, outy_g, outz_g,
        outx_a, outy_a, outz_a);
}