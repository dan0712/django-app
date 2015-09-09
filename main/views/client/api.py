__author__ = 'cristian'

from django.views.generic import TemplateView
from ..base import ClientView
import json
from ...models import Transaction, ClientAccount, PENDING, Goal, Platform
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from datetime import datetime
from portfolios.models import PortfolioByRisk

__all__ = ["ClientAppData", 'ClientAssetClasses', "ClientUserInfo", 'ClientVisitor', 'ClientAdvisor', 'ClientAccounts',
           "PortfolioAssetClasses", 'PortfolioPortfolios', 'PortfolioRiskFreeRates', 'ClientAccountPositions',
           'ClientFirm', 'NewTransactionsView', 'CancelableTransactionsView']


class ClientAppData(TemplateView):
    template_name = "appData.json"
    content_type = "application/json"


class ClientFirm(ClientView, TemplateView):
    template_name = "firms.json"
    content_type = "application/json"


class ClientAssetClasses(ClientView, TemplateView):
    template_name = "asset-classes.json"
    content_type = "application/json"

    def get_context_data(self, *args, **kwargs):
        ctx = super(ClientAssetClasses, self).get_context_data(*args, **kwargs)
        ctx["platform"] = Platform.objects.first()
        return ctx


class PortfolioAssetClasses(ClientView, TemplateView):
    template_name = "portfolio-asset-classes.json"
    content_type = "application/json"

    def get_context_data(self, *args, **kwargs):
        ctx = super(PortfolioAssetClasses, self).get_context_data(*args, **kwargs)
        ctx["portfolio_set"] = Platform.objects.first().portfolio_set
        return ctx


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


class ClientAccounts(ClientView, TemplateView):
    template_name = "accounts.json"
    content_type = "application/json"

    def post(self, requests, *args, **kwargs):
        model = json.loads(requests.POST.get("model", '{}'))
        goal = Goal()
        goal.account = self.client.accounts.first()
        goal.name = model.get("name")
        goal.type = model.get("goalType")
        goal.account_type = model.get("accountType")
        goal.completion_date = datetime.strptime(model.get("goalCompletionDate"), '%Y%m%d%H%M%S')
        goal.allocation = model.get("allocation")
        goal.target = model.get("goalAmount")
        goal.save()
        return HttpResponse(json.dumps({"id": goal.pk }), content_type='application/json')


class ClientAccountPositions(ClientView, TemplateView):
    template_name = "account-positions.json"
    content_type = "application/json"

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        goal = get_object_or_404(Goal, pk=pk)
        # get ideal portfolio
        portfolio_set = Platform.objects.first().portfolio_set
        pbr = PortfolioByRisk.objects.filter(portfolio_set=portfolio_set, risk__lte=goal.allocation).order_by('-risk').first()
        allocations = json.loads(pbr.allocations)
        print(allocations)
        # get positions

        positions = []
        for asset in portfolio_set.asset_classes.all():
            asset_total_value = 0
            new_p = dict()

            new_p["assetClass"] = {
                "assetClass": asset.name,
                "investmentType": asset.investment_type,
                "displayName": asset.display_name,
                "superAssetClass": asset.super_asset_class
            }

            new_p["tickerPositions"] = []
            for ticker in asset.tickers.all():
                asset_total_value += ticker.value(goal)
                new_t = {
                    "ticker": {
                        "id": ticker.pk,
                        "symbol": ticker.symbol,
                        "displayName": ticker.display_name,
                        "description": ticker.description,
                        "ordering": ticker.ordering,
                        "url": ticker.url,
                        "unitPrice": ticker.unit_price,
                        "primary": ticker.primary
                    },
                    "position": {
                        "shares": ticker.shares(goal),
                        "value": ticker.value(goal)
                    }
                }
                new_p["tickerPositions"].append(new_t)

            new_p["totalValue"] = asset_total_value

            new_p["allocation"] = allocations[asset.name]
            gtb = goal.total_balance

            if gtb != 0:
                real_allocation = asset_total_value / (1.0 * gtb)
                new_p["drift"] = real_allocation - new_p["allocation"]
            else:
                real_allocation = 0
                new_p["drift"] = 0

            positions.append(new_p)

        # calculate drift and allocations
        return HttpResponse(json.dumps(positions), content_type='application/json')


class CancelableTransactionsView(ClientView, TemplateView):
    content_type = "application/json"
    template_name = "account-positions.json"

    def get(self, request, *args, **kwargs):
        return HttpResponse('[]', content_type=self.content_type)


class NewTransactionsView(ClientView):

    def post(self, request, *args, **kwargs):
        model = json.loads(request.POST.get("model", '{}'))
        new_transaction = Transaction()
        new_transaction.account = get_object_or_404(Goal, pk=model['account'], account__primary_owner=self.client)
        new_transaction.from_account = None
        new_transaction.to_account = None
        new_transaction.type = model["type"]
        new_transaction.amount = model["amount"]

        if model["fromAccount"]:
            new_transaction.from_account = get_object_or_404(ClientAccount, pk=model['fromAccount'],
                                                             primary_owner=self.client)

        if model["toAccount"]:
            new_transaction.to_account = get_object_or_404(ClientAccount, pk=model['toAccount'],
                                                           primary_owner=self.client)

        new_transaction.save()

        nt_return = {"id": new_transaction.pk,
                     "account": new_transaction.account.pk,
                     "type": new_transaction.type,
                     "amount": new_transaction.amount}

        if new_transaction.from_account:
            nt_return["fromAccount"] = new_transaction.from_account

        if new_transaction.to_account:
            nt_return["toAccount"] = new_transaction.to_account

        return HttpResponse(json.dumps(nt_return), content_type='application/json')

