#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/drivers/gpio.h>
#include "imu.h"
#include "commondefines.h"
#include "emg.h"
#include "ble.h"
#include "packetBuilder.h"

LOG_MODULE_REGISTER(MAIN_LOG); //Logging

const struct gpio_dt_spec ledSpec0 = GPIO_DT_SPEC_GET(DT_NODELABEL(led0), gpios);
const struct gpio_dt_spec ledSpec1 = GPIO_DT_SPEC_GET(DT_NODELABEL(led1), gpios);
const struct gpio_dt_spec ledSpec2 = GPIO_DT_SPEC_GET(DT_NODELABEL(led2), gpios);

int main(void){
    int error = 0; 
    error = gpio_is_ready_dt(&ledSpec0) || gpio_is_ready_dt(&ledSpec1) || gpio_is_ready_dt(&ledSpec2);
	if(!error){
		LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to initalize GPIO - LED0", __FILE__, __func__, __LINE__);
		return error;
	}
    gpio_pin_configure_dt(&ledSpec0, GPIO_OUTPUT_INACTIVE);
    gpio_pin_configure_dt(&ledSpec1, GPIO_OUTPUT_INACTIVE);
    gpio_pin_configure_dt(&ledSpec2, GPIO_OUTPUT_INACTIVE);
    error = initIMU();
    if (error) {
        LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to initalize IMU", __FILE__, __func__, __LINE__);
		return error;
	}
    error = initEMG();
    if (error) {
        LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to initalize EMG", __FILE__, __func__, __LINE__);
		return error;
	}
	error = initBle();
    if (error) {
        LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to initalize BLE", __FILE__, __func__, __LINE__);
		return error;
	}
    int index = 0;
    while(1){
        int error = 0;
        // error = updatePayloadWithGyroData(index);
        // if (error) {
        //     LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to updateGyroPayload Values", __FILE__, __func__, __LINE__);
        //     return error;
        // }
        // error = updatePayloadWithAccelData(index);
        // if (error) {
        //     LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to updateGyroPayload Values", __FILE__, __func__, __LINE__);
        //     return error;
        // }
        error = updatePayloadWithEMGData(index);
        if (error) {
            LOG_ERR("ERROR@ file:%s, function:%s(), line:%d - Failed to updateEMGPayload Values", __FILE__, __func__, __LINE__);
            return error;
        }
        if(++index >= 20){
            sendPacket();
            index = 0;
        }
        // k_msleep(SLEEP_TIME_MS);
    }
    return error;
}