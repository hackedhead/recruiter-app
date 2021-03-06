import os
from collections import defaultdict

import sendgrid
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from sendgrid.helpers.mail import *

from sendemail.forms import SendEmailForm
from sendemail.xlsx_formatter import *
from sendemail.models.email_log import EmailLog
from sendemail.models.email_template import EmailTemplate
from events.models.attendance import Attendance
from events.models.event import Event


@login_required
def exportXlsx(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    file_name = "Attendee_List_Event_{0}.xlsx".format(event.id)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(file_name)

    attendance_list = Attendance.objects.filter(event=event)
    xlsx_data = writeToExcel(attendance_list, event)
    response.write(xlsx_data)
    return response


@login_required
def index(request):
    event_list = Event.objects.filter(enabled=True).order_by('-date_time')
    context = {'event_list': event_list}
    return render(request, 'sendemail/index.html', context)


@login_required
def detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    attendance_detail = Attendance.candidates_for_event(event_id)
    attendance_count = len(attendance_detail) #Attendance.objects.values_list('candidate').filter(event=event).distinct().count()
    no_email = request.user.email is None or request.user.email == '';

    if request.method == 'POST':  # if this is a POST request we need to process the form data
        form = SendEmailForm(request.POST)
        form.fields['email_templates'].choices = get_all_active_email_templates()
        if form.is_valid():
            email_template_id = request.POST.getlist('email_templates')[0]
            email_template = EmailTemplate.objects.get(id=email_template_id)
            attendance_list = Attendance.objects.filter(event=event)
            error_emails = send_emails(request, email_template, attendance_list, event)
            if len(error_emails):
                for attendance in attendance_detail:
                    if attendance.email in error_emails:
                        attendance.email_error = True
    else:  # if a GET (or any other method) we'll create a blank form
        form = SendEmailForm()
        form.fields['email_templates'].choices = get_all_active_email_templates()
        error_emails = None
        if event.email_template:
            form.initial['email_templates'] = event.email_template.id

    return render(request, 'sendemail/detail.html', {'event': event,
                                                 'no_email': no_email,
                                                 'user_id' : request.user.id,
                                                 'attendance_list': attendance_detail,
                                                 'bad_emails': error_emails,
                                                 'attendance_count': attendance_count,
                                                 'form': form})


def get_all_active_email_templates():
    templates = [(email_template.id, str(email_template)) for email_template in
                 EmailTemplate.objects.filter(enabled=True)]
    templates.insert(0, ('', ''))
    return templates


def send_emails(request, email_template, attendance_list, event, from_email=None):
    if not from_email:
        from_email = str(request.user.email)

    email_recipients = defaultdict(list)
    for attendance in attendance_list:
        email_recipients[attendance.candidate] += [attendance.selected_job_posting]

    email_errors = [];

    for candidate, job_postings in email_recipients.items():
        to_email = str(candidate.email)
        subject = str(email_template.subject)
        email_body = email_template.body.replace('##FIRST_NAME##', candidate.first_name)
        email_body = email_body.replace('##LAST_NAME##', candidate.last_name)
        email_body = email_body.replace('##EVENT##', event.title)

        job_names = []
        job_list = []
        job_posting = []
        for posting in job_postings:
            job_names += ['<a href="{link}">{name}</a>' \
                .format(name=posting.title, link=posting.job_link)]
            job_list += ['<li><a href="{link}">{name}</a></li>' \
                .format(name=posting.title, link=posting.job_link)]
            job_posting += ['<a href="{link}">{link}</a>'.format(link=posting.job_link)]

        job_names = format_list_string(job_names, separator_2_items=' or ', last_separator=', or ')
        job_list = format_list_string(job_list, prefix='<ul>', separator='', postfix='</ul>')
        job_posting = format_list_string(job_posting, separator_2_items=' and ', last_separator=', and ')

        email_body = email_body.replace('##JOB_NAMES##', job_names)
        email_body = email_body.replace('##JOBS_LIST##', job_list)
        email_body = email_body.replace('##JOBPOSTING##', job_posting)  # legacy

        response = send_email(event, candidate, from_email, to_email, subject, str(email_body))
        if response != 'SENT':
            email_errors.append(to_email)

    return email_errors

# Creates grammatically correct lists with and/or/but in English, no matter which comma rule is used
def format_list_string(list_items, prefix='', separator=', ', separator_2_items=None, last_separator=None, postfix=''):
    if not separator_2_items:
        separator_2_items = separator
    if not last_separator:
        last_separator = separator
    result = prefix
    if len(list_items) <= 1:
        result += separator.join(list_items[0:])
    elif len(list_items) <= 2:
        result += separator_2_items.join(list_items)
    else:
        result += separator.join(list_items[0:-1]) + last_separator + list_items[-1]
    result += postfix
    return result


def send_email(event, candidate, from_address, to_address, subject, body_text):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(from_address)
    to_email = Email(to_address)

    content = Content(type_='text/html', value=body_text)
    current_email = Mail(from_email, subject, to_email, content)
    print('#############################')
    print('Send Email {0} : {1}'.format(to_address, subject))
    print('#############################')
    try:
        if os.environ.get('SENDGRID_API_KEY'):
            response = sg.client.mail.send.post(request_body=current_email.get())
        else:
            if(to_address == 'test@bad.net'):
                response = send_mail(subject, body_text, from_address, [])
            else:
                response = send_mail(subject, body_text, from_address, [to_address])

    except Exception as err:
        response = 'Failed to send Email: ', err

    if response == 1 or (not isinstance(response, (int, str)) and response.status_code == 202):
        response = 'SENT'

    EmailLog(event_id=event,
             candidate_id=candidate,
             to_address=to_address,
             from_address=from_address,
             subject=subject,
             body=body_text,
             response=response).save()
    return response
