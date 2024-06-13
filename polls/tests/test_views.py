from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from polls.models import Poll, Vote, Choice
from django.urls import reverse
from django.contrib.messages import get_messages
from polls.forms import PollAddForm, EditPollForm, ChoiceAddForm


class PollsListViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='example', email='example@example.com', password='example1234')
        self.client.login(username='example', password='example1234')
        # Create some polls
        self.poll1 = Poll.objects.create(text="First Poll", owner=self.user)
        self.poll2 = Poll.objects.create(text="Second Poll", owner=self.user)
        self.poll3 = Poll.objects.create(text="Another Poll", owner=self.user)

    def test_polls_list_view(self):
        response = self.client.get(reverse('polls:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/polls_list.html')
        self.assertContains(response, self.poll1.text)
        self.assertContains(response, self.poll2.text)
        self.assertContains(response, self.poll3.text)

    def text_polls_list_unAuthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('polls:list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))

    def test_polls_list_sorted_by_name(self):
        response = self.client.get(reverse('polls:list'), {'name': True})
        self.assertTemplateUsed(response, 'polls/polls_list.html')
        self.assertEqual(response.status_code, 200)
        polls = list(response.context['polls'])
        self.assertEqual(polls[0], self.poll3)  # Another Poll
        self.assertEqual(polls[1], self.poll1)  # First Poll
        self.assertEqual(polls[2], self.poll2)  # Second Poll

    def test_polls_list_search(self):
        response = self.client.get(reverse('polls:list'), {'search': 'First'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/polls_list.html')
        self.assertContains(response, self.poll1.text)
        self.assertNotContains(response, self.poll2.text)
        self.assertNotContains(response, self.poll3.text)

    def test_polls_list_pagination(self):
        # Assuming the pagination is set to 6, add more polls to test pagination
        for i in range(7):
            Poll.objects.create(text=f"Poll {i + 4}", owner=self.user)

        response = self.client.get(reverse('polls:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/polls_list.html')
        self.assertEqual(len(response.context['polls']), 6)  # First page should have 6 polls

        response = self.client.get(reverse('polls:list'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/polls_list.html')
        self.assertEqual(len(response.context['polls']), 4)  # Second page should have remaining polls

    def test_polls_list_params(self):
        response = self.client.get(reverse('polls:list'), {'search': 'First', 'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/polls_list.html')
        self.assertIn('search=First', response.context['params'])
        self.assertNotIn('page=2', response.context['params'])


class UserPollViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='example', email='example@example.com', password='example1234')
        self.client.login(username='example', password='example1234')
        # Create another user
        self.other_user = User.objects.create_user(username='other', email='other@example.com', password='other1234')
        # Create some polls for the logged-in user
        for i in range(10):
            Poll.objects.create(text=f"User Poll {i+1}", owner=self.user)
        # Create some polls for another user
        for i in range(5):
            Poll.objects.create(text=f"Other User Poll {i+1}", owner=self.other_user)

    def test_user_polls_list_view(self):
        response = self.client.get(reverse('polls:list_by_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/polls_list.html')
        self.assertEqual(len(response.context['polls']), 6)  # Pagination, so first page should have 6 polls
        # Only polls created by the logged-in user should be listed
        for poll in response.context['polls']:
            self.assertEqual(poll.owner, self.user)

    def test_user_polls_list_pagination(self):
        response = self.client.get(reverse('polls:list_by_user'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/polls_list.html')
        # The second page should have the remaining polls
        self.assertEqual(len(response.context['polls']), 4)

    def test_user_polls_only(self):
        response = self.client.get(reverse('polls:list_by_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/polls_list.html')
        # Ensure no polls from other users are in the response
        other_user_polls = Poll.objects.filter(owner=self.other_user)
        for poll in other_user_polls:
            self.assertNotContains(response, poll.text)


class PollAddViewTest(TestCase):

    def setUp(self):
        # Create a user with permission to add a poll
        self.user = User.objects.create_user(username='example', email='example@example.com', password='example1234')
        content_type = ContentType.objects.get_for_model(Poll)
        permission = Permission.objects.get(codename='add_poll', content_type=content_type)
        self.user.user_permissions.add(permission)
        self.client.login(username='example', password='example1234')
        # Create a user without permission to add a poll
        self.other_user = User.objects.create_user(username='other', email='other@example.com', password='other1234')

    def test_GET_poll_add_view_authenticated(self):
        response = self.client.get(reverse('polls:add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/add_poll.html')
        self.assertIsInstance(response.context['form'], PollAddForm)

    def test_POST_poll_add_view_with_permission(self):
        data = {
            'text': 'Test Poll',
            'choice1': 'Choice 1',
            'choice2': 'Choice 2'
        }
        response = self.client.post(reverse('polls:add'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))

        # Check that the poll and choices were created
        poll = Poll.objects.get(text='Test Poll')
        self.assertEqual(poll.owner, self.user)
        self.assertTrue(Choice.objects.filter(poll=poll, choice_text='Choice 1').exists())
        self.assertTrue(Choice.objects.filter(poll=poll, choice_text='Choice 2').exists())

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Poll & Choices added successfully.")
        self.assertIn('alert alert-success alert-dismissible fade show', messages[0].tags)

    def test_POST_poll_add_view_without_permission(self):
        self.client.login(username='other', password='other1234')
        data = {
            'text': 'Test Poll',
            'choice1': 'Choice 1',
            'choice2': 'Choice 2'
        }
        response = self.client.post(reverse('polls:add'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))

        # Check that the poll and choices were not created
        self.assertFalse(Poll.objects.filter(text='Test Poll').exists())

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Sorry but you don't have permission to do that!")
        self.assertIn('alert alert-danger alert-dismissible fade show', messages[0].tags)

    def test_POST_poll_add_view_invalid_form(self):
        data = {
            'text': '',  # Missing text
            'choice1': 'Choice 1',
            'choice2': 'Choice 2'
        }
        response = self.client.post(reverse('polls:add'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/add_poll.html')
        self.assertIsInstance(response.context['form'], PollAddForm)
        self.assertFalse(response.context['form'].is_valid())


class BaseSetUpTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='example', email='example@example.com', password='example1234')
        self.other_user = User.objects.create_user(username='other', email='other@example.com', password='other1234')
        self.client.login(username='example', password='example1234')
        self.poll = Poll.objects.create(text='Test Poll', owner=self.user)


class PollsEditViewTest(BaseSetUpTestCase):

    def test_GET_poll_edit_view_with_permission(self):
        response = self.client.get(reverse('polls:edit', kwargs={'poll_id': self.poll.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/poll_edit.html')
        self.assertIsInstance(response.context['form'], EditPollForm)
        self.assertEqual(response.context['poll'], self.poll)

    def test_GET_poll_edit_view_without_permission(self):
        self.client.login(username='other', password='other1234')
        response = self.client.get(reverse('polls:edit', kwargs={'poll_id': self.poll.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You dont have permission to edit this Poll!")
        self.assertIn('alert alert-danger alert-dismissible fade show', messages[0].tags)

    def test_POST_poll_edit_view_with_valid_data(self):
        data = {'text': 'Updated Test Poll'}
        response = self.client.post(reverse('polls:edit', kwargs={'poll_id': self.poll.id}), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))
        self.poll.refresh_from_db()
        self.assertEqual(self.poll.text, 'Updated Test Poll')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Poll Updated successfully.")
        self.assertIn('alert alert-success alert-dismissible fade show', messages[0].tags)

    def test_POST_poll_edit_view_with_invalid_data(self):
        data = {'text': ''}  # Invalid data, empty text
        response = self.client.post(reverse('polls:edit', kwargs={'poll_id': self.poll.id}), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/poll_edit.html')
        self.assertIsInstance(response.context['form'], EditPollForm)
        self.assertFalse(response.context['form'].is_valid())
        self.poll.refresh_from_db()
        self.assertEqual(self.poll.text, 'Test Poll')


class DeletePollViewTest(BaseSetUpTestCase):

    def test_delete_poll_view_with_permission(self):
        response = self.client.get(reverse('polls:delete_poll', kwargs={'poll_id': self.poll.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))
        # Check that the poll was deleted
        self.assertFalse(Poll.objects.filter(id=self.poll.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Poll Deleted successfully.")
        self.assertIn('alert alert-success alert-dismissible fade show', messages[0].tags)

    def test_delete_poll_view_without_permission(self):
        self.client.login(username='other', password='other1234')
        response = self.client.get(reverse('polls:delete_poll', kwargs={'poll_id': self.poll.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))
        # Check that the poll was not deleted
        self.assertTrue(Poll.objects.filter(id=self.poll.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)

    def test_delete_poll_view_not_logged_in(self):
        self.client.logout()
        url = reverse('polls:delete_poll', kwargs={'poll_id': self.poll.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login') + '?next=' + url)


class AddChoiceViewTest(BaseSetUpTestCase):

    def test_GET_add_choice_view_with_permission(self):
        response = self.client.get(reverse('polls:add_choice', kwargs={'poll_id': self.poll.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/add_choice.html')
        self.assertIsInstance(response.context['form'], ChoiceAddForm)

    def test_GET_add_choice_view_without_permission(self):
        self.client.login(username='other', password='other1234')
        response = self.client.get(reverse('polls:add_choice', kwargs={'poll_id': self.poll.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You don't have permission to edit this Poll!")
        self.assertIn('alert alert-danger alert-dismissible fade show', messages[0].tags)

    def test_POST_add_choice_view_with_valid_data(self):
        data = {'choice_text': 'New Choice'}
        response = self.client.post(reverse('polls:add_choice', kwargs={'poll_id': self.poll.id}), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:edit', kwargs={'poll_id': self.poll.id}))
        self.assertTrue(Choice.objects.filter(poll=self.poll, choice_text='New Choice').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Choice added successfully.")
        self.assertIn('alert alert-success alert-dismissible fade show', messages[0].tags)

    def test_POST_add_choice_view_with_invalid_data(self):
        data = {'choice_text': ''}  # Invalid data, empty choice_text
        response = self.client.post(reverse('polls:add_choice', kwargs={'poll_id': self.poll.id}), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/add_choice.html')
        self.assertIsInstance(response.context['form'], ChoiceAddForm)
        self.assertFalse(response.context['form'].is_valid())
        self.assertFalse(Choice.objects.filter(poll=self.poll, choice_text='').exists())

    def test_POST_add_choice_view_without_permission(self):
        self.client.login(username='other', password='other1234')
        data = {'choice_text': 'New Choice'}
        response = self.client.post(reverse('polls:add_choice', kwargs={'poll_id': self.poll.id}), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))
        self.assertFalse(Choice.objects.filter(poll=self.poll, choice_text='New Choice').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)


class ChoiceEditViewTest(BaseSetUpTestCase):

    def setUp(self):
        super().setUp()
        self.choice = Choice.objects.create(poll=self.poll, choice_text='Initial Choice')

    def test_GET_choice_edit_view_with_permission(self):
        response = self.client.get(reverse('polls:choice_edit', kwargs={'choice_id': self.choice.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/add_choice.html')
        self.assertIsInstance(response.context['form'], ChoiceAddForm)
        self.assertTrue(response.context['edit_choice'])
        self.assertEqual(response.context['choice'], self.choice)

    def test_GET_choice_edit_view_without_permission(self):
        self.client.login(username='other', password='other1234')
        response = self.client.get(reverse('polls:choice_edit', kwargs={'choice_id': self.choice.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You dont have permission to edit this Choice!")
        self.assertIn('alert alert-danger alert-dismissible fade show', messages[0].tags)

    def test_POST_choice_edit_view_with_valid_data(self):
        data = {'choice_text': 'Updated Choice'}
        response = self.client.post(reverse('polls:choice_edit', kwargs={'choice_id': self.choice.id}), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:edit', kwargs={'poll_id': self.poll.id}))
        # Check that the choice was updated
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.choice_text, 'Updated Choice')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Choice updated successfully.")
        self.assertIn('alert alert-success alert-dismissible fade show', messages[0].tags)

    def test_POST_choice_edit_view_with_invalid_data(self):
        data = {'choice_text': ''}  # Invalid data, empty choice_text
        response = self.client.post(reverse('polls:choice_edit', kwargs={'choice_id': self.choice.id}), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/add_choice.html')
        self.assertIsInstance(response.context['form'], ChoiceAddForm)
        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue(response.context['edit_choice'])
        # Check that the choice was not updated
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.choice_text, 'Initial Choice')

    def test_POST_choice_edit_view_without_permission(self):
        self.client.login(username='other', password='other1234')
        data = {'choice_text': 'Updated Choice'}
        response = self.client.post(reverse('polls:choice_edit', kwargs={'choice_id': self.choice.id}), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))
        # Check that the choice was not updated
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.choice_text, 'Initial Choice')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)


class ChoiceDeleteViewTest(BaseSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.choice = Choice.objects.create(poll=self.poll, choice_text='Initial Choice')

    def test_GET_choice_delete_view_with_permission(self):
        response = self.client.get(reverse('polls:choice_delete', kwargs={'choice_id': self.choice.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:edit', kwargs={'poll_id': self.poll.id}))
        # Check that the choice was deleted
        self.assertFalse(Choice.objects.filter(pk=self.choice.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Choice Deleted successfully.")
        self.assertIn('alert alert-success alert-dismissible fade show', messages[0].tags)

    def test_GET_choice_delete_view_without_permission(self):
        self.client.login(username='other', password='other1234')
        response = self.client.get(reverse('polls:choice_delete', kwargs={'choice_id': self.choice.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))
        # Check that the choice was not deleted
        self.assertTrue(Choice.objects.filter(pk=self.choice.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)


class PollDetailViewTest(BaseSetUpTestCase):

    def setUp(self):
        super().setUp()
        self.poll_inactive = Poll.objects.create(text='Inactive Poll', owner=self.user, active=False)
        Choice.objects.create(poll=self.poll, choice_text='Choice 1')
        Choice.objects.create(poll=self.poll, choice_text='Choice 2')
        Choice.objects.create(poll=self.poll_inactive, choice_text='Choice 1')

    def test_GET_poll_detail_view_with_active_poll(self):
        response = self.client.get(reverse('polls:detail', kwargs={'poll_id': self.poll.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/poll_detail.html')
        self.assertEqual(response.context['poll'], self.poll)
        self.assertEqual(response.context['loop_time'], range(0, self.poll.choice_set.count()))

    def test_GET_poll_detail_view_with_inactive_poll(self):
        response = self.client.get(reverse('polls:detail', kwargs={'poll_id': self.poll_inactive.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/poll_result.html')
        self.assertEqual(response.context['poll'], self.poll_inactive)

    def test_GET_poll_detail_view_with_nonexistent_poll(self):
        response = self.client.get(reverse('polls:detail', kwargs={'poll_id': 9999}))
        self.assertEqual(response.status_code, 404)


class PollVoteViewTest(BaseSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.choice1 = Choice.objects.create(poll=self.poll, choice_text='Choice 1')
        self.choice2 = Choice.objects.create(poll=self.poll, choice_text='Choice 2')

    def test_POST_poll_vote_view_with_valid_choice(self):
        response = self.client.post(reverse('polls:vote', kwargs={'poll_id': self.poll.id}), {'choice': self.choice1.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/poll_result.html')
        self.assertEqual(response.context['poll'], self.poll)
        # Check that the vote was recorded
        self.assertTrue(Vote.objects.filter(user=self.user, poll=self.poll, choice=self.choice1).exists())

    def test_POST_poll_vote_view_with_no_choice_selected(self):
        response = self.client.post(reverse('polls:vote', kwargs={'poll_id': self.poll.id}), {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:detail', kwargs={'poll_id': self.poll.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "No choice selected!")
        self.assertIn('alert alert-warning alert-dismissible fade show', messages[0].tags)

    def test_POST_poll_vote_view_when_user_already_voted(self):
        Vote.objects.create(user=self.user, poll=self.poll, choice=self.choice1)
        response = self.client.post(reverse('polls:vote', kwargs={'poll_id': self.poll.id}), {'choice': self.choice2.id})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You already voted this poll!")
        self.assertIn('alert alert-warning alert-dismissible fade show', messages[0].tags)
        # Ensure no additional votes were recorded
        self.assertEqual(Vote.objects.filter(user=self.user, poll=self.poll).count(), 1)

    def test_POST_poll_vote_view_with_nonexistent_choice(self):
        response = self.client.post(reverse('polls:vote', kwargs={'poll_id': self.poll.id}), {'choice': 9999})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:detail', kwargs={'poll_id': self.poll.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Chioce does not exist")
        self.assertIn('alert alert-warning alert-dismissible fade show', messages[0].tags)


class EndPollTestCase(BaseSetUpTestCase):

    def setUp(self):
        super().setUp()
        self.poll_inactive = Poll.objects.create(text='Inactive Poll', owner=self.user, active=False)

    def test_GET_end_poll_view_with_active_poll(self):
        response = self.client.get(reverse('polls:end_poll', kwargs={'poll_id': self.poll.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/poll_result.html')
        self.poll.refresh_from_db()
        self.assertFalse(self.poll.active)
        self.assertEqual(response.context['poll'], self.poll)

    def test_GET_end_poll_view_with_inactive_poll(self):
        response = self.client.get(reverse('polls:end_poll', kwargs={'poll_id': self.poll_inactive.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/poll_result.html')
        self.poll_inactive.refresh_from_db()
        self.assertFalse(self.poll_inactive.active)
        self.assertEqual(response.context['poll'], self.poll_inactive)

    def test_GET_end_poll_view_with_nonexistent_poll(self):
        response = self.client.get(reverse('polls:end_poll', kwargs={'poll_id': 9999}))
        self.assertEqual(response.status_code, 404)


class PollModelTest(TestCase):
    def test_user_can_vote(self):
        user = User.objects.create_user(username='example', email='example@example.com', password='example1234')
        poll = Poll.objects.create(text='Test Poll', owner=user)
        self.assertTrue(poll.user_can_vote(user))
        choice = poll.choice_set.create(choice_text='choice test')
        Vote.objects.create(user=user, poll=poll, choice=choice)
        self.assertFalse(poll.user_can_vote(user))

