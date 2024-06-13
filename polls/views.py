from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
from .models import Poll, Choice, Vote
from .forms import PollAddForm, EditPollForm, ChoiceAddForm


def get_poll(request, poll_id) -> Poll | None:
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return None
    return poll


class PollsList(LoginRequiredMixin, View):
    login_url = 'accounts:login'

    def get(self, request):
        all_polls = Poll.objects.all()
        search_term = ''

        if 'name' in request.GET:
            all_polls = all_polls.order_by('text')
        if 'date' in request.GET:
            all_polls = all_polls.order_by('pub_date')
        if 'vote' in request.GET:
            all_polls = all_polls.annotate(Count('vote')).order_by('vote__count')
        if 'search' in request.GET:
            search_term = request.GET.get('search')
            all_polls = all_polls.filter(text__icontains=search_term)

        paginator = Paginator(all_polls, 6)
        page = request.GET.get('page')
        polls = paginator.get_page(page)

        get_dict_copy = request.GET.copy()
        params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()
        context = {'polls': polls, 'params': params, 'search_term': search_term}
        return render(request, 'polls/polls_list.html', context)


class UserPoll(LoginRequiredMixin, View):
    login_url = 'accounts:login'

    def get(self, request):
        all_polls = Poll.objects.filter(owner=request.user)
        paginator = Paginator(all_polls, 6)
        page = request.GET.get('page')
        polls = paginator.get_page(page)
        return render(request, 'polls/polls_list.html', {'polls': polls})


class PollAdd(LoginRequiredMixin, View):
    login_url = 'accounts:login'

    def get(self, request):
        form = PollAddForm()
        return render(request, 'polls/add_poll.html', {'form': form})

    def post(self, request):
        if request.user.has_perm('polls.add_poll'):
            form = PollAddForm(request.POST)
            if form.is_valid():
                poll = form.save(commit=False)
                poll.owner = request.user
                poll.save()
                Choice(poll=poll, choice_text=form.cleaned_data['choice1']).save()
                Choice(poll=poll, choice_text=form.cleaned_data['choice2']).save()
                messages.success(
                    request,
                    "Poll & Choices added successfully.",
                    extra_tags='alert alert-success alert-dismissible fade show'
                )
                return redirect('polls:list')
            form = PollAddForm()
            return render(request, 'polls/add_poll.html', {'form': form})
        else:
            messages.error(
                request,
                "Sorry but you don't have permission to do that!",
                extra_tags='alert alert-danger alert-dismissible fade show')
            return redirect('polls:list')


class PollsEdit(LoginRequiredMixin, View):
    login_url = 'accounts:login'

    def get(self, request, poll_id):
        poll = get_poll(request, poll_id)
        if not poll:
            messages.error(
                request,
                "You dont have permission to edit this Poll!",
                extra_tags='alert alert-danger alert-dismissible fade show'
            )
            return redirect('polls:list')
        form = EditPollForm(instance=poll)
        return render(request, "polls/poll_edit.html", {'form': form, 'poll': poll})

    def post(self, request, poll_id):
        poll = get_poll(request, poll_id)
        if not poll:
            return redirect('polls:list')
        form = EditPollForm(request.POST, instance=poll)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Poll Updated successfully.",
                extra_tags='alert alert-success alert-dismissible fade show'
            )
            return redirect("polls:list")
        return render(request, "polls/poll_edit.html", {'form': form, 'poll': poll})


class DeletePoll(LoginRequiredMixin, View):
    login_url = 'accounts:login'

    def get(self, request, poll_id):
        poll = get_poll(request, poll_id)
        if not poll:
            return redirect('polls:list')
        poll.delete()
        messages.success(request, "Poll Deleted successfully.",
                         extra_tags='alert alert-success alert-dismissible fade show')
        return redirect("polls:list")


