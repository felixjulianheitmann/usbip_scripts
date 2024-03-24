from subprocess import run
import click
from rich import print
from time import sleep


def chunks(list_a, chunk_size):
    for i in range(0, len(list_a), chunk_size):
        if i + chunk_size - 1 > len(list_a):
            return
        yield list_a[i : i + chunk_size]


def parse_devices(list_output, exceptions):
    devices = {}
    if len(list_output) < 0:
        return devices

    exceptions = exceptions.split(";")
    for [id, name, _] in chunks(list_output.split("\n"), 3):
        skip = False
        for ex in exceptions:
            if ex in id:
                print(f"skipping '{id}'")
                skip = True
                break

        if skip:
            continue

        id_start = id.find("busid") + 6
        id_end = id.find("(") - 1
        id = id[id_start:id_end]

        devices[name.strip()] = id

    return devices


@click.command()
@click.argument("usbip_bin")
@click.argument("exceptions")
def main(usbip_bin, exceptions):
    while True:
        lister = run([usbip_bin, "list", "-l"], capture_output=True)
        devices = parse_devices(lister.stdout.decode(), exceptions)
        for name, device in devices.items():
            try:
                bind_task = run([usbip_bin, "bind", "-b", device])
                if bind_task.returncode == 0:
                    print(f"bound device {name} - {device}...")
            except Exception as e:
                pass

        sleep(3)


if __name__ == "__main__":
    main()
