from django.contrib import messages

def add_message(request, level, message):
    messages.add_message(request, level, message)