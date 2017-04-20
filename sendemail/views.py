from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse

from sendemail.forms import SendEmailForm
from .models import EmailTemplate
from events.models import Event


def index(request):
    event_list = Event.objects.filter(enabled=True).order_by('-date_time')
    context = {'event_list': event_list}
    return render(request, 'sendemail/index.html', context)


def detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':  # if this is a POST request we need to process the form data
        form = SendEmailForm(request.POST)
        form.fields['email_templates'].choices = get_all_active_email_templates()
        if form.is_valid():
            send_emails(request, form, event_id)
            return HttpResponseRedirect('/sendemail')

    else:  # if a GET (or any other method) we'll create a blank form
        form = SendEmailForm()
        form.fields['email_templates'].choices = get_all_active_email_templates()
        return render(request, 'sendemail/detail.html', {'event': event, 'form': form})


def get_all_active_email_templates():
    return [(email_template.id, str(email_template)) for email_template in EmailTemplate.objects.filter(enabled=True)]


def send_emails(request, form, event_id):
    pass

