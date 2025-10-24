from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
import uuid

class WritingTemplate(models.Model):
    """Templates for different types of writing"""
    TEMPLATE_TYPES = [
        ('email', 'Email'),
        ('documentation', 'Documentation'),
        ('bug_report', 'Bug Report'),
        ('proposal', 'Project Proposal'),
        ('review', 'Code Review'),
        ('standup', 'Standup Update'),
        ('readme', 'README'),
        ('api_doc', 'API Documentation'),
        ('user_story', 'User Story'),
        ('post_mortem', 'Post-Mortem'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    description = models.TextField()
    
    # Template content
    structure = models.JSONField()  # Sections and guidelines
    example_content = models.TextField()
    key_phrases = ArrayField(models.CharField(max_length=200), default=list)
    dos_and_donts = models.JSONField(default=dict)
    
    # Requirements
    level = models.CharField(max_length=2)
    min_words = models.IntegerField(default=50)
    max_words = models.IntegerField(default=500)
    
    # Evaluation
    evaluation_criteria = models.JSONField()
    sample_feedback = models.JSONField(default=list)
    
    # Metadata
    tags = models.JSONField(blank=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'writing_templates'
        ordering = ['template_type', 'level']
        indexes = [
            models.Index(fields=['template_type', 'level']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.template_type})"


class WritingTask(models.Model):
    """Writing assignments/tasks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    
    # Task setup
    template = models.ForeignKey(
        WritingTemplate, null=True, blank=True, on_delete=models.SET_NULL
    )
    context = models.TextField()  # Scenario/background
    requirements = models.JSONField()  # Specific requirements
    
    # Content hints
    vocabulary_hints = models.ManyToManyField('vocabulary.Word', blank=True)
    grammar_focus = models.JSONField(default=list)
    
    # Constraints
    word_limit_min = models.IntegerField(default=50)
    word_limit_max = models.IntegerField(default=500)
    time_limit_minutes = models.IntegerField(null=True, blank=True)
    
    # Difficulty
    level = models.CharField(max_length=2)
    difficulty = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Association
    lesson = models.ForeignKey(
        'courses.Lesson', null=True, blank=True, on_delete=models.SET_NULL
    )
    
    # Metadata
    xp_reward = models.IntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'writing_tasks'
        ordering = ['level', 'difficulty']
        indexes = [
            models.Index(fields=['level', 'difficulty']),
        ]
    
    def __str__(self):
        return self.title


class WritingSubmission(models.Model):
    """User's writing submissions"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewing', 'Under Review'),
        ('reviewed', 'Reviewed'),
        ('revised', 'Revised'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    task = models.ForeignKey(WritingTask, on_delete=models.CASCADE)
    
    # Content
    content = models.TextField(validators=[MinLengthValidator(10)])
    word_count = models.IntegerField()
    
    # Versions
    version = models.IntegerField(default=1)
    previous_version = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL
    )
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # AI Analysis
    ai_feedback = models.JSONField(null=True, blank=True)
    grammar_errors = models.JSONField(default=list)
    style_suggestions = models.JSONField(default=list)
    vocabulary_analysis = models.JSONField(default=dict)
    
    # Scoring
    grammar_score = models.IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    vocabulary_score = models.IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    coherence_score = models.IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    task_completion_score = models.IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    overall_score = models.IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Peer review
    peer_reviews = models.ManyToManyField(
        'accounts.User', through='PeerReview', related_name='reviewed_writings'
    )
    
    # Time tracking
    time_spent_seconds = models.IntegerField(default=0)
    
    # Rewards
    xp_earned = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'writing_submissions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['task', 'status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title} (v{self.version})"
    
    def calculate_overall_score(self):
        """Calculate weighted overall score"""
        scores = [
            self.grammar_score,
            self.vocabulary_score,
            self.coherence_score,
            self.task_completion_score
        ]
        valid_scores = [s for s in scores if s is not None]
        if valid_scores:
            self.overall_score = sum(valid_scores) // len(valid_scores)
            self.save(update_fields=['overall_score'])


class PeerReview(models.Model):
    """Peer review for writing submissions"""
    submission = models.ForeignKey(WritingSubmission, on_delete=models.CASCADE)
    reviewer = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    
    # Feedback
    overall_feedback = models.TextField()
    strengths = models.JSONField(default=list)
    improvements = models.JSONField(default=list)
    
    # Inline comments
    inline_comments = models.JSONField(default=list)  # Position-based comments
    
    # Ratings
    helpfulness_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    clarity_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    grammar_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Metadata
    is_helpful = models.BooleanField(null=True)  # Rated by submission author
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'peer_reviews'
        unique_together = [['submission', 'reviewer']]
        indexes = [
            models.Index(fields=['submission', 'reviewer']),
        ]