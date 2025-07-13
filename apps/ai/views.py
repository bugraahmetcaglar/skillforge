from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.views import BaseAPIView
from apps.ai.services.dataset_loader import DatasetLoader

class AITrainingAPIView(BaseAPIView):
    """API for training AI with new data"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Train AI with user feedback"""
        message_text = request.data.get('message_text')
        correct_intent = request.data.get('correct_intent')
        
        if not message_text or not correct_intent:
            return self.error_response(
                "message_text and correct_intent required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Learn from user correction
        # feedback_service = UserFeedbackService()
        feedback_service = None
        try:
            # This would normally update patterns
            result = feedback_service.learn_from_user_input(
                message_text=message_text,
                correct_intent=correct_intent,
                user_id=request.user.id
            )
            
            return self.success_response(
                data=result,
                message="AI updated with your feedback"
            )
            
        except Exception as e:
            return self.error_response(f"Training failed: {e}")

class AITestAPIView(BaseAPIView):
    """API for testing AI accuracy"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get AI accuracy metrics"""
        from apps.ai.services.dataset_quality_checker import DatasetQualityChecker
        
        checker = DatasetQualityChecker()
        analysis = checker.analyze_dataset_quality()
        
        return self.success_response(data=analysis)
    
    def post(self, request):
        """Test AI with sample message"""
        message_text = request.data.get('message_text')
        
        if not message_text:
            return self.error_response("message_text required")
        
        from apps.ai.nlp.message_processor import TelegramMessageProcessor
        
        processor = TelegramMessageProcessor()
        result = processor.process_message(message_text, request.user.id)
        
        return self.success_response(data={
            'intent': result.intent,
            'confidence': result.confidence,
            'entities': result.entities,
            'original_text': result.original_text
        })