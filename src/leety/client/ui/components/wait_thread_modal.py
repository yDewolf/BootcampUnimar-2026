import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable, Any, Optional

from leety.client.app_protocol import AppProtocol
from leety.client.ui.abstract_screen import MFrame
from leety.client.ui.components.modals import CenterableModal
from leety.client.ui.ui_components import default_text, default_title


class WaitThreadModal(CenterableModal, MFrame[AppProtocol]):
    target_func: Callable[..., Any]
    args: tuple
    kwargs: Optional[dict]

    _thread: Optional[threading.Thread] = None
    result: Any = None
    error: Optional[Exception] = None

    def __init__(
        self,
        parent: tk.Misc,
        controller: AppProtocol,
        target_func: Callable[..., Any],
        args: tuple = (),
        kwargs: Optional[dict] = None,
        title: str = "Aguarde",
        message: str = "Processando, por favor aguarde..."
    ):
        self.controller = controller
        super().__init__(parent, "300x150")
        
        self.target_func = target_func
        self.args = args
        self.kwargs = kwargs or {}

        self.title(title)
        self.resizable(False, False)
        
        self._setup_ui(message)
        self.start()

    def _setup_ui(self, message: str):
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        default_title(container, "Aguarde...").pack(anchor="w", pady=(0, 10))
        message_txt = tk.Text(container, wrap="word", relief="flat", height=3)
        message_txt.insert(1.0, message)
        message_txt.pack(anchor="w", pady=(0, 15))

        self.progress_bar = ttk.Progressbar(container, mode="indeterminate", length=250)
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.start(10)

    def start(self):
        def wrapper():
            try:
                self.result = self.target_func(*self.args, **self.kwargs)
            except Exception as e:
                self.error = e

        self._thread = threading.Thread(target=wrapper, daemon=True)
        self._thread.start()
        
        self._check_thread()

    def _check_thread(self):
        if self._thread and self._thread.is_alive():
            self.after(500, self._check_thread)
        else:
            self.progress_bar.stop()
            self.destroy()

    @classmethod
    def execute(
        cls,
        parent: tk.Misc,
        controller: AppProtocol,
        target_func: Callable[..., Any],
        args: tuple = (),
        kwargs: Optional[dict] = None,
        title: str = "Aguarde",
        message: str = "Processando, por favor aguarde..."
    ) -> Any:
        modal = cls(parent, controller, target_func, args, kwargs, title, message)
        modal.grab_set()
        parent.wait_window(modal)
        
        if modal.error:
            raise modal.error

        return modal.result