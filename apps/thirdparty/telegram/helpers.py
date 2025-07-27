from typing import Dict, Any, Optional
from apps.finance.models import UserSubscription
from apps.user.models import User
import json


def get_telegram_welcome_message(user: User) -> str:
    """Telegram welcome message"""
    return f"""
🤖 **Hello {user.get_full_name() or user.username}!**

I'm your personal finance assistant! 

💰 **Example Questions:**
• "How much will I pay this month?"
• "Do I have a Netflix subscription?"
• "What's my most expensive subscription?"
• "Which category do I spend the most on?"

⚡ **Commands:**
/help - Help menu
/status - AI status

You can start asking questions right away! 🚀
    """


def get_telegram_help_message() -> str:
    """Telegram help message"""
    return """
🆘 **Help Menu**

**💬 How to Ask Questions?**
You can write in natural Turkish:
• "Is my Spotify subscription active?"
• "How much will I pay in total this month?"
• "What's my cheapest subscription?"

**📊 Question Types:**
• Subscription information
• Cost calculations  
• Category analysis
• Payment tracking

**🤖 AI Status:**
Use /status command to check if AI service is running.

Any other questions? 😊
    """


def get_ai_unavailable_message() -> str:
    """AI service unavailable message"""
    return """
🔧 **AI Service Not Active**

Sorry, AI assistant is currently unavailable.

**📱 Alternatives:**
• You can view your subscriptions via web interface
• You can do manual calculations
• You can try again later

**🛠️ Status:**
AI service might be under maintenance.

Check status with /status command.
    """


def get_no_subscription_message(user: User) -> str:
    """No subscription message"""
    return f"""
📭 **You Don't Have Any Subscriptions Yet**

Hello {user.get_full_name() or user.username}!

You haven't added any subscriptions yet. 

**🚀 Getting Started:**
• Add your subscriptions via web interface
• Set up automatic reminders
• Analyze with AI assistant

You can talk to me after adding subscriptions! 💪
    """


def get_user_financial_context(user: User) -> Optional[Dict[str, Any]]:
    """Get user's financial context"""
    subscriptions = UserSubscription.objects.filter(user=user, status="active").select_related(
        "subscription_service", "subscription_service__category"
    )

    if not subscriptions.exists():
        return None

    total_monthly_try = 0
    subscription_list = []
    categories = {}

    for sub in subscriptions:
        amount_try = float(sub.amount)
        if sub.currency == "USD":
            amount_try *= 30
        elif sub.currency == "EUR":
            amount_try *= 32

        total_monthly_try += amount_try

        category_name = sub.subscription_service.category.name if sub.subscription_service.category else "Other"
        if category_name not in categories:
            categories[category_name] = {"count": 0, "total": 0}
        categories[category_name]["count"] += 1
        categories[category_name]["total"] += amount_try

        subscription_list.append(
            {
                "name": sub.subscription_service.name,
                "amount": float(sub.amount),
                "currency": sub.currency,
                "amount_try": round(amount_try, 2),
                "cycle": sub.billing_cycle,
                "next_date": sub.next_billing_date.strftime("%d/%m/%Y") if sub.next_billing_date else None,
                "category": category_name,
            }
        )

    return {
        "user_name": user.get_full_name() or user.username,
        "subscriptions": subscription_list,
        "total_count": len(subscription_list),
        "estimated_monthly_try": round(total_monthly_try, 2),
        "estimated_yearly_try": round(total_monthly_try * 12, 2),
        "categories": categories,
    }


def create_system_prompt(user_context: Dict[str, Any]) -> str:
    """Create system prompt for AI"""
    return f"""You are SkillForge platform's Telegram finance assistant. 

User: {user_context['user_name']}
Total Subscriptions: {user_context['total_count']} items
Monthly Estimate: {user_context['estimated_monthly_try']} TRY
Yearly Estimate: {user_context['estimated_yearly_try']} TRY

Active Subscriptions:
{json.dumps(user_context['subscriptions'], ensure_ascii=False, indent=2)}

Category Analysis:
{json.dumps(user_context['categories'], ensure_ascii=False, indent=2)}

Telegram Message Rules:
1. Respond in Turkish, be friendly and helpful
2. Use emojis but don't overdo it
3. Keep explanations short and clear (max 3 paragraphs)
4. Specify currency units
5. Write dates in dd/mm/yyyy format
6. You can provide financial advice

Answer the user's question using their personal data."""


def format_telegram_error(error_type: str) -> str:
    """Format error messages for Telegram"""
    error_messages = {
        "no_data": "📭 You don't have any subscriptions yet. You can add them via web interface.",
        "ai_unavailable": "🤖 AI service is not active right now. Check with /status.",
        "timeout": "⏱️ AI timed out. Please try again.",
        "invalid_query": "❓ I couldn't understand the question. Please ask more clearly.",
        "permission_denied": "🔒 You don't have permission for this operation.",
        "user_not_found": "👤 User not found. Please link your account first.",
    }
    return error_messages.get(error_type, "❌ An unexpected error occurred.")