from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, EmailValidator
import uuid

class Company(models.Model):
    """Corporate/Company accounts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    
    # Company details
    industry = models.CharField(max_length=100)
    size = models.CharField(
        max_length=20,
        choices=[
            ('startup', '1-10 employees'),
            ('small', '11-50 employees'),
            ('medium', '51-200 employees'),
            ('large', '201-1000 employees'),
            ('enterprise', '1000+ employees'),
        ]
    )
    website = models.URLField(blank=True)
    
    # Branding
    logo = models.ImageField(upload_to='companies/logos/', null=True)
    primary_color = models.CharField(max_length=7, default='#2196F3')
    
    # Subscription
    subscription_plan = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'Trial'),
            ('basic', 'Basic'),
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='trial'
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('cancelled', 'Cancelled'),
            ('expired', 'Expired'),
        ],
        default='active'
    )
    max_users = models.IntegerField(default=10)
    subscription_ends = models.DateTimeField(null=True, blank=True)
    
    # Admin users
    admins = models.ManyToManyField(
        'accounts.User', 
        through='CompanyAdmin',
        related_name='administered_companies'
    )
    
    # Settings
    enforce_daily_practice = models.BooleanField(default=False)
    minimum_daily_minutes = models.IntegerField(default=15)
    allowed_domains = ArrayField(
        models.CharField(max_length=100), 
        blank=True, 
        default=list
    )  # Email domains for auto-approval
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'companies'
        verbose_name_plural = 'Companies'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CompanyAdmin(models.Model):
    """Company administrators"""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('instructor', 'Instructor'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    
    # Permissions
    can_manage_users = models.BooleanField(default=True)
    can_view_analytics = models.BooleanField(default=True)
    can_create_content = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)
    
    # Metadata
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        'accounts.User', 
        null=True, 
        on_delete=models.SET_NULL,
        related_name='admin_additions'
    )
    
    class Meta:
        db_table = 'company_admins'
        unique_together = [['company', 'user']]
        indexes = [
            models.Index(fields=['company', 'role']),
        ]


class Team(models.Model):
    """Teams within a company"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Team lead
    team_lead = models.ForeignKey(
        'accounts.User', 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='led_teams'
    )
    
    # Members
    members = models.ManyToManyField('accounts.User', through='TeamMembership')
    
    # Goals
    weekly_xp_goal = models.IntegerField(default=500)
    weekly_lesson_goal = models.IntegerField(default=5)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'teams'
        unique_together = [['company', 'name']]
        ordering = ['company', 'name']
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class TeamMembership(models.Model):
    """Team membership details"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    
    # Role in team
    role = models.CharField(
        max_length=20,
        choices=[
            ('member', 'Member'),
            ('lead', 'Team Lead'),
            ('mentor', 'Mentor'),
        ],
        default='member'
    )
    
    # Metadata
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'team_memberships'
        unique_together = [['team', 'user']]
        indexes = [
            models.Index(fields=['team', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]


class CompanyAnalytics(models.Model):
    """Aggregate analytics for companies"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField()
    
    # User metrics
    active_users = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    
    # Learning metrics
    total_xp_earned = models.IntegerField(default=0)
    lessons_completed = models.IntegerField(default=0)
    average_study_time_minutes = models.FloatField(default=0)
    
    # Engagement metrics
    average_streak_days = models.FloatField(default=0)
    completion_rate = models.FloatField(default=0)  # Percentage
    
    # Content metrics
    most_popular_course = models.ForeignKey(
        'courses.Course', 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL
    )
    vocabulary_words_learned = models.IntegerField(default=0)
    
    # Assessment metrics
    assessments_taken = models.IntegerField(default=0)
    average_assessment_score = models.FloatField(default=0)
    
    class Meta:
        db_table = 'company_analytics'
        unique_together = [['company', 'date']]
        ordering = ['company', '-date']
        indexes = [
            models.Index(fields=['company', '-date']),
        ]


class LearningPath(models.Model):
    """Custom learning paths for companies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Content
    courses = models.ManyToManyField('courses.Course', through='LearningPathItem')
    
    # Target audience
    target_roles = ArrayField(models.CharField(max_length=50), default=list)
    target_level = models.CharField(max_length=2)
    
    # Settings
    is_mandatory = models.BooleanField(default=False)
    deadline_weeks = models.IntegerField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'learning_paths'
        ordering = ['company', 'title']
    
    def __str__(self):
        return f"{self.company.name} - {self.title}"


class LearningPathItem(models.Model):
    """Items in a learning path"""
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    
    # Order and requirements
    order = models.IntegerField()
    is_required = models.BooleanField(default=True)
    
    # Time expectations
    expected_completion_days = models.IntegerField(null=True)
    
    class Meta:
        db_table = 'learning_path_items'
        unique_together = [['learning_path', 'course']]
        ordering = ['learning_path', 'order']


class CompanyInvoice(models.Model):
    """Billing invoices for companies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('paid', 'Paid'),
            ('overdue', 'Overdue'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft'
    )
    
    # Payment
    payment_method = models.CharField(max_length=50, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Files
    pdf_file = models.FileField(upload_to='invoices/', null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    
    class Meta:
        db_table = 'company_invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', '-created_at']),
            models.Index(fields=['status']),
        ]