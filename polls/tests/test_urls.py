from django.test import TestCase
from django.urls import reverse, resolve
from polls import views
from polls.models import Poll
from django.contrib.auth.models import User


class PollsTestUrl(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='example', email='example@example.com', password='example1234')
        self.poll = Poll.objects.create(text='Test Poll', owner=self.user)

    def test_polls_list(self):
        url = reverse('polls:list')
        self.assertEqual(resolve(url).func.view_class, views.PollsList)

    def test_user_polls_list(self):
        url = reverse('polls:list_by_user')
        self.assertEqual(resolve(url).func.view_class, views.UserPoll)

    def test_add_poll(self):
        url = reverse('polls:add')
        self.assertEqual(resolve(url).func.view_class, views.PollAdd)

    def test_edit_poll(self):
        url = reverse('polls:edit', kwargs={'poll_id': self.poll.id})
        self.assertEqual(resolve(url).func.view_class, views.PollsEdit)

    def test_delete_poll(self):
        url = reverse('polls:delete_poll', kwargs={'poll_id': self.poll.id})
        self.assertEqual(resolve(url).func.view_class, views.DeletePoll)

    def test_end_poll(self):
        url = reverse('polls:end_poll', kwargs={'poll_id': self.poll.id})
        self.assertEqual(resolve(url).func.view_class, views.EndPoll)

    def test_add_choice(self):
        url = reverse('polls:add_choice', kwargs={'poll_id': self.poll.id})
        self.assertEqual(resolve(url).func.view_class, views.AddChoice)

    def test_edit_choice(self):
        url = reverse('polls:choice_edit', kwargs={'choice_id': self.poll.id})
        self.assertEqual(resolve(url).func.view_class, views.ChoiceEdit)

    def test_delete_choice(self):
        url = reverse('polls:choice_delete', kwargs={'choice_id': self.poll.id})
        self.assertEqual(resolve(url).func.view_class, views.ChoiceDelete)

    def test_poll_detail(self):
        url = reverse('polls:detail', kwargs={'poll_id': self.poll.id})
        self.assertEqual(resolve(url).func.view_class, views.PollDetail)

    def test_poll_vote(self):
        url = reverse('polls:vote', kwargs={'poll_id': self.poll.id})
        self.assertEqual(resolve(url).func.view_class, views.PollVote)
