from shapely.geometry import Polygon, Point


class Zone():
    # popdensity is population per acres
    # zone name will be numbered as TAZ's across the region
    # boundaries are defining lines in terms of coordinates for the zone
    # boundaries are most critical aspect
    # Boundaries will be a list of points shaping the zone
    # Example: boundaries = [(0, 0), (4, 4), (5, 0), (6, 8)]]
    def __init__(self, params) -> None:
        self.name = params[0]
        self.pop_density = params[1]
        self.employment = params[2]
        self.boundaries = params[3]
        self.zone = Polygon(self.boundaries)
        self.equity_indicator = 0
        self.accessibility_indicator = 0

    #compare with other zones to see initial equity measurements
    def __lt__(self, other):
        return self.employment < other.employment

    def getEmployment(self):
        return self.employment
    
    def getArea(self):
        return self.zone.area
    def isIn(self, coordx, coordy):
        location = Point((coordx, coordy))
        return self.zone.contains(location)


#sample TAZ creation
###zone1 = Zone("TAZ1", 2.5, 600, ((0, 0), (5, 0), (9, 4), (4, 4)))
###print(zone1.getArea())