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
        self.boundaries = params[3]
        self.zone = Polygon(self.boundaries)
        self.equity_indicator = 0
        self.hospital_access = 0
        self.grocery_access = 0
        self.fire_access = 0
        self.accessibility_indicator = 0
        self.num_households = 0
        self.streetsThrough = []
        self.streetsLength = 0
        self.connectivity = 0

    # compare with other zones to see initial equity measurements
    def __lt__(self, other):
        return self.equity_indicator < other.equity_indicator

    def setStreetsThrough(self, routeName):
        self.streetsThrough.append(routeName)
        self.streetsLength += 1

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

    def addConnectivity(self, value1):
        self.connectivity += value1

    def setEquity(self, equity_value):
        self.equity_indicator = equity_value

    def setFire(self, equity_value):
        self.fire_access = equity_value
    def getName(self):
        return self.name

    def setGrocery(self, equity_value):
        self.grocery_access = equity_value

    def setHospital(self, equity_value):
        self.hospital_access = equity_value
    def getHospital(self):
        return self.hospital_access
    def getPolygon(self):
        return self.zone

# sample TAZ creation
###zone1 = Zone("TAZ1", 2.5, 600, ((0, 0), (5, 0), (9, 4), (4, 4)))
# print(zone1.getArea())
