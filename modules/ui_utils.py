import logging
import asyncio
from typing import Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)


def install_call_from_async(page: Any) -> Any:
    """
    Installe une méthode sûre `call_from_async` sur l'instance `page`.

    - Si on est dans Pyodide : exécute directement la fonction.
    - Si une boucle asyncio est disponible : planifie l'appel en thread-safe.
    - Sinon : exécute la fonction en fallback synchrone.

    Cela évite de modifier `site-packages` et exploite la boucle interne de Flet quand elle existe.
    """

    def _is_pyodide() -> bool:
        try:
            from flet.utils import is_pyodide
            return is_pyodide()
        except Exception:
            return False

    def call_from_async(func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """
        Appelle `func` de manière sûre depuis un contexte async.
        """
        print("call_from_async called")
        @wraps(func)
        def _safe_call() -> None:
            try:
                func(*args, **kwargs)
                print("Function executed in _safe_call")
            except Exception:
                logger.exception("Exception in call_from_async callback")
                print("Exception in call_from_async callback")

        if _is_pyodide():
            try:
                func(*args, **kwargs)
                logger.debug("Function executed in Pyodide context")
            except Exception:
                logger.exception("Exception in call_from_async (pyodide)")
            return

        loop: asyncio.AbstractEventLoop | None = getattr(page, "_Page__loop", None)
        if loop is None:
            print("No loop found, executing directly")
            try:
                func(*args, **kwargs)
                logger.debug("Function executed in fallback (no loop found)")
            except Exception:
                logger.exception("Exception in call_from_async (fallback)")
            return

        try:
            loop.call_soon_threadsafe(_safe_call)
            logger.debug("Function scheduled on asyncio loop")
            print("Function scheduled on asyncio loop")
        except Exception:
            logger.exception("Failed to schedule call_from_async on loop")
            print("Failed to schedule call_from_async on loop")

    try:
        setattr(page, "call_from_async", call_from_async)
        logger.debug("call_from_async installed successfully on page")
        print("call_from_async installed successfully on page")
    except Exception:
        logger.exception("Failed to install call_from_async on page")

    return page
