from typing import Optional

import customtkinter as ctk

from src.settings_manager import SettingsManager


class ThemeManager:
    _instance = None

    NEON_DARK = {
        "bg": "#050816",
        "bg_secondary": "#0a0e27",
        "bg_card": "#0d1233",
        "primary": "#00d4ff",
        "secondary": "#ff00ff",
        "accent": "#00fff7",
        "text": "#ffffff",
        "text_secondary": "#8892b0",
        "success": "#00ff88",
        "warning": "#ffaa00",
        "error": "#ff3355",
        "border": "#1a1f4e",
        "border_active": "#00d4ff",
        "glow_primary": "#005577",
        "glow_secondary": "#550055",
    }

    NEON_LIGHT = {
        "bg": "#f0f2ff",
        "bg_secondary": "#e0e4ff",
        "bg_card": "#ffffff",
        "primary": "#0066ff",
        "secondary": "#cc00cc",
        "accent": "#00ccbb",
        "text": "#0a0e27",
        "text_secondary": "#555577",
        "success": "#00aa55",
        "warning": "#cc8800",
        "error": "#cc2244",
        "border": "#c0c4e0",
        "border_active": "#0066ff",
        "glow_primary": "#aaccff",
        "glow_secondary": "#ffbbff",
    }

    def __init__(self, settings: Optional[SettingsManager] = None) -> None:
        self._settings = settings or SettingsManager()
        self._current_theme: str = "dark"
        self._colors: dict[str, str] = dict(self.NEON_DARK)
        self._apply_theme()

    def _apply_theme(self) -> None:
        theme_name = self._settings.get("appearance", "theme") or "dark"
        if theme_name == "light":
            self._colors = dict(self.NEON_LIGHT)
        else:
            self._colors = dict(self.NEON_DARK)

        self._current_theme = theme_name
        ctk.set_appearance_mode(theme_name)

        primary = self._colors["primary"]
        ctk.set_default_color_theme("dark-blue")
        try:
            ctk.ThemeManager.theme["color"]["button"] = [primary, primary]
        except Exception:
            pass

    def toggle_theme(self) -> str:
        new_theme = "light" if self._current_theme == "dark" else "dark"
        self._current_theme = new_theme
        self._settings.set("appearance", "theme", new_theme)
        self._apply_theme()
        return new_theme

    @property
    def colors(self) -> dict[str, str]:
        return dict(self._colors)

    @property
    def theme_name(self) -> str:
        return self._current_theme

    def c(self, name: str) -> str:
        return self._colors.get(name, "#ffffff")

    def configure_widget(self, widget: ctk.CTkBaseClass, **kwargs) -> None:
        for key, value in kwargs.items():
            try:
                widget.configure(**{key: value})
            except Exception:
                pass
