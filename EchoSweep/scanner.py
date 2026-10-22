import math
import platform
import shutil
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

SYSTEM = platform.system()


def ping_available():
    return shutil.which("ping") is not None


def build_ping_command(ip, timeout):
    if SYSTEM == "Windows":
        return ["ping", "-n", "1", "-w", str(int(timeout * 1000)), str(ip)]
    if SYSTEM == "Darwin":
        return ["ping", "-c", "1", "-W", str(int(timeout * 1000)), str(ip)]
    return ["ping", "-c", "1", "-W", str(max(1, math.ceil(timeout))), str(ip)]


def window_flags():
    if SYSTEM == "Windows":
        return getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return 0


def is_alive(ip, timeout):
    command = build_ping_command(ip, timeout)
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            errors="ignore",
            creationflags=window_flags(),
            timeout=timeout + 2,
        )
    except (subprocess.TimeoutExpired, OSError):
        return False

    if completed.returncode != 0:
        return False
    if SYSTEM == "Windows":
        return "TTL=" in completed.stdout.upper()
    return True


def lookup_hostname(ip):
    try:
        return socket.gethostbyaddr(str(ip))[0]
    except OSError:
        return None


def probe_host(ip, timeout, resolve):
    alive = is_alive(ip, timeout)
    hostname = lookup_hostname(ip) if alive and resolve else None
    return {"ip": ip, "alive": alive, "hostname": hostname}


def sweep(hosts, timeout, threads, resolve, on_result):
    results = []
    interrupted = False
    executor = ThreadPoolExecutor(max_workers=threads)
    futures = [executor.submit(probe_host, ip, timeout, resolve) for ip in hosts]

    try:
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            on_result(result)
    except KeyboardInterrupt:
        interrupted = True
        executor.shutdown(wait=False, cancel_futures=True)
    else:
        executor.shutdown()

    return results, interrupted
