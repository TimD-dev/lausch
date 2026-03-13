"""Windows autostart via registry."""

from __future__ import annotations

import logging
import sys
import winreg

logger = logging.getLogger(__name__)

_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APP_NAME = "Lausch"


def set_autostart(enabled: bool) -> None:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _KEY_PATH, 0, winreg.KEY_SET_VALUE
        )
        if enabled:
            exe_path = sys.executable
            # If running as frozen exe (PyInstaller), use that path
            if getattr(sys, "frozen", False):
                exe_path = sys.executable
            else:
                exe_path = f'"{sys.executable}" -m lausch'
            winreg.SetValueEx(key, _APP_NAME, 0, winreg.REG_SZ, exe_path)
            logger.info("Autostart enabled: %s", exe_path)
        else:
            try:
                winreg.DeleteValue(key, _APP_NAME)
                logger.info("Autostart disabled")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception:
        logger.warning("Failed to set autostart", exc_info=True)


def is_autostart_enabled() -> bool:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _KEY_PATH, 0, winreg.KEY_READ
        )
        winreg.QueryValueEx(key, _APP_NAME)
        winreg.CloseKey(key)
        return True
    except (FileNotFoundError, OSError):
        return False
