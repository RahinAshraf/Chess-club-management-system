from django.contrib import messages

def add_success_message(request,success_string):
    messages.add_message(request, messages.SUCCESS, success_string)

def add_error_message(request, error_string):
    messages.add_message(request, messages.ERROR, error_string)