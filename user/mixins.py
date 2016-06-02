"""
Mixins to handle authentication (and other) wrappers for class based views
https://docs.djangoproject.com/en/1.8/topics/class-based-views/intro/#mixins-that-wrap-as-view

- IsAuthenticatedMixin
- IsAdvisorMixin
- IsAdvisorManagerMixin
- IsAdvisorAnalystMixin
- IsClientMixin
- ...
"""

from decorators import (
    is_authenticated,
    is_advisor, is_advisor_manager, is_advisor_analyst,
    is_client,
)


class IsAuthenticatedMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(IsAuthenticatedMixin, cls).as_view(**initkwargs)
        return is_authenticated(view)


class IsAdvisorMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(IsAdvisorMixin, cls).as_view(**initkwargs)
        return is_advisor(view)


class IsAuthorizedRepresentativeMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(IsAuthorizedRepresentativeMixin, cls).as_view(**initkwargs)
        return is_authorized_representative(view)


class IsSupervisorMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(IsSupervisorMixin, cls).as_view(**initkwargs)
        return is_supervisor(view)


class IsClientMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(IsClientMixin, cls).as_view(**initkwargs)
        return is_client(view)


