import csv
import ipaddress

MAX_HOSTS = 65536


def parse_address(text):
    cleaned = text.strip()
    try:
        return ipaddress.IPv4Address(cleaned)
    except ValueError:
        raise ValueError(f"'{cleaned}' is not a valid IPv4 address") from None


def parse_cidr(text):
    try:
        network = ipaddress.IPv4Network(text, strict=False)
    except ValueError:
        raise ValueError(
            f"'{text}' is not a valid CIDR range (example: 192.168.0.0/24)"
        ) from None

    if network.num_addresses > MAX_HOSTS:
        raise ValueError(f"the range is too large (limit is {MAX_HOSTS} hosts)")

    return list(network.hosts()) or list(network)


def expand_range_end(start, end_text):
    if "." in end_text:
        return parse_address(end_text)
    prefix = str(start).rsplit(".", 1)[0]
    return parse_address(f"{prefix}.{end_text}")


def parse_range(text):
    start_text, end_text = text.split("-", 1)
    start = parse_address(start_text)
    end = expand_range_end(start, end_text.strip())

    if end < start:
        raise ValueError("the end of the range comes before its start")
    if int(end) - int(start) + 1 > MAX_HOSTS:
        raise ValueError(f"the range is too large (limit is {MAX_HOSTS} hosts)")

    return [ipaddress.IPv4Address(number) for number in range(int(start), int(end) + 1)]


def parse_target(text):
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("no IP range was provided")
    if "/" in cleaned:
        return parse_cidr(cleaned)
    if "-" in cleaned:
        return parse_range(cleaned)
    return [parse_address(cleaned)]


def table_headers(show_hostname):
    headers = ["IP", "STATUS"]
    if show_hostname:
        headers.append("HOSTNAME")
    return headers


def row_to_cells(row, show_hostname):
    cells = [str(row["ip"]), "up" if row["alive"] else "down"]
    if show_hostname:
        cells.append(row["hostname"] or "-")
    return cells


def join_cells(cells, widths):
    return "  ".join(cell.ljust(width) for cell, width in zip(cells, widths)).rstrip()


def format_table(rows, show_hostname):
    table = [table_headers(show_hostname)]
    table += [row_to_cells(row, show_hostname) for row in rows]
    widths = [max(len(cells[index]) for cells in table) for index in range(len(table[0]))]

    lines = [join_cells(table[0], widths), join_cells(["-" * width for width in widths], widths)]
    lines += [join_cells(cells, widths) for cells in table[1:]]
    return "\n".join(lines)


def format_live_line(result):
    line = f"[+] {str(result['ip']).ljust(15)}"
    if result["hostname"]:
        line += f"  {result['hostname']}"
    return line.rstrip()


def format_summary(total, alive, elapsed):
    return (
        f"Hosts tested : {total}\n"
        f"Hosts up     : {alive}\n"
        f"Elapsed time : {elapsed:.2f}s"
    )


def check_output_path(path):
    if not path.lower().endswith((".txt", ".csv")):
        raise ValueError("the output file must end with .txt or .csv")


def write_csv(path, rows, show_hostname):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(table_headers(show_hostname))
        for row in rows:
            writer.writerow(row_to_cells(row, show_hostname))


def write_text(path, rows, show_hostname):
    with open(path, "w", encoding="utf-8") as file:
        file.write(format_table(rows, show_hostname) + "\n")


def save_results(path, rows, show_hostname):
    if path.lower().endswith(".csv"):
        write_csv(path, rows, show_hostname)
    else:
        write_text(path, rows, show_hostname)
