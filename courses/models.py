from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid

class Course(models.Model):
    """Main course model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=255)
    
    # Categorization
    level = models.CharField(
        max_length=2,
        choices=[
            ('A1', 'Beginner'), ('A2', 'Elementary'),
            ('B1', 'Intermediate'), ('B2', 'Upper Intermediate'),
            ('C1', 'Advanced'), ('C2', 'Proficient'),
        ]
    )
    category = models.CharField(
        max_length=30,
        choices=[
            ('general', 'General IT English'),
            ('programming', 'Programming'),
            ('business', 'IT Business Communication'),
            ('technical', 'Technical Documentation'),
            ('interview', 'Job Interview Prep'),
        ]
    )
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    
    # Media
    thumbnail = models.ImageField(upload_to='courses/thumbnails/')
    preview_video_url = models.URLField(blank=True)
    
    # Metrics
    duration_hours = models.IntegerField(validators=[MinValueValidator(1)])
    difficulty = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_students = models.IntegerField(default=0)
    
    # Access control
    is_free = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Metadata
    order = models.IntegerField(default=0)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['order', 'level', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['level', 'is_published']),
            models.Index(fields=['category', 'is_published']),
            models.Index(fields=['-rating', 'is_published']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.level})"
    
    @property
    def total_lessons(self):
        return self.modules.aggregate(
            total=models.Count('lessons')
        )['total'] or 0
    
    @property
    def estimated_completion_days(self):
        """Estimate days to complete at 30 min/day"""
        return max(1, self.duration_hours * 2)


class Module(models.Model):
    """Course module/chapter"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Content
    learning_outcomes = models.JSONField(default=list)  # ["Can do X", "Understands Y"]
    prerequisites = models.JSONField(default=list, blank=True)
    
    # Organization
    order = models.IntegerField()
    duration_minutes = models.IntegerField(validators=[MinValueValidator(5)])
    is_locked = models.BooleanField(default=False)
    unlock_after_module = models.ForeignKey(
        'self', null=True, blank=True, 
        on_delete=models.SET_NULL, related_name='unlocks'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_modules'
        ordering = ['course', 'order']
        unique_together = [['course', 'order']]
        indexes = [
            models.Index(fields=['course', 'order']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """Individual lesson within a module"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220)
    
    # Content structure
    learning_objectives = models.JSONField(default=list)
    key_vocabulary = models.JSONField(default=list)  # [{"word": "", "definition": "", "example": ""}]
    grammar_points = models.JSONField(default=list)
    
    # Lesson type
    lesson_type = models.CharField(
        max_length=20,
        choices=[
            ('reading', 'Reading'),
            ('listening', 'Listening'),
            ('speaking', 'Speaking'),
            ('writing', 'Writing'),
            ('mixed', 'Mixed Skills'),
            ('assessment', 'Assessment'),
        ],
        default='mixed'
    )
    
    # Settings
    order = models.IntegerField()
    duration_minutes = models.IntegerField(validators=[MinValueValidator(5)])
    xp_reward = models.IntegerField(default=10)
    is_premium = models.BooleanField(default=False)
    allow_skip = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lessons'
        ordering = ['module', 'order']
        unique_together = [['module', 'slug']]
        indexes = [
            models.Index(fields=['module', 'order']),
            models.Index(fields=['lesson_type']),
        ]
    
    def __str__(self):
        return self.title


class Block(models.Model):
    """Content block within a lesson"""
    BLOCK_TYPES = [
        ('text', 'Text Content'),
        ('code', 'Code Snippet'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('image', 'Image'),
        ('quiz', 'Quiz Question'),
        ('exercise', 'Interactive Exercise'),
        ('markdown', 'Markdown Content'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='blocks')
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    
    # Content
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)  # For text, markdown, code
    media_file = models.FileField(upload_to='lessons/media/', null=True, blank=True)
    media_url = models.URLField(blank=True)  # For external content
    
    # For code blocks
    language = models.CharField(max_length=20, blank=True)  # python, javascript, etc
    is_executable = models.BooleanField(default=False)
    expected_output = models.TextField(blank=True)
    
    # For quiz/exercise
    question_data = models.JSONField(null=True, blank=True)  # Questions, options, correct answers
    
    # Settings
    order = models.IntegerField()
    is_optional = models.BooleanField(default=False)
    estimated_time_seconds = models.IntegerField(default=60)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lesson_blocks'
        ordering = ['lesson', 'order']
        indexes = [
            models.Index(fields=['lesson', 'order']),
            models.Index(fields=['block_type']),
        ]
    
    def __str__(self):
        return f"{self.lesson.title} - Block {self.order} ({self.block_type})"


class UserCourseEnrollment(models.Model):
    """Track user enrollment in courses"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    # Progress
    current_lesson = models.ForeignKey(Lesson, null=True, blank=True, on_delete=models.SET_NULL)
    progress_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    completed_lessons = models.IntegerField(default=0)
    total_study_time_minutes = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('enrolled', 'Enrolled'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('paused', 'Paused'),
        ],
        default='enrolled'
    )
    
    # Dates
    enrolled_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Certificate
    certificate_issued = models.BooleanField(default=False)
    certificate_url = models.URLField(blank=True)
    
    class Meta:
        db_table = 'user_course_enrollments'
        unique_together = [['user', 'course']]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['course', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class LessonProgress(models.Model):
    """Track individual lesson progress"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(UserCourseEnrollment, on_delete=models.CASCADE)
    
    # Completion
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_time_seconds = models.IntegerField(default=0)
    
    # Performance
    score = models.IntegerField(null=True, blank=True)
    max_score = models.IntegerField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    
    # Block progress
    completed_blocks = models.JSONField(default=list)  # List of block IDs
    block_responses = models.JSONField(default=dict)  # Store quiz/exercise responses
    
    # Rewards
    xp_earned = models.IntegerField(default=0)
    perfect_completion = models.BooleanField(default=False)
    
    # Metadata
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lesson_progress'
        unique_together = [['user', 'lesson']]
        indexes = [
            models.Index(fields=['user', 'lesson']),
            models.Index(fields=['enrollment', 'is_completed']),
        ]