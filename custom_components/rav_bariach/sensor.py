"""Handle Sensor operations."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LockStatus, OnlineStatus
from .entity import RavBariachEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Rav Bariach Lock sensors from a config entry."""
    data_pack = hass.data[DOMAIN][entry.entry_id]
    gateway = data_pack["gateway"]
    devices = data_pack["coordinator"].data.locks

    entities = []
    for device_data in devices:
        entities.append(RavBariachBatterySensor(gateway, device_data))
        entities.append(RavBariachLockStatusSensor(gateway, device_data))
        entities.append(RavBariachLockAvailabilitySensor(gateway, device_data))
    async_add_entities(entities)


def _int_field(data: dict, key: str) -> int | None:
    """Return data[key] as an int, or None if it is missing or malformed."""
    try:
        return int(data[key])
    except (KeyError, ValueError, TypeError):
        return None


class RavBariachBatterySensor(RavBariachEntity, SensorEntity):
    """Representation of a Rav Bariach Lock Battery Sensor."""

    _attr_translation_key = "battery_status"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, gateway, data):
        """Initialize the sensor."""
        super().__init__(gateway, data)
        self._attr_unique_id = f"rav_bariach_lock_battery_{self._device_id}"

    @property
    def native_value(self) -> int | None:
        """Return the battery level, or None when the lock has not reported one."""
        return _int_field(self._data, "batteryLevel")


class RavBariachLockStatusSensor(RavBariachEntity, SensorEntity):
    """Representation of a Rav Bariach Lock State Sensor."""

    _attr_translation_key = "lock_status"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["locked", "unlocked"]

    def __init__(self, gateway, data):
        """Initialize the sensor."""
        super().__init__(gateway, data)
        self._attr_unique_id = f"rav_bariach_lock_status_{self._device_id}"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return {
            LockStatus.UNLOCKED: "unlocked",
            LockStatus.LOCKED: "locked",
        }.get(_int_field(self._data, "status"))

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return {
            "locked": "mdi:lock",
            "unlocked": "mdi:lock-open-variant",
        }.get(self.native_value, "mdi:lock-question")


class RavBariachLockAvailabilitySensor(RavBariachEntity, SensorEntity):
    """Representation of a Rav Bariach Lock Online - Offline Sensor."""

    _attr_translation_key = "hub_status"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["online", "offline"]
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, gateway, data):
        """Initialize the sensor."""
        super().__init__(gateway, data)
        self._attr_unique_id = f"rav_bariach_lock_online_{self._device_id}"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        status = _int_field(self._data, "isOnline")
        if status is None:
            return None
        return "online" if status == OnlineStatus.ONLINE else "offline"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:router-wireless" if self.native_value == "online" else "mdi:router-wireless-off"
