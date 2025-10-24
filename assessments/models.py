from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import hashlib

class Assessment(models.Model):
    """Main assessment/test model"""
    ASSESSMENT_TYPES = [
        ('placement', 'Placement Test'),
        ('module', 'Module Test'),
        ('final', 'Final Assessment'),
        ('diagnostic', 'Diagnostic Test'),
        ('practice', 'Practice Test'),
        ('certification', 'Certification Exam'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    
    # Association
    course = models.ForeignKey(
        'courses.Course', null=True, blank=True, on_delete=models.CASCADE
    )
    module = models.ForeignKey(
        'courses.Module', null=True, blank=True, on_delete=models.CASCADE
    )
    
    # Test structure
    sections = models.JSONField()  # Test sections configuration
    total_questions = models.IntegerField()
    time_limit_minutes = models.IntegerField(null=True, blank=True)
    
    # Scoring
    passing_score = models.IntegerField(
        default=70, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_attempts = models.IntegerField(default=3)
    
    # Requirements
    level = models.CharField(max_length=2)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    # Certificate
    awards_certificate = models.BooleanField(default=False)
    certificate_template = models.ForeignKey(
        'CertificateTemplate', null=True, blank=True, on_delete=models.SET_NULL
    )
    
    # Settings
    randomize_questions = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=True)
    allow_review = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assessments'
        ordering = ['assessment_type', 'title']
        indexes = [
            models.Index(fields=['assessment_type', 'is_active']),
            models.Index(fields=['course', 'module']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.assessment_type})"


class Question(models.Model):
    """Question bank for assessments"""
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('fill_blank', 'Fill in the Blank'),
        ('matching', 'Matching'),
        ('ordering', 'Ordering'),
        ('essay', 'Essay'),
        ('code', 'Code Writing'),
        ('audio', 'Audio Response'),
    ]
    
    SKILL_TYPES = [
        ('reading', 'Reading'),
        ('listening', 'Listening'),
        ('grammar', 'Grammar'),
        ('vocabulary', 'Vocabulary'),
        ('writing', 'Writing'),
        ('speaking', 'Speaking'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Content
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    skill_type = models.CharField(max_length=20, choices=SKILL_TYPES)
    
    # Additional content
    context = models.TextField(blank=True)  # Reading passage, code snippet, etc.
    media_file = models.FileField(
        upload_to='assessments/media/', null=True, blank=True
    )
    
    # Answer options (for applicable types)
    options = models.JSONField(null=True, blank=True)
    correct_answer = models.JSONField()  # Can be string, list, or complex object
    
    # Scoring
    points = models.IntegerField(default=1)
    partial_credit_allowed = models.BooleanField(default=False)
    
    # Metadata
    difficulty = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    tags = ArrayField(models.CharField(max_length=30), blank=True, default=list)
    explanation = models.TextField(blank=True)  # Explanation of correct answer
    
    # Usage tracking
    times_used = models.IntegerField(default=0)
    times_answered_correctly = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assessment_questions'
        indexes = [
            models.Index(fields=['question_type', 'skill_type']),
            models.Index(fields=['difficulty']),
        ]
    
    def __str__(self):
        return f"{self.question_type} - {self.question_text[:50]}"
    
    @property
    def success_rate(self):
        """Calculate question success rate"""
        if self.times_used == 0:
            return 0
        return (self.times_answered_correctly / self.times_used) * 100


class AssessmentAttempt(models.Model):
    """User's attempt at an assessment"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    
    # Attempt info
    attempt_number = models.IntegerField(default=1)
    
    # Progress
    current_question_index = models.IntegerField(default=0)
    questions_answered = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    
    # Scoring
    score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    passed = models.BooleanField(null=True)
    
    # Section scores
    section_scores = models.JSONField(default=dict)
    skill_breakdown = models.JSONField(default=dict)
    
    # Time tracking
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.IntegerField(default=0)
    
    # Generated questions (order matters)
    question_order = models.JSONField(default=list)  # List of question IDs
    
    class Meta:
        db_table = 'assessment_attempts'
        ordering = ['-started_at']
        unique_together = [['user', 'assessment', 'attempt_number']]
        indexes = [
            models.Index(fields=['user', 'assessment']),
            models.Index(fields=['-started_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.assessment.title} - Attempt {self.attempt_number}"


class Answer(models.Model):
    """User's answer to a question"""
    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # Answer content
    user_answer = models.JSONField()
    
    # Evaluation
    is_correct = models.BooleanField(null=True)
    points_earned = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    
    # Feedback
    ai_feedback = models.TextField(blank=True)
    manual_feedback = models.TextField(blank=True)
    
    # Metadata
    time_spent_seconds = models.IntegerField(null=True)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'assessment_answers'
        unique_together = [['attempt', 'question']]
        indexes = [
            models.Index(fields=['attempt', 'question']),
        ]


class Certificate(models.Model):
    """Issued certificates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE)
    
    # Certificate details
    certificate_number = models.CharField(max_length=50, unique=True)
    
    # Achievement details
    score = models.DecimalField(max_digits=5, decimal_places=2)
    level_achieved = models.CharField(max_length=50)
    
    # Files
    pdf_file = models.FileField(upload_to='certificates/')
    
    # Verification
    verification_code = models.CharField(max_length=100, unique=True)
    qr_code = models.ImageField(upload_to='certificates/qr/', null=True)
    
    # Metadata
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'certificates'
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['user', '-issued_at']),
            models.Index(fields=['certificate_number']),
            models.Index(fields=['verification_code']),
        ]
    
    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.user.username}"
    
    def generate_verification_code(self):
        """Generate unique verification code"""
        data = f"{self.user.id}{self.assessment.id}{self.issued_at}"
        return hashlib.sha256(data.encode()).hexdigest()[:20].upper()


class CertificateTemplate(models.Model):
    """Templates for certificate generation"""
    name = models.CharField(max_length=100)
    html_template = models.TextField()
    css_styles = models.TextField()
    
    # Customization
    logo = models.ImageField(upload_to='certificate_templates/')
    signature_image = models.ImageField(upload_to='certificate_templates/', null=True)
    background_image = models.ImageField(upload_to='certificate_templates/', null=True)
    
    # Settings
    paper_size = models.CharField(
        max_length=10,
        choices=[('A4', 'A4'), ('Letter', 'Letter')],
        default='A4'
    )
    orientation = models.CharField(
        max_length=10,
        choices=[('portrait', 'Portrait'), ('landscape', 'Landscape')],
        default='landscape'
    )
    
    is_default = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'certificate_templates'