from Zone import Zone
from Grocery import Grocery
from Hospital import Hospital
from Street import Street
class Setup():
    zones = []
    grocery_stores = []
    hospitals = []
    streets = []
    def __init__(self, TAZShapefile, HospitalShapefile, GroceryShapefile, StreetShapefile) -> None:
        print("hello")
        self.TAZShapes = TAZShapefile
        self.HospitalShapes = HospitalShapefile
        self.GroceryShapes = GroceryShapefile
        self.StreetShapes = StreetShapefile

    def run(self):
        self.process()
        self.calculateZoneMetrics()

    def process(self):
        self.processTAZ(self.TAZShapes)
        self.processHospitals(self.HospitalShapes)
        self.processGrocery(self.GroceryShapes)
        self.processStreet(self.StreetShapes)


    def processTAZ(self, Shapefilezones):
        #Insert Yash code for extracting data from shapefiles GQIS
        #For now, put placeholder values
        Shapefilezones = [["TAZ1", 4, 600, ((0, 0), (5, 0), (9, 4), (4, 4))], ["TAZ2", 2, 400, ((0, 7), (5, 14), (9, 12), (4, 4))]]
        for zone in Shapefilezones:
            self.zones.append(Zone(zone))
    def processHospitals(self, hospitalData):
        #Insert Yash code for extracting data from shapefiles GQIS
        #For now, put placeholder value
        hospitalData = [[(4, 6), "Atrium Health"], [(8, 4), "Novant Health Center"]]
        for hospital in hospitalData:
            self.hospitals.append(Hospital(hospital))
    def processGrocery(self, groceryData):
        #Insert Yash code for extracting data from shapefiles GQIS
        #For now, put placeholder value
        groceryData = [[(3, 2), "Publix"], [(4, 12), "Whole Foods Market"]]
        for grocery in groceryData:
            self.grocery_stores.append(Grocery(grocery))
    def processStreet(self, streetsData):
        #Insert Yash code for extracting data from shapefiles GQIS
        #For now, put placeholder value
        streetsData = [[(3, 2), (8, 11)], [(4, 12), (6, 8)], [(6, 6), (9, 4)]]
        for street in streetsData:
            self.streets.append(Street(street))
    
    def calculateZoneMetrics(self):
        
        self.zones.sort()
        #Sort zones based on employment
        for zone in self.zones:
            print(zone.getEmployment())
        
            
setup = Setup(10, 10, 10, 10)
setup.run()