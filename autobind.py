from subprocess import run
import click
from loguru import logger as log
import asyncio
import re
from pathlib import Path

def call(cmd):
    return run(cmd, capture_output=True).stdout.decode()


def get_ids(text):
    return re.findall("([0-9a-f]{4}:[0-9a-f]{4})", text)


def get_buses(text):
    # TODO: Figure out how to exclude matches with leading/trailing slash
    
    return re.findall("([0-9]+-[0-9]+\.?[0-9]?)", text)


def get_ports(text):
    return re.findall("Port ([0-9]{2}):", text)


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
    if run(["usbip", "bind", "-b", device]).returncode == 0:
        return True
    else:
        return False


def process_device(device, host):
    if host is not None:
        success = bind(device)
    else:
        success = attach(host, device)

    if success:
        log.info(f"Successfully processed [{device}]!")


def process_devices(devices, host):
    if host is not None:
        available = list_remote(host)
        processed = list_attached()
    else:
        available = list_local()
        processed = list_exported()

    for dev in devices:
        if dev in available.keys() and dev not in processed.keys():
            process_device(available[dev], host)


async def loop(devices, host):
    log.info("Starting loop, binding following devices if available: ", devices)

    while True:
        process_devices(devices, host)

        await asyncio.sleep(1)


@click.command()
@click.argument("devices_file", default="devices.txt")
@click.argument("log_file", default="log.txt")
@click.option("host", default=None)
def main(devices_file, log_file, host):
    print("Creating log at: ", log_file)
    log.add(log_file, rotation="10 kB", retention="10 days")

    with open(devices_file, "r") as f:
        devices = f.read().splitlines()

    asyncio.run(loop(devices, host))

    log.info("Stopping autobind service")


if __name__ == "__main__":
    main()
