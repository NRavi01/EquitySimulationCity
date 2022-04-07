import math
class Hospital():
    #Location of hospital
    #Type of hospital: Health provider
    def __init__(self, params) -> None:
        coord1 = params[0]
        type = params[1]
        self.coord1x = coord1[0]
        self.coord1y = coord1[1]
        self.type = type

    def getLocation(self):
        return (self.coord1x, self.coord1y)