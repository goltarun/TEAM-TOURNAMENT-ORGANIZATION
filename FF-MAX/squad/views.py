import json
from datetime import timedelta

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum
from django.urls import reverse
from django.utils import timezone
from .models import Player, Tournament, TournamentRegistration, News


# ───────────────────────────────────────────────────────────────
# USER PANEL
# ───────────────────────────────────────────────────────────────

def user_home(request):
    """Serve the public user home page"""
    return render(request, 'user/index.html', {'active_nav': 'home'})

def tournaments_page(request):
    """Tournaments listing page"""
    return render(request, 'user/tournaments.html', {'active_nav': 'tournaments'})

def players_page(request):
    """Players listing page"""
    return render(request, 'user/players.html', {'active_nav': 'players'})

def register_page(request):
    """Player registration page"""
    return render(request, 'user/register.html', {'active_nav': 'register'})

def news_page(request):
    """News listing page"""
    return render(request, 'user/news.html', {'active_nav': 'news'})


# ───────────────────────────────────────────────────────────────
# API ENDPOINTS (for the React user panel)
# ───────────────────────────────────────────────────────────────

def api_players(request):
    """Return all active players as JSON"""
    players = Player.objects.all().order_by('-created_at')
    data = [
        {
            'id': p.id,
            'name': p.name,
            'role': p.role,
            'rank': p.rank,
            'game_type': p.game_type,
            'verified': p.verified,
            'contact': p.contact,
            'age': p.age,
            'id_code': p.id_code,
            'experience': p.experience,
            'playing_time': p.playing_time,
            'bio': p.bio or '',
        }
        for p in players
    ]
    return JsonResponse(data, safe=False)


def api_tournaments(request):
    """Return all tournaments as JSON"""
    tournaments = Tournament.objects.all().order_by('-date')
    data = [
        {
            'id': t.id,
            'title': t.title,
            'prize': t.prize,
            'date': str(t.date),
            'time': t.time.strftime('%I:%M %p') if t.time else '',
            'per_kill': t.per_kill,
            'map': t.map_name,
            'game_mode': t.game_mode,
            'mode': t.mode,
            'entry': t.entry_fee,
            'status': t.status,
            'max_slots': t.max_slots,
            'available_slots': t.available_slots,
            'rules': t.rules or '',
        }
        for t in tournaments
    ]
    return JsonResponse(data, safe=False)


def api_news(request):
    """Return active news items as JSON"""
    news_items = News.objects.filter(is_active=True).order_by('-created_at')
    data = [
        {
            'id': n.id,
            'title': n.title,
            'content': n.content,
            'date': n.date_display,
        }
        for n in news_items
    ]
    return JsonResponse(data, safe=False)


