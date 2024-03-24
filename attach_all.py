from subprocess import run
import click
from rich import print
from time import sleep


def parse_devices(list_output, exceptions):
    devices = {}
    if len(list_output) < 0:
        return devices

    # Drop header
    list_output = list_output.split("\n")[2:]

    exceptions = exceptions.split(";")

    for line in list_output:
        line = line.strip()

        if len(line) == 0 or line[:2] == "- " or line[0] == ":":
            continue

        # Skip exceptions
        skip = False
        for exception in exceptions:
            if exception in line:
                skip = True
                break
        if skip:
            print(f"skipping {line}")
            continue

        id_end = line.find(":")
        name_start = line[id_end:].find(":")
        id = line[:id_end]
        name = line[name_start:]

        devices[name.strip()] = id

    return devices


@click.command()
@click.argument("usbip_bin")
@click.argument("server")
@click.argument("exceptions")
def main(usbip_bin, server, exceptions):
    while True:
        lister = run([usbip_bin, "list", "-r", server], capture_output=True)
        devices = parse_devices(lister.stdout.decode(), exceptions)
        for name, device in devices.items():
            try:
                bind_task = run([usbip_bin, "attach", "-r", server, "-d", device])
                if bind_task.returncode == 0:
                    print(f"attaching to {name} - {device}...")
            except Exception as e:
                pass

        sleep(3)


if __name__ == "__main__":
    main()
