import csv
import ipaddress
import os
import tempfile
import unittest

from utils import (
    check_output_path,
    format_live_line,
    format_summary,
    format_table,
    parse_target,
    save_results,
)


def make_row(ip, alive=True, hostname=None):
    return {"ip": ipaddress.IPv4Address(ip), "alive": alive, "hostname": hostname}


class ParseTargetTests(unittest.TestCase):
    def test_cidr_returns_usable_hosts(self):
        hosts = parse_target("192.168.0.0/30")
        self.assertEqual([str(host) for host in hosts], ["192.168.0.1", "192.168.0.2"])

    def test_cidr_with_host_bits_is_accepted(self):
        hosts = parse_target("192.168.0.5/30")
        self.assertEqual([str(host) for host in hosts], ["192.168.0.5", "192.168.0.6"])

    def test_single_host_cidr(self):
        self.assertEqual([str(host) for host in parse_target("10.0.0.7/32")], ["10.0.0.7"])

    def test_full_range(self):
        hosts = parse_target("192.168.0.1-192.168.0.4")
        self.assertEqual(len(hosts), 4)
        self.assertEqual(str(hosts[-1]), "192.168.0.4")

    def test_short_range(self):
        hosts = parse_target("192.168.0.10-12")
        self.assertEqual([str(host) for host in hosts], ["192.168.0.10", "192.168.0.11", "192.168.0.12"])

    def test_single_address(self):
        self.assertEqual([str(host) for host in parse_target(" 8.8.8.8 ")], ["8.8.8.8"])

    def test_reversed_range_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_target("192.168.0.50-192.168.0.1")

    def test_invalid_inputs_are_rejected(self):
        for text in ["", "banana", "300.1.1.1", "192.168.0.0/33", "192.168.0.1-abc", "1.2.3.4-5.6.7"]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_target(text)

    def test_huge_ranges_are_rejected(self):
        for text in ["10.0.0.0/8", "10.0.0.0-10.255.255.255"]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_target(text)


class FormattingTests(unittest.TestCase):
    def test_table_without_hostname(self):
        table = format_table([make_row("192.168.0.1"), make_row("192.168.0.20", alive=False)], False)
        lines = table.splitlines()
        self.assertEqual(lines[0], "IP            STATUS")
        self.assertEqual(lines[2], "192.168.0.1   up")
        self.assertEqual(lines[3], "192.168.0.20  down")

    def test_table_with_hostname(self):
        table = format_table([make_row("192.168.0.1", hostname="router.lan"), make_row("192.168.0.2")], True)
        lines = table.splitlines()
        self.assertTrue(lines[0].endswith("HOSTNAME"))
        self.assertTrue(lines[2].endswith("router.lan"))
        self.assertTrue(lines[3].endswith("-"))

    def test_live_line(self):
        self.assertEqual(format_live_line(make_row("10.0.0.1")), "[+] 10.0.0.1")
        self.assertEqual(
            format_live_line(make_row("10.0.0.1", hostname="gateway")),
            "[+] 10.0.0.1         gateway",
        )

    def test_summary(self):
        summary = format_summary(254, 4, 2.5)
        self.assertIn("Hosts tested : 254", summary)
        self.assertIn("Hosts up     : 4", summary)
        self.assertIn("Elapsed time : 2.50s", summary)


class ExportTests(unittest.TestCase):
    def test_extension_check(self):
        check_output_path("results.csv")
        check_output_path("RESULTS.TXT")
        with self.assertRaises(ValueError):
            check_output_path("results.json")

    def test_csv_export(self):
        rows = [make_row("10.0.0.1", hostname="gateway"), make_row("10.0.0.2")]
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "out.csv")
            save_results(path, rows, True)
            with open(path, newline="", encoding="utf-8") as file:
                content = list(csv.reader(file))
        self.assertEqual(content[0], ["IP", "STATUS", "HOSTNAME"])
        self.assertEqual(content[1], ["10.0.0.1", "up", "gateway"])
        self.assertEqual(content[2], ["10.0.0.2", "up", "-"])

    def test_text_export(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "out.txt")
            save_results(path, [make_row("10.0.0.1")], False)
            with open(path, encoding="utf-8") as file:
                content = file.read()
        self.assertIn("10.0.0.1", content)
        self.assertTrue(content.startswith("IP"))


if __name__ == "__main__":
    unittest.main()
