import os
from pathlib import Path
import tkinter as tk
from typing import Optional

import customtkinter as ctk

from src.font_manager import ui_font, is_using_fallback
from src.history_manager import HistoryManager
from src.lottery_engine import LotteryEngine
from src.main_window import MainWindow
from src.monitor_manager import MonitorManager
from src.public_window import PublicWindow
from src.settings_manager import SettingsManager
from src.sound_manager import SoundManager
from src.splash_screen import SplashScreen
from src.theme_manager import ThemeManager


class App:

    def __init__(self) -> None:
        self._settings = SettingsManager()
        self._theme = ThemeManager(self._settings)
        self._engine = LotteryEngine()
        self._history = HistoryManager(
            self._settings.get("history", "save_path") or "exports"
        )
        self._sound = SoundManager()
        self._monitor_mgr = MonitorManager()

        self._root: Optional[ctk.CTk] = None
        self._main_window: Optional[MainWindow] = None
        self._public_window: Optional[PublicWindow] = None
        self._icon_images: list[tk.PhotoImage] = []

    def _load_window_icon(self) -> None:
        """Loads the app icon and sets it as the default for all windows.

        Multiple pre-scaled PNGs are provided so the window manager can pick
        the best size. (A single large icon, or images created with
        ``subsample``, are written as an empty ``_NET_WM_ICON`` on some X11
        setups.)
        """
        try:
            project_root = Path(__file__).resolve().parent.parent
            assets = project_root / "assets"
            files = [assets / f"icone_{size}.png" for size in (16, 32, 48, 64, 128)]
            files.append(project_root / "icone.png")
            self._icon_images = []
            for path in files:
                if path.exists():
                    self._icon_images.append(tk.PhotoImage(file=str(path)))
            if self._icon_images:
                self._root.iconphoto(True, *self._icon_images)
        except Exception:
            self._icon_images = []

    def run(self) -> None:
        window_w, window_h = 900, 850
        self._root = ctk.CTk(className="SorteioProfissional")
        self._root.minsize(900, 850)
        self._root.configure(fg_color=self._theme.c("bg"))
        self._load_window_icon()

        if is_using_fallback():
            ctk.set_widget_scaling(1.5)
            ctk.set_window_scaling(1.2)

        primary = self._monitor_mgr.primary
        if primary is not None:
            x = primary.x + max((primary.width - window_w) // 2, 0)
            y = primary.y + max((primary.height - window_h) // 2, 0)
        else:
            sw = self._root.winfo_screenwidth()
            sh = self._root.winfo_screenheight()
            x = (sw - window_w) // 2
            y = (sh - window_h) // 2
        self._root.geometry(f"{window_w}x{window_h}+{x}+{y}")

        splash = SplashScreen(self._root, self._theme, self._monitor_mgr.primary)
        splash.grab_set()
        self._root.wait_window(splash)

        self._main_window = MainWindow(
            master=self._root,
            theme=self._theme,
            settings=self._settings,
            engine=self._engine,
            history=self._history,
            sound=self._sound,
            on_start_draw=self._on_start_draw,
            on_new_draw=self._on_new_draw,
            on_reset=self._on_reset,
            on_clear=self._on_clear,
            on_settings=self._on_settings,
            on_export=self._on_export,
            on_fullscreen=self._on_fullscreen,
            on_quit=self._on_quit,
            on_toggle_theme=self._toggle_theme,
            on_toggle_minimize=self._on_toggle_minimize,
        )

        self._sound.enabled = bool(self._settings.get("sound", "enabled"))

        self._setup_public_display()
        self._setup_keyboard_shortcuts()

        self._root.after(150, self._root.lift)
        self._root.after(300, self._root.focus_force)

        self._root.protocol("WM_DELETE_WINDOW", self._on_quit)
        self._root.mainloop()

    def _setup_public_display(self) -> None:
        use_public = False
        public_monitor = None

        if self._monitor_mgr.has_multiple_monitors:
            idx = self._settings.get("display", "public_monitor") or 1
            public_monitor = self._monitor_mgr.get_public_monitor(idx)
            use_public = public_monitor is not None

        if use_public and public_monitor:
            self._public_window = PublicWindow(self._theme, self._settings)
            self._public_window.create(
                x=public_monitor.x,
                y=public_monitor.y,
                w=public_monitor.width,
                h=public_monitor.height,
                fullscreen=self._settings.get("display", "fullscreen") or False,
            )
        else:
            answer = tk.messagebox.askyesno(
                title="Monitor Público",
                message="Nenhum monitor secundário detectado.\n\n"
                        "Deseja utilizar apenas uma tela?\n\n"
                        "Sim: O sorteio será exibido nesta janela.\n"
                        "Não: O sorteio funcionará apenas no modo operador "
                        "(sem exibição pública).",
            )
            if answer:
                self._public_window = PublicWindow(self._theme, self._settings)
                self._public_window.create(
                    x=200, y=200, w=800, h=600,
                    fullscreen=False,
                )

    def _setup_keyboard_shortcuts(self) -> None:
        if self._root:
            self._root.bind("<F11>", lambda e: self._on_fullscreen())
            self._root.bind("<space>", lambda e: self._on_space())
            self._root.bind("<Control-r>", lambda e: self._on_reset())
            self._root.bind("<Control-e>", lambda e: self._on_export())
            self._root.bind("<Escape>", lambda e: self._on_quit())
            self._root.bind("<Control-m>", lambda e: self._on_toggle_minimize())
            self._root.bind("<Control-q>", lambda e: self._on_quit())
            self._root.bind("<Control-t>", lambda e: self._toggle_theme())

    # ── Event handlers ──

    def _on_start_draw(self, numbers: list[int]) -> None:
        self._sound.play("transition")
        if self._public_window and self._public_window.is_open:
            if self._engine.mode == "names":
                self._public_window.start_draw_names(
                    numbers,
                    name_pool=self._engine.all_items,
                    on_end=self._on_public_animation_end,
                )
            else:
                self._public_window.start_draw(
                    numbers,
                    range_min=self._engine.start,
                    range_max=self._engine.end,
                    on_end=self._on_public_animation_end,
                )
        else:
            self._sound.play("firework")
            self._check_completed()

    def _on_public_animation_end(self) -> None:
        self._sound.play("firework")
        self._check_completed()

    def _on_new_draw(self) -> None:
        self._check_completed()

    def _on_reset(self) -> None:
        if self._public_window and self._public_window.is_open:
            self._public_window.close()
            self._setup_public_display()

    def _on_clear(self) -> None:
        if self._public_window and self._public_window.is_open:
            self._public_window.show_idle()

    def _on_settings(self) -> None:
        self._show_settings_dialog()

    def _on_export(self) -> None:
        self._show_export_dialog()

    def _show_export_dialog(self) -> None:
        """Custom save dialog that only lists the user's common (non-hidden)
        folders and files, starting at the home directory."""
        from tkinter import messagebox

        dialog = ctk.CTkToplevel(self._root)
        dialog.title("Exportar Histórico")
        dialog.configure(fg_color=self._theme.c("bg"))
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.geometry(f"680x520+{self._root.winfo_x() + 100}+{self._root.winfo_y() + 100}")

        current_dir = [os.path.expanduser("~")]
        selected = ["sorteios.csv"]

        ctk.CTkLabel(
            dialog,
            text="Exportar Histórico",
            font=(ui_font(), 18, "bold"),
            text_color=self._theme.c("primary"),
        ).pack(anchor="w", padx=15, pady=(15, 5))

        path_bar = ctk.CTkFrame(dialog, fg_color="transparent")
        path_bar.pack(fill="x", padx=15, pady=5)

        def go_home() -> None:
            current_dir[0] = os.path.expanduser("~")
            refresh()

        def go_up() -> None:
            parent = os.path.dirname(current_dir[0])
            if os.path.isdir(parent):
                current_dir[0] = parent
                refresh()

        ctk.CTkButton(
            path_bar,
            text="Início",
            width=70, height=28,
            font=(ui_font(), 11),
            fg_color=self._theme.c("primary"),
            command=go_home,
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            path_bar,
            text="Subir",
            width=70, height=28,
            font=(ui_font(), 11),
            fg_color=self._theme.c("text_secondary"),
            command=go_up,
        ).pack(side="left")

        path_lbl = ctk.CTkLabel(
            path_bar,
            text="",
            font=(ui_font(), 11),
            text_color=self._theme.c("text_secondary"),
            anchor="w",
        )
        path_lbl.pack(side="left", fill="x", expand=True, padx=(10, 0))

        list_frame = ctk.CTkScrollableFrame(
            dialog,
            fg_color=self._theme.c("bg_card"),
            corner_radius=8,
        )
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        def open_folder(name: str) -> None:
            current_dir[0] = os.path.join(current_dir[0], name)
            refresh()

        def pick_file(name: str) -> None:
            selected[0] = name
            entry_filename.delete(0, "end")
            entry_filename.insert(0, name)

        def refresh() -> None:
            for widget in list_frame.winfo_children():
                widget.destroy()

            def bind_row(row, handler) -> None:
                row.bind("<Button-1>", lambda e: handler())
                row.bind("<Double-Button-1>", lambda e: handler())
                for child in row.winfo_children():
                    child.bind("<Button-1>", lambda e: handler())
                    child.bind("<Double-Button-1>", lambda e: handler())

            path = current_dir[0]
            path_lbl.configure(text=path)

            try:
                entries = sorted(os.listdir(path))
            except OSError as e:
                ctk.CTkLabel(
                    list_frame,
                    text=f"Não foi possível abrir a pasta:\n{e}",
                    font=(ui_font(), 12),
                    text_color=self._theme.c("error"),
                ).pack(pady=10)
                return

            folders = [
                name for name in entries
                if not name.startswith(".")
                and os.path.isdir(os.path.join(path, name))
            ]
            files = [
                name for name in entries
                if not name.startswith(".")
                and os.path.isfile(os.path.join(path, name))
                and name.lower().endswith((".csv", ".txt"))
            ]

            for folder in folders:
                row = ctk.CTkFrame(list_frame, fg_color="transparent")
                row.pack(fill="x", padx=2, pady=1)
                ctk.CTkLabel(
                    row,
                    text=f"  {folder}/",
                    font=(ui_font(), 12),
                    text_color=self._theme.c("text"),
                    anchor="w",
                ).pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(
                    row,
                    text="Pasta",
                    font=(ui_font(), 10),
                    text_color=self._theme.c("text_secondary"),
                ).pack(side="right")
                bind_row(row, lambda n=folder: open_folder(n))

            for file in files:
                row = ctk.CTkFrame(list_frame, fg_color="transparent")
                row.pack(fill="x", padx=2, pady=1)
                ctk.CTkLabel(
                    row,
                    text=f"  {file}",
                    font=(ui_font(), 12),
                    text_color=self._theme.c("text"),
                    anchor="w",
                ).pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(
                    row,
                    text="Arquivo",
                    font=(ui_font(), 10),
                    text_color=self._theme.c("text_secondary"),
                ).pack(side="right")
                bind_row(row, lambda n=file: pick_file(n))

            if not folders and not files:
                ctk.CTkLabel(
                    list_frame,
                    text="Nenhuma pasta ou arquivo visível aqui.",
                    font=(ui_font(), 12),
                    text_color=self._theme.c("text_secondary"),
                ).pack(pady=10)

        name_row = ctk.CTkFrame(dialog, fg_color="transparent")
        name_row.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            name_row,
            text="Nome do arquivo:",
            font=(ui_font(), 12),
            text_color=self._theme.c("text_secondary"),
        ).pack(side="left", padx=(0, 10))

        entry_filename = ctk.CTkEntry(
            name_row,
            font=(ui_font(), 12),
            height=32,
        )
        entry_filename.insert(0, selected[0])
        entry_filename.pack(side="left", fill="x", expand=True)

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(fill="x", padx=15, pady=(5, 15))

        def save() -> None:
            name = entry_filename.get().strip()
            if not name:
                return
            if not name.lower().endswith((".csv", ".txt")):
                name += ".csv"
            filepath = os.path.join(current_dir[0], name)
            dialog.destroy()
            self._perform_export(filepath, messagebox)

        ctk.CTkButton(
            btn_row,
            text="Salvar",
            width=120, height=36,
            font=(ui_font(), 12, "bold"),
            fg_color=self._theme.c("primary"),
            command=save,
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            btn_row,
            text="Cancelar",
            width=120, height=36,
            font=(ui_font(), 12),
            fg_color=self._theme.c("text_secondary"),
            command=dialog.destroy,
        ).pack(side="right")

        refresh()

    def _perform_export(self, filepath: str, messagebox) -> None:
        try:
            if filepath.endswith(".csv"):
                result = self._history.export_csv(filepath)
            else:
                result = self._history.export_txt(filepath)

            messagebox.showinfo(
                title="Exportado",
                message=f"Histórico exportado com sucesso!\n{result}",
            )
        except Exception as e:
            messagebox.showerror(
                title="Erro",
                message=f"Erro ao exportar: {e}",
            )

    def _on_fullscreen(self) -> None:
        if self._public_window and self._public_window.is_open:
            self._public_window.toggle_fullscreen()

    def _on_toggle_minimize(self) -> None:
        if self._public_window and self._public_window.is_open:
            minimized = self._public_window.toggle_minimize()
            if self._main_window:
                self._main_window.set_public_minimized(minimized)

    def _on_quit(self) -> None:
        self._sound.cleanup()
        if self._public_window:
            self._public_window.close()
        if self._root:
            self._root.destroy()

    def _on_space(self) -> None:
        widget = self._root.focus_get() if self._root else None
        if isinstance(widget, (tk.Entry, ctk.CTkEntry, ctk.CTkCheckBox)):
            return
        if self._main_window:
            self._main_window._on_new_click()

    def _toggle_theme(self) -> None:
        self._theme.toggle_theme()
        if self._main_window:
            self._main_window.refresh_theme()

    def _check_completed(self) -> None:
        if self._engine.is_completed():
            if self._main_window:
                self._main_window.show_completed_message()
            if self._public_window and self._public_window.is_open:
                self._public_window.show_completed(
                    is_names=self._engine.mode == "names"
                )

    def _show_settings_dialog(self) -> None:
        dialog = ctk.CTkToplevel(self._root)
        dialog.title("Configurações")
        dialog.geometry("500x500")
        dialog.configure(fg_color=self._theme.c("bg"))
        dialog.resizable(False, False)
        dialog.grab_set()

        x = self._root.winfo_x() + 100
        y = self._root.winfo_y() + 100
        dialog.geometry(f"500x500+{x}+{y}")

        main_frame = ctk.CTkScrollableFrame(
            dialog,
            fg_color="transparent",
        )
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            main_frame,
            text="Configurações",
            font=(ui_font(), 20, "bold"),
            text_color=self._theme.c("primary"),
        ).pack(anchor="w", pady=(0, 15))

        sections = [
            ("Animação", [
                ("Duração (s)",
                 str(self._settings.get("animation", "duration") or 1.2)),
                ("Velocidade Inicial (ms)",
                 str(self._settings.get("animation", "initial_speed") or 30)),
                ("Velocidade Mínima (ms)",
                 str(self._settings.get("animation", "min_speed") or 200)),
            ]),
            ("Áudio", [
                ("Som Ativado",
                 "Sim" if self._settings.get("sound", "enabled") else "Sim"),
                ("Volume",
                 str(self._settings.get("sound", "volume") or 0.5)),
            ]),
            ("Monitor", [
                ("Tela Cheia",
                 "Sim" if self._settings.get("display", "fullscreen") else "Sim"),
                ("Transparência da Tela",
                 str(self._settings.get("display", "public_alpha") or 1.0)),
            ]),
        ]

        entries = {}

        for section_name, fields in sections:
            section_frame = ctk.CTkFrame(
                main_frame,
                fg_color=self._theme.c("bg_card"),
                corner_radius=8,
            )
            section_frame.pack(fill="x", pady=(0, 10))

            ctk.CTkLabel(
                section_frame,
                text=section_name,
                font=(ui_font(), 14, "bold"),
                text_color=self._theme.c("primary"),
            ).pack(anchor="w", padx=15, pady=(10, 5))

            for field_name, default in fields:
                row = ctk.CTkFrame(section_frame, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=3)

                ctk.CTkLabel(
                    row,
                    text=field_name,
                    font=(ui_font(), 12),
                    text_color=self._theme.c("text_secondary"),
                ).pack(side="left")

                entry = ctk.CTkEntry(
                    row,
                    width=150,
                    height=30,
                    font=(ui_font(), 12),
                )
                entry.insert(0, default)
                entry.pack(side="right")
                entries[f"{section_name}:{field_name}"] = entry

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(
            btn_frame,
            text="Salvar",
            command=lambda: self._save_settings(dialog, entries),
            width=120,
            height=36,
            font=(ui_font(), 12, "bold"),
            fg_color=self._theme.c("primary"),
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=dialog.destroy,
            width=120,
            height=36,
            font=(ui_font(), 12),
            fg_color=self._theme.c("text_secondary"),
        ).pack(side="right")

    def _save_settings(
        self,
        dialog: ctk.CTkToplevel,
        entries: dict,
    ) -> None:
        try:
            self._settings.set(
                "animation", "duration",
                float(entries["Animação:Duração (s)"].get())
            )
            self._settings.set(
                "animation", "initial_speed",
                int(entries["Animação:Velocidade Inicial (ms)"].get())
            )
            self._settings.set(
                "animation", "min_speed",
                int(entries["Animação:Velocidade Mínima (ms)"].get())
            )
            self._settings.set(
                "sound", "volume",
                float(entries["Áudio:Volume"].get())
            )
            self._settings.set(
                "sound", "enabled",
                entries["Áudio:Som Ativado"].get().lower() == "sim"
            )
            self._settings.set(
                "display", "fullscreen",
                entries["Monitor:Tela Cheia"].get().lower() == "sim"
            )
            alpha = float(entries["Monitor:Transparência da Tela"].get())
            if not 0.2 <= alpha <= 1.0:
                raise ValueError("Transparência deve estar entre 0.2 e 1.0")
            self._settings.set("display", "public_alpha", alpha)

            self._sound.volume = self._settings.get("sound", "volume") or 0.5
            self._sound.enabled = self._settings.get("sound", "enabled") or False
            if self._public_window and self._public_window.is_open:
                self._public_window.set_alpha(alpha)
            dialog.destroy()

        except ValueError as e:
            tk.messagebox.showerror(
                title="Erro",
                message=f"Valor inválido: {e}",
            )


def create_app() -> App:
    return App()
