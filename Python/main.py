#Brandon Maestas
#011825600
#WGU C950 Data Structure II

import csv
import datetime

gblTime = None

#Loads the .csv files
#Stores the lookup value (0-26), name, and address
with open("python/addresses.csv") as addressFile:
    addresses = csv.reader(addressFile)
    addresses = list(addresses)
#Stores the distance between addresses
with open("python/distances.csv") as distanceFile:
    distances = csv.reader(distanceFile)
    distances = list(distances)   

#Creates a hash table class
class HashTable:
    #Creates a table with an initial capacity of 40 (total # of packages)
    def __init__(self, initialcapacity=40):
        self.table = []
        for i in range(initialcapacity):
            self.table.append([])

    #Inserts/updates an item (Package class entity) in the hash table
    def insert(self, key, item):
        bucket = hash(key) % len(self.table)
        bucketList = self.table[bucket]
        for kv in bucketList:
            if kv[0] == key:
                kv[1] = item
                return True
        #Inserts at the end if it is not found   
        key_value = [key, item]
        bucketList.append(key_value)
        return True
    
    #Searches for specified key, returns none if not found
    def lookup(self, key):
        bucket = hash(key) % len(self.table)
        bucketList = self.table[bucket]
        for kv in bucketList:
            if kv[0] == key:
                return kv[1] 
        return None 
        
    #Removes an item based on a key
    def remove(self, key):
        bucket = hash(key) % len(self.table)
        bucketList = self.table[bucket]
        if key in bucketList:
            bucketList.remove(key)

#Creates a package class to represent and store information about packages   
class Package:
    #Constructor
    def __init__(self, id, street, city, state, zip,deadline,weight, notes, status,
                 departureTime, deliveryTime):
        self.id = id
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip
        self.deadline = deadline
        self.weight = weight
        self.notes = notes
        self.status = status
        self.departureTime = None
        self.deliveryTime = None

    #Outputs a string containing all package information (Used to output to the terminal)
    def __str__(self):
        #Ensures times aren't output before they occur
        if (gblTime < self.departureTime):
            departTime = None
        else:
           departTime = self.departureTime

        if (gblTime < self.deliveryTime):
            deliverTime = None
        else:
            deliverTime = self.deliveryTime

        #Converts variables to a single string and formats them into columns
        return "|ID: {:<2}|{:<30}|{:<16}|{:<2}|{:<5}|{:<8}|{:<2}|{:<9}|Departure: {:<8}|Delivery: {:<8}"\
        .format(self.id, str(self.street)[:30], self.city, self.state, self.zip, self.deadline, self.weight,
        self.status, str(departTime), str(deliverTime))   
    
    #Updates a package's status
    def updateStatus(self, time):

        #Updates package's status based off current time
        if (self.deliveryTime == None or time < self.departureTime):
            self.status = "Hub"  
        elif time < self.deliveryTime:
            self.status = "En Route"     
        else:
            self.status = "Delivered" 

        #Logic implemented for package 9's special conditions
        #If the time is past 10:20 then the address is able to be corrected
        if self.id == 9:          
            if time > datetime.timedelta (hours=10, minutes= 20):
                self.street = "410 S State St"  
                self.zip = "84111"  
            else:
                self.street = "300 State St"
                self.zip = "84103"     

#Class to represent a delivery truck and store its packages
class Trucks:
    #Constructor
    def __init__(self, speed, miles, currentLocation, departTime, packages):
        self.speed = speed
        self.miles = miles
        self.currentLocation = currentLocation
        self.time = departTime
        self.departTime = departTime
        self.packages = packages

#Finds the next address on the list
def nextAddress(address):
    for row in addresses:
        if address in row[2]:
           return int(row[0])


#Finds the distance between address1 and address2
def distAddress(address1,address2):
    distance = distances[address1][address2]
    if distance == '':
        distance = distances[address2][address1]
    return float(distance)

#Create hash table entity
Packages = HashTable() 

