from debin import debin
from dataclasses import dataclass, field
from debin.primitives.string import nullstr


@debin
class StringExample:
    first_name: nullstr
    last_name: nullstr
    full_name: nullstr = field(metadata={"calc": "first_name + ' ' + last_name"})


def main():
    buffer = bytearray([
        0x4A, 0x6F, 0x68, 0x6E, 0x00,  # first_name = "John"
        0x44, 0x6F, 0x65, 0x00,        # last_name = "Doe"
    ])

    example = StringExample().read(buffer)
    print(example)


if __name__ == "__main__":
    main()
