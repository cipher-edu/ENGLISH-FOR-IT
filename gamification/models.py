from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
import uuid

class Badge(models.Model):
    """Achievement badges"""
    BADGE_TYPES = [
        ('achievement', 'Achievement'),
        ('milestone', 'Milestone'),
        ('skill', 'Skill'),
        ('special', 'Special Event'),
        ('level', 'Level'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    
    # Visual
    icon = models.ImageField(upload_to='badges/')
    color_scheme = models.CharField(max_length=7, default='#4CAF50')  # Hex color
    
    # Requirements
    criteria = models.JSONField()  # Conditions to earn
    auto_award = models.BooleanField(default=True)
    
    # Rewards
    xp_reward = models.IntegerField(default=0)
    coins_reward = models.IntegerField(default=0)
    
    # Rarity
    rarity = models.CharField(
        max_length=20,
        choices=[
            ('common', 'Common'),
            ('uncommon', 'Uncommon'),
            ('rare', 'Rare'),
            ('epic', 'Epic'),
            ('legendary', 'Legendary'),
        ],
        default='common'
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'badges'
        ordering = ['badge_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.rarity})"


class UserBadge(models.Model):
    """Badges earned by users"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    
    # Achievement details
    earned_at = models.DateTimeField(auto_now_add=True)
    progress = models.JSONField(default=dict)  # Progress towards earning
    
    # Display
    is_featured = models.BooleanField(default=False)  # Show on profile
    
    class Meta:
        db_table = 'user_badges'
        unique_together = [['user', 'badge']]
        indexes = [
            models.Index(fields=['user', 'earned_at']),
            models.Index(fields=['user', 'is_featured']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class Leaderboard(models.Model):
    """Different leaderboard types"""
    LEADERBOARD_TYPES = [
        ('global', 'Global'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('course', 'Course'),
        ('company', 'Company'),
        ('friends', 'Friends'),
    ]
    
    PERIOD_TYPES = [
        ('all_time', 'All Time'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('today', 'Today'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    leaderboard_type = models.CharField(max_length=20, choices=LEADERBOARD_TYPES)
    period = models.CharField(max_length=20, choices=PERIOD_TYPES, default='all_time')
    
    # Scope
    course = models.ForeignKey(
        'courses.Course', null=True, blank=True, on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        'corporate.Company', null=True, blank=True, on_delete=models.CASCADE
    )
    
    # Settings
    metric = models.CharField(
        max_length=20,
        choices=[
            ('xp', 'XP Points'),
            ('streak', 'Streak Days'),
            ('lessons', 'Lessons Completed'),
            ('words', 'Words Learned'),
            ('accuracy', 'Accuracy'),
        ],
        default='xp'
    )
    min_participants = models.IntegerField(default=5)
    max_display = models.IntegerField(default=100)
    
    # Cache
    last_updated = models.DateTimeField(null=True)
    cached_rankings = models.JSONField(default=list)
    
    class Meta:
        db_table = 'leaderboards'
        indexes = [
            models.Index(fields=['leaderboard_type', 'period']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.leaderboard_type})"


class LeaderboardEntry(models.Model):
    """Individual leaderboard entries"""
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    
    # Ranking
    rank = models.IntegerField()
    previous_rank = models.IntegerField(null=True)
    
    # Metrics
    score = models.IntegerField()
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leaderboard_entries'
        unique_together = [['leaderboard', 'user']]
        ordering = ['rank']
        indexes = [
            models.Index(fields=['leaderboard', 'rank']),
            models.Index(fields=['user', 'leaderboard']),
        ]


class Challenge(models.Model):
    """Daily/Weekly challenges"""
    CHALLENGE_TYPES = [
        ('daily', 'Daily Challenge'),
        ('weekly', 'Weekly Challenge'),
        ('special', 'Special Event'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    
    # Requirements
    tasks = models.JSONField()  # List of tasks to complete
    target_value = models.IntegerField()  # e.g., "Complete 5 lessons"
    
    # Rewards
    xp_reward = models.IntegerField(default=50)
    coins_reward = models.IntegerField(default=10)
    badge = models.ForeignKey(Badge, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'challenges'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['challenge_type', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.challenge_type})"


class UserChallenge(models.Model):
    """User's progress in challenges"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    
    # Progress
    current_progress = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Rewards claimed
    rewards_claimed = models.BooleanField(default=False)
    
    # Metadata
    started_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_challenges'
        unique_together = [['user', 'challenge']]
        indexes = [
            models.Index(fields=['user', 'challenge']),
            models.Index(fields=['user', 'is_completed']),
        ]


class XPTransaction(models.Model):
    """Track XP transactions"""
    TRANSACTION_TYPES = [
        ('lesson', 'Lesson Completion'),
        ('quiz', 'Quiz'),
        ('challenge', 'Challenge'),
        ('achievement', 'Achievement'),
        ('bonus', 'Bonus'),
        ('penalty', 'Penalty'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    
    # Transaction details
    amount = models.IntegerField()  # Can be negative for penalties
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    
    # Related object (generic relation)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.CharField(max_length=255, null=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'xp_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.amount}XP ({self.transaction_type})"