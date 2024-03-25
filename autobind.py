from subprocess import run
import click
from rich import print
from time import sleep
import asyncio
import re


def call(cmd):
    return run(cmd, capture_output=True).stdout.decode()


def do_regex(text, regex):
    result = re.search(regex, text)
    return [x for x in result.groups()]


def get_ids(text):
    return do_regex("[0-9a-f]{4}:[0-9a-f]{4}", text)


def get_buses(text):
    return do_regex("([0-9]+-[0-9]+\.?[0-9]?):", text)


def get_ports(text):
    return do_regex("Port ([0-9]{2}):", text)


def list_local():
    output = call(["usbip", "list", "-p", "-l"])
    ids = get_ids(output)
    buses = get_buses(output)
    return dict(zip(ids, buses))


def list_remote(host):
    output = call(["usbip", "list", "-r", host, "-p", "-l"])
    ids = get_ids(output)
    buses = get_buses(output)
    return dict(zip(ids, buses))


def list_attached():
    output = call(["usbip", "port", "-l"])
    ids = get_ids(output)
    ports = get_ports(output)
    return dict(zip(ids, ports))


def list_exported():
    return list_remote("localhost")


def attach(host, device):
    run(["usbip", "attach", "-r", host, "-b", device])


def bind(device):
    run(["usbip", "bind", "-b", device])


async def loop(devices):

    while True:
        available = parse_minimal_lines(call(usbip_list_available_cmd), devices)
        processed = parse_verbose_lines(call(usbip_list_done_cmd), with_bus=False)

        asyncio.sleep(1)


@click.command()
@click.option("devices_file", default="devices.txt")
def main(host, attach_mode, devices_file):
    with open(devices_file, "r") as f:
        devices = f.read()

    asyncio.run(loop(host, devices))


if __name__ == "__main__":
    main()
