from datetime import timedelta, datetime


class Package:
    def __init__(self, id_number, delivery_address, priority=None, delivery_window=None):
        self.id_number = id_number
        self.delivery_address = delivery_address
        self.delivery_status = None  # e.g., "Pending", "En route", "Delivered"
        self.assigned_truck_id = None  # To track which truck is delivering this package
        self.en_route_timestamp = None
        self.delivery_timestamp = None
        self.priority = priority  # Optional: "High", "Low", etc.
        self.delivery_window = delivery_window  # Optional: e.g., "10:00-12:00"


class Truck:
    # Constants used to change the properties of all Truck objects created
    average_speed = 18  # miles per hour
    max_num_packages = 16  # Maximum number of packages a truck can carry

    # Truck constructor with optional parameter to define the average speed (in miles per hour) that the truck travels
    def __init__(self, truck_id, mph=average_speed, max_num_packages=max_num_packages):
        self.id = truck_id
        self.packages_id_list = []  # List of package IDs assigned to this truck
        self.mph = mph  # Truck speed
        self.max_num_packages = max_num_packages  # Max packages truck can carry
        self.total_distance_traveled = 0
        self.mileage_timestamps = []  # Keep track of the time and mileage at different points
        self.driver = None
        self.time_obj = timedelta(hours=8, minutes=0, seconds=0)  # Starting time for the truck (e.g., 8:00 AM)
        self.hub_address = "4001 South 700 East"  # Hub location
        self.at_hub = True

    # Adds the package to the list of packages that will be delivered by this Truck
    def assign_package(self, package):
        if len(self.packages_id_list) < self.max_num_packages:
            self.packages_id_list.append(package.id_number)
            package.assigned_truck_id = self.id  # Track which truck is assigned to the package
        else:
            return False

    # Sets the Delivery Status to "En route" for all Packages loaded onto the Truck
    def set_packages_en_route(self, ht):
        for package_id in self.packages_id_list:
            package = ht.lookup(package_id)
            package.delivery_status = "En route"
            package.en_route_timestamp = self.time_obj

    # Delivers the Package
    def deliver_package(self, ht, package_id, distance_traveled):
        package = ht.lookup(package_id)
        self.packages_id_list.remove(package_id)
        self.at_hub = False
        self.add_mileage(distance_traveled)
        self.time_obj += timedelta(minutes=(distance_traveled / self.mph * 60))  # Update time based on distance
        self.mileage_timestamps.append([self.total_distance_traveled, self.time_obj])
        package.delivery_status = "Delivered"
        package.delivery_timestamp = self.time_obj
        package.assigned_truck_id = self.id  # Track truck ID after delivery

    # Sends the Truck back to the hub and updates the distance covered and time passed for the Truck
    def send_back_to_hub(self, distance_from_hub):
        self.add_mileage(distance_from_hub)
        self.time_obj += timedelta(minutes=(distance_from_hub / self.mph * 60))
        self.mileage_timestamps.append([self.total_distance_traveled, self.time_obj])
        self.at_hub = True

    # Adds mileage to the total distance traveled metric
    def add_mileage(self, miles):
        self.total_distance_traveled += miles

    # Returns a list of Package objects correlating to the Truck's packages_id_list
    def get_package_list(self, ht):
        packages_list = []
        for package_id in self.packages_id_list:
            packages_list.append(ht.lookup(package_id))
        return packages_list

    # Returns True if the Truck's number of Packages assigned is equal to the maximum number of Packages it can carry
    def is_full(self):
        return len(self.packages_id_list) == self.max_num_packages

    # Returns a list of packages assigned to the truck, including their delivery status and truck ID
    def get_assigned_packages(self, ht):
        assigned_packages = []
        for package_id in self.packages_id_list:
            package = ht.lookup(package_id)
            assigned_packages.append({
                "package_id": package.id_number,
                "delivery_address": package.delivery_address,
                "status": package.delivery_status,
                "assigned_truck_id": package.assigned_truck_id,
                "delivery_timestamp": package.delivery_timestamp,
                "en_route_timestamp": package.en_route_timestamp,
                "package_priority": package.priority if hasattr(package, "priority") else "Normal",  # Optional priority
                "delivery_window": package.delivery_window if package.delivery_window else "None",  # Optional delivery window
            })
        return assigned_packages


class HashTable:
    def __init__(self):
        self.table = {}

    # Method to insert or update a package in the table
    def insert(self, package):
        self.table[package.id_number] = package

    # Method to lookup a package by its ID
    def lookup(self, package_id):
        return self.table.get(package_id)


# Evaluate delivery constraints based on truck assignment and package requirements
def evaluate_delivery_constraints(truck, ht, current_time):
    assigned_packages = truck.get_assigned_packages(ht)
    
    for package in assigned_packages:
        print(f"Package {package['package_id']} to {package['delivery_address']} is assigned to Truck {package['assigned_truck_id']}")
        
        # Check if the package has a delivery window constraint
        if package["delivery_window"] != "None":
            delivery_start, delivery_end = package["delivery_window"].split('-')
            if current_time < delivery_start or current_time > delivery_end:
                print(f"Package {package['package_id']} is outside its delivery window.")
        
        # Priority evaluation
        if package["package_priority"] == "High":
            print(f"Package {package['package_id']} is high priority and needs to be prioritized.")


# Display package delivery status for each truck
def display_package_delivery_status(ht, trucks):
    for truck in trucks:
        assigned_packages = truck.get_assigned_packages(ht)
        print(f"\nTruck {truck.id} Delivery Status:")
        for package in assigned_packages:
            print(f"Package ID: {package['package_id']}, Status: {package['status']}, Truck ID: {package['assigned_truck_id']}, Address: {package['delivery_address']}")
            if package["delivery_timestamp"]:
                print(f"Delivery Timestamp: {package['delivery_timestamp']}")
            if package["en_route_timestamp"]:
                print(f"En Route Timestamp: {package['en_route_timestamp']}")
            if package["delivery_window"] != "None":
                print(f"Delivery Window: {package['delivery_window']}")
            print(f"Priority: {package['package_priority']}")

# Creating HashTable
ht = HashTable()

# Creating Packages
package1 = Package(id_number=1, delivery_address="123 Main St", priority="High", delivery_window="09:00-11:00")
package2 = Package(id_number=2, delivery_address="456 Oak St", priority="Low", delivery_window="10:00-12:00")
package3 = Package(id_number=3, delivery_address="789 Pine St", priority="Normal", delivery_window="None")

# Adding Packages to HashTable
ht.insert(package1)
ht.insert(package2)
ht.insert(package3)

# Creating Trucks
truck1 = Truck(truck_id=1)
truck2 = Truck(truck_id=2)

# Assigning packages to trucks
truck1.assign_package(package1)
truck1.assign_package(package2)
truck2.assign_package(package3)

# Creating a list of trucks for displaying delivery status
trucks = [truck1, truck2]

# Displaying Package Delivery Status
display_package_delivery_status(ht, trucks)

# Evaluating delivery constraints for truck1
current_time = "09:30"  # Example current time
evaluate_delivery_constraints(truck1, ht, current_time)

