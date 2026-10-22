<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=26&duration=3000&pause=1000&color=3FB950&center=true&vCenter=true&width=640&height=60&lines=EchoSweep;Discover+live+hosts+in+seconds;Threaded+ping+sweep.+Pure+Python.;CIDR+or+range.+Windows%2C+Linux%2C+macOS." alt="EchoSweep - Discover live hosts in seconds">

**EchoSweep**

A small, fast ping sweep tool that finds which hosts are up in an IP range.

[Quick start](#quick-start) · [Arguments](#arguments) · [PyCharm](#running-in-pycharm) · [Tests](#running-the-tests)

</div>

---

## Features

- **Flexible input:** CIDR (`192.168.0.0/24`), full range (`192.168.0.1-192.168.0.50`), short range (`192.168.0.1-50`) or a single IP
- **Cross-platform:** builds the right `ping` command on Windows, Linux and macOS, with no extra console windows on Windows
- **Fast:** pings many hosts at once with a configurable thread pool
- **Live output:** active hosts show up the moment they answer
- **Hostnames:** optional reverse lookup with `--resolve`
- **Clean report:** table sorted by IP and a summary with hosts tested, hosts up and elapsed time
- **Export:** save results to `.txt` or `.csv`
- **Graceful stop:** Ctrl+C stops the threads and shows what was found so far
- **Zero dependencies:** standard library only

## Quick start

```bash
python main.py 192.168.0.0/24
```

Run it with no arguments and it asks for the range:

```bash
python main.py
```

## Example output

```text
$ python main.py 192.168.0.1-20 --resolve

EchoSweep by nyxaev
Warning: only scan networks you own or have explicit permission to test.

Scanning 20 host(s) with 20 thread(s)...

[+] 192.168.0.1    router.lan
[+] 192.168.0.5    nyxaev-desktop
[+] 192.168.0.12   living-room-tv
[+] 192.168.0.9

IP            STATUS  HOSTNAME
------------  ------  --------------
192.168.0.1   up      router.lan
192.168.0.5   up      nyxaev-desktop
192.168.0.9   up      -
192.168.0.12  up      living-room-tv

Hosts tested : 20
Hosts up     : 4
Elapsed time : 1.34s
```

## Examples

```bash
python main.py 192.168.0.0/24
python main.py 192.168.0.1-192.168.0.50
python main.py 192.168.0.1-50 --resolve
python main.py 10.0.0.0/24 --timeout 2 --threads 50
python main.py 192.168.0.0/24 --resolve --output results.csv
python main.py 192.168.0.0/28 --show-down --output results.txt
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| `ip_range` | CIDR or `start-end` range (asked interactively if empty) | - |
| `--timeout` | Seconds to wait for each reply | `1` |
| `--threads` | Number of simultaneous pings (1 to 1000) | `100` |
| `--resolve` | Try to find the hostname of active hosts | off |
| `--show-down` | Also list hosts that did not answer in the final table | off |
| `--output` | Save results to a `.txt` or `.csv` file | - |

## Running in PyCharm

<details>
<summary>Step by step</summary>

<br>

1. Open the `EchoSweep` folder in PyCharm (**File > Open**).
2. Go to **Run > Edit Configurations...** and click **+ > Python**.
3. Set **Name** to `EchoSweep` and **Script path** to `main.py`.
4. In **Parameters**, type the arguments, for example `192.168.0.0/24 --resolve --timeout 1`.
5. Make sure **Working directory** is the project root and click **OK**.
6. Press **Run**.

Leave **Parameters** empty to be asked for the IP range when the program starts.

If Ctrl+C does not stop the scan gracefully in the Run window, enable **Emulate terminal in output console** in the same configuration.

</details>

## Project structure

```text
EchoSweep/
├── main.py          arguments, flow and output
├── scanner.py       ping command, threads and hostname lookup
├── utils.py         IP parsing, formatting and export
├── tests/           unit tests
├── requirements.txt
└── README.md
```

## Running the tests

```bash
python -m unittest discover -s tests -t .
```

In PyCharm you can also right-click the `tests` folder and choose **Run 'Python tests in tests'**.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Scan finished |
| `1` | Invalid input or `ping` not available |
| `130` | Scan interrupted with Ctrl+C |

## Notes

- Some hosts block ping, so they may show up as down even when they are online.
- Ranges are limited to 65536 hosts.
- The ping timeout flag is in seconds on Linux and in milliseconds on Windows and macOS. EchoSweep handles this for you.

## Responsible use

Use EchoSweep only on networks you own or have explicit permission to test.

---

<div align="center">

Made by **nyxaev**

</div>
