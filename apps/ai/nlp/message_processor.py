from __future__ import annotations

import logging
from dataclasses import dataclass

from apps.ai.models import IntentPattern

logger = logging.getLogger(__name__)


@dataclass
class ProcessedMessage:
    """Processed message with extracted intent and entities"""

    original_text: str
    cleaned_text: str
    intent: str = ""
    entities: dict | None = None
    confidence: float = 0.0
    pattern_id: int | None = None

    def __post_init__(self):
        if self.entities is None:
            self.entities = {}


class TelegramMessageProcessor:
    """Main message processor for Telegram bot"""

    def __init__(self):
        from apps.ai.nlp.text_processor import TurkishTextProcessor

        self.text_processor = TurkishTextProcessor()

    def process_message(self, message_text: str, user_id: int) -> ProcessedMessage:
        """Process incoming message and extract intent + entities"""

        logger.info(f"Processing message from user {user_id}: {message_text}")

        # Clean and preprocess text
        cleaned_text = self.text_processor.clean_text(text=message_text)

        # Extract entities first
        entities = self.text_processor.extract_entities(text=cleaned_text)

        # Classify intent using database patterns
        intent_result = self._classify_intent(text=cleaned_text, user_id=user_id)

        processed = ProcessedMessage(
            original_text=message_text,
            cleaned_text=cleaned_text,
            intent=intent_result.get("intent", "unknown"),
            confidence=intent_result.get("confidence", 0.0),
            entities=entities,
            pattern_id=intent_result.get("pattern_id"),
        )

        logger.info(f"Processed result: intent={processed.intent}, confidence={processed.confidence}")

        return processed

    def _classify_intent(self, text: str, user_id: int) -> dict:
        """Classify intent using database patterns"""
        from apps.ai.models import IntentPattern, UserMessage

        # Get active patterns sorted by accuracy
        patterns = IntentPattern.objects.filter(is_active=True).order_by("-accuracy_rate", "-usage_count")

        logger.info(f"Found {patterns.count()} patterns in database")

        if not patterns.exists():
            # No patterns yet, store message for future learning
            self._store_unknown_message(text=text, user_id=user_id)
            return {"intent": "unknown", "confidence": 0.0}

        words = text.lower().split()
        logger.info(f"Processing words: {words}")

        scores = {}
        pattern_used = None

        for pattern in patterns:
            logger.info(
                f"Testing pattern: {pattern.intent_name}, keywords: {pattern.keywords}, required: {pattern.required_words}"
            )  # DEBUG
            score = self._calculate_pattern_score(words, pattern)
            logger.info(
                f"Pattern {pattern.intent_name} scored: {score}, threshold: {pattern.confidence_threshold}"
            )  # DEBUG

            if score > pattern.confidence_threshold:
                scores[pattern.intent_name] = {"score": score, "pattern": pattern}
            else:
                logger.info(
                    f"Pattern {pattern.intent_name} failed threshold check: {score} <= {pattern.confidence_threshold}"
                )  # DEBUG

        logger.info(f"Final scores: {scores}")

        if not scores:
            self._store_unknown_message(text=text, user_id=user_id)
            return {"intent": "unknown", "confidence": 0.0}

        # Get best match
        best_intent = max(scores, key=lambda x: scores[x]["score"])
        best_score = scores[best_intent]["score"]
        pattern_used = scores[best_intent]["pattern"]

        # Record pattern usage
        pattern_used.record_usage(success=True)

        # Store message for learning
        self._store_classified_message(
            text=text, user_id=user_id, intent=best_intent, confidence=best_score, pattern=pattern_used
        )

        return {"intent": best_intent, "confidence": best_score, "pattern_id": pattern_used.id}

    def _calculate_pattern_score(self, words: list[str], pattern: IntentPattern) -> float:
        """Calculate similarity score for a pattern"""

        text = " ".join(words)

        # Check required words first
        for required in pattern.required_words:
            if required not in text:
                return 0.0

        # Calculate keyword matches
        keyword_matches = sum(1 for keyword in pattern.keywords if keyword in text)

        if keyword_matches == 0:
            return 0.0

        # Calculate score
        keyword_ratio = keyword_matches / len(pattern.keywords) if pattern.keywords else 0
        base_score = keyword_ratio * pattern.weight

        # Apply accuracy multiplier
        accuracy_multiplier = pattern.accuracy_rate if pattern.accuracy_rate > 0 else 0.5
        total_score = base_score * accuracy_multiplier

        return min(total_score, 1.0)

    def _store_classified_message(
        self, text: str, user_id: int, intent: str, confidence: float, pattern: IntentPattern
    ):
        """Store classified message for learning"""
        from apps.ai.models import UserMessage

        UserMessage.objects.create(
            telegram_user_id=user_id,
            message_text=text,
            processed_text=text.lower(),
            detected_intent=intent,
            confidence_score=confidence,
            pattern_used=pattern,
        )

    def _store_unknown_message(self, text: str, user_id: int):
        """Store unknown message for future learning"""
        from apps.ai.models import UserMessage

        UserMessage.objects.create(
            telegram_user_id=user_id,
            message_text=text,
            processed_text=text.lower(),
            detected_intent="unknown",
            confidence_score=0.0,
        )

        logger.info(f"Stored unknown message for learning: {text}")
