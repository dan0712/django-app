__author__ = 'cristian'

from django.views.generic import TemplateView
from ..base import ClientView
import json
from ...models import Transaction, ClientAccount, PENDING, Goal, Platform, ALLOCATION, TransactionMemo,\
    AutomaticDeposit, WITHDRAWAL
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from datetime import datetime
from portfolios.models import PortfolioByRisk, PortfolioSet

__all__ = ["ClientAppData", 'ClientAssetClasses', "ClientUserInfo", 'ClientVisitor', 'ClientAdvisor', 'ClientAccounts',
           "PortfolioAssetClasses", 'PortfolioPortfolios', 'PortfolioRiskFreeRates', 'ClientAccountPositions',
           'ClientFirm', 'NewTransactionsView', 'CancelableTransactionsView', 'ChangeAllocation',
           'NewTransactionMemoView', 'ChangeGoalView', 'SetAutoDepositView', 'Withdrawals']


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


class PortfolioPortfolios(ClientView, TemplateView):
    template_name = "portfolio-portfolios.json"
    content_type = "application/json"

    def get(self, request, *args, **kwargs):
        portfolio_set = get_object_or_404(PortfolioSet, pk = kwargs["pk"])
        ret = []
        for portfolio in portfolio_set.risk_profiles.all():
            new_pr = { "risk": portfolio.risk,
                       "expectedReturn": portfolio.expected_return,
                       "volatility": portfolio.volatility,
                       'allocations': json.loads(portfolio.allocations)
                       }
            ret.append(new_pr)

        return HttpResponse(json.dumps(ret), content_type="application/json")


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


class ChangeAllocation(ClientView):

    def post(self, request, *args, **kwargs):
        goal = get_object_or_404(Goal, pk=kwargs["pk"], account__primary_owner=self.client)
        payload = json.loads(request.body.decode("utf-8"))
        goal.allocation = payload["allocation"]
        new_t = Transaction()
        new_t.account = goal
        new_t.amount = goal.allocation
        new_t.type = ALLOCATION
        # remove all the pending allocation transactions for this account
        Transaction.objects.filter(account=goal,type=ALLOCATION, status=PENDING).all().delete()
        new_t.save()
        goal.save()
        return HttpResponse(json.dumps({"transactionId": new_t.pk}), content_type="application/json")


class NewTransactionMemoView(ClientView):

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body.decode("utf-8"))
        tr = get_object_or_404(Transaction, pk=payload["user_transaction_id"].replace("f", ""))
        trm = TransactionMemo()
        trm.transaction = tr
        trm.category = payload["category"]
        trm.comment = payload["comment"]
        trm.transaction_type = payload["transaction_type"]
        trm.save()
        return HttpResponse(json.dumps({"success": "ok"}), content_type="application/json")


class ChangeGoalView(ClientView):

    def put(self, request, *args, **kwargs):
        goal = get_object_or_404(Goal, pk=kwargs["pk"], account__primary_owner=self.client)
        payload = json.loads(request.body.decode("utf-8"))
        goal.name = payload["name"]
        goal.completion_date = datetime.strptime(payload["goalCompletionDate"], '%Y%m%d%H%M%S')
        goal.type = payload["goalType"]
        goal.account_type = payload["accountType"]
        goal.save()
        return HttpResponse('null', content_type="application/json")


class SetAutoDepositView(ClientView):

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.POST.get("model"))
        pk = payload["account"]
        goal = get_object_or_404(Goal, pk=pk, account__primary_owner=self.client)

        if hasattr(goal, "auto_deposit"):
            ad = goal.auto_deposit
        else:
            ad = AutomaticDeposit(account=goal)

        ad.amount = payload.get("amount", 0)
        ad.frequency = payload["frequency"]
        ad.enabled = payload["enabled"]
        ad.transaction_date_time_1 = datetime.strptime(payload["transactionDateTime1"], '%Y%m%d%H%M%S')
        td2 = payload.get("transactionDateTime2", None)
        if td2:
            ad.transaction_date_time_2 = datetime.strptime(td2, '%Y%m%d%H%M%S')
        ad.save()

        payload["id"] = ad.pk
        payload["lastPlanChange"] = ad.last_plan_change.strftime('%Y%m%d%H%M%S')
        payload["nextTransaction"] = ad.next_transaction.strftime('%Y%m%d%H%M%S')
        payload["amount"] = str(ad.amount)

        return HttpResponse(json.dumps(payload), content_type="application/json")


class Withdrawals(ClientView):

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body.decode('utf8'))
        goal = get_object_or_404(Goal, pk=kwargs["pk"], account__primary_owner=self.client)
        new_transaction = Transaction()
        new_transaction.account = goal
        new_transaction.from_account = None
        new_transaction.to_account = None
        new_transaction.type = WITHDRAWAL
        new_transaction.amount = payload["amount"]
        new_transaction.save()

        nt_return = {"transactionId": new_transaction.pk,
                     "account": new_transaction.account.pk,
                     "type": new_transaction.type,
                     "amount": new_transaction.amount}

        return HttpResponse(json.dumps(nt_return), content_type="application/json")
