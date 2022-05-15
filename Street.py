import math


class Street():
    # Start and end of street
    # TODO: Update street to hold the LINESTRING Z datastructure rather than 2 coords
    def __init__(self, params) -> None:
        self.id = params[0]
        self.suffix = params[1]
        self.name = params[2]
        self.linestring = params[3]
        self.length = params[3].length
        self.numZones = 0
        self.sampleZone = ''

    def getLength(self):
        return self.length

    def addZone(self):
        self.numZones += 1

    def addSampleZone(self, string):
        self.sampleZone = string

    def getSample(self):
        return self.sampleZone
    def getName(self):
        return self.name

    def getLinestring(self):
        return self.linestring

    def getCoords(self):
        return list(self.linestring.coords)
