import math
class Street():
    # Start and end of street
    # TODO: Update street to hold the LINESTRING Z datastructure rather than 2 coords
    def __init__(self, params) -> None:
        coord1 = params[0]
        self.coord1x = coord1[0]
        self.coord1y = coord1[1]
        self.length = 0

    def getLength(self):
        return self.length