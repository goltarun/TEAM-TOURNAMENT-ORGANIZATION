from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Tournament, TournamentRegistration, News


class RegistrationListSearchTests(TestCase):
    def setUp(self):
        self.alpha_tournament = Tournament.objects.create(
            title='Alpha Cup',
            prize='1000',
            entry_fee='Free',
            per_kill='N/A',
            date='2026-08-01',
            time='20:00:00',
            game_mode='BR Rank',
            mode='Solo',
            map_name='Bermuda',
            status='Today',
        )
        self.beta_tournament = Tournament.objects.create(
            title='Beta Cup',
            prize='2000',
            entry_fee='Free',
            per_kill='N/A',
            date='2026-08-02',
            time='20:00:00',
            game_mode='BR Rank',
            mode='Solo',
            map_name='Bermuda',
            status='Today',
        )
        self.alpha_registration = TournamentRegistration.objects.create(
            tournament=self.alpha_tournament,
            player_name='Alpha Player',
            team_name='Alpha Team',
            contact_number='1234567890',
            slot_number=1,
            payment_status='Paid',
        )
        self.beta_registration = TournamentRegistration.objects.create(
            tournament=self.beta_tournament,
            player_name='Beta Player',
            team_name='Beta Team',
            contact_number='0987654321',
            slot_number=1,
            payment_status='Pending',
        )

    def test_search_filters_registrations_by_tournament_title(self):
        response = self.client.get(reverse('registration_list'), {'q': 'alpha'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['registrations'].count(), 1)
        self.assertEqual(list(response.context['registrations']), [self.alpha_registration])

    def test_toggle_news_status_marks_inactive_news_active(self):
        news_item = News.objects.create(
            title='Test News',
            content='Test content',
            date_display='Today',
            is_active=False,
        )

        response = self.client.post(reverse('toggle_news_status', args=[news_item.id]))

        news_item.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(news_item.is_active)

    def test_tournament_registrations_count_includes_paid_as_confirmed(self):
        response = self.client.get(reverse('tournament_registrations', args=[self.alpha_tournament.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['paid_count'], 1)
        self.assertEqual(response.context['confirmed_count'], 1)

    def test_tournament_alert_banner_shows_match_name_and_details(self):
        tournament = Tournament.objects.create(
            title='Upcoming Cup',
            prize='500',
            entry_fee='100',
            per_kill='10',
            date=timezone.now().date() + timedelta(days=1),
            time='20:00:00',
            game_mode='Clash Squad',
            mode='Duo',
            map_name='Erangel',
            status='Today',
        )

        response = self.client.get(reverse('tournament_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upcoming Cup')
        self.assertContains(response, 'Clash Squad')
        self.assertContains(response, 'Duo')
        self.assertContains(response, 'Erangel')
        self.assertContains(response, '100')
        self.assertContains(response, '10')

    def test_send_otp_stores_confirmation_code(self):
        tournament = Tournament.objects.create(
            title='Upcoming Cup',
            prize='500',
            entry_fee='Free',
            per_kill='N/A',
            date=timezone.now().date() + timedelta(days=1),
            time='20:00:00',
            game_mode='BR Rank',
            mode='Solo',
            map_name='Bermuda',
            status='Today',
        )

        response = self.client.post(
            reverse('cancel_tournament_alert', args=[tournament.id]),
            {'action': 'send_otp'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('otp_sent=1', response.url)
        self.assertIn('otp_code=', response.url)
        self.assertEqual(self.client.session['tournament_alert_phone_number'], '6353978826')
        self.assertTrue(self.client.session['tournament_alert_otp'])

    def test_cancel_tournament_alert_marks_alert_cancelled(self):
        tournament = Tournament.objects.create(
            title='Upcoming Cup',
            prize='500',
            entry_fee='Free',
            per_kill='N/A',
            date=timezone.now().date() + timedelta(days=1),
            time='20:00:00',
            game_mode='BR Rank',
            mode='Solo',
            map_name='Bermuda',
            status='Today',
        )
        session = self.client.session
        session['tournament_alert_otp'] = '1234'
        session['tournament_alert_phone_number'] = '6353978826'
        session.save()

        response = self.client.post(
            reverse('cancel_tournament_alert', args=[tournament.id]),
            {'action': 'confirm', 'otp': '1234'}
        )

        tournament.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(tournament.alert_cancelled)

    def test_confirm_payment_stores_payment_confirmation_time(self):
        registration = TournamentRegistration.objects.create(
            tournament=self.alpha_tournament,
            player_name='Paying Player',
            team_name='Paying Team',
            contact_number='1111111111',
            slot_number=2,
            payment_status='Pending',
        )

        response = self.client.post(
            reverse('api_confirm_payment'),
            {'registration_id': registration.id},
            content_type='application/json',
        )

        registration.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(registration.payment_status, 'Paid')
        self.assertIsNotNone(registration.payment_confirmed_at)
