import abc


class SerializedType:
    """ The base class for all binary codec types. """
    def __init__(self):
        self.bytes = bytearray()

    @abc.abstractmethod
    def from_parser(self, parser, length_hint=None):
        raise NotImplemented("SerializedType.from_parser not implemented.")

    @abc.abstractmethod
    def from_value(self, value):
        raise NotImplemented("SerializedType.from_value not implemented.")

    def to_bytes_sink(self, bytesink):
        """
        Write the bytes representation of a SerializedType to a bytearray.
        :param bytesink: The bytearray to write self.bytes to.
        """
        bytesink.append(self.bytes)

    def to_bytes(self):
        """
        Get the bytes representation of a SerializedType.
        """
        return self.bytes

    def to_json(self):
        """
        Return the JSON representation of a SerializedType.
        If not overridden, returns hex string representation of bytes.
        """
        return self.to_hex()

    def to_string(self):
        """
        Returns the hex string representation of self.bytes.
        """
        return self.to_hex()

    def to_hex(self):
        """
        Get the hex representation of a SerializedType's bytes.
        """
        return self.bytes.hex()

