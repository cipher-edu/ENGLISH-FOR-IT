from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
from django.db.models import Q, Avg, Count
import uuid
from datetime import timedelta

class User(AbstractUser):
    """Custom User model with extended fields for IT English learning"""
    
    LEVEL_CHOICES = [
        ('A1', 'Beginner'),
        ('A2', 'Elementary'),
        ('B1', 'Intermediate'),
        ('B2', 'Upper Intermediate'),
        ('C1', 'Advanced'),
        ('C2', 'Proficient'),
    ]
    
    SPECIALIZATION_CHOICES = [
        ('backend', 'Backend Development'),
        ('frontend', 'Frontend Development'),
        ('devops', 'DevOps'),
        ('mobile', 'Mobile Development'),
        ('data', 'Data Science'),
        ('security', 'Cybersecurity'),
        ('qa', 'QA/Testing'),
        ('pm', 'Project Management'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True
    )
    
    # Learning Profile
    current_level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default='A1')
    target_level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default='B2')
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES)
    daily_goal_minutes = models.IntegerField(default=30, validators=[MinValueValidator(5)])
    
    # Gamification
    xp_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    coins = models.IntegerField(default=100, validators=[MinValueValidator(0)])
    streak_days = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    longest_streak = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    last_activity_date = models.DateField(null=True, blank=True)
    
    # Corporate
    is_corporate = models.BooleanField(default=False)
    company = models.ForeignKey('corporate.Company', null=True, blank=True, on_delete=models.SET_NULL)
    department = models.CharField(max_length=100, blank=True)
    
    # Settings & Preferences  
    timezone = models.CharField(max_length=50, default='UTC')
    preferred_study_time = models.TimeField(null=True, blank=True)
    enable_notifications = models.BooleanField(default=True)
    enable_sound_effects = models.BooleanField(default=True)
    interface_language = models.CharField(max_length=5, default='en')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    premium_until = models.DateTimeField(null=True, blank=True)
    referral_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['current_level']),
            models.Index(fields=['company', 'is_corporate']),
            models.Index(fields=['-xp_points']),  # For leaderboard
            models.Index(fields=['last_activity_date']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.current_level})"
    
    @property
    def is_premium_active(self):
        """Check if premium subscription is active"""
        if not self.is_premium:
            return False
        if self.premium_until:
            return self.premium_until > timezone.now()
        return True
    
    @property
    def level_progress_percentage(self):
        """Calculate progress to next level"""
        level_thresholds = {
            'A1': 0, 'A2': 1000, 'B1': 3000,
            'B2': 6000, 'C1': 10000, 'C2': 15000
        }
        current_threshold = level_thresholds.get(self.current_level, 0)
        next_level = self.get_next_level()
        if not next_level:
            return 100
        next_threshold = level_thresholds.get(next_level, 0)
        progress = (self.xp_points - current_threshold) / (next_threshold - current_threshold) * 100
        return min(100, max(0, progress))
    
    def get_next_level(self):
        """Get next level in progression"""
        levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        try:
            current_index = levels.index(self.current_level)
            if current_index < len(levels) - 1:
                return levels[current_index + 1]
        except ValueError:
            pass
        return None
    
    def update_streak(self, activity_date=None):
        """Update user's streak"""
        activity_date = activity_date or timezone.now().date()
        
        if self.last_activity_date:
            days_diff = (activity_date - self.last_activity_date).days
            if days_diff == 1:
                self.streak_days += 1
            elif days_diff == 0:
                pass  # Same day activity
            else:
                self.streak_days = 1
        else:
            self.streak_days = 1
        
        self.longest_streak = max(self.longest_streak, self.streak_days)
        self.last_activity_date = activity_date
        self.save(update_fields=['streak_days', 'longest_streak', 'last_activity_date'])
    
    def add_xp(self, points):
        """Add XP and check for level up"""
        self.xp_points += points
        self.check_level_up()
        self.save(update_fields=['xp_points', 'current_level'])
    
    def check_level_up(self):
        """Check if user should level up based on XP"""
        level_thresholds = {
            'A2': 1000, 'B1': 3000, 'B2': 6000,
            'C1': 10000, 'C2': 15000
        }
        for level, threshold in level_thresholds.items():
            if self.xp_points >= threshold and self.current_level < level:
                self.current_level = level
                # Trigger level up event/notification
                break


class UserProfile(models.Model):
    """Extended profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    
    # Learning preferences
    learning_style = models.CharField(
        max_length=20,
        choices=[
            ('visual', 'Visual'),
            ('auditory', 'Auditory'),
            ('reading', 'Reading/Writing'),
            ('kinesthetic', 'Kinesthetic'),
        ],
        default='visual'
    )
    
    # Statistics
    total_study_time_minutes = models.IntegerField(default=0)
    words_learned = models.IntegerField(default=0)
    lessons_completed = models.IntegerField(default=0)
    perfect_lessons = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile of {self.user.username}"


class UserDevice(models.Model):
    """Track user devices for push notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(
        max_length=10,
        choices=[('ios', 'iOS'), ('android', 'Android'), ('web', 'Web')]
    )
    push_token = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_devices'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_id']),
        ]