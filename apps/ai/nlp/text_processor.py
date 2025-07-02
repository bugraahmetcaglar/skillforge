import re
import json
from pathlib import Path
from typing import Dict, Any, List


class TurkishTextProcessor:
    """Turkish text preprocessing and entity extraction"""

    def __init__(self):
        self.stopwords = self._load_stopwords()
        self.time_patterns = self._load_time_patterns()
        self.financial_terms = self._load_financial_terms()
        self.interaction_patterns = self._load_interaction_patterns()

    def _load_stopwords(self) -> set:
        """Load stopwords from file"""
        file_path = Path(__file__).parent / "data" / "stopwords.txt"
        with open(file_path, "r", encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip()}

    def _load_time_patterns(self) -> dict:
        """Load time patterns from JSON file"""
        file_path = Path(__file__).parent / "data" / "time_patterns.json"
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_financial_terms(self) -> dict:
        """Load financial terms from JSON file"""
        file_path = Path(__file__).parent / "data" / "financial_terms.json"
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_interaction_patterns(self) -> dict:
        """Load interaction patterns from JSON file"""
        file_path = Path(__file__).parent / "data" / "interaction_patterns.json"
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def clean_text(self, text: str) -> str:
        """Clean text - simple approach, no normalization"""
        # Convert to lowercase
        text = text.lower()

        # Remove punctuation except Turkish characters
        text = re.sub(r"[^\w\sğüşıöçĞÜŞIÖÇ]", " ", text)

        # Remove extra whitespace
        text = " ".join(text.split())

        return text

    def remove_stopwords(self, text: str) -> str:
        """Remove Turkish stopwords"""
        words = text.split()
        filtered_words = [word for word in words if word not in self.stopwords]
        return " ".join(filtered_words)

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        entities = {}

        # Extract time period
        time_period = self._extract_time_period(text)
        if time_period:
            entities["time_period"] = time_period

        # Extract financial terms
        financial_context = self._extract_financial_context(text)
        if financial_context:
            entities["financial_context"] = financial_context

        # Extract interaction patterns
        interaction_type = self._extract_interaction_patterns(text)
        if interaction_type:
            entities["interaction_type"] = interaction_type

        # Extract amounts/numbers
        amounts = self._extract_amounts(text)
        if amounts:
            entities["amounts"] = amounts

        return entities

    def _extract_time_period(self, text: str) -> str | None:
        """Extract time period from text"""
        for period, patterns in self.time_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return period
        return None

    def _extract_financial_context(self, text: str) -> List[str]:
        """Extract financial context from text"""
        context = []
        for category, terms in self.financial_terms.items():
            for term in terms:
                if term in text:
                    context.append(category)
                    break
        return list(set(context))  # Remove duplicates

    def _extract_amounts(self, text: str) -> List[str]:
        """Extract monetary amounts"""
        amount_patterns = [r"\d+\s*tl", r"\d+\s*lira", r"\d+\s*₺", r"\d+\.\d+\s*tl", r"\d+,\d+\s*tl"]

        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            amounts.extend(matches)

        return amounts

    def _extract_interaction_patterns(self, text: str) -> str | None:
        """Extract interaction patterns from text"""
        for pattern_type, patterns in self.interaction_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return pattern_type
        return None
