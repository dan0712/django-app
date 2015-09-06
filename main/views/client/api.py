__author__ = 'cristian'

from django.views.generic import TemplateView
from ..base import ClientView
__all__ = ["ClientAppData", 'ClientAssetClasses', "ClientUserInfo", 'ClientVisitor', 'ClientAdvisor', 'ClientAccounts',
           "PortfolioAssetClasses", 'PortfolioPortfolios', 'PortfolioRiskFreeRates', 'ClientAccountPositions', 'ClientFirm']


class ClientAppData(TemplateView):
    template_name = "appData.json"
    content_type = "application/json"


class ClientFirm(TemplateView, ClientView):
    template_name = "firms.json"
    content_type = "application/json"


class ClientAssetClasses(TemplateView):
    template_name = "asset-classes.json"
    content_type = "application/json"


class PortfolioAssetClasses(TemplateView):
    template_name = "portfolio-asset-classes.json"
    content_type = "application/json"


class PortfolioPortfolios(TemplateView):
    template_name = "portfolio-portfolios.json"
    content_type = "application/json"


class PortfolioRiskFreeRates(TemplateView):
    template_name = "portfolio-risk-free-rates.json"
    content_type = "application/json"


class ClientUserInfo(ClientView, TemplateView):
    template_name = "user.json"
    content_type = "application/json"


class ClientVisitor(TemplateView):
    template_name = "visitor.json"
    content_type = "application/json"


class ClientAdvisor(ClientView, TemplateView):
    template_name = "advisors.json"
    content_type = "application/json"


class ClientAccounts(TemplateView):
    template_name = "accounts.json"
    content_type = "application/json"


class ClientAccountPositions(TemplateView):
    template_name = "account-positions.json"
    content_type = "application/json"