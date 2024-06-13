from django.urls import path
from . import views

app_name = "polls"

urlpatterns = [
    path('list/', views.PollsList.as_view(), name='list'),
    path('list/user/', views.UserPoll.as_view(), name='list_by_user'),
    path('add/', views.PollAdd.as_view(), name='add'),
    path('edit/<int:poll_id>/', views.PollsEdit.as_view(), name='edit'),
    path('delete/<int:poll_id>/', views.DeletePoll.as_view(), name='delete_poll'),
    path('end/<int:poll_id>/', views.EndPoll.as_view(), name='end_poll'),
    path('edit/<int:poll_id>/choice/add/', views.AddChoice.as_view(), name='add_choice'),
    path('edit/choice/<int:choice_id>/', views.ChoiceEdit.as_view(), name='choice_edit'),
    path('delete/choice/<int:choice_id>/', views.ChoiceDelete.as_view(), name='choice_delete'),
    path('<int:poll_id>/', views.PollDetail.as_view(), name='detail'),
    path('<int:poll_id>/vote/', views.PollVote.as_view(), name='vote'),
]