@csrf_exempt
def api_register_player(request):
    """Create a new player from the React registration form"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    # Basic validation
    required = ['name', 'role', 'rank', 'game_type', 'contact', 'id_code', 'age']
    for field in required:
        if not body.get(field):
            return JsonResponse({'success': False, 'error': f'{field} is required'}, status=400)

    # Duplicate check
    if Player.objects.filter(id_code=body.get('id_code')).exists():
        return JsonResponse({'success': False, 'error': 'Game UID already registered'}, status=400)
    if Player.objects.filter(contact=body.get('contact')).exists():
        return JsonResponse({'success': False, 'error': 'WhatsApp number already registered'}, status=400)

    player = Player.objects.create(
        name=body.get('name'),
        role=body.get('role'),
        rank=body.get('rank'),
        game_type=body.get('game_type'),
        contact=body.get('contact'),
        id_code=body.get('id_code'),
        age=int(body.get('age', 18)),
        experience=body.get('experience', 'Beginner'),
        playing_time=body.get('playing_time', 'Flexible'),
        bio=body.get('bio', ''),
        verified=False,
    )
    return JsonResponse({'success': True, 'player_id': player.id})


@csrf_exempt
def api_register_tournament(request):
    """Create a tournament registration from the React join form"""
    if request.method == 'GET':
        registrations = TournamentRegistration.objects.all().values(
            'id', 'tournament', 'slot_number', 'player_name', 'team_name', 'contact_number', 'payment_status'
        )
        return JsonResponse(list(registrations), safe=False)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    tournament_id = body.get('tournament_id')
    team_name = body.get('team_name', 'Solo')
    contact = body.get('contact')
    slot_number = body.get('slot_number')
    player_name = body.get('player_name', 'Player')
    device_time = body.get('device_registration_time')

    if not all([tournament_id, contact, slot_number]):
        return JsonResponse({'success': False, 'error': 'Tournament, contact and slot number are required'}, status=400)

    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tournament not found'}, status=404)

    try:
        slot_number = int(slot_number)
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid slot number'}, status=400)

    if slot_number < 1 or slot_number > tournament.max_slots:
        return JsonResponse({'success': False, 'error': 'Slot is outside tournament limit'}, status=400)

    # Slot uniqueness check
    if TournamentRegistration.objects.filter(tournament=tournament, slot_number=slot_number).exists():
        return JsonResponse({'success': False, 'error': 'Slot already taken'}, status=400)

    # Parse device registration time if provided
    device_registration_time = None
    if device_time:
        try:
            from datetime import datetime
            device_registration_time = datetime.fromisoformat(device_time.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            pass  # If parsing fails, just use None

    reg = TournamentRegistration.objects.create(
        tournament=tournament,
        player_name=player_name,
        team_name=team_name,
        contact_number=contact,
        slot_number=slot_number,
        payment_status='Pending' if tournament.entry_fee != 'Free' else 'Confirmed',
        payment_amount=tournament.entry_fee if tournament.entry_fee != 'Free' else None,
        device_registration_time=device_registration_time,
    )
    payment_required = tournament.entry_fee != 'Free'
    return JsonResponse({
        'success': True, 
        'registration_id': reg.id,
        'payment_required': payment_required,
        'entry_fee': tournament.entry_fee if payment_required else None
    })


@csrf_exempt
def api_confirm_payment(request):
    """Mark tournament registration payment as paid"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body)
        reg_id = body.get('registration_id')
        transaction_id = body.get('transaction_id', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    if not transaction_id:
        return JsonResponse({'success': False, 'error': 'Transaction ID is required'}, status=400)

    try:
        reg = TournamentRegistration.objects.get(id=reg_id)
        reg.payment_status = 'Paid'
        reg.payment_confirmed_at = timezone.now()
        reg.transaction_id = transaction_id
        reg.save(update_fields=['payment_status', 'payment_confirmed_at', 'transaction_id'])
        return JsonResponse({'success': True, 'message': 'Payment confirmed'})
    except TournamentRegistration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Registration not found'}, status=404)


# ───────────────────────────────────────────────────────────────
# ADMIN PANEL
# ───────────────────────────────────────────────────────────────

def dashboard(request):
    """Admin dashboard with statistics"""
    context = {
        'total_players': Player.objects.count(),
        'total_tournaments': Tournament.objects.count(),
        'total_registrations': TournamentRegistration.objects.count(),
        'verified_players': Player.objects.filter(verified=True).count(),
        'active_tournaments': Tournament.objects.count(),
        'recent_players': Player.objects.all()[:5],
        'recent_registrations': TournamentRegistration.objects.all()[:5],
        'upcoming_tournaments': Tournament.objects.all().order_by('date')[:5],
    }
    return render(request, 'admin/dashboard.html', context)

def player_list(request):
    """List all players"""
    players = Player.objects.all().order_by('-created_at')
    context = {
        'players': players,
        'verified_count': players.filter(verified=True).count(),
        'br_count': players.filter(game_type='BR').count(),
    }
    return render(request, 'admin/player_list.html', context)

def tournament_list(request):
    """List all tournaments"""
    query = request.GET.get('q', '').strip()
    tournaments = Tournament.objects.all()

    if query:
        tournaments = tournaments.filter(title__icontains=query)

    tournaments = tournaments.order_by('date')
    today = timezone.now().date()
    alert_tournaments = []
    for tournament in tournaments:
        if not tournament.alert_cancelled and tournament.date and tournament.date <= today + timedelta(days=2):
            alert_tournaments.append(tournament)

    otp_sent = request.GET.get('otp_sent') == '1'
    otp_code = request.GET.get('otp_code', '').strip()

    total_regs = sum(t.registrations.count() for t in tournaments)
    context = {
        'tournaments': tournaments,
        'query': query,
        'alert_tournaments': alert_tournaments,
        'active_count': tournaments.count(),
        'free_count': tournaments.filter(entry_fee='Free').count(),
        'total_regs': total_regs,
        'otp_sent': otp_sent,
        'otp_code': otp_code,
    }
    return render(request, 'admin/tournament_list.html', context)

def registration_list(request):
    """List all tournament registrations"""
    query = request.GET.get('q', '').strip()
    registrations = TournamentRegistration.objects.select_related('tournament').all()

    if query:
        registrations = registrations.filter(
            tournament__title__icontains=query
        )

    registrations = registrations.order_by('tournament__date', 'tournament__title', '-registered_at')
    confirmed_statuses = ['Confirmed', 'Paid']
    context = {
        'registrations': registrations,
        'query': query,
        'paid_count': registrations.filter(payment_status='Paid').count(),
        'pending_count': registrations.filter(payment_status='Pending').count(),
        'confirmed_count': registrations.filter(payment_status__in=confirmed_statuses).count(),
    }
    return render(request, 'admin/registration_list.html', context)


def tournament_registrations(request, tournament_id):
    """Show all registrations for one tournament with full details"""
    tournament = Tournament.objects.get(id=tournament_id)
    registrations = TournamentRegistration.objects.filter(tournament=tournament).order_by('slot_number', '-registered_at')
    confirmed_statuses = ['Confirmed', 'Paid']
    context = {
        'tournament': tournament,
        'registrations': registrations,
        'paid_count': registrations.filter(payment_status='Paid').count(),
        'pending_count': registrations.filter(payment_status='Pending').count(),
        'confirmed_count': registrations.filter(payment_status__in=confirmed_statuses).count(),
    }
    return render(request, 'admin/tournament_registrations.html', context)


def cancel_tournament_alert(request, tournament_id):
    """Send an OTP to the provided phone number and confirm it before cancelling the alert."""
    tournament = Tournament.objects.get(id=tournament_id)
    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        if action == 'send_otp':
            import random
            otp_code = f"{random.randint(100000, 999999)}"
            request.session['tournament_alert_otp'] = otp_code
            request.session['tournament_alert_phone_number'] = '6353978826'
            request.session['tournament_alert_tournament_id'] = tournament_id
            return redirect(f"{reverse('tournament_list')}?otp_sent=1&otp_code={otp_code}&tournament_id={tournament_id}")

        otp = request.POST.get('otp', '').strip()
        if otp and otp == request.session.get('tournament_alert_otp'):
            tournament.alert_cancelled = True
            tournament.save(update_fields=['alert_cancelled'])
            request.session.pop('tournament_alert_otp', None)
            request.session.pop('tournament_alert_phone_number', None)
            request.session.pop('tournament_alert_tournament_id', None)
    return redirect('tournament_list')

def news_list(request):
    """List all news updates"""
    news_items = News.objects.all().order_by('-created_at')
    context = {
        'news_items': news_items,
        'total_news': news_items.count(),
        'active_news': news_items.filter(is_active=True).count(),
        'inactive_news': news_items.filter(is_active=False).count(),
    }
    return render(request, 'admin/news_list.html', context)

def toggle_news_status(request, news_id):
    """Activate an inactive news item and redirect back to the news list"""
    try:
        news_item = News.objects.get(id=news_id)
        news_item.is_active = True
        news_item.save(update_fields=['is_active'])
    except News.DoesNotExist:
        pass
    return redirect('news_list')


def delete_news(request, news_id):
    """Directly delete a news item and redirect back to news list"""
    try:
        News.objects.get(id=news_id).delete()
    except News.DoesNotExist:
        pass
    return redirect('news_list')

def delete_tournament(request, tournament_id):
    """Directly delete a tournament and redirect back to tournament list"""
    try:
        Tournament.objects.get(id=tournament_id).delete()
    except Tournament.DoesNotExist:
        pass
    return redirect('tournament_list')

def delete_registration(request, registration_id):
    """Directly delete a registration and redirect back to registration list"""
    try:
        TournamentRegistration.objects.get(id=registration_id).delete()
    except TournamentRegistration.DoesNotExist:
        pass
    return redirect('registration_list')
