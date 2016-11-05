from django.contrib import messages
from django.contrib.auth import (
    logout as auth_logout,
)
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import (
    login as auth_views_login,
)
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.shortcuts import redirect
from geolocation.geolocation import check_ip_city
import logging
import os
from retiresmartz.models import RetirementAdvice, RetirementPlan
from pinax.eventlog.models import log
from retiresmartz import advice_responses
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
logger = logging.getLogger('main.views.login')


class AuthenticationFormWithInactiveUsersOkay(AuthenticationForm):
    def confirm_login_allowed(self, user):
        # users in the middle of onboarding
        # have is_active as False and caused login
        # to fail with users coming back
        # TODO: when login is re-worked remove this
        # and use is_active to determine what users
        # can login ok.
        pass


@never_cache
@csrf_protect
@sensitive_post_parameters()
def login(request, template_name='registration/login.html',
          authentication_form=AuthenticationFormWithInactiveUsersOkay,
          extra_context=None):

    # TODO: maybe to add expected user role (based on url) to extra_context
    response = auth_views_login(request,
                                authentication_form=authentication_form,
                                extra_context=extra_context)
    user = request.user

    if user.is_authenticated():
        # custom extra checking

        # TODO: temp temp temp
        # TODO: discuss "confirmation" feature
        # it should be deeply refactored in the first place
        # we need to (also) use "is_active" user flag for that stuff

        is_client = user.is_client
        is_advisor = user.is_advisor
        is_representative = user.is_authorised_representative
        # Geolocation restriction, configurable per account - set city to restrict
        if not user.is_superuser:
            city_lock = None
            if is_client:
                if user.client.geolocation_lock:
                    city_lock = user.client.geolocation_lock
            elif is_advisor:
                if user.advisor.geolocation_lock:
                    city_lock = user.advisor.geolocation_lock
            elif is_representative:
                if user.authorised_representative.geolocation_lock:
                    city_lock = user.authorised_representative.geolocation_lock

            if city_lock is not None and city_lock is not '':
                if not check_ip_city(request, city_lock) and (ENVIRONMENT == 'demo' or ENVIRONMENT == 'production'):
                    messages.error(request, 'Sorry, the BetaSmartz demo is only available to the %s area on this account.' % city_lock)
                    form = authentication_form(request)
                    context = {'form': form}
                    return TemplateResponse(request, template_name, context)

        confirmed_client = is_client and user.client.is_confirmed
        confirmed_advisor = is_advisor and user.advisor.is_confirmed
        confirmed_representative = is_representative and user.authorised_representative.is_confirmed
        is_confirmed = confirmed_client or confirmed_advisor or confirmed_representative

        if not is_confirmed:
            # check if user is in the middle of onboarding
            if hasattr(user, 'invitation'):
                if user.invitation.status == 2 or user.invitation.status == 3:
                    # redirect to client onboarding
                    return redirect('/client/onboarding/' + user.invitation.invite_key)
            messages.error(request, 'Your account has not been confirmed yet.')
            form = authentication_form(request)
            context = {'form': form}

            return TemplateResponse(request, template_name, context)

        # RetirementAdvice Check
        if is_client:
            plan = RetirementPlan.objects.filter(client=user.client).first()
            if plan:
                elog = log(user=user, action='Returning user')
                advice = RetirementAdvice(plan=plan,
                                          trigger=elog)
                advice.text = advice_responses.get_welcome(advice)
                advice.save()


        # custom redirect
        redirect_to = request.GET.get('next',
                                      reverse_lazy('client:page',
                                                   args=(user.client.id,))
                                      if is_client
                                      else reverse_lazy('advisor:overview')
                                      if is_advisor
                                      else reverse_lazy('firm:overview')
                                      if is_representative
                                      else None)

        if redirect_to:
            response = HttpResponseRedirect(redirect_to)

    return response


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse_lazy('login'))
