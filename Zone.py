from shapely.geometry import Polygon, Point
import geopandas

class Zone():
    # popdensity is population per acres
    # zone name will be numbered as TAZ's across the region
    # boundaries are defining lines in terms of coordinates for the zone
    # boundaries are most critical aspect
    # Boundaries will be a list of points shaping the zone
    # Example: boundaries = [(0, 0), (4, 4), (5, 0), (6, 8)]]
    # Boundaries will be represented as a Polygon and passed in as params[3]
    def __init__(self, params) -> None:
        self.name = params[0]
        self.pop_density = params[1]
        self.employment = params[2]
        self.zone = params[3]
        self.equity_indicator = 0
        self.accessibility_indicator = 0
        self.num_households = 0

    #compare with other zones to see initial equity measurements
    def __lt__(self, other):
        return self.equity_indicator < other.equity_indicator

    def getEmployment(self):
        return self.employment
    def getPop(self):
        return self.pop_density
    def incrementHouse(self):
        self.num_households += 1
    def getArea(self):
        return self.zone.area
    def isIn(self, coordx, coordy):
        location = Point((coordx, coordy))
        return self.zone.contains(location)
    def getPolygon(self):
        return self.zone
    def setEquity(self, equity_value):
        self.equity_indicator = equity_value


#sample TAZ creation
###zone1 = Zone("TAZ1", 2.5, 600, ((0, 0), (5, 0), (9, 4), (4, 4)))
###print(zone1.getArea())