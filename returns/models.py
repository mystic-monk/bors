from django.db import models

COUNTY_CHOICES = [
    ('Antrim', 'Antrim'), ('Armagh', 'Armagh'), ('Carlow', 'Carlow'),
    ('Cavan', 'Cavan'), ('Clare', 'Clare'), ('Cork', 'Cork'),
    ('Derry', 'Derry'), ('Donegal', 'Donegal'), ('Down', 'Down'),
    ('Dublin', 'Dublin'), ('Fermanagh', 'Fermanagh'), ('Galway', 'Galway'),
    ('Kerry', 'Kerry'), ('Kildare', 'Kildare'), ('Kilkenny', 'Kilkenny'),
    ('Laois', 'Laois'), ('Leitrim', 'Leitrim'), ('Limerick', 'Limerick'),
    ('Longford', 'Longford'), ('Louth', 'Louth'), ('Mayo', 'Mayo'),
    ('Meath', 'Meath'), ('Monaghan', 'Monaghan'), ('Offaly', 'Offaly'),
    ('Roscommon', 'Roscommon'), ('Sligo', 'Sligo'), ('Tipperary', 'Tipperary'),
    ('Tyrone', 'Tyrone'), ('Waterford', 'Waterford'), ('Westmeath', 'Westmeath'),
    ('Wexford', 'Wexford'), ('Wicklow', 'Wicklow'),
]

FUEL_CHOICES = [
    ('Petrol', 'Petrol'), ('Diesel', 'Diesel'),
    ('Electric', 'Electric'), ('Hybrid', 'Hybrid'),
]

EURO_CHOICES = [
    ('', 'Not known'),
    ('Euro I', 'Euro I'), ('Euro II', 'Euro II'), ('Euro III', 'Euro III'),
    ('Euro IV', 'Euro IV'), ('Euro V', 'Euro V'), ('Euro VI', 'Euro VI'),
    ('Euro VII', 'Euro VII'),
]

WHEELCHAIR_ACCESS_CHOICES = [
    ('Low-floor', 'Low-floor vehicle suitable for wheelchair access'),
    ('Lift', 'Vehicle with lift suitable for wheelchair access'),
    ('Both', 'Both low-floor and has a wheelchair lift'),
    ('None', 'Not wheelchair accessible'),
]

STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
]


class OperatorReturn(models.Model):
    data_year = models.PositiveIntegerField(verbose_name='Data Year')
    operator_name = models.CharField(max_length=200, verbose_name="Operator's Name")
    trading_name = models.CharField(max_length=200, blank=True, verbose_name='Trading Name')
    county = models.CharField(max_length=50, choices=COUNTY_CHOICES, verbose_name='County of Establishment')
    annual_revenue = models.DecimalField(
        max_digits=14, decimal_places=2,
        verbose_name='Annual Total Ticket Revenue (€)',
        help_text='Include online/pre-paid tickets, Young Adult and Student Card revenue. Exclude Free Travel Scheme, NTA Grant, contractual, and private hire revenues.'
    )
    taxsaver = models.BooleanField(verbose_name='TaxSaver Participant?')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Operator Return'
        verbose_name_plural = 'Operator Returns'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.operator_name} — {self.data_year} ({self.status})'


