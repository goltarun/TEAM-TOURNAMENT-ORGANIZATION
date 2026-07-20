from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Player(models.Model):
    GAME_TYPES = [
        ('BR', 'Battle Royale'),
        ('CS', 'Counter Strike'),
    ]
    
    ROLES = [
        ('Rusher', 'Rusher'),
        ('Sniper', 'Sniper'),
        ('Support', 'Support'),
        ('Assaulter', 'Assaulter'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('Beginner', 'Beginner (0-6 months)'),
        ('Intermediate', 'Intermediate (6 months-2 years)'),
        ('Advanced', 'Advanced (2-5 years)'),
        ('Pro', 'Pro (5+ years)'),
    ]
    
    PLAYING_TIMES = [
        ('Morning', 'Morning (6AM - 12PM)'),
        ('Afternoon', 'Afternoon (12PM - 6PM)'),
        ('Evening', 'Evening (6PM - 12AM)'),
        ('Night', 'Night (12AM - 6AM)'),
        ('Flexible', 'Flexible (Any time)'),
    ]

    name = models.CharField(max_length=100, verbose_name="IGN (Game Name)")
    game_type = models.CharField(max_length=2, choices=GAME_TYPES, verbose_name="Game Type")
    role = models.CharField(max_length=20, choices=ROLES, verbose_name="Playing Role")
    rank = models.CharField(max_length=50, verbose_name="Rank")
    age = models.PositiveIntegerField(verbose_name="Age")
    id_code = models.CharField(max_length=12, unique=True, verbose_name="Game UID")
    contact = models.CharField(max_length=15, verbose_name="WhatsApp Number")
    experience = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, verbose_name="Experience Level")
    playing_time = models.CharField(max_length=20, choices=PLAYING_TIMES, verbose_name="Preferred Playing Time")
    bio = models.TextField(blank=True, null=True, verbose_name="Short Bio")
    verified = models.BooleanField(default=False, verbose_name="Verified Player")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Player"
        verbose_name_plural = "Players"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.role})"

class Tournament(models.Model):
    GAME_MODES = [
        ('BR Rank', 'BR Rank'),
        ('Clash Squad', 'Clash Squad'),
    ]

    TEAM_MODES = [
        ('Solo', 'Solo'),
        ('Duo', 'Duo'),
        ('Squad', 'Squad'),
    ]

    SLOT_RULES = {
        ('BR Rank', 'Solo'): 48,
        ('BR Rank', 'Duo'): 24,
        ('BR Rank', 'Squad'): 12,
        ('Clash Squad', 'Solo'): 2,
        ('Clash Squad', 'Duo'): 2,
        ('Clash Squad', 'Squad'): 2,
    }
    
    STATUS_CHOICES = [
        ('Today', 'Today'),
        ('Aavti Kale', 'Aavti Kale'),
        ('Param Day', 'Param Day'),
        ('5 Days Pachi', '5 Days Pachi'),
        ('10 Days Pachi', '10 Days Pachi'),
    ]

    title = models.CharField(max_length=200, verbose_name="Tournament Title")
    prize = models.CharField(max_length=50, verbose_name="Win Prize")
    entry_fee = models.CharField(max_length=20, default='Free', verbose_name="Entry Fee")
    per_kill = models.CharField(max_length=20, default='N/A', verbose_name="Per Kill Prize")
    date = models.DateField(verbose_name="Tournament Date")
    time = models.TimeField(verbose_name="Match Time")
    game_mode = models.CharField(max_length=20, choices=GAME_MODES, default='BR Rank', verbose_name="Game Mode")
    mode = models.CharField(max_length=20, choices=TEAM_MODES, default='Solo', verbose_name="Team Mode")
    map_name = models.CharField(max_length=50, default='Bermuda', verbose_name="Map Name")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Today', verbose_name="Status")
    max_slots = models.PositiveIntegerField(default=48, verbose_name="Maximum Slots")
    description = models.TextField(blank=True, null=True, verbose_name="Tournament Description")
    rules = models.TextField(blank=True, null=True, verbose_name="Custom Rules")
    alert_cancelled = models.BooleanField(default=False, verbose_name="Alert Cancelled")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tournament"
        verbose_name_plural = "Tournaments"
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.date}"

    @classmethod
    def default_slots_for(cls, game_mode, team_mode):
        return cls.SLOT_RULES.get((game_mode, team_mode), 48)

    def save(self, *args, **kwargs):
        self.max_slots = self.default_slots_for(self.game_mode, self.mode)
        super().save(*args, **kwargs)

    @property
    def available_slots(self):
        return max(0, self.max_slots - self.registrations.count())

class TournamentRegistration(models.Model):
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='registrations')
    player_name = models.CharField(max_length=100, verbose_name="Player Name")
    team_name = models.CharField(max_length=100, verbose_name="Team Name")
    contact_number = models.CharField(max_length=15, verbose_name="WhatsApp Number")
    slot_number = models.PositiveIntegerField(verbose_name="Team Slot Number")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending', verbose_name="Payment Status")
    payment_amount = models.CharField(max_length=20, blank=True, null=True, verbose_name="Payment Amount")
    payment_confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name="Payment Confirmed At")
    device_registration_time = models.DateTimeField(blank=True, null=True, verbose_name="User Device Registration Time")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Transaction ID")
    registered_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, verbose_name="Admin Notes")

    class Meta:
        verbose_name = "Tournament Registration"
        verbose_name_plural = "Tournament Registrations"
        ordering = ['-registered_at']
        unique_together = ['tournament', 'slot_number']

    def __str__(self):
        return f"{self.player_name} - {self.tournament.title} (Slot {self.slot_number})"

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="News Title")
    content = models.TextField(verbose_name="News Content")
    date_display = models.CharField(max_length=50, verbose_name="Display Date")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.date_display}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=200, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Read")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
