class ParticipantDetails():
    def __init__(self, p_name, p_address, p_phone):
        self.name = p_name
        self.address = p_address
        self.phone = p_phone

class ScanDetails():
    def __init__(self, scan_time, scan_site, appt_detail, staff):
        self.time = scan_time
        self.site = scan_site
        self.appt = appt_detail
        self.staff = staff

class StaffDetails():
    def __init__(self, staff_id, staff_name, staff_phone):
        self.id = staff_id
        self.name = staff_name
        self.phone = staff_phone

class SiteDetails():
    def __init__(self, site_name, site_address):
        self.name = site_name
        self.address = site_address

class OrderTimes():
    def __init__(self, dropoff_time, pickup_time):
        self.dropoff = dropoff_time
        self.pickup = pickup_time

