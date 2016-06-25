from django.conf import settings

from django.contrib.auth.views import (
    login as auth_views_login, 
    logout as auth_views_logout,
)
from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
)

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse_lazy

__all__ = ['login', 'logout']


@never_cache
@csrf_protect
@sensitive_post_parameters()
def login(request, template_name='registration/login.html',
        authentication_form=AuthenticationForm,
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
        is_confirmed = (True
            and (user.client.is_confirmed if user.is_client else True)
            and (user.advisor.is_confirmed if user.is_advisor else True)
            and (user.authorised_representative.is_confirmed if user.is_authorised_representative else True)
        )

        if not is_confirmed:
            messages.error(request, 'Your account has not been confirmed yet.')
            form = authentication_form(request)
            context = {'form': form}

            return TemplateResponse(request, template_name, context)

        # custom redirect
        redirect_to = (reverse_lazy('client:app', args=(user.client.id,)) if user.is_client
            else reverse_lazy('advisor:overview') if user.is_advisor
            else reverse_lazy('firm:overview') if user.is_authorised_representative
            else None
        )

        if redirect_to:
            response = HttpResponseRedirect(redirect_to)
            response.set_cookie('token', user.get_token())

    return response


def logout(request):
    auth_logout(request)
    response = HttpResponseRedirect(reverse_lazy('login'))
    response.delete_cookie('token')
    return response
