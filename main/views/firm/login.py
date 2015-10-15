__author__ = 'cristian'

from django.conf import settings
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (
    REDIRECT_FIELD_NAME,  login as auth_login
)
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.forms import AuthenticationForm
from main.models import User, AuthorisedRepresentative, Advisor, Client
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import (logout as auth_logout)


__all__ = ["firm_login", "firm_logout"]

INVALID_CREDENTIALS = "Invalid email or password."

firm_class = [Advisor, AuthorisedRepresentative, Client]


@never_cache
@csrf_protect
@sensitive_post_parameters()
def firm_login(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME,
               authentication_form=AuthenticationForm, current_app=None, extra_context=None):

    redirect_to = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name, ''))

    if request.method == "POST":

        username = request.POST.get("username", '')

        try:
            user = User.objects.get(email=username)
            if user.prepopulated:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            user = None
            messages.error(request, INVALID_CREDENTIALS)

    if request.method == "POST" and (user is not None):
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            continue_login = True
            user_class_object = None
            user_class_name = None

            for user_class in firm_class:

                try:
                    user_class_object = user_class.objects.get(user=user)
                    user_class_name = user_class.__class__.__name__
                    break
                except ObjectDoesNotExist:
                    pass

            if user_class_object is None:
                continue_login = False
                messages.error(request, "You can't login with your current credentials")

            else:
                if not user_class_object.is_confirmed:
                    messages.error(request, "Your %s account has not been confirmed yet." % user_class_name)
                    continue_login = False
                else:
                    if user_class is Client:
                        redirect_to = request.POST.get(redirect_field_name,
                                                       request.GET.get(redirect_field_name, '/client/app'))

                    if user_class is Advisor:
                        redirect_to = request.POST.get(redirect_field_name,
                                                       request.GET.get(redirect_field_name, '/advisor/summary'))

                    if user_class is AuthorisedRepresentative:
                        redirect_to = request.POST.get(redirect_field_name,
                                                       request.GET.get(redirect_field_name, '/firm/summary'))

            if continue_login:
                # Ensure the user-originating redirection url is safe.
                if not is_safe_url(url=redirect_to, host=request.get_host()):
                    redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
                #clear session
                request.session.clear()
                # Okay, security check complete. Log the user in.
                auth_login(request, form.get_user())

                return HttpResponseRedirect(redirect_to)
            else:
                form = authentication_form(request)
        else:
            messages.error(request, INVALID_CREDENTIALS)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'user_class_name': '',
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)


def firm_logout(request):
    auth_logout(request)

    return HttpResponseRedirect('/firm/login')

