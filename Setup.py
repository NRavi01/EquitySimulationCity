from Zone import Zone
from Grocery import Grocery
from Hospital import Hospital
from Street import Street
from Fire import Fire
from shapely.geometry import Polygon, Point
import geopandas
import operator
import random
import math


class Setup:
    zones = []
    grocery_stores = []
    hospitals = []
    streets = []
    fire_stores = []

    def __init__(self, TAZShapefile, HospitalShapefile, GroceryShapefile, StreetShapefile, FireShapefile) -> None:
        self.TAZShapes = TAZShapefile
        self.HospitalShapes = HospitalShapefile
        self.GroceryShapes = GroceryShapefile
        self.FireShapes = FireShapefile
        self.StreetShapes = StreetShapefile

    def run(self):
        self.process()
        self.calculateZoneMetrics()
        print("NEW HOSPITAL LOCATIONS AS FOLLOWS:")
        self.distributeHospitals(3)
        print("NEW GROCERY LOCATIONS AS FOLLOWS:")
        self.distributeGroceries(5)
        print("NOW DISTRIBUTING HOUSEHOLDS")
        self.distributeHouseholds(1000)

    def process(self):
        self.processTAZ(self.TAZShapes)
        self.processHospitals(self.HospitalShapes)
        self.processGrocery(self.GroceryShapes)
        # self.processStreet(self.StreetShapes)
        # self.processFire(self.FireShapes)

    def processTAZ(self, Shapefilezones):
        zone_data = []
        if Shapefilezones is None:
            zone_data = [["TAZ1", 4, 600, Polygon(((0, 0), (5, 0), (9, 4), (4, 4)))], [
                "TAZ2", 2, 400, Polygon(((0, 7), (5, 14), (9, 12), (4, 4)))]]
        else:
            for zone in Shapefilezones.iterrows():
                zone_data.append([zone[1].get("TAZ"), zone[1].get(
                    "POP_2018"), zone[1].get("EMPL_2018"), zone[1].get("geometry")])

        for zone in zone_data:
            self.zones.append(Zone(zone))

    def processHospitals(self, hospitalShapes):
        hospitalData = []
        if hospitalShapes is None:
            hospitalData = [[(4, 6), "Atrium Health"], [
                (8, 4), "Novant Health Center"]]
        else:
            for hospital in hospitalShapes.iterrows():
                hospitalData.append([(hospital[1].get("geometry").x, hospital[1].get(
                    "geometry").y), hospital[1].get("Type")])

        for hospital in hospitalData:
            self.hospitals.append(Hospital(hospital))

    def processGrocery(self, groceryShapes):
        groceryData = []
        if groceryShapes is None:
            groceryData = [[(3, 2), "Publix"], [(4, 12), "Whole Foods Market"]]
        else:
            for grocery_store in groceryShapes.iterrows():
                groceryData.append([(grocery_store[1].get("geometry").x, grocery_store[1].get(
                    "geometry").y), grocery_store[1].get("Type")])

        for grocery in groceryData:
            self.grocery_stores.append(Grocery(grocery))

    def processFire(self, fireShapes):
        fireData = []
        if fireShapes is None:
            fireData = [[(3, 2), "Fire1"], [(4, 12), "Fire"]]
        else:
            for fire_station in fireShapes.iterrows():
                fireData.append([(fireData[1].get("geometry").x, fireData[1].get(
                    "geometry").y), fireData[1].get("Type")])

        for fire in fireData:
            self.fire_stores.append(Fire(fire))

    # TODO: Add code to parse street shapefiles (streets are in a "LINESTRING Z" datastructure)
    def processStreet(self, streetsData):
        if streetsData is None:
            streetsData = [[(3, 2), (8, 11)], [
                (4, 12), (6, 8)], [(6, 6), (9, 4)]]
        print(type(streetsData))
        for street in streetsData:
            print(type(street))
            self.streets.append(Street(street))

    def calculateZoneMetrics(self):

        # TODO: Generic distance factor yet to be turned depending on how large the values for coordinates are
        distance_factor = 100

        hospital_weightage = 0.2
        grocery_weightage = 0.1
        fire_weightage = 0.1
        employment_weightage = 0.25
        population_weightage = 0.25
        size_weightage = 0.1

        for zone in self.zones:
            zonep = geopandas.GeoSeries(zone.getPolygon())
            distance_list = []
            total_distance = 0
            for hospital in self.hospitals:
                hospital_location = hospital.getLocation()
                center = zonep.centroid
                distance = math.sqrt(math.pow((hospital_location[0] - center.x), 2) +
                                     math.pow((hospital_location[1] - center.y), 2)) / distance_factor
                total_distance += distance
            hospital_metric = total_distance * hospital_weightage
            zone.setHospital(hospital_metric)

            distance_list.append(total_distance)

            total_distance = 0
            for grocery in self.grocery_stores:
                grocery_location = grocery.getLocation()
                center = zonep.centroid
                distance = math.sqrt(math.pow((grocery_location[0] - center.x), 2) +
                                     math.pow((grocery_location[1] - center.y), 2)) / distance_factor
                total_distance += distance
            grocery_metric = total_distance * grocery_weightage
            zone.setGrocery(grocery_metric)
            distance_list.append(total_distance)

            total_distance = 0
            for fire in self.fire_stores:
                fire_location = fire.getLocation()
                center = zonep.centroid
                distance = math.sqrt(math.pow((fire_location[0] - center.x), 2) +
                                     math.pow((fire_location[1] - center.y), 2)) / distance_factor
                total_distance += distance
            fire_metric = total_distance * fire_weightage
            zone.setFire(fire_metric)
            distance_list.append(total_distance)

            total_distance = 0
            zone_metric = distance_list[0] * hospital_weightage + distance_list[1] * grocery_weightage + \
                zone.getEmployment() * employment_weightage + zone.getPop() * population_weightage + \
                zone.getArea() * size_weightage + \
                distance_list[2] * fire_weightage
            zone.setEquity(zone_metric)

        # Zones now sorted by current equity measurement
        self.zones.sort()

    def add_random_point(self, polygon):
        xmin, ymin, xmax, ymax = polygon.bounds
        while True:
            x = random.uniform(xmin, xmax)
            y = random.uniform(ymin, ymax)

            if Point(x, y).within(polygon):
                # if this condition is true, add to a dataframe here

                return(x, y)

    def recalculateHospitalEquity(self):
        distance_factor = 100
        hospital_weightage = 0.2
        for zone in self.zones:
            zonep = geopandas.GeoSeries(zone.getPolygon())
            distance_list = []
            total_distance = 0
            for hospital in self.hospitals:
                hospital_location = hospital.getLocation()
                center = zonep.centroid
                distance = math.sqrt(math.pow((hospital_location[0] - center.x), 2) +
                                     math.pow((hospital_location[1] - center.y), 2)) / distance_factor
                total_distance += distance
            hospital_metric = total_distance * hospital_weightage
            zone.setHospital(hospital_metric)

    def recalculateGroceryEquity(self):
        distance_factor = 100
        grocery_weightage = 0.2
        for zone in self.zones:
            zonep = geopandas.GeoSeries(zone.getPolygon())
            distance_list = []
            total_distance = 0
            for grocery in self.grocery_stores:
                grocery_location = grocery.getLocation()
                center = zonep.centroid
                distance = math.sqrt(math.pow((grocery_location[0] - center.x), 2) +
                                     math.pow((grocery_location[1] - center.y), 2)) / distance_factor
                total_distance += distance
            grocery_metric = total_distance * grocery_weightage
            zone.setHospital(grocery_metric)

    # TODO: implement distributeHospitals
    def distributeHospitals(self, num_hospitals=5):
        hospital_sorted = sorted(
            self.zones, key=operator.attrgetter('hospital_access'), reverse=True)
        hospitals_left = num_hospitals
        zones_added = []
        while hospitals_left > 0:
            zone = hospital_sorted[0]
            if zone.getName() not in zones_added:
                zones_added.append(zone.getName())
                location = zone.getPolygon().centroid
                print("DONE")
                print("Zone in: " + str(zone.getName()))
                print("Coordinates are : " +
                      str(location.x) + " , " + str(location.y))
                print("DONE")
                self.hospitals.append(
                    Hospital(((location.x, location.x), "new Hospital")))
                self.recalculateHospitalEquity()

            else:
                i = 0
                next_zone = hospital_sorted[i]
                while (next_zone.getName() in zones_added):
                    i += 1
                    next_zone = hospital_sorted[i]
                zones_added.append(next_zone.getName())
                location = next_zone.getPolygon().centroid
                random = self.add_random_point(zone.getPolygon())
                print("DONE")
                print("Zone in: " + str(next_zone.getName()))
                print("Coordinates are : " +
                      str(location.x) + " , " + str(location.y))
                print("DONE")
                self.hospitals.append(
                    Hospital(((random[0], random[1]), "new Hospital")))
                self.recalculateHospitalEquity()
            hospital_sorted = sorted(
                self.zones, key=operator.attrgetter('hospital_access'), reverse=True)
            hospitals_left -= 1

    def distributeGroceries(self, num_groceries):
        groceries_sorted = sorted(
            self.zones, key=operator.attrgetter('grocery_access'), reverse=True)
        groceries_left = num_groceries
        zones_added = []
        while groceries_left > 0:
            zone = groceries_sorted[0]

            if zone.getName() not in zones_added:
                zones_added.append(zone.getName())
                location = zone.getPolygon().centroid
                print("DONE")
                print("Zone in: " + str(zone.getName()))
                print("Coordinates are : " +
                      str(location.x) + " , " + str(location.y))
                print("DONE")
                self.grocery_stores.append(
                    Grocery(((location.x, location.x), "new Grocery")))
                self.recalculateGroceryEquity()

            else:
                i = 0
                next_zone = groceries_sorted[i]
                while (next_zone.getName() in zones_added):
                    i += 1
                    next_zone = groceries_sorted[i]
                zones_added.append(next_zone.getName())
                location = next_zone.getPolygon().centroid
                random = self.add_random_point(zone.getPolygon())
                print("DONE")
                print("Zone in: " + str(next_zone.getName()))
                print("Coordinates are : " +
                      str(location.x) + " , " + str(location.y))
                print("DONE")
                self.grocery_stores.append(
                    Grocery(((location.x, location.x), "new Grocery")))
                self.recalculateGroceryEquity()
            groceries_sorted = sorted(
                self.zones, key=operator.attrgetter('grocery_access'), reverse=True)
            groceries_left -= 1

    def distributeFire(self, num_fire=1):
        fire_sorted = sorted(
            self.zones, key=operator.attrgetter('fire_access'))
        zone_to_add = fire_sorted[0]
        location = zone_to_add.centroid
        self.fire_stores.append(Fire((location, "New Fire")))
        return location

    def distributeHouseholds(self, num_households):
        # Max new household per zone
        max_household = 20
        list_zones = []
        households_left = num_households
        zone_sorted = sorted(
            self.zones, key=operator.attrgetter('equity_indicator'), reverse=True)
        for zone in zone_sorted:
            added = 0
            while added <= max_household and households_left > 0:
                zone.incrementHouse()
                list_zones.append(zone)
                households_left -= 1
            print("20 Households Recommended in Zone :" + str(zone.getName()))


zones = geopandas.read_file(
    "zip://./data/SE Data by TAZ.zip!SE Data by TAZ")
hospitals = geopandas.read_file(
    "zip://./data/Medical Facilities.zip!Medical Facilities")
grocery_stores = geopandas.read_file(
    "zip://./data/GroceryStores.zip!GroceryStores")
streets = geopandas.read_file("zip://./data/Streets.zip!Streets")
fire = geopandas.read_file("zip://./data/Fire_EMS.zip!Fire_EMS")
greenway = geopandas.read_file(
    "zip://./data/Greenways.zip!Greenways")

print(greenway.head)
# print(roadway.head)
s = Setup(zones, hospitals, grocery_stores, streets, fire)
# s.run()
