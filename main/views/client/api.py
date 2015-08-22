__author__ = 'cristian'

from django.views.generic import TemplateView

__all__ = ["ClientAppData", 'ClientAssetClasses', "ClientUserInfo", 'ClientVisitor', 'ClientAdvisor', 'ClientAccounts',
           "PortfolioAssetClasses", 'PortfolioPortfolios', 'PortfolioRiskFreeRates', 'ClientAccountPositions']


class ClientAppData(TemplateView):
    template_name = "appData.json"
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


class ClientUserInfo(TemplateView):
    template_name = "user.json"
    content_type = "application/json"


class ClientVisitor(TemplateView):
    template_name = "visitor.json"
    content_type = "application/json"


class ClientAdvisor(TemplateView):
    template_name = "advisors.json"
    content_type = "application/json"


class ClientAccounts(TemplateView):
    template_name = "accounts.json"
    content_type = "application/json"


class ClientAccountPositions(TemplateView):
    template_name = "account-positions.json"
    content_type = "application/json"