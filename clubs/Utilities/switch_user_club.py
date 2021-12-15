from django.shortcuts import redirect

def help_switch_club(request):
    """Whenever the user chooses a club from the drop down in the navbar,
    the club object is saved in request.session['club_choice']
    and the user is redirected back to the same page.
    If the previous page doesn't exist, user is redirected to the test page"""

    previous_url = request.META.get('HTTP_REFERER')

    club = request.GET.get('club_choice', False)
    if club!=False:
        request.session['club_choice'] = club

    if previous_url:
        return redirect(previous_url)
    else:
        return redirect('user_profile')