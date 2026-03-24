from django.db import models


class Company(models.Model):
    SERVICE_CHOICES = [
        ('tree', 'Tree Removal'),
        ('electrical', 'Electrical'),
        ('roofing', 'Roofing'),
        ('general', 'General Construction'),
        ('plumbing', 'Plumbing'),
        ('hvac', 'HVAC'),
        ('equipment', 'Equipment Rental'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('deployed', 'Deployed'),
        ('unavailable', 'Unavailable'),
    ]

    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    services = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StormEvent(models.Model):
    SEVERITY_CHOICES = [
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('catastrophic', 'Catastrophic'),
    ]

    name = models.CharField(max_length=255)
    date = models.DateField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    affected_area = models.TextField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} ({self.date})"


class Deployment(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('confirmed', 'Confirmed'),
        ('en_route', 'En Route'),
        ('on_site', 'On Site'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='deployments')
    storm_event = models.ForeignKey(StormEvent, on_delete=models.CASCADE, related_name='deployments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    requested_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    deployed_from_city = models.CharField(max_length=100, blank=True)
    deployed_from_state = models.CharField(max_length=50, blank=True)
    arrived_at = models.DateTimeField(null=True, blank=True)
    active_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.company.name} - {self.storm_event.name}"
