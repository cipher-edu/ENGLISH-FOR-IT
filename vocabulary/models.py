from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta
import uuid

class WordCategory(models.Model):
    """Categories for vocabulary organization"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)  # Icon class name
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'word_categories'
        verbose_name_plural = 'Word categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Word(models.Model):
    """Individual vocabulary word"""
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('expert', 'Expert'),
    ]
    
    WORD_TYPES = [
        ('noun', 'Noun'),
        ('verb', 'Verb'),
        ('adjective', 'Adjective'),
        ('adverb', 'Adverb'),
        ('phrase', 'Phrase'),
        ('idiom', 'Idiom'),
        ('abbreviation', 'Abbreviation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Core content
    term = models.CharField(max_length=100, db_index=True)
    definition = models.TextField()
    part_of_speech = models.CharField(max_length=20, choices=WORD_TYPES)
    pronunciation_ipa = models.CharField(max_length=100, blank=True)
    audio_url = models.URLField(blank=True)
    
    # Examples and context
    example_sentence = models.TextField()
    code_context = models.TextField(blank=True)  # Code snippet showing usage
    synonyms = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    antonyms = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    related_terms = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    
    # Categorization
    category = models.ForeignKey(WordCategory, on_delete=models.SET_NULL, null=True)
    subcategory = models.CharField(max_length=50, blank=True)
    tags = ArrayField(models.CharField(max_length=30), blank=True, default=list)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='medium')
    frequency_rank = models.IntegerField(null=True, blank=True)  # How common the word is
    
    # IT-specific fields
    technology_stack = ArrayField(
        models.CharField(max_length=30), blank=True, default=list
    )  # ['python', 'javascript', 'react']
    documentation_links = models.JSONField(default=list, blank=True)
    
    # Learning metadata
    appears_in_lessons = models.ManyToManyField('courses.Lesson', blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'words'
        ordering = ['term']
        indexes = [
            models.Index(fields=['term']),
            models.Index(fields=['category', 'difficulty']),
            models.Index(fields=['frequency_rank']),
        ]
    
    def __str__(self):
        return f"{self.term} ({self.part_of_speech})"


class UserWord(models.Model):
    """Track user's relationship with words (Spaced Repetition)"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('learning', 'Learning'),
        ('review', 'Review'),
        ('learned', 'Learned'),
        ('ignored', 'Ignored'),
    ]
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    
    # Spaced Repetition (SM-2 Algorithm)
    repetitions = models.IntegerField(default=0)
    easiness_factor = models.FloatField(default=2.5)
    interval = models.IntegerField(default=1)  # Days until next review
    next_review = models.DateTimeField(default=datetime.now)
    
    # Learning progress
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    times_reviewed = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    times_incorrect = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    
    # Performance metrics
    average_response_time = models.FloatField(null=True, blank=True)  # seconds
    last_response_quality = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    confidence_level = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Dates
    first_seen = models.DateTimeField(auto_now_add=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    learned_date = models.DateTimeField(null=True, blank=True)
    
    # User notes
    personal_note = models.TextField(blank=True)
    custom_example = models.TextField(blank=True)
    
    class Meta:
        db_table = 'user_words'
        unique_together = [['user', 'word']]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'next_review']),
            models.Index(fields=['user', '-confidence_level']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.word.term}"
    
    def update_repetition(self, quality):
        """
        Update spaced repetition parameters based on response quality
        Quality: 0-5 (0=complete blackout, 5=perfect response)
        """
        if quality >= 3:
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.easiness_factor)
            
            self.repetitions += 1
            self.easiness_factor = max(1.3, 
                self.easiness_factor + 0.1 - (5.0 - quality) * (0.08 + (5.0 - quality) * 0.02)
            )
        else:
            self.repetitions = 0
            self.interval = 1
            self.easiness_factor = max(1.3, self.easiness_factor - 0.2)
        
        self.next_review = datetime.now() + timedelta(days=self.interval)
        self.last_reviewed = datetime.now()
        self.last_response_quality = quality
        
        # Update stats
        self.times_reviewed += 1
        if quality >= 3:
            self.times_correct += 1
            self.streak += 1
        else:
            self.times_incorrect += 1
            self.streak = 0
        
        # Update status
        if self.repetitions >= 5 and self.easiness_factor >= 2.5:
            self.status = 'learned'
            self.learned_date = datetime.now()
        elif self.repetitions > 0:
            self.status = 'review'
        else:
            self.status = 'learning'
        
        self.save()


class WordSet(models.Model):
    """Collection of words for study"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Content
    words = models.ManyToManyField(Word, through='WordSetItem')
    
    # Type
    is_public = models.BooleanField(default=True)
    is_official = models.BooleanField(default=False)  # Created by platform
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    
    # Associated content
    course = models.ForeignKey('courses.Course', null=True, blank=True, on_delete=models.SET_NULL)
    lesson = models.ForeignKey('courses.Lesson', null=True, blank=True, on_delete=models.SET_NULL)
    
    # Metadata
    tags = ArrayField(models.CharField(max_length=30), blank=True, default=list)
    difficulty = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'word_sets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by', 'is_public']),
            models.Index(fields=['course']),
        ]
    
    def __str__(self):
        return self.title


class WordSetItem(models.Model):
    """Through model for WordSet words with ordering"""
    word_set = models.ForeignKey(WordSet, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'word_set_items'
        ordering = ['order']
        unique_together = [['word_set', 'word']]


class VocabularyQuiz(models.Model):
    """Quiz sessions for vocabulary practice"""
    QUIZ_TYPES = [
        ('flashcard', 'Flashcard'),
        ('multiple_choice', 'Multiple Choice'),
        ('type_in', 'Type In'),
        ('listening', 'Listening'),
        ('matching', 'Matching'),
        ('context', 'Context Clues'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES)
    
    # Content
    word_set = models.ForeignKey(WordSet, null=True, blank=True, on_delete=models.SET_NULL)
    words = models.ManyToManyField(Word)
    total_questions = models.IntegerField()
    
    # Results
    correct_answers = models.IntegerField(default=0)
    incorrect_answers = models.IntegerField(default=0)
    skipped_questions = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    accuracy_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    
    # Time tracking
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Rewards
    xp_earned = models.IntegerField(default=0)
    coins_earned = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'vocabulary_quizzes'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['quiz_type']),
        ]


class QuizQuestion(models.Model):
    """Individual question in a quiz"""
    quiz = models.ForeignKey(VocabularyQuiz, on_delete=models.CASCADE, related_name='questions')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    
    # Question details
    question_text = models.TextField()
    question_type = models.CharField(max_length=20)
    options = models.JSONField(null=True, blank=True)  # For multiple choice
    correct_answer = models.CharField(max_length=200)
    
    # User response
    user_answer = models.CharField(max_length=200, blank=True)
    is_correct = models.BooleanField(null=True)
    response_time_seconds = models.IntegerField(null=True)
    
    # Order
    question_number = models.IntegerField()
    
    class Meta:
        db_table = 'quiz_questions'
        ordering = ['quiz', 'question_number']