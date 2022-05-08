from Zone import Zone
from Grocery import Grocery
from Hospital import Hospital
from Street import Street
from shapely.geometry import Polygon, Point
import geopandas

class Setup():
    zones = []
    grocery_stores = []
    hospitals = []
    streets = []
    def __init__(self, TAZShapefile, HospitalShapefile, GroceryShapefile, StreetShapefile) -> None:
        self.TAZShapes = TAZShapefile
        self.HospitalShapes = HospitalShapefile
        self.GroceryShapes = GroceryShapefile
        self.StreetShapes = StreetShapefile

    def run(self):
        self.process()
        self.calculateZoneMetrics()
        self.distributeHospitals(3)

    def process(self):
        self.processTAZ(self.TAZShapes)
        self.processHospitals(self.HospitalShapes)
        self.processGrocery(self.GroceryShapes)
        self.processStreet(self.StreetShapes)


    def processTAZ(self, Shapefilezones):
        zone_data = []
        if Shapefilezones is None:
            zone_data = [["TAZ1", 4, 600, Polygon(((0, 0), (5, 0), (9, 4), (4, 4)))], ["TAZ2", 2, 400, Polygon(((0, 7), (5, 14), (9, 12), (4, 4)))]]
        else:
            for zone in Shapefilezones.iterrows():
                zone_data.append([zone[1].get("TAZ"), zone[1].get("POP_2018"), zone[1].get("EMPL_2018"), zone[1].get("geometry")])

        for zone in zone_data:
            self.zones.append(Zone(zone))

    def processHospitals(self, hospitalShapes):
        hospitalData = []
        if hospitalShapes is None:
            hospitalData = [[(4, 6), "Atrium Health"], [(8, 4), "Novant Health Center"]]
        else:
            for hospital in hospitalShapes.iterrows():
                hospitalData.append([(hospital[1].get("geometry").x, hospital[1].get("geometry").y), hospital[1].get("Type")])
        
        for hospital in hospitalData:
            self.hospitals.append(Hospital(hospital))

    def processGrocery(self, groceryShapes):
        groceryData = []
        if groceryShapes is None:
            groceryData = [[(3, 2), "Publix"], [(4, 12), "Whole Foods Market"]]
        else:
            for grocery_store in groceryShapes.iterrows():
                groceryData.append([(grocery_store[1].get("geometry").x, grocery_store[1].get("geometry").y), grocery_store[1].get("Type")])

        for grocery in groceryData:
            self.grocery_stores.append(Grocery(grocery))
        
    # TODO: Add code to parse street shapefiles (streets are in a "LINESTRING Z" datastructure)
    def processStreet(self, streetsData):
        if streetsData is None:
            streetsData = [[(3, 2), (8, 11)], [(4, 12), (6, 8)], [(6, 6), (9, 4)]]

        for street in streetsData:
            self.streets.append(Street(street))
    
    def calculateZoneMetrics(self):
        
        # TODO: Generic distance factor yet to be turned depending on how large the values for coordinates are
        distance_factor = 100

        hospital_weightage = 0.2
        grocery_weightage = 0.1
        # TODO: Fire not implemented yet
        fire_weightage = 0.1
        employment_weightage = 0.25
        population_weightage = 0.25
        size_weightage = 0.1

        for zone in self.zones:
            zonep = geopandas.GeoSeries(zone.getPolygon())
            distance_list = []
            total_distance = 0
            for hospital in self.hospitals:
                hospital_location = geopandas.GeoSeries([Point(hospital.getLocation())])
                distance = zonep.distance(hospital_location)[0] / distance_factor
                total_distance += distance
            distance_list.append(total_distance)
            total_distance = 0

            for grocery in self.grocery_stores:
                grocery_location = geopandas.GeoSeries([Point(grocery.getLocation())])
                distance = zonep.distance(grocery_location)[0] / distance_factor
                total_distance += distance
            distance_list.append(total_distance)
            total_distance = 0

            zone_metric = distance_list[0] * hospital_weightage + distance_list[1] * grocery_weightage + \
                zone.getEmployment() * employment_weightage + zone.getPop() * population_weightage + \
                    zone.getArea() * size_weightage
            zone.setEquity(zone_metric)
        
        # Zones now sorted by current equity measurement
        self.zones.sort()


    # TODO: implement distributeHospitals
    def distributeHospitals(self, num_hospitals):
        return True

    # TODO: implement distributeGroceries
    def distributeGroceries(self, num_groceries):
        pass

    
    def distributeHouseholds(self, num_households):
        # Max new household per zone
        max_household = 20

        households_left = num_households
        zone_sorted = self.zones.sort()
        for zone in zone_sorted:
            added = 0
            while added <= max_household and households_left > 0:
                zone.incrementHouse()
                households_left -= 1