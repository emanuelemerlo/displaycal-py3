"""Tests for the DisplayCAL.util_dbus module."""

import importlib
import sys

import pytest

pytestmark = pytest.mark.skipif(
    sys.platform in ("darwin", "win32"), reason="D-Bus is only used on Linux"
)


@pytest.fixture
def util_dbus_without_buses(monkeypatch):
    """Reload util_dbus with every D-Bus connection attempt failing."""
    from DisplayCAL import util_dbus

    def fail(*_args, **_kwargs):
        raise util_dbus.DBusException("no bus available")

    if util_dbus.USE_GI:
        monkeypatch.setattr(util_dbus.Gio, "bus_get_sync", fail)
    else:
        monkeypatch.setattr(util_dbus.dbus, "SessionBus", fail)
        monkeypatch.setattr(util_dbus.dbus, "SystemBus", fail)
    try:
        yield importlib.reload(util_dbus)
    finally:
        monkeypatch.undo()
        # Restore real connections so other tests see the normal module state
        importlib.reload(util_dbus)


def test_import_survives_missing_buses(util_dbus_without_buses):
    """Importing util_dbus must not fail when no D-Bus bus can be reached."""
    assert util_dbus_without_buses.dbus_session is None
    assert util_dbus_without_buses.dbus_system is None


@pytest.mark.parametrize("bus_type_name", ["BUSTYPE_SESSION", "BUSTYPE_SYSTEM"])
def test_dbus_object_raises_handled_error_without_bus(
    util_dbus_without_buses, bus_type_name
):
    """DBusObject raises a DBusException subclass that callers already catch."""
    util_dbus = util_dbus_without_buses
    with pytest.raises(util_dbus.DBusException, match="bus is not available"):
        util_dbus.DBusObject(
            getattr(util_dbus, bus_type_name), "org.freedesktop.ColorManager"
        )
