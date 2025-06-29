from apps.finance.models import SubscriptionService, SubscriptionServiceCategory


def add_categories():
    """Populate subscription service categories - Run from shell"""

    categories_data = [
        {"name": "Video Streaming", "description": "Video streaming platforms like Netflix, Disney+"},
        {"name": "Music Streaming", "description": "Music streaming services like Spotify, Apple Music"},
        {"name": "Cloud Storage", "description": "Cloud storage services like Google Drive, Dropbox"},
        {"name": "Productivity", "description": "Productivity tools like Microsoft 365, Notion"},
        {"name": "Design", "description": "Design and creative tools like Adobe, Figma"},
        {"name": "Development", "description": "Development tools and platforms like GitHub, AWS"},
        {"name": "Communication", "description": "Communication tools like Slack, Zoom"},
        {"name": "Education", "description": "Learning platforms like Udemy, Coursera"},
        {"name": "Gaming", "description": "Gaming services like Xbox Game Pass, PlayStation Plus"},
        {"name": "VPN & Security", "description": "VPN and security services like NordVPN, 1Password"},
        {"name": "News & Media", "description": "News and media subscriptions like Medium, NYT"},
        {"name": "Health & Fitness", "description": "Health and fitness apps like MyFitnessPal, Strava"},
        {"name": "E-commerce", "description": "E-commerce premium services like Amazon Prime"},
        {"name": "Finance", "description": "Financial services like Revolut, Tosla"},
        {"name": "Transportation", "description": "Transportation services like Uber One"},
        {"name": "Dating", "description": "Dating services like Tinder Plus, Bumble Boost"},
        {"name": "AI Services", "description": "AI and machine learning services like OpenAI, Jasper"},
        {"name": "Travel", "description": "Travel booking services like Expedia, Booking.com"},
        {"name": "Entertainment", "description": "Entertainment services like Hulu, Peacock"},
        {"name": "Newsletter", "description": "Newsletter subscriptions like Substack, Revue"},
        {"name": "Fitness", "description": "Fitness and wellness apps like Fitbit Premium, Peloton"},
        {"name": "Gaming Services", "description": "Gaming subscription services like EA Play, Ubisoft+"},
        {"name": "Social Media", "description": "Social media premium features like Twitter Blue"},
        {"name": "Shopping", "description": "Shopping and retail subscriptions like Walmart+."},
        {"name": "News", "description": "News subscriptions like The Guardian, BBC News"},
        {"name": "Music", "description": "Music subscriptions like Tidal, Deezer"},
        {"name": "Video", "description": "Video subscriptions like Vimeo, Dailymotion"},
        {"name": "Books", "description": "Book subscription services like Audible, Kindle Unlimited"},
        {"name": "Software", "description": "Software tools and services like Microsoft Visual Studio"},
        {"name": "Hardware", "description": "Hardware subscription services like AppleCare+"},
        {"name": "Automation", "description": "Automation tools like Zapier, IFTTT Pro"},
        {"name": "Marketing", "description": "Marketing tools and platforms like Mailchimp Pro"},
        {"name": "Gaming Subscriptions", "description": ""},
        {"name": "Cloud Services", "description": ""},
        {"name": "Computer Programs", "description": ""},
        {"name": "Mobile Apps", "description": ""},
        {"name": "Web Service", "description": ""},
        {"name": "Other", "description": "Other subscription services not categorized above"},
    ]

    print(f"Starting to populate categories...")

    SubscriptionServiceCategory.objects.bulk_create(
        [
            SubscriptionServiceCategory(
                name=category_data["name"],
                description=category_data.get("description", ""),
            )
            for category_data in categories_data
        ],
        ignore_conflicts=True,  # Ignore duplicates based on unique constraints
    )

    print(f"\n🎉 Completed!")


