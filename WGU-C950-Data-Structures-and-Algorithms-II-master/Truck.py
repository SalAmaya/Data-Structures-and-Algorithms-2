from datetime import datetime, timedelta

class Package:
    def __init__(self, id_number, delivery_address, delivery_city, delivery_state, delivery_zip, delivery_deadline,
                 package_mass, special_notes, delivery_status):
        self.id_number = id_number
        self.delivery_address = delivery_address
        self.delivery_city = delivery_city
        self.delivery_state = delivery_state
        self.delivery_zip = delivery_zip
        self.delivery_deadline = delivery_deadline
        self.package_mass = package_mass
        self.special_notes = special_notes
        self.delivery_status = delivery_status
        self.assigned_truck_id = None
        self.on_truck = False
        self.en_route_timestamp = None
        self.delivery_timestamp = None

    def is_truck_assigned(self):
        return self.assigned_truck_id is not None

    def get_required_truck_id(self):
        if "Can only be on truck" in self.special_notes:
            specified_truck_id = [int(i) for i in self.special_notes.split() if i.isdigit()]
            if specified_truck_id:
                return specified_truck_id[0]
        return None

    def get_delayed_arrival_time(self):
        if "Delayed on flight---will not arrive to depot until" in self.special_notes:
            tokenized_special_notes = self.special_notes.split()
            for token in tokenized_special_notes:
                try:
                    timestamp = datetime.strptime(token, "%H:%M")
                    delayed_arrival_timedelta = timedelta(hours=timestamp.hour, minutes=timestamp.minute)
                    return delayed_arrival_timedelta
                except:
                    pass
        if "Wrong address listed" in self.special_notes:
            delayed_arrival_timedelta = timedelta(hours=10, minutes=20)
            return delayed_arrival_timedelta
        return None

    def get_delivery_deadline_timedelta(self):
        tokenized_special_notes = self.delivery_deadline.split()
        for token in tokenized_special_notes:
            try:
                timestamp = datetime.strptime(token, "%H:%M")
                delivery_deadline_timedelta = timedelta(hours=timestamp.hour, minutes=timestamp.minute)
                return delivery_deadline_timedelta
            except:
                pass


class Truck:
    def __init__(self, truck_id, driver_name, capacity):
        self.truck_id = truck_id
        self.driver_name = driver_name
        self.capacity = capacity
        self.packages = []  # List to hold packages assigned to this truck

    def assign_package(self, package):
        if len(self.packages) < self.capacity:
            self.packages.append(package)
            package.assigned_truck_id = self.truck_id
            package.on_truck = True
        else:
            print(f"Truck {self.truck_id} is full, cannot assign more packages.")


class DeliveryManager:
    def __init__(self):
        self.packages = {}  # Dictionary to store packages by their ID

    def add_package(self, package):
        self.packages[package.id_number] = package

    def get_package(self, package_id):
        return self.packages.get(package_id)

    def handle_package_delivery(self, package_id, current_time):
        package = self.get_package(package_id)
        if package:
            delayed_arrival_time = package.get_delayed_arrival_time()
            if delayed_arrival_time:
                if current_time < delayed_arrival_time:
                    return f"Package {package_id} will be delivered after {delayed_arrival_time} due to address correction."
                else:
                    return f"Package {package_id} has been delivered."
            else:
                return f"Package {package_id} has been delivered on time."
        return "Package not found."

    def display_package_at_time(self, current_time):
        for package_id, package in self.packages.items():
            delivery_status = self.handle_package_delivery(package_id, current_time)
            truck_info = f"Truck ID: {package.assigned_truck_id}" if package.assigned_truck_id else "No truck assigned"
            print(f"Package ID: {package_id} | {delivery_status} | {truck_info}")


# Example of Bulk Package Creation
manager = DeliveryManager()

# Create 10 packages with various special conditions
for i in range(1, 11):
    special_notes = ""
    if i % 3 == 0:
        special_notes = "Wrong address listed. Will be corrected at 10:20 AM."
    elif i % 5 == 0:
        special_notes = "Delayed on flight---will not arrive to depot until 12:00."
    
    package = Package(
        id_number=i,
        delivery_address=f"Address {i}",
        delivery_city="Salt Lake City",
        delivery_state="UT",
        delivery_zip="84101",
        delivery_deadline="10:00",
        package_mass=5,
        special_notes=special_notes,
        delivery_status="Pending"
    )

    manager.add_package(package)

# Simulate user input for current time
user_time_input = input("Enter the current time in HH:MM format: ")
current_time = datetime.strptime(user_time_input, "%H:%M").time()
current_time = timedelta(hours=current_time.hour, minutes=current_time.minute)

# Display package details at the entered time
manager.display_package_at_time(current_time)
