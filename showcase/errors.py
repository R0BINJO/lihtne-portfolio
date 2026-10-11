from django.shortcuts import render

def csrf_failure(request, reason=''):
    return render(request, '403.html', status=403)
