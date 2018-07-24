def bytes_to_array(b):
    hex_string = b.hex()
    decimal_array = []
    for c in range(0, len(hex_string), 2):
        c = (hex_string[c] + hex_string[c + 1])
        decimal_array.append(int(c,16))
    return decimal_array


def hex_to_bytes(hex_string):
    if hex_string is None:
        return ""
    return bytes([b for b in bytearray.fromhex(hex_string)])

def hex_to_array(hex_string):
    if hex_string is None:
        return ""
    return [b for b in bytearray.fromhex(hex_string)]