#include "ble.h"
#include <zephyr/logging/log.h>
#include <dk_buttons_and_leds.h>
#include "commondefines.h"
#include <zephyr/bluetooth/gatt.h>

LOG_MODULE_REGISTER(BLE_LOG); 

static K_SEM_DEFINE(bt_init_ok, 1, 1);

static struct bt_conn *current_conn;
enum bt_button_notifications_enabled notifications_enabled;

void button_chrc_ccc_cfg_changed(const struct bt_gatt_attr *attr, uint16_t value);
void on_notif_changed(enum bt_button_notifications_enabled status);

struct bt_remote_service_cb {
	void (*notif_changed)(enum bt_button_notifications_enabled status);
};

struct bt_remote_service_cb remote_callbacks = {
	.notif_changed = on_notif_changed,
};

struct bt_conn_cb bluetooth_callbacks = {
	.connected 		= on_connected,
	.disconnected 	= on_disconnected,
};

enum bt_button_notifications_enabled {
	BT_BUTTON_NOTIFICATIONS_ENABLED,
	BT_BUTTON_NOTIFICATIONS_DISABLED,
};

BT_GATT_SERVICE_DEFINE(remote_srv, BT_GATT_PRIMARY_SERVICE(BT_UUID_REMOTE_SERVICE),
	BT_GATT_CHARACTERISTIC(BT_UUID_MYSENSOR, BT_GATT_CHRC_READ | BT_GATT_CHRC_NOTIFY, BT_GATT_PERM_READ, NULL, NULL, NULL),
	BT_GATT_CCC(button_chrc_ccc_cfg_changed, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
);

void button_chrc_ccc_cfg_changed(const struct bt_gatt_attr *attr, uint16_t value)
{
    bool notif_enabled = (value == BT_GATT_CCC_NOTIFY);

	notifications_enabled = notif_enabled? BT_BUTTON_NOTIFICATIONS_ENABLED:BT_BUTTON_NOTIFICATIONS_DISABLED;
    if (remote_callbacks.notif_changed) {
        remote_callbacks.notif_changed(notifications_enabled);
    }
}

static struct bt_le_adv_param *adv_param = BT_LE_ADV_PARAM(
	(BT_LE_ADV_OPT_CONNECTABLE |
	 BT_LE_ADV_OPT_USE_IDENTITY), /* Connectable advertising and use identity address */
	800, /* Min Advertising Interval 500ms (800*0.625ms) */
	801, /* Max Advertising Interval 500.625ms (801*0.625ms) */
	NULL); /* Set to NULL for undirected advertising */

// Advertising Data
static const struct bt_data ad[] = {
    BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
    BT_DATA(BT_DATA_NAME_COMPLETE, DEVICE_NAME, DEVICE_NAME_LEN)
};

// Scan Response Data
static const struct bt_data sd[] = {
    BT_DATA_BYTES(BT_DATA_UUID128_ALL, BT_UUID_REMOTE_SERV_VAL),
};

// Callbacks

void on_notif_changed(enum bt_button_notifications_enabled status)
{
	if (status == BT_BUTTON_NOTIFICATIONS_ENABLED) {
		LOG_INF("Notifications enabled");
	}
	else {
		LOG_INF("Notificatons disabled");
	}
}

void on_connected(struct bt_conn *conn, uint8_t err)
{
	if(err) {
		LOG_ERR("connection err: %d", err);
		return;
	}
	LOG_INF("Connected.");
	current_conn = bt_conn_ref(conn);
	dk_set_led_on(CONN_STATUS_LED);
}

void on_disconnected(struct bt_conn *conn, uint8_t reason)
{
	LOG_INF("Disconnected (reason: %d)", reason);
	dk_set_led_off(CONN_STATUS_LED);
	if(current_conn) {
		bt_conn_unref(current_conn);
		current_conn = NULL;
	}
}

void readyBle(int error)
{
    if(error)
    {
        LOG_ERR("readyBle returned %d.", error);
    }
}

void on_sent(struct bt_conn *conn, void *user_data)
{
    ARG_UNUSED(user_data);
    LOG_INF("Notification sent on connection %p", (void *)conn);
}

void request_data_len_update(void)
{
	int err;
	err = bt_conn_le_data_len_update(current_conn, BT_LE_DATA_LEN_PARAM_MAX);
		if (err) {
			LOG_ERR("LE data length update request failed: %d",  err);
		}
}

void request_phy_update(void)
{
	int err;

	err = bt_conn_le_phy_update(current_conn, BT_CONN_LE_PHY_PARAM_2M);
		if (err) {
			LOG_ERR("Phy update request failed: %d",  err);
		}
}

int send_sensor_notification(int8_t* data, uint16_t length)
{
    int error = 0;

    struct bt_gatt_notify_params params = {0};
    const struct bt_gatt_attr *attr = &remote_srv.attrs[2];

    params.attr = attr;
    params.data = data;
    params.len  = length;
    params.func = on_sent;
    error 		= bt_gatt_notify_cb(current_conn, &params);
    // err = bt_gatt_notify(current_conn, &remote_srv.attrs[1], notify_data, sizeof(notify_data));

    return error;
}

int initBle()
{
    int error = 0;
    LOG_INF("Initializing BLE.");

    bt_conn_cb_register(&bluetooth_callbacks);
	remote_callbacks.notif_changed = remote_callbacks.notif_changed;
    error = bt_enable(readyBle);
    if(error)
    {
        return error;
    }

    k_sem_take(&bt_init_ok, K_FOREVER);

    error = bt_le_adv_start(adv_param, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
    if (error){
        LOG_ERR("Advertising start failed: (err = %d", error);
        return error;
    }
    LOG_ERR("Advertising successfully started");
    return error;
}
