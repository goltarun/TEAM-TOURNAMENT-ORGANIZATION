import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ff_squad_admin.settings')
django.setup()

from django.contrib.auth.models import User
from squad.models import Player, Tournament, TournamentRegistration, News

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created: admin/admin123")

# Create sample data
print("Creating sample data...")

# Sample Players
players_data = [
    {
        'name': 'Viper_FF',
        'game_type': 'BR',
        'role': 'Rusher',
        'rank': 'Grandmaster',
        'age': 19,
        'id_code': '12345678',
        'experience': 'Pro',
        'playing_time': 'Night',
        'bio': 'Best rusher in state. Aggressive gameplay.',
        'contact': '9876543210',
        'verified': True
    },
    {
        'name': 'Silent_Killer',
        'game_type': 'CS',
        'role': 'Sniper',
        'rank': 'Heroic',
        'age': 21,
        'id_code': '87654321',
        'experience': 'Advanced',
        'playing_time': 'Evening',
        'bio': 'One tap specialist. I never miss a headshot.',
        'contact': '9822334455',
        'verified': True
    },
    {
        'name': 'Pro_Support',
        'game_type': 'BR',
        'role': 'Support',
        'rank': 'Diamond IV',
        'age': 17,
        'id_code': '11223344',
        'experience': 'Intermediate',
        'playing_time': 'Morning',
        'bio': 'I provide best backup. Team player.',
        'contact': '9123456789',
        'verified': False
    },
    {
        'name': 'Legend_Booyah',
        'game_type': 'CS',
        'role': 'Assaulter',
        'rank': 'Heroic',
        'age': 20,
        'id_code': '44332211',
        'experience': 'Advanced',
        'playing_time': 'Flexible',
        'bio': 'Looking for a competitive squad for tournaments.',
        'contact': '9554433221',
        'verified': False
    }
]

for player_data in players_data:
    if not Player.objects.filter(id_code=player_data['id_code']).exists():
        Player.objects.create(**player_data)
        print(f"Created player: {player_data['name']}")

# Sample Tournaments
tournaments_data = [
    {
        'title': 'Mega Booyah Cup',
        'prize': '₹10,000',
        'entry_fee': '₹50',
        'per_kill': '₹20',
        'date': '2024-04-25',
        'time': '20:00:00',
        'mode': 'Squad',
        'map_name': 'Bermuda',
        'status': 'Open',
        'max_slots': 50,
        'description': 'Biggest tournament of the month with massive prize pool!',
        'rules': 'No Hack / No Emulator players allowed. Teaming up with enemies leads to permanent ban.'
    },
    {
        'title': 'Solo Survival Pro',
        'prize': '₹5,000',
        'entry_fee': 'Free',
        'per_kill': '₹10',
        'date': '2024-04-30',
        'time': '16:00:00',
        'mode': 'Solo',
        'map_name': 'Purgatory',
        'status': 'Open',
        'max_slots': 50,
        'description': 'Test your solo skills in this intense battle.',
        'rules': 'Standard BR rules apply. No teaming allowed.'
    },
    {
        'title': 'Duo Masters BR',
        'prize': '₹3,000',
        'entry_fee': '₹40',
        'per_kill': '₹15',
        'date': '2024-04-28',
        'time': '21:00:00',
        'mode': 'Duo',
        'map_name': 'Kalahari',
        'status': 'Open',
        'max_slots': 26,
        'description': 'Perfect tournament for duo partners.',
        'rules': 'Duo rules apply. Communication is key!'
    },
    {
        'title': 'CS Clash Royale',
        'prize': '₹2,500',
        'entry_fee': '₹30',
        'per_kill': 'N/A',
        'date': '2024-05-05',
        'time': '19:30:00',
        'mode': 'CS Squad',
        'map_name': 'Bermuda (Remastered)',
        'status': 'Coming Soon',
        'max_slots': 25,
        'description': 'Counter Strike mode tournament.',
        'rules': 'CS rules apply. Strategic gameplay required.'
    }
]

for tournament_data in tournaments_data:
    if not Tournament.objects.filter(title=tournament_data['title']).exists():
        Tournament.objects.create(**tournament_data)
        print(f"Created tournament: {tournament_data['title']}")

# Sample News
news_data = [
    {
        'title': 'Season 40 Rewards leaked!',
        'content': 'New Thompson skin and exclusive bundle coming next month.',
        'date_display': 'Today',
        'is_active': True
    },
    {
        'title': 'Character Buffs Update',
        'content': 'Chronos shield cooldown reduced by 5 seconds in latest patch.',
        'date_display': 'Yesterday',
        'is_active': True
    }
]

for news_item in news_data:
    if not News.objects.filter(title=news_item['title']).exists():
        News.objects.create(**news_item)
        print(f"Created news: {news_item['title']}")

print("Sample data creation completed!")
print("Admin login: http://127.0.0.1:8000/admin/")
print("Username: admin")
print("Password: admin123")
