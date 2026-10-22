import argparse
import sys
import time

from scanner import ping_available, sweep
from utils import (
    check_output_path,
    format_live_line,
    format_summary,
    format_table,
    parse_target,
    save_results,
)


BANNER = "EchoSweep by nyxaev"
WARNING = "Warning: only scan networks you own or have explicit permission to test."
MAX_THREADS = 1000


def positive_float(value):
    number = float(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return number


def thread_count(value):
    number = int(value)
    if not 1 <= number <= MAX_THREADS:
        raise argparse.ArgumentTypeError(f"must be between 1 and {MAX_THREADS}")
    return number


def build_parser():
    parser = argparse.ArgumentParser(
        prog="echosweep",
        description="Ping sweep tool that finds which hosts are up in an IP range.",
        epilog="EchoSweep by nyxaev",
    )
    parser.add_argument(
        "ip_range",
        nargs="?",
        help="CIDR (192.168.0.0/24) or range (192.168.0.1-192.168.0.50)",
    )
    parser.add_argument(
        "--timeout",
        type=positive_float,
        default=1.0,
        help="seconds to wait for each reply (default: 1)",
    )
    parser.add_argument(
        "--threads",
        type=thread_count,
        default=100,
        help=f"number of simultaneous pings, up to {MAX_THREADS} (default: 100)",
    )
    parser.add_argument(
        "--resolve",
        action="store_true",
        help="try to find the hostname of each active host",
    )
    parser.add_argument(
        "--show-down",
        action="store_true",
        help="include hosts that did not answer in the final table",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="save the results to a .txt or .csv file",
    )
    return parser


def ask_for_range():
    try:
        return input("IP range (CIDR or start-end): ").strip()
    except EOFError:
        return ""


def show_live(result):
    if result["alive"]:
        print(format_live_line(result), flush=True)


def save_output(path, rows, show_hostname):
    try:
        save_results(path, rows, show_hostname)
    except OSError as error:
        print(f"\nCould not save the results: {error}")
    else:
        print(f"\nResults saved to {path}")


def report(results, args, elapsed, interrupted):
    results.sort(key=lambda result: result["ip"])
    alive = [result for result in results if result["alive"]]
    rows = results if args.show_down else alive

    print()
    if interrupted:
        print("Scan interrupted, showing what was found so far.\n")
    if rows:
        print(format_table(rows, args.resolve))
    else:
        print("No active hosts found.")
    print()
    print(format_summary(len(results), len(alive), elapsed))

    if args.output:
        save_output(args.output, rows, args.resolve)


def run():
    args = build_parser().parse_args()

    print(BANNER)
    print(WARNING)
    print()

    if not ping_available():
        print("Error: the 'ping' command was not found on this system.")
        return 1

    ip_range = args.ip_range or ask_for_range()
    try:
        hosts = parse_target(ip_range)
        if args.output:
            check_output_path(args.output)
    except ValueError as error:
        print(f"Error: {error}")
        return 1

    threads = min(args.threads, len(hosts))
    print(f"Scanning {len(hosts)} host(s) with {threads} thread(s)...\n")

    started = time.perf_counter()
    results, interrupted = sweep(hosts, args.timeout, threads, args.resolve, show_live)
    elapsed = time.perf_counter() - started

    report(results, args, elapsed, interrupted)
    return 130 if interrupted else 0


def main():
    try:
        return run()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