def start():
    """Populate subscription services - Run from shell"""

    categories = {c.name: c for c in SubscriptionServiceCategory.objects.all()}
    services_data = [
        # Video Streaming
        {"name": "Netflix", "category": categories["Video Streaming"], "website_url": "https://netflix.com"},
        {
            "name": "Amazon Prime Video",
            "category": categories["Video Streaming"],
            "website_url": "https://primevideo.com",
        },
        {"name": "Disney+", "category": categories["Video Streaming"], "website_url": "https://disneyplus.com"},
        {
            "name": "YouTube Premium",
            "category": categories["Video Streaming"],
            "website_url": "https://youtube.com/premium",
        },
        {"name": "Apple TV+", "category": categories["Video Streaming"], "website_url": "https://tv.apple.com"},
        {"name": "HBO Max", "category": categories["Video Streaming"], "website_url": "https://hbomax.com"},
        {"name": "Exxen", "category": categories["Video Streaming"], "website_url": "https://exxen.com"},
        {"name": "BluTV", "category": categories["Video Streaming"], "website_url": "https://blutv.com"},
        {"name": "Puhu TV", "category": categories["Video Streaming"], "website_url": "https://puhutv.com"},
        {"name": "Gain", "category": categories["Video Streaming"], "website_url": "https://gain.tv"},
        {"name": "TOD", "category": categories["Video Streaming"], "website_url": "https://tod.tv"},
        {"name": "Tabii", "category": categories["Video Streaming"], "website_url": "https://tabii.com"},
        # Music Streaming
        {"name": "Spotify", "category": categories["Music Streaming"], "website_url": "https://spotify.com"},
        {"name": "Apple Music", "category": categories["Music Streaming"], "website_url": "https://music.apple.com"},
        {
            "name": "YouTube Music",
            "category": categories["Music Streaming"],
            "website_url": "https://music.youtube.com",
        },
        {"name": "Amazon Music", "category": categories["Music Streaming"], "website_url": "https://music.amazon.com"},
        {"name": "Deezer", "category": categories["Music Streaming"], "website_url": "https://deezer.com"},
        {"name": "Tidal", "category": categories["Music Streaming"], "website_url": "https://tidal.com"},
        {"name": "Fizy", "category": categories["Music Streaming"], "website_url": "https://fizy.com"},
        {"name": "Muud", "category": categories["Music Streaming"], "website_url": "https://muud.com"},
        # Cloud Storage
        {"name": "Google Drive", "category": categories["Cloud Storage"], "website_url": "https://drive.google.com"},
        {"name": "Dropbox", "category": categories["Cloud Storage"], "website_url": "https://dropbox.com"},
        {"name": "iCloud+", "category": categories["Cloud Storage"], "website_url": "https://icloud.com"},
        {"name": "OneDrive", "category": categories["Cloud Storage"], "website_url": "https://onedrive.com"},
        {"name": "MEGA", "category": categories["Cloud Storage"], "website_url": "https://mega.nz"},
        # Productivity
        {
            "name": "Microsoft 365",
            "category": categories["Productivity"],
            "website_url": "https://microsoft.com/microsoft-365",
        },
        {
            "name": "Google Workspace",
            "category": categories["Productivity"],
            "website_url": "https://workspace.google.com",
        },
        {"name": "Notion", "category": categories["Productivity"], "website_url": "https://notion.so"},
        {"name": "Todoist", "category": categories["Productivity"], "website_url": "https://todoist.com"},
        {"name": "Evernote", "category": categories["Productivity"], "website_url": "https://evernote.com"},
        {"name": "Asana", "category": categories["Productivity"], "website_url": "https://asana.com"},
        {"name": "Trello", "category": categories["Productivity"], "website_url": "https://trello.com"},
        # Design & Creative
        {"name": "Adobe Creative Cloud", "category": categories["Design"], "website_url": "https://adobe.com"},
        {"name": "Canva Pro", "category": categories["Design"], "website_url": "https://canva.com"},
        {"name": "Figma", "category": categories["Design"], "website_url": "https://figma.com"},
        {"name": "Sketch", "category": categories["Design"], "website_url": "https://sketch.com"},
        # Development
        {"name": "GitHub", "category": categories["Development"], "website_url": "https://github.com"},
        {"name": "JetBrains", "category": categories["Development"], "website_url": "https://jetbrains.com"},
        {"name": "Visual Studio", "category": categories["Development"], "website_url": "https://visualstudio.com"},
        {"name": "AWS", "category": categories["Development"], "website_url": "https://aws.amazon.com"},
        {"name": "Google Cloud", "category": categories["Development"], "website_url": "https://cloud.google.com"},
        {"name": "DigitalOcean", "category": categories["Development"], "website_url": "https://digitalocean.com"},
        {"name": "Vercel", "category": categories["Development"], "website_url": "https://vercel.com"},
        {"name": "Netlify", "category": categories["Development"], "website_url": "https://netlify.com"},
        # Communication
        {"name": "Slack", "category": categories["Communication"], "website_url": "https://slack.com"},
        {"name": "Zoom", "category": categories["Communication"], "website_url": "https://zoom.us"},
        {
            "name": "Microsoft Teams",
            "category": categories["Communication"],
            "website_url": "https://teams.microsoft.com",
        },
        {"name": "Discord Nitro", "category": categories["Communication"], "website_url": "https://discord.com"},
        {"name": "Telegram Premium", "category": categories["Communication"], "website_url": "https://telegram.org"},
        # Education
        {"name": "Udemy", "category": categories["Education"], "website_url": "https://udemy.com"},
        {"name": "Coursera", "category": categories["Education"], "website_url": "https://coursera.org"},
        {
            "name": "LinkedIn Learning",
            "category": categories["Education"],
            "website_url": "https://linkedin.com/learning",
        },
        {"name": "Pluralsight", "category": categories["Education"], "website_url": "https://pluralsight.com"},
        {"name": "MasterClass", "category": categories["Education"], "website_url": "https://masterclass.com"},
        {"name": "Duolingo Plus", "category": categories["Education"], "website_url": "https://duolingo.com"},
        # Gaming
        {"name": "Xbox Game Pass", "category": categories["Gaming"], "website_url": "https://xbox.com/game-pass"},
        {"name": "PlayStation Plus", "category": categories["Gaming"], "website_url": "https://playstation.com/plus"},
        {"name": "Steam", "category": categories["Gaming"], "website_url": "https://store.steampowered.com"},
        {"name": "EA Play", "category": categories["Gaming"], "website_url": "https://ea.com/ea-play"},
        # VPN & Security
        {"name": "NordVPN", "category": categories["VPN & Security"], "website_url": "https://nordvpn.com"},
        {"name": "ExpressVPN", "category": categories["VPN & Security"], "website_url": "https://expressvpn.com"},
        {"name": "Surfshark", "category": categories["VPN & Security"], "website_url": "https://surfshark.com"},
        {"name": "1Password", "category": categories["VPN & Security"], "website_url": "https://1password.com"},
        {"name": "LastPass", "category": categories["VPN & Security"], "website_url": "https://lastpass.com"},
        {"name": "Bitwarden", "category": categories["VPN & Security"], "website_url": "https://bitwarden.com"},
        # News & Media
        {"name": "Medium", "category": categories["News & Media"], "website_url": "https://medium.com"},
        {"name": "New York Times", "category": categories["News & Media"], "website_url": "https://nytimes.com"},
        {"name": "Wall Street Journal", "category": categories["News & Media"], "website_url": "https://wsj.com"},
        # Health & Fitness
        {
            "name": "MyFitnessPal Premium",
            "category": categories["Health & Fitness"],
            "website_url": "https://myfitnesspal.com",
        },
        {"name": "Strava Premium", "category": categories["Health & Fitness"], "website_url": "https://strava.com"},
        {"name": "Headspace", "category": categories["Health & Fitness"], "website_url": "https://headspace.com"},
        {"name": "Calm", "category": categories["Health & Fitness"], "website_url": "https://calm.com"},
        # E-commerce
        {"name": "Amazon Prime", "category": categories["E-commerce"], "website_url": "https://amazon.com/prime"},
        {"name": "Trendyol Premium", "category": categories["E-commerce"], "website_url": "https://trendyol.com"},
        {
            "name": "Hepsiburada Premium",
            "category": categories["E-commerce"],
            "website_url": "https://hepsiburada.com",
        },
        {"name": "N11 Premium", "category": categories["E-commerce"], "website_url": "https://n11.com"},
        # Finance
        {"name": "Tosla Premium", "category": categories["Finance"], "website_url": "https://tosla.com"},
        {"name": "Revolut Premium", "category": categories["Finance"], "website_url": "https://revolut.com"},
        # Transportation
        {"name": "Uber One", "category": categories["Transportation"], "website_url": "https://uber.com"},
        {"name": "BiTaksi Premium", "category": categories["Transportation"], "website_url": "https://bitaksi.com"},
    ]
    print(f"Starting to populate services...")

    try:
        SubscriptionService.objects.bulk_create(
            [
                SubscriptionService(
                    name=service_data["name"],
                    description=service_data.get("description", ""),
                    category=service_data["category"],
                    logo_url=service_data.get("logo_url", ""),
                    website_url=service_data.get("website_url", ""),
                )
                for service_data in services_data
            ],
            ignore_conflicts=True,  # Ignore duplicates based on unique constraints
        )

        print(f"\n🎉 Completed!")
    except Exception as err:
        print(f"Error occurred while populating services: {err}")
