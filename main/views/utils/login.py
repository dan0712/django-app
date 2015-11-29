__author__ = 'cristian'

from django.conf import settings
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login as auth_login
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
from main.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

__all__ = ["create_login"]

INVALID_CREDENTIALS = "Invalid email or password."


def create_login(user_class, user_class_name, redirect):
    @never_cache
    @csrf_protect
    @sensitive_post_parameters()
    def login(request, template_name='registration/login.html',
              redirect_field_name=REDIRECT_FIELD_NAME,
              authentication_form=AuthenticationForm,
              current_app=None, extra_context=None):

        """
        Displays the login form and handles the login action.
        """
        redirect_to = request.POST.get(redirect_field_name,
                                       request.GET.get(redirect_field_name, redirect))

        if request.method == "POST":

            username = request.POST.get("username", '')

            try:
                user = User.objects.get(email=username)
            except ObjectDoesNotExist:
                user = None
                messages.error(request, INVALID_CREDENTIALS)

        if request.method == "POST" and (user is not None):
            form = authentication_form(request, data=request.POST)
            if form.is_valid():
                continue_login = True

                try:
                    user_class_object = user_class.objects.get(user=user)
                except ObjectDoesNotExist:
                    user_class_object = None
                    continue_login = False
                    messages.error(request, "You can't login as %s with your current credentials" % user_class_name)

                if user_class_object is not None:
                    if not user_class_object.is_confirmed:
                        messages.error(request, "Your %s account has not been confirmed yet." % user_class_name)
                        continue_login = False

                if continue_login:
                    # Ensure the user-originating redirection url is safe.
                    if not is_safe_url(url=redirect_to, host=request.get_host()):
                        redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

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
            'user_class_name': user_class_name,
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

    return login
