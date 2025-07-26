from typing import Dict, Any, Optional
from apps.finance.models import UserSubscription
from apps.user.models import User
import json


def get_telegram_welcome_message(user: User) -> str:
    """Telegram karşılama mesajı"""
    return f"""
🤖 **Merhaba {user.get_full_name() or user.username}!**

Ben senin kişisel finans asistanınım! 

💰 **Soru Örnekleri:**
• "Bu ay ne kadar ödeyeceğim?"
• "Netflix aboneliğim var mı?"
• "En pahalı aboneliğim hangisi?"
• "Hangi kategoride en çok harcıyorum?"

⚡ **Komutlar:**
/help - Yardım menüsü
/status - AI durumu

Hemen soru sormaya başlayabilirsin! 🚀
    """


def get_telegram_help_message() -> str:
    """Telegram yardım mesajı"""
    return """
🆘 **Yardım Menüsü**

**💬 Nasıl Soru Sorarım?**
Doğal Türkçe ile yazabilirsin:
• "Spotify aboneliğim aktif mi?"
• "Bu ay toplam ne kadar ödeyeceğim?"
• "En ucuz aboneliğim hangisi?"

**📊 Soru Türleri:**
• Abonelik bilgileri
• Maliyet hesaplamaları  
• Kategori analizleri
• Ödeme takibi

**🤖 AI Durumu:**
/status komutuyla AI servisinin çalışıp çalışmadığını öğrenebilirsin.

Başka sorun var mı? 😊
    """


def get_ai_unavailable_message() -> str:
    """AI servisi kapalı mesajı"""
    return """
🔧 **AI Servisi Aktif Değil**

Üzgünüm, şu anda AI asistanı kullanılamıyor.

**📱 Alternatifler:**
• Web arayüzünden aboneliklerini görüntüleyebilirsin
• Manuel hesaplamalar yapabilirsin
• Daha sonra tekrar deneyebilirsin

**🛠️ Durum:**
AI servisi şu anda bakımda olabilir.

/status komutuyla durumu kontrol edebilirsin.
    """


def get_no_subscription_message(user: User) -> str:
    """Abonelik yok mesajı"""
    return f"""
📭 **Henüz Aboneliğin Yok**

Merhaba {user.get_full_name() or user.username}!

Henüz hiç abonelik eklememişsin. 

**🚀 Başlangıç:**
• Web arayüzünden aboneliklerini ekle
• Otomatik hatırlatmalar kur
• AI asistanıyla analiz yap

Abonelik ekledikten sonra benimle konuşabilirsin! 💪
    """


def get_user_financial_context(user: User) -> Optional[Dict[str, Any]]:
    """"""
    subscriptions = UserSubscription.objects.filter(user=user, status="active").select_related(
        "subscription_service", "subscription_service__category"
    )

    if not subscriptions.exists():
        return None

    total_monthly_try = 0
    subscription_list = []
    categories = {}

    for sub in subscriptions:
        # TRY'ye dönüştürme
        amount_try = float(sub.amount)
        if sub.currency == "USD":
            amount_try *= 30
        elif sub.currency == "EUR":
            amount_try *= 32

        total_monthly_try += amount_try

        # Kategori analizi
        category_name = sub.subscription_service.category.name if sub.subscription_service.category else "Diğer"
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
    """AI için sistem prompt'u oluştur"""
    return f"""Sen SkillForge platformunun Telegram finans asistanısın. 

Kullanıcı: {user_context['user_name']}
Toplam Abonelik: {user_context['total_count']} adet
Aylık Tahmini: {user_context['estimated_monthly_try']} TRY
Yıllık Tahmini: {user_context['estimated_yearly_try']} TRY

Aktif Abonelikler:
{json.dumps(user_context['subscriptions'], ensure_ascii=False, indent=2)}

Kategori Analizi:
{json.dumps(user_context['categories'], ensure_ascii=False, indent=2)}

Telegram Mesaj Kuralları:
1. Türkçe yanıt ver, samimi ol
2. Emoji kullan ama abartma
3. Kısa ve net açıklamalar (max 3 paragraf)
4. Para birimlerini belirt
5. Tarihleri dd/mm/yyyy formatında yaz
6. Finansal tavsiyelerde bulunabilirsin

Kullanıcının sorusunu kişisel verileriyle yanıtla."""


def format_telegram_error(error_type: str) -> str:
    """Telegram için hata mesajlarını formatla"""
    error_messages = {
        "no_data": "📭 Henüz aboneliğin yok. Web arayüzünden ekleyebilirsin.",
        "ai_unavailable": "🤖 AI servisi şu anda aktif değil. /status ile kontrol et.",
        "timeout": "⏱️ AI zaman aşımına uğradı. Tekrar dene.",
        "invalid_query": "❓ Soruyu anlayamadım. Daha açık bir şekilde sor.",
        "permission_denied": "🔒 Bu işlem için yetkin yok.",
        "user_not_found": "👤 Kullanıcı bulunamadı. Önce hesap bağla.",
    }
    return error_messages.get(error_type, "❌ Beklenmeyen hata oluştu.")