class AddChoice(LoginRequiredMixin, View):
    login_url = 'accounts:login'

    def get(self, request, poll_id):
        poll = get_poll(request, poll_id)
        if not poll:
            messages.error(
                request, "You don't have permission to edit this Poll!",
                extra_tags='alert alert-danger alert-dismissible fade show')
            return redirect('polls:list')
        form = ChoiceAddForm()
        return render(request, 'polls/add_choice.html', {'form': form})

    def post(self, request, poll_id):
        poll = get_poll(request, poll_id)
        if not poll:
            return redirect('polls:list')
        form = ChoiceAddForm(request.POST)
        if form.is_valid():
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request, "Choice added successfully.",
                extra_tags='alert alert-success alert-dismissible fade show')
            return redirect('polls:edit', poll.id)
        return render(request, 'polls/add_choice.html', {'form': form})


class ChoiceEdit(LoginRequiredMixin, View):
    login_url = 'accounts:login'

    def get(self, request, choice_id):
        choice = get_object_or_404(Choice, pk=choice_id)
        poll = get_poll(request, poll_id=choice.poll.id)
        if not poll:
            messages.error(
                request, "You dont have permission to edit this Choice!",
                extra_tags='alert alert-danger alert-dismissible fade show')
            return redirect('polls:list')
        form = ChoiceAddForm(instance=choice)
        context = {'form': form, 'edit_choice': True, 'choice': choice}
        return render(request, 'polls/add_choice.html', context)

    def post(self, request, choice_id):
        choice = get_object_or_404(Choice, pk=choice_id)
        poll = get_poll(request, poll_id=choice.poll.id)
        if not poll:
            return redirect('polls:list')
        form = ChoiceAddForm(request.POST, instance=choice)
        if form.is_valid():
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request, "Choice updated successfully.",
                extra_tags='alert alert-success alert-dismissible fade show'
            )
            return redirect('polls:edit', poll.id)
        context = {'form': form, 'edit_choice': True, 'choice': choice}
        return render(request, 'polls/add_choice.html', context)


class ChoiceDelete(LoginRequiredMixin, View):
    login_url = 'accounts:login'

    def get(self, request, choice_id):
        choice = get_object_or_404(Choice, pk=choice_id)
        poll = get_poll(request, poll_id=choice.poll.id)
        if not poll:
            return redirect('polls:list')
        choice.delete()
        messages.success(request, "Choice Deleted successfully.",
                         extra_tags='alert alert-success alert-dismissible fade show')
        return redirect('polls:edit', poll.id)


class PollDetail(View):
    def get(self, request, poll_id):
        poll = get_object_or_404(Poll, pk=poll_id)
        if not poll.active:
            return render(request, 'polls/poll_result.html', {'poll': poll})
        loop_count = poll.choice_set.count()
        context = {
            'poll': poll,
            'loop_time': range(0, loop_count),
        }
        return render(request, 'polls/poll_detail.html', context)


class PollVote(LoginRequiredMixin, View):
    login_url = 'accounts:login'

    def post(self, request, poll_id):
        poll = get_object_or_404(Poll, pk=poll_id)
        choice_id = request.POST.get('choice')
        if not poll.user_can_vote(request.user):
            messages.error(
                request, "You already voted this poll!", extra_tags='alert alert-warning alert-dismissible fade show')
            return redirect("polls:list")

        if choice_id:
            try:
                choice = Choice.objects.get(id=choice_id)
                vote = Vote(user=request.user, poll=poll, choice=choice)
                vote.save()
                return render(request, 'polls/poll_result.html', {'poll': poll})
            except Choice.DoesNotExist:
                messages.error(
                    request, "Chioce does not exist", extra_tags='alert alert-warning alert-dismissible fade show')
                return redirect("polls:detail", poll_id)
        else:
            messages.error(
                request, "No choice selected!", extra_tags='alert alert-warning alert-dismissible fade show')
            return redirect("polls:detail", poll_id)


class EndPoll(LoginRequiredMixin, View):
    login_url = 'accounts:login'

    def get(self, request, poll_id):
        poll = get_poll(request, poll_id)
        if not poll:
            return redirect('polls:list')
        elif poll.active is True:
            poll.active = False
            poll.save()
            return render(request, 'polls/poll_result.html', {'poll': poll})
        return render(request, 'polls/poll_result.html', {'poll': poll})
