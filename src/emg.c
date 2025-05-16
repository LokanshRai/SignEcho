#include "emg.h"
#include "commondefines.h"
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(EMG_LOG); //Logging
int16_t emgData[ARRAY_SIZE(adc_channels)];
int initEMG(){
    int error = 0;
	for (size_t i = 0U; i < ARRAY_SIZE(adc_channels); i++) {
		error = !adc_is_ready_dt(&adc_channels[i]);
		if (error) {
            LOG_ERR("ADC controller device %s not ready\n", adc_channels[i].dev->name);
            return error;
        }
		//returns 0 on success -ENOTSUP (134) or 1 on failure
		error = adc_channel_setup_dt(&adc_channels[i]);
		if (error){
            LOG_ERR("Could not setup channel #%d (%d)\n", i, error);
            return error;
        } 
	}
    return error;
}

int readEMG(){
	int16_t buf;
	struct adc_sequence sequence = {
		.buffer = &buf,
		.buffer_size = sizeof(buf),
	};
	int error;
	for (size_t i = 0U; i < ARRAY_SIZE(adc_channels); i++) {
		int val_mv;
		(void)adc_sequence_init_dt(&adc_channels[i], &sequence);
		error = adc_read_dt(&adc_channels[i], &sequence);
		if (error < 0) {
			continue;
		}
		val_mv = (int)buf;
		error = adc_raw_to_millivolts_dt(&adc_channels[i],
							&val_mv);
		/* conversion to mV may not be supported, skip if not */
		if (error < 0) {
			LOG_ERR(" (value in mV not available)\n");
		} else {
			emgData[i] = val_mv;
		}
	
	}
	return error;
}

void printEMGData(){
    LOG_INF("INFO@ Printing EMG Data");
    for(int i = 0; i < ARRAY_SIZE(emgData); i++){
        LOG_INF("INDEX: %d HEXADECIMAL VALUE: %hx", i, emgData[i]);
    }
}