#Creates and loads data from packages file
#Contains crucial data about each package: delivery address, deadline, weight, etc.
with open("python/packages.csv") as packageFile:
    packages = csv.reader(packageFile, delimiter=',')
    next (packages)

    for package in packages:
        id = int(package[0])
        street = package[1]
        city = package[2]
        state = package[3]
        zip = package[4]
        deadline = package[5]
        weight = package[6]
        notes = package[7]
        status = "Hub"
        departureTime = None
        deliveryTime = None

        #Inserts packages into hash table
        p = Package(id, street, city, state, zip, deadline, weight, notes, status, 
                    departureTime, deliveryTime)
        Packages.insert(id, p)

#Implementation of the delivery algorithm
def deliveryAlgorithm(truck):
    #List containing packages waiting to be delivered
    enroute = []

    #Loads packages from the waiting list to the enroute list
    for packageID in truck.packages:
        package = Packages.lookup(packageID)
        enroute.append(package)

    truck.packages.clear()

    #Take the current location
    #Find the closest location that a package needs to be delivered to
    #Move to new location
    #Remove package from list
    #Update time, mileage, etc.
    #Algorithm continues until package list is empty
    while len(enroute) > 0:
        pkgDist = 10000
        nextPackage = None

        for package in enroute:
            if (package.id == 6 or package.id == 25):
                nextPackage = package
                pkgDist = distAddress(nextAddress(truck.currentLocation), 
                                          nextAddress(package.street))
                break

            #Loop to find the closest package in the enroute list
            if distAddress(nextAddress(truck.currentLocation), 
                           nextAddress(package.street)) <= pkgDist:
                pkgDist = distAddress(nextAddress(truck.currentLocation), 
                                          nextAddress(package.street))
                nextPackage = package

        truck.packages.append(nextPackage.id)    
        enroute.remove(nextPackage)

        #Calculate distance and updates time
        truck.miles += pkgDist
        truck.currentLocation = nextPackage.street
        truck.time += datetime.timedelta(hours=pkgDist / 18)
        nextPackage.deliveryTime = truck.time
        nextPackage.departureTime = truck.departTime

#Manually loads and initialize trucks
#Requirements:  3, 18, 36, and 38 must be on truck 2
#               13, 14, 15, 16, 19, and 20 must be delivered together
#               6, 9, 25, 28, and 32 are delayed and should be on truck 3 
#               15 must be delivered by 9, should be on truck 1 or 2
#               1, 6, 13, 14, 16, 20, 25, 29, 30, 31, 34, 37, 40 must be delivered by 10:30, truck 1 or 2 is ideal     
truck1 = Trucks(18, 0.0, "4001 South 700 East", datetime.timedelta(hours=8),\
                [1,13,14,15,16,19,20,27,29,30,31,34,37,40])
truck2 = Trucks(18, 0.0, "4001 South 700 East", datetime.timedelta(hours=9, minutes=5),\
                [3,6,7,8,10,11,12,18,21,22,23,24,25,36,38])
truck3 = Trucks(18, 0.0, "4001 South 700 East", datetime.timedelta(hours=10, minutes=20),\
                [2,4,5,9,17,26,28,32,33,35,39])

#Calls delivery algorithm (starts package delivery)
deliveryAlgorithm(truck1)
deliveryAlgorithm(truck2)

#Once truck 1 or 2 return, truck 3 departs, but only after the address for package 9 is corrected
truck3.departTime = max(datetime.timedelta (hours=10, minutes= 20), min(truck1.time, truck2.time))
deliveryAlgorithm(truck3)

#Formatting for UI
print("Package Delivery Algorithm for C950")
total_distance = truck1.miles + truck2.miles + truck3.miles
print(f"Total distance traveled: {total_distance:.2f} miles")

terminal = input("Please enter a time (HH:MM) or type 'exit': ")

while (terminal != 'exit'):
    (h, m) = terminal.split(":")
    gblTime = datetime.timedelta(hours=int(h), minutes=int(m))

    packageList =  range(1, 41)

    for packageID in packageList:
        package = Packages.lookup(packageID)
        package.updateStatus(gblTime)

        if (truck1.departTime == package.departureTime):
            print("Truck 1", str(package))
        elif (truck2.departTime == package.departureTime):
            print("Truck 2", str(package))
        elif (truck3.departTime == package.departureTime):
            print("Truck 3", str(package)) 

    terminal = input("Please enter a time (HH:MM) or type 'exit': ")