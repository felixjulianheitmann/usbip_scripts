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


def parse_verbose_lines(list_output, with_bus=False):
    devices = {}
    if len(list_output) < 0:
        return devices

        ids += id.group(0)
        if not with_bus:
            bus = re.search("[0-9]+-[0-9]+\.?[0-9]?", line)
            if bus is None:
                continue

        return ids

        devices[id.group(0)] = bus.group(0)

    return devices


async def loop(host, attach_mode, devices):

    usbip_proc_cmd = [
        "usbip",
        "attach" if attach_mode else "bind",
        "-r",
        host,
        "-b",
    ]

    usbip_list_done_cmd = [
        "usbip",
        "port" if attach_mode else "list",
        "-l",
    ]

    while True:
        available = parse_minimal_lines(call(usbip_list_available_cmd), devices)
        processed = parse_verbose_lines(call(usbip_list_done_cmd), with_bus=False)

        # check for devices to process that haven't been processed yet
        for dev in devices:
            if dev not in processed.values() and dev in available.values():
                print(f"processing {dev}...")
                run(usbip_proc_cmd + [available[dev]])

        asyncio.sleep(1)


@click.command()
@click.argument("host")
@click.option("attach_mode", default=False)
@click.option("devices_file", default="devices.txt")
def main(host, attach_mode, devices_file):
    with open(devices_file, "r") as f:
        devices = f.read()

    asyncio.run(loop(host, attach_mode, devices))
        # devices = parse_devices(lister.stdout.decode(), exceptions)
        # for name, device in devices.items():
        #     try:
        #         bind_task = run([usbip_bin, "attach", "-r", server, "-d", device])
        #         if bind_task.returncode == 0:
        #             print(f"attaching to {name} - {device}...")
        #     except Exception as e:
        #         pass

        # sleep(3)


if __name__ == "__main__":
    main()
