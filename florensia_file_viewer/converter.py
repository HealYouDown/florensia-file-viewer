import struct
import re
from typing import List, Dict


def columntypes(t: int) -> int:
    if t in [0, 1, 2]:
        return 4
    elif t == 3:
        return 12
    elif t == 4:
        return 32
    elif t == 5:
        return 128
    else:
        return 0


def bin2list(fp) -> List[Dict]:
    """
    4 bytes: number_of_rows
    4 bytes: dataset_length
    4 bytes: number_of_columns
    number_of_columns *
        32 bytes: column_name
        4 bytes: column_length
    number_of_rows *
        4 bytes: trash
        column_length bytes: data
    4 bytes: trash
    """

    number_of_rows = struct.unpack("i", fp.read(4))[0]
    dataset_length = struct.unpack("i", fp.read(4))[0]  # noqa F841
    number_of_columns = struct.unpack("i", fp.read(4))[0]

    column_headers = []
    for _ in range(number_of_columns):
        byte_seq = fp.read(32)

        # Workaround for some malformed byte sequence (wtf AHA?)
        if byte_seq == (b"\xba\xb8\xbb\xf3\xbc"
                        b"\xf6\xb7\xae55\x00\x00"
                        b"\x01\x00\x00\x00(B\n\x08"
                        b"\x0f\x1b\x00\x80 \xff\xa9"
                        b"\x0b\xc8\xff\xa9\x0b"):
            cname = "보상수량55"
        else:
            cname = re.sub(b"\x00.*", b"", byte_seq).decode("euc_kr")

        length = columntypes(struct.unpack("i", fp.read(4))[0])
        column_headers.append({
            "name": cname.strip(),
            "length": length
        })

    rows = []
    for _ in range(number_of_rows):
        row = {}
        # trash
        _ = fp.read(4)

        for header in column_headers:
            byte_data = fp.read(header["length"])

            if header["length"] != 4:  # string
                try:
                    byte_seq = re.sub(b"\x00.*", b"", byte_data)
                    data = byte_seq.decode("euc_kr").strip()
                except UnicodeDecodeError:
                    try:
                        # Workaround for some bad strings in dress
                        byte_seq = re.sub(b"\x00.*",
                                            b"",
                                            byte_data[2:(len(byte_data)-1)])
                        data = byte_seq.decode("euc_kr").strip()
                    except UnicodeDecodeError:
                        # if this also fails, AHA messed up (happens a lot)
                        # so we just take the string and keep the errors
                        byte_seq = re.sub(b"\x00.*", b"", byte_data)
                        data = byte_seq.decode(
                            "euc_kr", errors="ignore").strip()

            else:  # number
                data = struct.unpack("L", byte_data)[0]

            row[header["name"]] = data

        rows.append(row)

    return rows


def dat2list(doc) -> List[Dict]:

    lines = doc.read().splitlines(True)

    headers = [h.strip() for h in lines[:1][0].split("\t")]
    data = lines[1:]

    datasets = []
    for line in data:
        row = []
        for d in line.strip().split("\t"):
            d = d.strip()
            if d != "__END":
                row.append(d)
        if row:
            # fix missing objects in line or some other sh*t AHA did
            while len(headers) != len(row):
                row.append("")

            datasets.append(row)

    rows_as_dict = []
    for row in datasets:
        row_as_dict = {}
        for index, data in enumerate(row):
            row_as_dict[headers[index]] = data

        rows_as_dict.append(row_as_dict)

    return rows_as_dict
