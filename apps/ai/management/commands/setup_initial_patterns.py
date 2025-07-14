from django.core.management.base import BaseCommand
from apps.ai.models import IntentPattern


class Command(BaseCommand):
    help = "Setup initial intent patterns for AI learning"

    def handle(self, *args, **options):
        """Create basic intent patterns"""

        initial_patterns = [
            {
                "intent_name": "greeting",
                "keywords": ["merhaba", "selam", "sa"],
                "required_words": [],
                "weight": 1.0,
                "confidence_threshold": 0.2,
            },
            {
                "intent_name": "subscription_next_month_cost",
                "keywords": ["gelecek", "ay", "abonelik", "tutar"],
                "required_words": ["gelecek", "abonelik"],
                "weight": 1.0,
                "confidence_threshold": 0.4,
            },
            {
                "intent_name": "help",
                "keywords": ["yardım", "help"],
                "required_words": ["yardım"],
                "weight": 1.0,
                "confidence_threshold": 0.3,
            },
        ]

        created_count = 0
        for pattern_data in initial_patterns:
            pattern, created = IntentPattern.objects.get_or_create(
                intent_name=pattern_data["intent_name"], defaults=pattern_data
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created pattern: {pattern.intent_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Pattern already exists: {pattern.intent_name}"))

        self.stdout.write(self.style.SUCCESS(f"Setup complete! Created {created_count} new patterns."))
