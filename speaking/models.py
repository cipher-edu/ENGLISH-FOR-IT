from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class SpeakingScenario(models.Model):
    """Pre-defined speaking practice scenarios"""
    SCENARIO_TYPES = [
        ('interview', 'Job Interview'),
        ('standup', 'Daily Standup'),
        ('presentation', 'Technical Presentation'),
        ('meeting', 'Team Meeting'),
        ('phone', 'Phone Call'),
        ('networking', 'Networking Event'),
        ('support', 'Customer Support'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    scenario_type = models.CharField(max_length=20, choices=SCENARIO_TYPES)
    
    # Content
    context = models.TextField()  # Scenario background
    role_description = models.TextField()  # User's role
    ai_role = models.CharField(max_length=100)  # AI's role (interviewer, colleague, etc.)
    
    # Dialogue structure
    dialogue_flow = models.JSONField()  # Expected conversation flow
    key_phrases = ArrayField(models.CharField(max_length=200), default=list)
    vocabulary_focus = models.ManyToManyField('vocabulary.Word', blank=True)
    
    # Settings
    level = models.CharField(max_length=2)
    difficulty = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    estimated_duration_minutes = models.IntegerField(default=5)
    
    # Evaluation criteria
    evaluation_rubric = models.JSONField()  # Criteria for scoring
    
    # Metadata
    tags = models.JSONField(blank=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'speaking_scenarios'
        ordering = ['scenario_type', 'level']
        indexes = [
            models.Index(fields=['scenario_type', 'level']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.scenario_type})"


class SpeakingSession(models.Model):
    """Individual speaking practice session"""
    SESSION_TYPES = [
        ('scenario', 'Scenario Practice'),
        ('pronunciation', 'Pronunciation'),
        ('free_talk', 'Free Talk'),
        ('shadowing', 'Shadowing'),
        ('reading', 'Reading Aloud'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    scenario = models.ForeignKey(
        SpeakingScenario, null=True, blank=True, on_delete=models.SET_NULL
    )
    
    # Recording
    audio_file = models.FileField(upload_to='speaking/recordings/%Y/%m/', null=True)
    duration_seconds = models.IntegerField(null=True)
    transcript = models.TextField(blank=True)
    
    # AI Interaction
    ai_responses = models.JSONField(default=list)  # List of AI responses
    conversation_history = models.JSONField(default=list)  # Full conversation
    
    # Analysis results
    pronunciation_score = models.IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    fluency_score = models.IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    accuracy_score = models.IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    vocabulary_score = models.IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Detailed feedback
    pronunciation_issues = models.JSONField(default=list)  # Problem words/sounds
    grammar_corrections = models.JSONField(default=list)
    vocabulary_suggestions = models.JSONField(default=list)
    general_feedback = models.TextField(blank=True)
    
    # Progress tracking
    completed = models.BooleanField(default=False)
    xp_earned = models.IntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'speaking_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['session_type', 'completed']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.session_type} ({self.started_at})"


class PronunciationChallenge(models.Model):
    """Specific pronunciation challenges"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Content
    target_sound = models.CharField(max_length=50)  # IPA notation
    example_words = ArrayField(models.CharField(max_length=100))
    example_sentences = ArrayField(models.TextField())
    
    # Instructions
    tongue_position = models.TextField(blank=True)
    mouth_shape = models.TextField(blank=True)
    common_mistakes = models.JSONField(default=list)
    tips = models.JSONField(default=list)
    
    # Media
    demo_video_url = models.URLField(blank=True)
    demo_audio_file = models.FileField(upload_to='pronunciation/demos/', null=True)
    
    # Difficulty
    difficulty_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    class Meta:
        db_table = 'pronunciation_challenges'
        ordering = ['difficulty_level', 'title']
    
    def __str__(self):
        return f"{self.title} - {self.target_sound}"


class UserPronunciationProgress(models.Model):
    """Track user's pronunciation improvement"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    challenge = models.ForeignKey(PronunciationChallenge, on_delete=models.CASCADE)
    
    # Progress
    attempts = models.IntegerField(default=0)
    best_score = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    average_score = models.FloatField(default=0)
    
    # Mastery
    is_mastered = models.BooleanField(default=False)
    mastered_at = models.DateTimeField(null=True, blank=True)
    
    # History
    score_history = models.JSONField(default=list)  # List of scores over time
    last_practiced = models.DateTimeField(null=True)
    
    class Meta:
        db_table = 'user_pronunciation_progress'
        unique_together = [['user', 'challenge']]
        indexes = [
            models.Index(fields=['user', 'is_mastered']),
        ]