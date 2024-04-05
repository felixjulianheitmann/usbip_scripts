from subprocess import run
import click
from loguru import logger as log
import asyncio
import re

def call(cmd):
    out = run(cmd, capture_output=True).stdout.decode()
    log.debug(f"cmd {cmd}:\n{out}")
    return out


def get_ids(text):
    return re.findall("([0-9a-f]{4}:[0-9a-f]{4})", text)


def get_buses(text):
    return re.findall("[^\/]([0-9]+-[0-9]+(?>\.?[0-9])*)", text)


def get_ports(text):
    return re.findall("Port ([0-9]{2}):", text)


def list_local():
    output = call(["usbip", "list", "-p", "-l"])
    ids = get_ids(output)
    log.info(f"ids: {ids}")
    buses = get_buses(output)
    log.info(f"buses: {buses}")
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
    return run(["usbip", "attach", "-r", host, "-b", device]).returncode == 0


def bind(device):
    return run(["usbip", "bind", "-b", device]).returncode == 0


def process_device(device, host):
    if host != '':
        success = attach(host, device)
    else:
        success = bind(device)

    if success:
        log.info(f"Successfully processed [{device}]!")


def process_devices(devices, host):
    if host != '':
        available = list_remote(host)
        processed = list_attached()
    else:
        available = list_local()
        processed = list_exported()

    log.info(f"Available: {available}")
    log.info(f"Processed: {processed}")
    for dev in devices:
        if dev in available.keys() and dev not in processed.keys():
            process_device(available[dev], host)


async def loop(devices, host):
    log.info(f"Starting loop, binding following devices if available: {devices}")

    while True:
        process_devices(devices, host)

        await asyncio.sleep(1)


@click.command()
@click.argument("devices_file", default="devices.txt")
@click.argument("log_file", default="log.txt")
@click.argument("host", default='')
def main(devices_file, log_file, host):
    print("Creating log at: ", log_file)
    log.add(log_file, rotation="10 kB", retention="10 days")

    with open(devices_file, "r") as f:
        devices = f.read().splitlines()

    try:
        asyncio.run(loop(devices, host))
    except:
        log.info("Stopping service")


if __name__ == "__main__":
    main()
