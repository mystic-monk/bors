import secrets
from django.db import models
from django.utils import timezone

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
    TAXSAVER_CHOICES = [
        ('yes',   'Yes'),
        ('no',    'No'),
        ('other', 'Other'),
    ]
    taxsaver = models.CharField(
        max_length=10, choices=TAXSAVER_CHOICES, default='no',
        verbose_name='TaxSaver Tickets: Offered?',
    )
    taxsaver_other = models.TextField(
        blank=True,
        verbose_name='TaxSaver — other details',
        help_text='Required when "Other" is selected above.',
    )
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


class OperatorAccess(models.Model):
    """One record per operator. Admin creates these and emails the token manually."""
    token = models.CharField(max_length=64, unique=True, editable=False)
    operator_name = models.CharField(max_length=200)
    operator_email = models.EmailField()
    operator_return = models.OneToOneField(
        OperatorReturn, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='access',
    )
    is_active = models.BooleanField(default=True, help_text='Uncheck to revoke access.')
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Operator Access'
        verbose_name_plural = 'Operator Accesses'

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def regenerate_token(self):
        self.token = secrets.token_urlsafe(32)
        self.save(update_fields=['token'])

    def __str__(self):
        return f'{self.operator_name} <{self.operator_email}>'


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


class SeedLicence(models.Model):
    """NTA-provided route data seeded before operator fills in their return."""
    operator_access = models.ForeignKey(
        OperatorAccess, on_delete=models.CASCADE, related_name='seed_licences'
    )
    year = models.PositiveIntegerField()
    route_no = models.CharField(max_length=50)

    class Meta:
        unique_together = [['operator_access', 'year', 'route_no']]
        ordering = ['year', 'route_no']
        verbose_name = 'Seed Licence'

    def __str__(self):
        return f'{self.operator_access.operator_name} — Route {self.route_no} ({self.year})'


class SeedVehicle(models.Model):
    """NTA-provided vehicle data seeded before operator fills in their return."""
    operator_access = models.ForeignKey(
        OperatorAccess, on_delete=models.CASCADE, related_name='seed_vehicles'
    )
    year = models.PositiveIntegerField()
    res_id = models.CharField(max_length=50, blank=True)
    vehicle_reg = models.CharField(max_length=20)
    make = models.CharField(max_length=100, blank=True)
    model_version = models.CharField(max_length=100, blank=True)
    transmission = models.CharField(max_length=50, blank=True)
    engine_type = models.CharField(max_length=50, blank=True)
    seats_on_record = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = [['operator_access', 'year', 'vehicle_reg']]
        ordering = ['year', 'res_id', 'vehicle_reg']
        verbose_name = 'Seed Vehicle'

    def __str__(self):
        return f'{self.operator_access.operator_name} — {self.vehicle_reg} ({self.year})'


class VehicleRouteUsage(models.Model):
    vehicle = models.ForeignKey(
        VehicleEmission, on_delete=models.CASCADE, related_name='route_usages'
    )
    route_no = models.CharField(max_length=50)
    usage_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = [['vehicle', 'route_no']]
        ordering = ['route_no']
        verbose_name = 'Vehicle Route Usage'

    def __str__(self):
        return f'{self.vehicle} — {self.route_no}: {self.usage_percent}%'


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


class YearLock(models.Model):
    """Staff can lock a data year to prevent operators editing or submitting returns for that year."""
    year = models.PositiveIntegerField(unique=True)
    locked_by = models.CharField(max_length=200, blank=True)
    locked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Year Lock'
        ordering = ['-year']

    def __str__(self):
        return f'{self.year} (locked)'


class Declaration(models.Model):
    operator_return = models.OneToOneField(
        OperatorReturn, on_delete=models.CASCADE, related_name='declaration'
    )
    signed_by = models.CharField(
        max_length=200, blank=True,
        verbose_name='Signed',
        help_text='Leave blank if completing digitally.',
    )
    printed_name = models.CharField(
        max_length=200, blank=True,
        verbose_name='Print name in block capitals',
        help_text='Leave blank if completing digitally.',
    )
    declaration_date = models.DateField(verbose_name='Date')
    position_in_company = models.CharField(
        max_length=200,
        verbose_name='Position in Company (block capitals)',
    )

    class Meta:
        verbose_name = 'Declaration'

    def __str__(self):
        return f'Declaration — {self.operator_return}'