class LicenceReturn(models.Model):
    operator_return = models.ForeignKey(
        OperatorReturn, on_delete=models.CASCADE, related_name='licences'
    )
    licence_no = models.CharField(max_length=50, blank=True, verbose_name='Licence No')
    route_no = models.CharField(max_length=50, verbose_name='Route No')
    on_free_travel = models.BooleanField(verbose_name='On Free Travel Scheme?')
    on_yasc = models.BooleanField(verbose_name='On Young Adult / Student Card (YASC)?')
    date_joined = models.DateField(verbose_name='Date Joined Scheme')
    service_commenced = models.BooleanField(verbose_name='Has the service commenced?')
    service_ceased = models.BooleanField(verbose_name='Has the service ceased?')
    date_ceased = models.DateField(null=True, blank=True, verbose_name='Date Ceased (if applicable)')
    total_passenger_journeys = models.PositiveIntegerField(verbose_name='Total Annual Passenger Journeys')
    free_travel_percent = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name='Free Travel Passengers as % of all journeys'
    )
    km_operated = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='2024 Kilometres Operated')
    daily_pvr = models.PositiveIntegerField(verbose_name='2024 Daily PVR')

    class Meta:
        verbose_name = 'Licence Return'
        ordering = ['route_no']

    def __str__(self):
        return f'Route {self.route_no} — {self.licence_no}'


class VehicleEmission(models.Model):
    operator_return = models.ForeignKey(
        OperatorReturn, on_delete=models.CASCADE, related_name='emissions'
    )
    res_id = models.CharField(max_length=50, verbose_name='RES ID')
    vehicle_reg = models.CharField(max_length=20, verbose_name='Vehicle Reg No.')
    regularly_deployed = models.BooleanField(verbose_name='Regularly deployed on scheduled services?')
    make = models.CharField(max_length=100, verbose_name='Make')
    model_version = models.CharField(max_length=100, verbose_name='Model / Version')
    transmission = models.CharField(max_length=50, verbose_name='Transmission')
    engine_type = models.CharField(max_length=50, verbose_name='Engine Type')
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, verbose_name='Fuel Type')
    euro_standard = models.CharField(max_length=20, choices=EURO_CHOICES, blank=True, verbose_name='Euro Emission Standard')
    make_model_correct = models.BooleanField(verbose_name='Are the make/model/engine type details correct?')
    seats_on_record = models.PositiveIntegerField(null=True, blank=True, verbose_name='Seats on record')
    correct_seats = models.PositiveIntegerField(null=True, blank=True, verbose_name='Correct number of seats (if different)')
    avl_gps = models.BooleanField(verbose_name='Vehicle has AVL/GPS on board?')

    class Meta:
        verbose_name = 'Vehicle Emission Record'

    def __str__(self):
        return f'{self.vehicle_reg} ({self.res_id})'


class VehicleAccessibility(models.Model):
    operator_return = models.ForeignKey(
        OperatorReturn, on_delete=models.CASCADE, related_name='accessibility'
    )
    res_id = models.CharField(max_length=50, verbose_name='RES ID')
    vehicle_reg = models.CharField(max_length=20, verbose_name='Vehicle Reg No.')
    wheelchair_spaces = models.PositiveIntegerField(null=True, blank=True, verbose_name='Number of wheelchair spaces')
    wheelchair_access_type = models.CharField(
        max_length=50, choices=WHEELCHAIR_ACCESS_CHOICES, blank=True,
        verbose_name='Wheelchair access type'
    )
    mechanical_ramp = models.BooleanField(default=False, verbose_name='Mechanical access ramp?')
    centre_door_ramps = models.BooleanField(default=False, verbose_name='Equipped with centre door ramps?')
    exterior_displays = models.BooleanField(default=False, verbose_name='Exterior backlit route displays?')
    interior_stop_displays = models.BooleanField(default=False, verbose_name='Interior stop displays?')
    audio_announcements = models.BooleanField(default=False, verbose_name='Interior automated audible stop announcements?')
    yellow_handrails = models.BooleanField(default=False, verbose_name='Yellow coloured handrails?')
    priority_seating = models.BooleanField(default=False, verbose_name='Priority seating?')
    contrasting_seat_covers = models.BooleanField(default=False, verbose_name='Seat covers contrasting with floor colour?')
    induction_loop = models.BooleanField(default=False, verbose_name='Induction loop system?')

    class Meta:
        verbose_name = 'Vehicle Accessibility Record'

    def __str__(self):
        return f'{self.vehicle_reg} — accessibility'
