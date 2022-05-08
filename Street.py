import math
class Street():
    # Start and end of street
    # TODO: Update street to hold the LINESTRING Z datastructure rather than 2 coords
    def __init__(self, params) -> None:
        coord1 = params[0]
        coord2 = params[1]
        self.coord1x = coord1[0]
        self.coord1y = coord1[1]
        self.coord2x = coord2[0]
        self.coord2y = coord2[1]
        self.length = math.sqrt(math.pow((self.coord1x - self.coord2x),2) + math.pow((self.coord1y - self.coord2y),2))

    def getLength(self):
        return self.length