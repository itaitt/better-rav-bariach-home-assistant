"""Shared base for Rav Bariach entities."""

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, MANUFACTURER


class RavBariachEntity(Entity):
    """An entity backed by one lock's data dict, kept fresh by the WebSocket.

    All entities of a lock share the same dict from the coordinator. Each one
    subscribes to the gateway itself, so none depends on another being enabled.
    """

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, gateway, data) -> None:
        """Initialize the entity."""
        self._gateway = gateway
        self._data = data
        self._device_id = str(data.get("deviceId"))

    async def async_added_to_hass(self) -> None:
        """Subscribe to WebSocket updates for this lock."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self._gateway.register_listener(self._device_id, self._handle_update)
        )

    @callback
    def _handle_update(self, msg_data) -> None:
        """Merge a WebSocket update and write the new state."""
        if isinstance(msg_data, dict):
            self._data.update(msg_data)
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information for Home Assistant."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._data.get("deviceName", "Rav Bariach Lock"),
            manufacturer=MANUFACTURER,
            model=self._data.get("deviceModel"),
            sw_version=self._data.get("firmwareVersion"),
            hw_version=self._data.get("hardwareVersion"),
            suggested_area=self._data.get("deviceName"),
        )
