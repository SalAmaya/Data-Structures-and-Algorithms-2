from datetime import datetime, timedelta


class Package:
    # Constructor for the Package object
    # Creates a Package object with the attributes passed into the constructor method
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

    # Returns True if the Package is assigned to a Truck
    def is_truck_assigned(self):
        return self.assigned_truck_id is not None

    # Returns the id of the Truck that must deliver the Package
    def get_required_truck_id(self):
        if "Can only be on truck" in self.special_notes:
            # Find the specific Truck ID from special notes
            specified_truck_id = [int(i) for i in self.special_notes.split() if i.isdigit()]
            if specified_truck_id:
                return specified_truck_id[0]
        return None

    # If the Package arrives at the depot late, this function returns the delayed arrival time
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
        # Address is wrong and corrected at 10:20 AM
        if "Wrong address listed" in self.special_notes:
            delayed_arrival_timedelta = timedelta(hours=10, minutes=20)  # Address correction at 10:20 AM
            return delayed_arrival_timedelta
        return None

    # Converts the delivery_deadline from String format to timedelta format and returns the timedelta value
    def get_delivery_deadline_timedelta(self):
        tokenized_special_notes = self.delivery_deadline.split()
        for token in tokenized_special_notes:
            try:
                timestamp = datetime.strptime(token, "%H:%M")
                delivery_deadline_timedelta = timedelta(hours=timestamp.hour, minutes=timestamp.minute)
                return delivery_deadline_timedelta
            except:
                pass


# Add additional logic for Package handling based on delayed address corrections
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
                # If there are no delays
                return f"Package {package_id} has been delivered on time."
        return "Package not found."


# Example usage

# Creating Package #9 with incorrect address (will be corrected at 10:20 AM)
package9 = Package(
    id_number=9,
    delivery_address="Third District Juvenile Court",  # Wrong address
    delivery_city="Salt Lake City",
    delivery_state="UT",
    delivery_zip="84101",
    delivery_deadline="10:00",
    package_mass=5,
    special_notes="Wrong address listed. Will be corrected at 10:20 AM.",
    delivery_status="Pending"
)

# Creating Delivery Manager and adding the package
manager = DeliveryManager()
manager.add_package(package9)

# Testing delivery at different times
current_time = timedelta(hours=9, minutes=30)  # Before address correction
print(manager.handle_package_delivery(9, current_time))  # Expect a delayed message due to wrong address

current_time = timedelta(hours=10, minutes=30)  # After address correction
print(manager.handle_package_delivery(9, current_time))  # Should say "Package 9 has been delivered."

