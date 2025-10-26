import abc
import asyncio
import importlib
import logging
import os
from typing import Any, Dict, Optional


class BaseAlgorithm(abc.ABC):

    name: str = "base"
    version: str = "0.1.0"

    def __init__(
        self,
        strategy: Dict[str, Any],
        logger: Optional[logging.Logger] = None,
        stop_evt: Optional[asyncio.Event] = None,
    ):
        self.strategy = strategy or {}
        self.logger = logger or logging.getLogger(f"algo.{self.strategy.get('id', 'unknown')}")
        self.stop_evt = stop_evt or asyncio.Event()


    async def initialize(self) -> None:
        """Run once before the first tick (e.g., load models, connect DB)."""
        pass

    async def before_tick(self, context: Dict[str, Any]) -> None:
        """Hook before each tick. Override if needed."""
        pass

    async def after_tick(self, context: Dict[str, Any], result: Any) -> None:
        """Hook after each tick. Override if needed."""
        pass

    async def aclose(self) -> None:
        """Cleanup hook on shutdown."""
        pass

    # ------------------------------------------------------------------ #
    # Main execution
    # ------------------------------------------------------------------ #
    async def arun(self, context: Dict[str, Any]) -> Any:
        """
        Async entrypoint. Falls back to sync `run()` if not overridden.
        Subclasses can implement either `arun()` or `run()`.
        """
        run_fn = getattr(self, "run", None)
        if callable(run_fn):
            out = run_fn(context)
            if asyncio.iscoroutine(out):
                out = await out
            return out
        raise NotImplementedError("Subclass must implement `run()` or override `arun()`.")

    # ------------------------------------------------------------------ #
    # Parameter & secret helpers
    # ------------------------------------------------------------------ #
    def merged_params(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Merge defaults < strategy.params < context.params."""
        defaults = defaults or {}
        context = context or {}
        p_ctx = (context.get("params") or {})
        p_strat = (self.strategy.get("params") or {})
        return {**defaults, **p_strat, **p_ctx}

    def get_param(self, key: str, default: Any = None, context: Optional[Dict[str, Any]] = None) -> Any:
        return self.merged_params({key: default}, context).get(key, default)

    def get_secret(
        self, key: str, default: Any = None, context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Resolve secret from context.secrets > strategy.secrets."""
        context = context or {}
        s_ctx = (context.get("secrets") or {})
        s_strat = (self.strategy.get("secrets") or {})
        return s_ctx.get(key, s_strat.get(key, default))

    def env_or_secret(
        self,
        env_var: str,
        secret_key: Optional[str] = None,
        default: Any = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Return value from environment or secrets."""
        val = os.getenv(env_var)
        if val:
            return val
        return self.get_secret(secret_key or env_var.lower(), default, context)
    
    def require_import(self, module_name: str, install_hint: Optional[str] = None):
        """Import a dependency or raise with a clear hint."""
        try:
            return importlib.import_module(module_name)
        except Exception as e:
            hint = f" (try `pip install {install_hint}`)" if install_hint else ""
            raise RuntimeError(f"Missing dependency: {module_name}{hint}") from e

    def cancelled(self) -> bool:
        """Check if the controller stop event is set."""
        return self.stop_evt.is_set()

    def meta(self) -> Dict[str, Any]:
        """Metadata for logging or diagnostics."""
        return {
            "name": getattr(self, "name", self.__class__.__name__),
            "version": getattr(self, "version", "0.0.0"),
            "strategy_id": self.strategy.get("id"),
        }
