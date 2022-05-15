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
        self.distributeGroceries(3)
        print("NOW DISTRIBUTING HOUSEHOLDS")
        self.distributeHouseholds(8600)
        print("NOW DISTRIBUTING FIRE STATION")
        self.distributeFire(1)
        self.calculateStreetsAcross()
        self.calculateSuggestedStreets()

    def process(self):
        self.processTAZ(self.TAZShapes)
        self.processHospitals(self.HospitalShapes)
        self.processGrocery(self.GroceryShapes)
        self.processStreet(self.StreetShapes)
        self.processFire(self.FireShapes)

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
                fireData.append([(fire_station[1].get("geometry").x, fire_station[1].get(
                    "geometry").y), fire_station[1].get("Type")])

        for fire in fireData:
            self.fire_stores.append(Fire(fire))

    # TODO: Add code to parse street shapefiles (streets are in a "LINESTRING Z" datastructure)
    def processStreet(self, streetsData):
        if streetsData is None:
            streetsData = [[(3, 2), (8, 11)], [
                (4, 12), (6, 8)], [(6, 6), (9, 4)]]
        for street in streetsData.values:
            self.streets.append(Street(street))

    def calculateStreetsAcross(self):
        for street in self.streets:
            linestring = street.getLinestring()
            for zone in self.zones:
                # Add street to zone's through parameter if it passes through that zones
                if zone.getPolygon().intersects(linestring):
                    zone.setStreetsThrough(street)
                    street.addZone()
                    street.addSampleZone(zone.getName())

    def calculateSuggestedStreets(self):
        street_sorted = sorted(
            self.zones, key=operator.attrgetter('streetsLength'))
        for zone in street_sorted:

            if(zone.streetsLength == 0):
                zone.addConnectivity(0)
            else:
                for street in zone.streetsThrough:
                    zone.addConnectivity(street.numZones)
        # Now calculate where roads from each zone should go. Try to connect zones to other zones which are not currently connected

        print("CURRENT ZONE CONNECTIVITY THROUGH ROADS BELOW")
        for zone in self.zones:
            routes = ''
            for street in zone.streetsThrough:
                routes += (str(street.getName()) + ' and ')
            if routes == '':
                routes = 'no major routes and '

            print("ZONE " + str(zone.getName()) + " contains " + routes +
                  "has an initial connectivity of " + str(zone.connectivity))
            # Calculate which streets are not included all we need to do is link this zone with one zone in the path of these streets
            suggestion = ''
            for street in self.streets:
                if street not in zone.streetsThrough:
                    suggestion += ('We suggest connecting Zone ' + str(zone.getName()) + ' with Route ' +
                                   str(street.getName(
                                   )) + ' by adding a roadway from this zone to zone ' + str(street.getSample()) + '. ')

                    zone.addConnectivity(street.numZones * .5)
            if suggestion == '':
                suggestion = 'Zone ' + \
                    str(zone.getName()) + \
                    ' has good connectivity no immediate roadways necessary'
            print(suggestion)
            print("ZONE " + str(zone.getName()) +
                  " new connectivity with these roadways is now " + str(zone.connectivity))

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

    def recalculateFireEquity(self):
        distance_factor = 100
        fire_weightage = 0.2
        for zone in self.zones:
            zonep = geopandas.GeoSeries(zone.getPolygon())
            distance_list = []
            total_distance = 0
            for fire in self.fire_stores:
                fire_location = fire.getLocation()
                center = zonep.centroid
                distance = math.sqrt(math.pow((fire_location[0] - center.x), 2) +
                                     math.pow((fire_location[1] - center.y), 2)) / distance_factor
                total_distance += distance
            fire_metric = total_distance * fire_weightage
            zone.setFire(fire_metric)

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
            zone.setGrocery(grocery_metric)

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
                print("Zone in: " + str(zone.getName()) +
                      " which had previous hospital equity index of " + str(zone.hospital_access))
                print("Coordinates are : " +
                      str(location.x) + " , " + str(location.y))
                self.hospitals.append(
                    Hospital(((location.x, location.x), "new Hospital")))
                self.recalculateHospitalEquity()
                print("Zone " + str(zone.getName()) +
                      " now has hospital equity index of " + str(zone.hospital_access))

            else:
                i = 0
                next_zone = hospital_sorted[i]
                while (next_zone.getName() in zones_added):
                    i += 1
                    next_zone = hospital_sorted[i]
                zones_added.append(next_zone.getName())
                location = next_zone.getPolygon().centroid
                random = self.add_random_point(zone.getPolygon())
                print("Zone in: " + str(next_zone.getName()) +
                      " which had previous hospital equity index of " + str(zone.hospital_access))
                print("Coordinates are : " +
                      str(location.x) + " , " + str(location.y))
                self.hospitals.append(
                    Hospital(((random[0], random[1]), "new Hospital")))
                self.recalculateHospitalEquity()
                print("Zone " + str(zone.getName()) +
                      " now has hospital equity index of " + str(zone.hospital_access))
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
                print("Zone in: " + str(zone.getName()) +
                      " which had previous grocery equity index of " + str(zone.grocery_access))
                print("Coordinates are : " +
                      str(location.x) + " , " + str(location.y))
                self.grocery_stores.append(
                    Grocery(((location.x, location.x), "new Grocery")))
                self.recalculateGroceryEquity()
                print("Zone " + str(zone.getName()) +
                      " now has grocery equity index of " + str(zone.grocery_access))

            else:
                i = 0
                next_zone = groceries_sorted[i]
                while (next_zone.getName() in zones_added):
                    i += 1
                    next_zone = groceries_sorted[i]
                zones_added.append(next_zone.getName())
                location = next_zone.getPolygon().centroid
                random = self.add_random_point(zone.getPolygon())
                print("Zone in: " + str(next_zone.getName()) +
                      " which had previous grocery equity index of " + str(zone.grocery_access))
                print("Coordinates are : " +
                      str(location.x) + " , " + str(location.y))
                self.grocery_stores.append(
                    Grocery(((location.x, location.x), "new Grocery")))
                self.recalculateGroceryEquity()
                print("Zone " + str(zone.getName()) +
                      " now has grocery equity index of " + str(zone.grocery_access))
            groceries_sorted = sorted(
                self.zones, key=operator.attrgetter('grocery_access'), reverse=True)
            groceries_left -= 1

    def distributeFire(self, num_fire=1):
        fire_sorted = sorted(
            self.zones, key=operator.attrgetter('fire_access'))
        zone_to_add = fire_sorted[0]
        location = zone_to_add.getPolygon().centroid
        self.fire_stores.append(
            Fire(((location.x, location.y), "New Fire")))
        print("Zone in: " + str(zone_to_add.getName()) +
              " which had previous fire equity index of " + str(zone_to_add.fire_access))
        print("Coordinates are : " + str(location.x) + " , " + str(location.y))
        self.recalculateFireEquity()
        print("Zone " + str(zone_to_add.getName()) +
              " now has fire equity index of " + str(zone_to_add.fire_access))
        return location

    def distributeHouseholds(self, num_households):
        # Max new household per zone

        households_left = num_households
        total_equity = 0
        for zone in self.zones:
            total_equity += zone.equity_indicator
        zone_sorted = sorted(
            self.zones, key=operator.attrgetter('equity_indicator'), reverse=True)
        print(total_equity)
        for zone in zone_sorted:
            fraction = zone.equity_indicator / total_equity
            num_adding = round(fraction * num_households)
            while num_adding > 0 and households_left > 0:
                zone.incrementHouse()
                households_left -= 1
                num_adding -= 1
            print(str(round(fraction * num_households)) +
                  " Households Recommended in Zone " + str(zone.getName()) + " which has equity index of " + str(zone.equity_indicator))

        print(len(self.zones))


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

# print(roadway.head)
s = Setup(zones, hospitals, grocery_stores, streets, fire)
s.run()
