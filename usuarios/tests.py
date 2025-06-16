from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import datetime
import urllib.parse # For encoding next parameter

from .models import SearchLog
# from aranceles.models import Partida, Subpartida # If needed for search setup

class SearchLogCreationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.search_url_name = 'aranceles:search_predictive'
        self.search_url = reverse(self.search_url_name)
        self.login_url_name = 'usuarios:login' # Assuming this is your login URL name
        self.login_url = reverse(self.login_url_name)

    def test_search_log_created_for_authenticated_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.search_url, {'q': 'test query'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(SearchLog.objects.filter(user=self.user, term='test query').exists())

    def test_search_log_not_created_for_empty_query(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.search_url, {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SearchLog.objects.filter(user=self.user, term='').exists())
        self.assertEqual(SearchLog.objects.count(), 0)

    def test_search_log_not_created_for_unauthenticated_user(self):
        # The search_predictive view is @login_required.
        query_params = urllib.parse.urlencode({'q': 'another query'})
        expected_next_url = f"{self.search_url}?{query_params}"
        expected_redirect_url = f"{self.login_url}?next={urllib.parse.quote(expected_next_url)}"

        response = self.client.get(f"{self.search_url}?{query_params}")
        self.assertRedirects(response, expected_redirect_url, fetch_redirect_response=False) # Check only header
        self.assertFalse(SearchLog.objects.filter(term='another query').exists())


class SearchLogsDashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.dashboard_url_name = 'usuarios:search_logs_dashboard'
        self.dashboard_url = reverse(self.dashboard_url_name)
        self.login_url_name = 'usuarios:login'
        self.login_url = reverse(self.login_url_name)

        # Create some search logs
        # All these are "today" for the sake of consistent testing
        now = timezone.now()
        SearchLog.objects.create(user=self.user1, term='apple', timestamp=now)
        SearchLog.objects.create(user=self.user1, term='banana', timestamp=now - datetime.timedelta(days=1))
        SearchLog.objects.create(user=self.user2, term='apple', timestamp=now)
        SearchLog.objects.create(user=self.user2, term='orange', timestamp=now)
        SearchLog.objects.create(user=self.user1, term='apple', timestamp=now) # user1 searches apple again

    def test_dashboard_authentication_required(self):
        response = self.client.get(self.dashboard_url)
        expected_redirect_url = f"{self.login_url}?next={self.dashboard_url}"
        self.assertRedirects(response, expected_redirect_url, fetch_redirect_response=False)


    def test_dashboard_loads_for_logged_in_user(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/search_logs_page.html')

    def test_daily_logs_display(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'apple') # Check that some expected daily terms are broadly in response
        self.assertContains(response, 'orange')

        # Specific check for 'banana' in daily_logs context
        daily_logs_in_context = response.context['daily_logs']
        banana_in_daily_logs = any(log.term == 'banana' for log in daily_logs_in_context)
        self.assertFalse(banana_in_daily_logs, "'banana' (yesterday's log) should not be in the daily_logs context data.")

        # Logs created "today": user1-apple, user2-apple, user2-orange, user1-apple (again) = 4
        self.assertEqual(len(daily_logs_in_context), 4)


    def test_user_specific_logs_display(self):
        self.client.login(username='user1', password='password')
        # User1 logs: apple (today), banana (yesterday), apple (today) = 3 logs
        response = self.client.get(self.dashboard_url + f'?user_id={self.user1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Search history for {self.user1.username}')
        self.assertContains(response, 'apple')
        self.assertContains(response, 'banana')

        # More specific check for 'orange'
        user1_logs_in_context = response.context['selected_user_logs']
        orange_in_user1_logs = any(log.term == 'orange' for log in user1_logs_in_context)
        self.assertFalse(orange_in_user1_logs, "'orange' should not be in user1's specific logs context.")

        self.assertEqual(len(response.context['selected_user_logs']), 3)
        for log in response.context['selected_user_logs']:
            self.assertEqual(log.user, self.user1)

    def test_user_specific_logs_invalid_user(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(self.dashboard_url + '?user_id=999') # Non-existent user
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuario seleccionado no válido.")
        self.assertIsNone(response.context.get('selected_user_logs'))
        self.assertIsNone(response.context.get('selected_user_instance'))


    def test_most_searched_terms_display(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

        # Expected: apple (3 times), orange (1 time), banana (1 time from yesterday, but most_searched is global)
        # The dashboard shows top 10 global terms.
        # Setup: apple (user1, today), banana (user1, yesterday), apple (user2, today), orange (user2, today), apple (user1, today)
        # Counts: apple: 3, orange: 1, banana: 1

        most_searched = response.context['most_searched_terms']

        self.assertContains(response, 'apple')
        self.assertContains(response, '3</span>') # Count for apple
        self.assertContains(response, 'orange')
        self.assertContains(response, '1</span>') # Count for orange
        self.assertContains(response, 'banana')
        self.assertContains(response, '1</span>') # Count for banana

        self.assertEqual(len(most_searched), 3)
        self.assertEqual(most_searched[0]['term'], 'apple')
        self.assertEqual(most_searched[0]['count'], 3)

        # Check other terms, order might vary for ties
        found_orange = any(item['term'] == 'orange' and item['count'] == 1 for item in most_searched)
        found_banana = any(item['term'] == 'banana' and item['count'] == 1 for item in most_searched)
        self.assertTrue(found_orange)
        self.assertTrue(found_banana)

    def test_users_list_in_context(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('users_list', response.context)
        self.assertEqual(len(response.context['users_list']), 2)
        usernames_in_context = [u.username for u in response.context['users_list']]
        self.assertIn('user1', usernames_in_context)
        self.assertIn('user2', usernames_in_context)
