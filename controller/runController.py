import asyncio, json, time, signal, sys, importlib, logging, inspect
from typing import Any, Dict

try:
    import httpx
except ImportError:
    httpx = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

def load_config(path: str) -> dict:
    with open(path, "r") as f:
        cfg = json.load(f)
    assert isinstance(cfg.get("strategies"), list), "strategies must be a list"
    return cfg

def import_attr(module_path: str, attr_name: str):
    mod = importlib.import_module(module_path)
    if not hasattr(mod, attr_name):
        raise AttributeError(f"{module_path}.{attr_name} not found")
    return getattr(mod, attr_name)

def resolve_executor_attr(strategy: dict):
    ex = strategy["executor"]
    mod = ex["module"]
    name = ex.get("class") or ex.get("function") or ex.get("attr")
    if not name:
        raise KeyError("executor must specify 'class' or 'function'")
    return import_attr(mod, name)


async def exec_python(strategy: dict, context: Dict[str, Any], stop_evt: asyncio.Event) -> Dict[str, Any]:
    attr = resolve_executor_attr(strategy)

    # Class-based algorithm (preferred)
    try:
        from algorithms.base import BaseAlgorithm
    except Exception:
        BaseAlgorithm = None

    if inspect.isclass(attr) and BaseAlgorithm and issubclass(attr, BaseAlgorithm):
        algo = attr(strategy=strategy, stop_evt=stop_evt)  # type: ignore
        try:
            await algo.initialize()
            await algo.before_tick(context)
            out = await algo.arun(context)
            await algo.after_tick(context, out)
            return {"ok": True, "result": out, "meta": getattr(algo, "meta", lambda: {})()}
        finally:
            try:
                await algo.aclose()
            except Exception:
                pass

    # Function-style (backward-compatible)
    if callable(attr):
        out = attr(context)
        if asyncio.iscoroutine(out):
            out = await out
        return {"ok": True, "result": out}

    raise TypeError("executor attr must be a callable or BaseAlgorithm subclass")


async def exec_http(strategy: dict, context: Dict[str, Any]) -> Dict[str, Any]:
    if httpx is None:
        raise RuntimeError("httpx not installed. `pip install httpx`")
    url = strategy["executor"]["url"]
    method = strategy["executor"].get("method", "POST").upper()
    timeout = float(strategy["executor"].get("timeout_sec", 5))
    headers = strategy["executor"].get("headers") or {"Content-Type": "application/json"}
    payload = strategy["executor"].get("payload", context)

    async with httpx.AsyncClient(timeout=timeout) as client:
        if method == "GET":
            r = await client.get(url, headers=headers, params=payload)
        elif method == "POST":
            r = await client.post(url, headers=headers, json=payload)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        r.raise_for_status()
        try:
            data = r.json()
        except Exception:
            data = {"text": r.text}
    return {"ok": True, "status_code": r.status_code, "result": data}

async def strategy_loop(strategy: dict, stop_evt: asyncio.Event):
    sid = strategy["id"]
    interval = int(strategy["interval_sec"])
    logging.info(f"[{sid}] start interval={interval}s")
    while not stop_evt.is_set():
        start = time.time()
        try:
            context = {
                "strategy_id": sid,
                "now": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            }
            etype = strategy["executor"]["type"]
            if etype == "python":
                res = await exec_python(strategy, context, stop_evt)
            elif etype == "http":
                res = await exec_http(strategy, context)
            else:
                raise ValueError(f"unknown executor type: {etype}")
            logging.info(f"[{sid}] ok → {truncate(res, 240)}")
        except Exception as e:
            logging.error(f"[{sid}] ERROR: {e}", exc_info=False)
        # wait for next tick
        elapsed = time.time() - start
        remaining = max(0.0, interval - elapsed)
        await sleep_until(stop_evt, remaining)

def truncate(obj: Any, n: int) -> str:
    s = str(obj)
    return s if len(s) <= n else s[: n - 3] + "..."

async def sleep_until(stop_evt: asyncio.Event, seconds: float):
    end = time.time() + seconds
    while not stop_evt.is_set() and time.time() < end:
        await asyncio.sleep(min(0.25, end - time.time()))

class App:
    def __init__(self, cfg_path: str):
        self.cfg_path = cfg_path
        self.stop_evt = asyncio.Event()
        self.tasks = []

    def _install_signals(self):
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self.stop_evt.set)
            except NotImplementedError:
                pass  # e.g., Windows

    async def start(self):
        cfg = load_config(self.cfg_path)
        self._install_signals()
        for s in cfg["strategies"]:
            if not s.get("enabled", True):
                logging.info(f"[{s['id']}] disabled; skipping")
                continue
            self.tasks.append(asyncio.create_task(strategy_loop(s, self.stop_evt)))
        logging.info("Controller running. Ctrl+C to stop.")
        await self.stop_evt.wait()

    async def stop(self):
        logging.info("Stopping…")
        self.stop_evt.set()
        for t in self.tasks:
            t.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        logging.info("Stopped.")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python run_controller.py strategies.json")
        sys.exit(2)
    app = App(sys.argv[1])
    try:
        await app.start()
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
