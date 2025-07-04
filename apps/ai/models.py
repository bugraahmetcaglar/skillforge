from django.db import models
from core.models import BaseModel


class IntentPattern(BaseModel):
    """Dynamic intent patterns that learn from user interactions"""

    intent_name = models.CharField(max_length=100, db_index=True)
    keywords = models.JSONField(default=list, help_text="Keywords for this intent")
    required_words = models.JSONField(default=list, help_text="Must-have words")
    weight = models.FloatField(default=1.0, help_text="Pattern importance weight")
    confidence_threshold = models.FloatField(default=0.3)

    # Learning metrics
    usage_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    failure_count = models.PositiveIntegerField(default=0)
    accuracy_rate = models.FloatField(default=0.0)

    # Dynamic updates
    auto_generated = models.BooleanField(default=False)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["intent_name"]),
            models.Index(fields=["accuracy_rate"]),
        ]

    def __str__(self):
        return f"{self.intent_name} (accuracy: {self.accuracy_rate:.2f})"

    def update_success_rate(self):
        """Calculate and update accuracy rate"""
        total = self.success_count + self.failure_count
        if total > 0:
            self.accuracy_rate = self.success_count / total
        self.save(update_fields=["accuracy_rate"])

    def record_usage(self, success: bool = True):
        """Record pattern usage and success/failure"""
        from django.utils import timezone

        self.usage_count += 1
        self.last_used = timezone.now()

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        self.update_success_rate()


class UserMessage(BaseModel):
    """Store user messages for learning"""

    telegram_user_id = models.BigIntegerField(db_index=True)
    message_text = models.TextField()
    processed_text = models.TextField()

    # AI results
    detected_intent = models.CharField(max_length=100, null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    extracted_entities = models.JSONField(default=dict)

    # User feedback
    user_confirmed = models.BooleanField(null=True, blank=True)
    correct_intent = models.CharField(max_length=100, null=True, blank=True)
    feedback_received = models.BooleanField(default=False)

    # Learning data
    pattern_used = models.ForeignKey(IntentPattern, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["telegram_user_id"]),
            models.Index(fields=["detected_intent"]),
        ]

    def __str__(self):
        return f"Message from {self.telegram_user_id}: {self.message_text[:50]}..."


class LearnedKeyword(BaseModel):
    """Keywords learned from user interactions"""

    keyword = models.CharField(max_length=100, db_index=True)
    intent = models.CharField(max_length=100, db_index=True)
    frequency = models.PositiveIntegerField(default=1)
    confidence = models.FloatField(default=0.5)

    # Learning source
    learned_from_message = models.ForeignKey(UserMessage, on_delete=models.CASCADE, null=True)
    auto_discovered = models.BooleanField(default=True)

    class Meta:
        unique_together = ["keyword", "intent"]
        indexes = [
            models.Index(fields=["intent", "confidence"]),
        ]

    def __str__(self):
        return f"{self.keyword} -> {self.intent} (freq: {self.frequency})"

    def increase_frequency(self):
        """Increase keyword frequency and confidence"""
        self.frequency += 1
        # Increase confidence but cap at 0.95
        self.confidence = min(0.95, self.confidence + 0.05)
        self.save()


class UserFeedback(BaseModel):
    """User feedback for improving AI"""

    user_message = models.ForeignKey(UserMessage, on_delete=models.CASCADE)
    feedback_type = models.CharField(
        max_length=50,
        choices=[
            ("correct", "Correct Response"),
            ("wrong_intent", "Wrong Intent Detected"),
            ("missing_info", "Missing Information"),
            ("unclear", "Unclear Response"),
        ],
    )

    suggested_intent = models.CharField(max_length=100, null=True, blank=True)
    feedback_text = models.TextField(null=True, blank=True)

    # Processing status
    processed = models.BooleanField(default=False)
    applied_to_model = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback: {self.feedback_type} for message {self.user_message.id}"
