import socket
import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import scanner


def fake_reply(returncode, output=""):
    return SimpleNamespace(returncode=returncode, stdout=output)


class BuildCommandTests(unittest.TestCase):
    def test_windows_command(self):
        with patch.object(scanner, "SYSTEM", "Windows"):
            command = scanner.build_ping_command("10.0.0.1", 1.5)
        self.assertEqual(command, ["ping", "-n", "1", "-w", "1500", "10.0.0.1"])

    def test_linux_command_rounds_timeout_up(self):
        with patch.object(scanner, "SYSTEM", "Linux"):
            command = scanner.build_ping_command("10.0.0.1", 1.2)
        self.assertEqual(command, ["ping", "-c", "1", "-W", "2", "10.0.0.1"])

    def test_linux_command_never_uses_zero_timeout(self):
        with patch.object(scanner, "SYSTEM", "Linux"):
            command = scanner.build_ping_command("10.0.0.1", 0.1)
        self.assertEqual(command[4], "1")

    def test_macos_command_uses_milliseconds(self):
        with patch.object(scanner, "SYSTEM", "Darwin"):
            command = scanner.build_ping_command("10.0.0.1", 2)
        self.assertEqual(command, ["ping", "-c", "1", "-W", "2000", "10.0.0.1"])


class IsAliveTests(unittest.TestCase):
    def test_linux_success(self):
        with patch.object(scanner, "SYSTEM", "Linux"):
            with patch("scanner.subprocess.run", return_value=fake_reply(0)):
                self.assertTrue(scanner.is_alive("10.0.0.1", 1))

    def test_linux_failure(self):
        with patch.object(scanner, "SYSTEM", "Linux"):
            with patch("scanner.subprocess.run", return_value=fake_reply(1)):
                self.assertFalse(scanner.is_alive("10.0.0.1", 1))

    def test_windows_needs_ttl_in_output(self):
        replied = fake_reply(0, "Reply from 10.0.0.1: bytes=32 time=1ms TTL=64")
        unreachable = fake_reply(0, "Reply from 10.0.0.9: Destination host unreachable.")
        with patch.object(scanner, "SYSTEM", "Windows"):
            with patch("scanner.subprocess.run", return_value=replied):
                self.assertTrue(scanner.is_alive("10.0.0.1", 1))
            with patch("scanner.subprocess.run", return_value=unreachable):
                self.assertFalse(scanner.is_alive("10.0.0.2", 1))

    def test_timeout_means_down(self):
        error = subprocess.TimeoutExpired("ping", 3)
        with patch("scanner.subprocess.run", side_effect=error):
            self.assertFalse(scanner.is_alive("10.0.0.1", 1))


class HostnameTests(unittest.TestCase):
    def test_returns_name(self):
        with patch("scanner.socket.gethostbyaddr", return_value=("router.lan", [], [])):
            self.assertEqual(scanner.lookup_hostname("10.0.0.1"), "router.lan")

    def test_returns_none_when_lookup_fails(self):
        with patch("scanner.socket.gethostbyaddr", side_effect=socket.herror):
            self.assertIsNone(scanner.lookup_hostname("10.0.0.1"))


class ProbeAndSweepTests(unittest.TestCase):
    def test_hostname_only_looked_up_for_active_hosts(self):
        with patch("scanner.is_alive", return_value=False):
            with patch("scanner.lookup_hostname") as lookup:
                result = scanner.probe_host("10.0.0.1", 1, True)
        lookup.assert_not_called()
        self.assertFalse(result["alive"])
        self.assertIsNone(result["hostname"])

    def test_sweep_reports_every_host(self):
        def fake_probe(ip, timeout, resolve):
            return {"ip": ip, "alive": str(ip).endswith("1"), "hostname": None}

        seen = []
        hosts = ["10.0.0.1", "10.0.0.2", "10.0.0.11"]
        with patch("scanner.probe_host", side_effect=fake_probe):
            results, interrupted = scanner.sweep(hosts, 1, 2, False, seen.append)
        self.assertFalse(interrupted)
        self.assertEqual(len(results), 3)
        self.assertEqual(len(seen), 3)

    def test_sweep_stops_on_keyboard_interrupt(self):
        def stop_now(result):
            raise KeyboardInterrupt

        with patch("scanner.probe_host", return_value={"ip": "10.0.0.1", "alive": True, "hostname": None}):
            results, interrupted = scanner.sweep(["10.0.0.1", "10.0.0.2"], 1, 1, False, stop_now)
        self.assertTrue(interrupted)
        self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
