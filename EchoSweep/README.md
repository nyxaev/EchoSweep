# EchoSweep

EchoSweep by nyxaev

EchoSweep is a small ping sweep tool. It checks which hosts are up in an IP range by pinging them in parallel, then prints a table sorted by IP with a short summary.

Use it only on networks you own or have explicit permission to test.

## Features

- Accepts CIDR notation (`192.168.0.0/24`), a full range (`192.168.0.1-192.168.0.50`) or a short range (`192.168.0.1-50`)
- Also accepts a single IP address
- Works on Windows, Linux and macOS, building the right `ping` command for each one
- No extra console windows on Windows
- Pings many hosts at once with a configurable number of threads
- Shows active hosts in real time while the scan runs
- Optional hostname lookup
- Final table sorted by IP, plus total tested, total up and elapsed time
- Export to `.txt` or `.csv`
- Stops cleanly on Ctrl+C and shows what was found so far
- Friendly error messages for invalid input
- Standard library only

## Requirements

- Python 3.9 or newer
- The `ping` command available on the system (it is included by default on Windows, macOS and most Linux distributions)

## Project structure

```
EchoSweep/
├── main.py            arguments, flow and output
├── scanner.py         ping command, threads and hostname lookup
├── utils.py           IP parsing, formatting and export
├── tests/             unit tests
├── requirements.txt
└── README.md
```

## How to run

```
python main.py 192.168.0.0/24
```

Without arguments, the program asks for the IP range:

```
python main.py
```

## Examples

```
python main.py 192.168.0.0/24
python main.py 192.168.0.1-192.168.0.50
python main.py 192.168.0.1-50 --resolve
python main.py 10.0.0.0/24 --timeout 2 --threads 50
python main.py 192.168.0.0/24 --resolve --output results.csv
python main.py 192.168.0.0/28 --show-down --output results.txt
python main.py --help
```

## Arguments

| Argument      | Description                                              | Default |
|---------------|----------------------------------------------------------|---------|
| `ip_range`    | CIDR or `start-end` range (asked interactively if empty) | -       |
| `--timeout`   | Seconds to wait for each reply                           | 1       |
| `--threads`   | Number of simultaneous pings (1 to 1000)                 | 100     |
| `--resolve`   | Try to find the hostname of active hosts                 | off     |
| `--show-down` | Also list hosts that did not answer in the final table   | off     |
| `--output`    | Save results to a `.txt` or `.csv` file                  | -       |

## Running in PyCharm

1. Open the `EchoSweep` folder in PyCharm (**File > Open**).
2. Go to **Run > Edit Configurations...** and click **+ > Python**.
3. Set **Name** to `EchoSweep` and **Script path** to `main.py`.
4. In **Parameters**, type the arguments, for example:
   `192.168.0.0/24 --resolve --timeout 1`
5. Make sure **Working directory** is the project root and click **OK**.
6. Press **Run**.

Leave **Parameters** empty to be asked for the IP range when the program starts.

If Ctrl+C does not stop the scan gracefully in the Run window, enable **Emulate terminal in output console** in the same configuration.

## Running the tests

From the project root:

```
python -m unittest discover -s tests -t .
```

In PyCharm you can also right-click the `tests` folder and choose **Run 'Python tests in tests'**.

## Exit codes

| Code | Meaning                                  |
|------|------------------------------------------|
| 0    | Scan finished                            |
| 1    | Invalid input or `ping` not available    |
| 130  | Scan interrupted with Ctrl+C             |

## Notes

- Some hosts block ping, so they may appear as down even when they are online.
- Ranges are limited to 65536 hosts.
- The ping timeout flag is in seconds on Linux and in milliseconds on Windows and macOS. EchoSweep handles this for you.

## Credits

Created by nyxaev.
