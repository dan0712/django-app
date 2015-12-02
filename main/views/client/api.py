import json
import time
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from portfolios.bl_model import OptimizationException
from portfolios.management.commands.calculate_portfolios import calculate_portfolios_for_goal
from portfolios.models import PortfolioSet
from ..base import ClientView
from ...models import Transaction, ClientAccount, PENDING, Goal, ALLOCATION, TransactionMemo, \
    AutomaticDeposit, AutomaticWithdrawal, WITHDRAWAL, Performer, STRATEGY, SymbolReturnHistory, \
    MARKET_CHANGE, EXECUTED, FEE, CostOfLivingIndex, FinancialPlan, FinancialProfile, FinancialPlanAccount, \
    FinancialPlanExternalAccount, AssetClass

__all__ = ['ClientAppData', 'ClientAssetClasses', 'ClientUserInfo', 'ClientVisitor', 'ClientAdvisor',
           'ClientAccounts', 'PortfolioAssetClasses', 'PortfolioPortfolios', 'PortfolioRiskFreeRates',
           'ClientAccountPositions', 'ClientFirm', 'NewTransactionsView', 'CancelableTransactionsView',
           'ChangeAllocation', 'NewTransactionMemoView', 'ChangeGoalView', 'SetAutoDepositView',
           'Withdrawals', 'ContactPreference', 'AnalysisReturns', 'AnalysisBalances',
           'SetAutoWithdrawalView', 'ZipCodes', 'FinancialProfileView',
           'FinancialPlansView', 'FinancialPlansAccountAdditionView', 'FinancialPlansAccountDeletionView',
           'FinancialPlansExternalAccountAdditionView', 'FinancialPlansExternalAccountDeletionView']


class ClientAppData(TemplateView):
    template_name = "appData.json"
    content_type = "application/json"


class ContactPreference(TemplateView):
    template_name = "contact-preference.json"
    content_type = "application/json"


class ClientFirm(ClientView, TemplateView):
    template_name = "firms.json"
    content_type = "application/json"


class ClientAssetClasses(ClientView, TemplateView):
    template_name = "asset-classes.json"
    content_type = "application/json"

    def get_context_data(self, *args, **kwargs):
        ctx = super(ClientAssetClasses, self).get_context_data(*args, **kwargs)
        ctx["asset_classes"] = AssetClass.objects.all()
        return ctx


class PortfolioAssetClasses(ClientView, TemplateView):
    template_name = "portfolio-asset-classes.json"
    content_type = "application/json"

    def get_context_data(self, *args, **kwargs):
        pk = kwargs["goal_pk"]
        goal = get_object_or_404(Goal, pk=pk)
        ctx = super(PortfolioAssetClasses, self).get_context_data(*args, **kwargs)
        ctx["portfolio_set"] = goal.portfolio_set
        return ctx


class PortfolioPortfolios(ClientView, TemplateView):
    template_name = "portfolio-portfolios.json"
    content_type = "application/json"

    def get(self, request, *args, **kwargs):
        portfolio_set = Goal().portfolio_set
        goal_pk = kwargs.get("goal_pk", None)
        if goal_pk:
            try:
                goal = Goal.objects.get(pk=goal_pk,
                                        account__primary_owner=self.client)
            except ObjectDoesNotExist:
                goal = None

            if goal:
                if goal.is_custom_size:
                    if goal.portfolios in [None, "{}", "[]", ""]:
                        try:
                            portfolios = calculate_portfolios_for_goal(goal)
                            goal.portfolios = json.dumps(portfolios)
                            goal.save()
                        except OptimizationException:
                            goal.custom_regions = None
                            goal.save()
                            portfolios = json.loads(goal.portfolio_set.portfolios)
                    else:
                        portfolios = json.loads(goal.portfolios)
                else:
                    portfolios = json.loads(goal.portfolio_set.portfolios)

                ret = []
                for k in portfolios:
                    new_pr = {
                        "risk": int(100 * portfolios[k]["risk"]) / 100,
                        "expectedReturn": portfolios[k]["expectedReturn"],
                        "volatility": portfolios[k]["volatility"],
                        'allocations': portfolios[k]["allocations"]
                    }
                    ret.append(new_pr)
                return HttpResponse(json.dumps(ret), content_type="application/json")

        ret = []
        portfolios = json.loads(portfolio_set.portfolios)
        for k in portfolios:
            new_pr = {
                "risk": int(100 * portfolios[k]["risk"]) / 100,
                "expectedReturn": portfolios[k]["expectedReturn"],
                "volatility": portfolios[k]["volatility"],
                'allocations': portfolios[k]["allocations"]
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

        if "ETHICAL" in goal.type:
            goal.custom_portfolio_set = PortfolioSet.objects.get(name="Ethical")

        goal.account_type = model.get("accountType")
        goal.completion_date = datetime.strptime(
            model.get("goalCompletionDate"), '%Y%m%d%H%M%S')
        goal.allocation = model.get("allocation")
        goal.target = model.get("goalAmount", None)
        if goal.target is None:
            goal.target = 0
        goal.income = model.get("income", False)
        goal.save()
        return HttpResponse(json.dumps({"id": goal.pk}),
                            content_type='application/json')


class ClientAccountPositions(ClientView, TemplateView):
    template_name = "account-positions.json"
    content_type = "application/json"

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        goal = get_object_or_404(Goal, pk=pk)
        # get ideal portfolio
        target_portfolio = goal.target_portfolio
        allocations = target_portfolio["allocations"]

        positions = []
        for asset in goal.portfolio_set.asset_classes.all():
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
            if new_p["allocation"] == 0 and new_p["totalValue"] == 0:
                continue
            positions.append(new_p)

        # calculate drift and allocations
        return HttpResponse(json.dumps(positions),
                            content_type='application/json')


class CancelableTransactionsView(ClientView, TemplateView):
    content_type = "application/json"
    template_name = "account-positions.json"

    def get(self, request, *args, **kwargs):
        return HttpResponse('[]', content_type=self.content_type)


class NewTransactionsView(ClientView):
    def get(self, request, *args, **kwargs):
        goal_pk = self.request.GET.get("account", None)
        days_ago = self.request.GET.get("startDaysAgo", None)
        _format = self.request.GET.get("format", None)

        try:
            days_ago = int(days_ago)
        except (ValueError, TypeError):
            days_ago = None

        if goal_pk:
            goal = get_object_or_404(Goal,
                                     pk=goal_pk,
                                     account__primary_owner=self.client)
            query_set = goal.transactions.order_by("executed_date").filter(
                status=EXECUTED)
        else:
            query_set = Transaction.objects.order_by("executed_date").filter(
                status=EXECUTED,
                account__account__primary_owner=self.client)

        if days_ago:
            days_ago = datetime.today() - timedelta(days=days_ago)
            query_set = query_set.filter(executed_date__gte=days_ago)

        transactions = []
        market_change_by_week = {}

        for transaction in query_set.all():
            if transaction.type == MARKET_CHANGE:
                dt = transaction.executed_date
                week_day = str(dt.isocalendar()[1])
                if week_day not in market_change_by_week:
                    start_day_dt = dt - timedelta(days=dt.weekday())
                    end_day_dt = start_day_dt + timedelta(days=6)
                    start_day = start_day_dt.strftime('%b %d')
                    end_day = end_day_dt.strftime('%b %d')

                    market_change_by_week[week_day] = {
                        "date": start_day_dt,
                        "dateString": "{0} to {1}".format(start_day, end_day),
                        "description": "Market Changes",
                        "shortDescription": "Market Changes",
                        "childTransactions": [],
                        "change": "0"
                    }
                ct = {
                    "isDocument": False,
                    "isAllocation": False,
                    "fullTime": dt.strftime('%Y-%m-%d %H:%M:%S'),
                    "id": "{0}".format(transaction.pk),
                    "accountName": transaction.account.name,
                    "accountID": "{0}".format(transaction.account.pk),
                    "type": MARKET_CHANGE,
                    "typeID": "2",
                    "date": dt.strftime('%Y%m%d%H%M%S'),
                    "dateString": dt.strftime('%b %d'),
                    "change": "{:.2f}".format(transaction.amount),
                    "balance": "{:.2f}".format(transaction.new_balance),
                    "createdDate":
                        transaction.created_date.strftime('%Y%m%d%H%M%S'),
                    "completedDate": dt.strftime('%Y%m%d%H%M%S'),
                    "isCanceled": False,
                    "shortDescription": "Market Change",
                    "description": "Market Change",
                    "pending": False,
                    "failed": False,
                    "canBeCanceled": False
                }

                market_change_by_week[week_day]["childTransactions"].append(ct)
                market_change_by_week[week_day]["balance"] = "{:.2f}".format(
                    transaction.new_balance)
                change = float(market_change_by_week[week_day][
                                   "change"]) + transaction.amount
                market_change_by_week[week_day]["change"] = "{:.2f}".format(
                    change)

            else:
                dt = transaction.executed_date
                ctx = {
                    "isDocument": False,
                    "fullTime": dt.strftime('%Y-%m-%d %H:%M:%S'),
                    "isAllocation": False,
                    "id": "{0}".format(transaction.pk),
                    "accountName": transaction.account.name,
                    "accountID": "{0}".format(transaction.account.pk),
                    "type": transaction.type,
                    "typeID": "1",
                    "date": dt,
                    "dateString": dt.strftime('%b %d'),
                    "change": "{:.2f}".format(transaction.amount),
                    "balance": "{:.2f}".format(transaction.new_balance),
                    "createdDate":
                        transaction.created_date.strftime('%Y%m%d%H%M%S'),
                    "completedDate": dt.strftime('%Y%m%d%H%M%S'),
                    "isCanceled": False,
                    "shortDescription": transaction.type.replace(
                        "_", " ").capitalize(),
                    "description": transaction.type.replace("_",
                                                            " ").capitalize(),
                    "pending": False,
                    "failed": False,
                    "canBeCanceled": False
                }
                if transaction.type == ALLOCATION:
                    ctx["isAllocation"] = True
                    ctx["change"] = "0"
                    stocks = int(transaction.amount * 100)
                    bonds = 100 - stocks
                    ctx["description"] = "Allocation Change ({0}% stocks, {1}% bonds)".format(
                        stocks, bonds)

                if transaction.type in (WITHDRAWAL, FEE):
                    ctx["change"] = "{:.2f}".format(-float(ctx["change"]))

                transactions.append(ctx)

        for k, v in market_change_by_week.items():
            transactions.append(v)

        def format_date(x):
            x['date'] = x['date'].strftime('%Y%m%d%H%M%S')
            return x

        new_list = list(map(format_date,
                            sorted(transactions,
                                   key=lambda ko: ko['date'])))

        if _format == "csv":
            csv = "Account Name, Transaction Description, Amount, Ending Balance, Date Completed\n"
            for tr in transactions:
                if 'childTransactions' in tr:
                    for child_tr in tr["childTransactions"]:
                        csv += "{0}, \"{1}\", {2}, {3}, {4}\n" \
                            .format(child_tr["accountName"], child_tr["description"],
                                    child_tr["change"], child_tr["balance"], child_tr["fullTime"])
                else:
                    csv += "{0}, \"{1}\", {2}, {3}, {4}\n" \
                        .format(tr["accountName"], tr["description"],
                                tr["change"], tr["balance"], tr["fullTime"])

            return HttpResponse(csv, content_type="text/csv")
        return HttpResponse(json.dumps(new_list),
                            content_type="application/json")

    def post(self, request, *args, **kwargs):
        model = json.loads(request.POST.get("model", '{}'))
        new_transaction = Transaction()
        new_transaction.account = get_object_or_404(
            Goal,
            pk=model['account'],
            account__primary_owner=self.client)
        new_transaction.from_account = None
        new_transaction.to_account = None
        new_transaction.type = model["type"]
        new_transaction.amount = model["amount"]

        if model["fromAccount"]:
            new_transaction.from_account = get_object_or_404(
                ClientAccount,
                pk=model['fromAccount'],
                primary_owner=self.client)

        if model["toAccount"]:
            new_transaction.to_account = get_object_or_404(
                ClientAccount,
                pk=model['toAccount'],
                primary_owner=self.client)

        new_transaction.save()

        nt_return = {
            "id": new_transaction.pk,
            "account": new_transaction.account.pk,
            "type": new_transaction.type,
            "amount": new_transaction.amount
        }

        if new_transaction.from_account:
            nt_return["fromAccount"] = new_transaction.from_account

        if new_transaction.to_account:
            nt_return["toAccount"] = new_transaction.to_account

        return HttpResponse(json.dumps(nt_return),
                            content_type='application/json')


class ChangeAllocation(ClientView):
    def post(self, request, *args, **kwargs):
        goal = get_object_or_404(Goal,
                                 pk=kwargs["pk"],
                                 account__primary_owner=self.client)
        payload = json.loads(request.body.decode("utf-8"))
        goal.allocation = payload["allocation"]
        new_t = Transaction()
        new_t.account = goal
        new_t.amount = goal.allocation
        new_t.type = ALLOCATION
        # remove all the pending allocation transactions for this account
        Transaction.objects.filter(account=goal,
                                   type=ALLOCATION,
                                   status=PENDING).all().delete()
        new_t.save()
        goal.save()
        return HttpResponse(json.dumps({"transactionId": new_t.pk}),
                            content_type="application/json")


class NewTransactionMemoView(ClientView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("[]", content_type="application/json")

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body.decode("utf-8"))
        tr = get_object_or_404(
            Transaction,
            pk=payload["user_transaction_id"].replace("f", ""))
        trm = TransactionMemo()
        trm.transaction = tr
        trm.category = payload["category"]
        trm.comment = payload["comment"]
        trm.transaction_type = payload["transaction_type"]
        trm.save()
        return HttpResponse(json.dumps({"success": "ok"}),
                            content_type="application/json")


class ChangeGoalView(ClientView):
    def put(self, request, *args, **kwargs):
        goal = get_object_or_404(Goal,
                                 pk=kwargs["pk"],
                                 account__primary_owner=self.client)
        payload = json.loads(request.body.decode("utf-8"))
        goal.name = payload["name"]
        goal.completion_date = datetime.strptime(payload["goalCompletionDate"],
                                                 '%Y%m%d%H%M%S')
        goal.type = payload["goalType"]
        goal.account_type = payload["accountType"]
        goal.save()

        has_changed = False
        # clear payload
        region_allocations = payload["regions_allocation"]

        total_size = 0
        allocation_keys = region_allocations.keys()
        new_region_allocations = {}

        for k in allocation_keys:
            if int(region_allocations[k]["size"]*100) == 0:
                continue
            else:
                new_region_allocations[k] = {"size": region_allocations[k]["size"]}
            total_size += int(region_allocations[k]["size"]*100)

        if total_size != 100:
            region_allocations = None
        else:
            region_allocations = new_region_allocations

        if region_allocations:
            try:
                custom_regions = json.loads(goal.custom_regions)
            except (JSONDecodeError, TypeError):
                custom_regions = {}
            if len(custom_regions) > 0:
                if custom_regions == region_allocations:
                    has_changed = False
                else:
                    has_changed = True
                    goal.custom_regions = json.dumps(region_allocations)
            else:
                has_changed = True
                goal.custom_regions = json.dumps(region_allocations)

        # check optimization model
        optimization_mode = payload["optimization_mode"]
        if optimization_mode != goal.optimization_mode:
            goal.custom_optimization_mode = optimization_mode
            has_changed = True

        # check picked regions
        picked_regions = list(set(payload["picked_regions"]))
        if set(picked_regions) != set(json.loads(goal.picked_regions)):
            goal.custom_picked_regions = json.dumps(picked_regions)
            has_changed = True

        goal.custom_hedges = json.dumps(payload["hedges"])
        goal.save()

        if has_changed:
            if goal.is_custom_size:
                try:
                    goal.portfolios = json.dumps(calculate_portfolios_for_goal(goal))
                except OptimizationException as e:
                    print(e)
                    return HttpResponse('null',
                                        content_type="application/json",
                                        status=500)
            else:
                goal.portfolios = None
            goal.save()
            new_t = Transaction()
            new_t.account = goal
            new_t.amount = goal.allocation
            new_t.type = ALLOCATION
            # remove all the pending allocation transactions for this account
            Transaction.objects.filter(account=goal,
                                       type=ALLOCATION,
                                       status=PENDING).all().delete()
            new_t.save()

        return HttpResponse('null', content_type="application/json")


class SetAutoDepositView(ClientView):
    def post(self, request, *args, **kwargs):
        payload = json.loads(request.POST.get("model"))
        pk = payload["account"]
        goal = get_object_or_404(Goal,
                                 pk=pk,
                                 account__primary_owner=self.client)

        if hasattr(goal, "auto_deposit"):
            ad = goal.auto_deposit
        else:
            ad = AutomaticDeposit(account=goal)

        ad.amount = payload.get("amount", 0)
        ad.frequency = payload["frequency"]
        ad.enabled = payload["enabled"]
        ad.transaction_date_time_1 = datetime.strptime(
            payload["transactionDateTime1"], '%Y%m%d%H%M%S')
        td2 = payload.get("transactionDateTime2", None)
        if td2:
            ad.transaction_date_time_2 = datetime.strptime(td2, '%Y%m%d%H%M%S')
        ad.save()

        payload["id"] = ad.pk
        payload["lastPlanChange"] = ad.last_plan_change.strftime(
            '%Y%m%d%H%M%S')
        payload["nextTransaction"] = ad.next_transaction.strftime(
            '%Y%m%d%H%M%S')
        payload["amount"] = str(ad.amount)

        return HttpResponse(json.dumps(payload),
                            content_type="application/json")


class SetAutoWithdrawalView(ClientView):
    def post(self, request, *args, **kwargs):
        payload = json.loads(request.POST.get("model"))
        pk = payload["account"]
        goal = get_object_or_404(Goal,
                                 pk=pk,
                                 account__primary_owner=self.client)

        if hasattr(goal, "auto_withdrawal"):
            ad = goal.auto_withdrawal
        else:
            ad = AutomaticWithdrawal(account=goal)

        ad.amount = payload.get("amount", 0)
        ad.frequency = payload["frequency"]
        ad.enabled = payload["enabled"]
        ad.transaction_date_time_1 = datetime.strptime(
            payload["transactionDateTime1"], '%Y%m%d%H%M%S')
        td2 = payload.get("transactionDateTime2", None)
        if td2:
            ad.transaction_date_time_2 = datetime.strptime(td2, '%Y%m%d%H%M%S')
        ad.save()

        payload["id"] = ad.pk
        payload["lastPlanChange"] = ad.last_plan_change.strftime(
            '%Y%m%d%H%M%S')
        payload["nextTransaction"] = ad.next_transaction.strftime(
            '%Y%m%d%H%M%S')
        payload["amount"] = str(ad.amount)

        return HttpResponse(json.dumps(payload),
                            content_type="application/json")


class Withdrawals(ClientView):
    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body.decode('utf8'))
        goal = get_object_or_404(Goal,
                                 pk=kwargs["pk"],
                                 account__primary_owner=self.client)
        new_transaction = Transaction()
        new_transaction.account = goal
        new_transaction.from_account = None
        new_transaction.to_account = None
        new_transaction.type = WITHDRAWAL
        new_transaction.amount = payload["amount"]
        new_transaction.save()

        nt_return = {
            "transactionId": new_transaction.pk,
            "account": new_transaction.account.pk,
            "type": new_transaction.type,
            "amount": new_transaction.amount
        }

        return HttpResponse(json.dumps(nt_return),
                            content_type="application/json")


class AnalysisBalances(ClientView):
    def get(self, request, *args, **kwargs):
        # get all the performances
        ret = []
        goal_pk = request.GET.get("account")
        goal = get_object_or_404(Goal,
                                 pk=goal_pk,
                                 account__primary_owner=self.client)
        trs = goal.transactions.filter(
            type=MARKET_CHANGE).order_by('executed_date').all()
        if trs:
            for transaction in trs:
                r_obj = {
                    "d": transaction.executed_date.strftime('%Y%m%d%H%M%S'),
                    "inv": transaction.inversion,
                    "bal": transaction.new_balance
                }

                ret.append(r_obj)

        return HttpResponse(json.dumps(ret), content_type="application/json")


class AnalysisReturns(ClientView):
    def get(self, request, *args, **kwargs):
        # get all the performances
        ret = []
        counter = 0
        for p in Performer.objects.all():
            counter += 1
            obj = {}
            if p.group == STRATEGY:
                obj["name"] = p.name
            else:
                obj["name"] = "{0} ({1})".format(p.name, p.symbol)

            obj["group"] = p.group
            obj["initial"] = False
            obj["lineID"] = counter
            obj["returns"] = []
            returns = SymbolReturnHistory.objects.filter(
                symbol=p.symbol).order_by('date').all()
            if returns:
                b_date = returns[0].date - timedelta(days=1)
                obj["returns"].append({
                    "d": "{0}".format(int(1000 * time.mktime(b_date.timetuple(
                    )))),
                    "i": 0,
                    "ac": 1,
                    "zero_balance": True
                })
            for r in returns:
                r_obj = {
                    "d":
                        "{0}".format(int(1000 * time.mktime(r.date.timetuple()))),
                    "i": r.return_number
                }
                if p.group == STRATEGY:
                    r_obj["ac"] = p.allocation
                obj["returns"].append(r_obj)

            ret.append(obj)

        for account in self.client.accounts.all():
            for goal in account.goals.all():
                trs = goal.transactions.filter(
                    type=MARKET_CHANGE).order_by('executed_date').all()
                if not trs:
                    continue
                counter += 1
                obj = dict()
                obj["name"] = goal.name
                obj["group"] = "ACCOUNT"
                obj["createdDate"] = goal.created_date.strftime('%Y%m%d%H%M%S')
                obj["initial"] = False
                obj["lineID"] = counter
                b_date_1 = trs[0].executed_date - timedelta(days=2)
                b_date_2 = trs[0].executed_date - timedelta(days=1)

                obj["returns"] = [{
                    "d": "{0}".format(int(1000 * time.mktime(
                        b_date_1.timetuple()))),
                    "i": 0,
                    "zero_balance": True,
                    "ac": goal.allocation
                }, {
                    "d": "{0}".format(int(1000 * time.mktime(
                        b_date_2.timetuple()))),
                    "i": 0,
                    "zero_balance": True
                }]

                for transaction in trs:
                    r_obj = {
                        "d": "{0}".format(int(1000 * time.mktime(
                            transaction.executed_date.timetuple()))),
                        "i": transaction.return_fraction
                    }

                    obj["returns"].append(r_obj)

                ret.append(obj)

        return HttpResponse(json.dumps(ret), content_type="application/json")


class ZipCodes(ClientView):
    def get(self, request, *args, **kwargs):
        col, is_new = CostOfLivingIndex.objects.get_or_create(
            state=self.client.state)

        ret = {
            "zip_code": self.client.post_code,
            "state": self.client.state,
            "cost_of_living_index": "{0}".format(col.value)
        }

        return HttpResponse(json.dumps(ret), content_type="application/json")


class FinancialPlansView(ClientView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(self.client.get_financial_plan,
                            content_type="application/json")

    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body.decode('utf-8'))

        if hasattr(self.client, 'financial_plan'):
            plan = self.client.financial_plan
        else:
            plan = FinancialPlan(client=self.client, name=payload["name"])

        for k, v in payload.items():
            setattr(plan, k, v)
        plan.save()
        payload["id"] = plan.pk
        return HttpResponse(json.dumps(payload),
                            content_type="application/json")


class FinancialPlansAccountAdditionView(ClientView):
    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body.decode('utf-8'))
        goal = get_object_or_404(Goal,
                                 pk=payload["account_id"].strip("f"),
                                 account__primary_owner=self.client)

        fp_account, is_new = FinancialPlanAccount.objects.get_or_create(
            client=self.client,
            account=goal)
        fp_account.annual_contribution_cents = payload[
            "annual_contribution_cents"]
        fp_account.save()
        payload["id"] = fp_account.pk
        payload["bettermentdb_account_id"] = goal.pk
        del payload["account_id"]
        return HttpResponse(json.dumps(payload),
                            content_type="application/json")


class FinancialPlansAccountDeletionView(ClientView):
    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body.decode('utf-8'))
        goal = get_object_or_404(Goal,
                                 pk=payload["account_id"].strip("f"),
                                 account__primary_owner=self.client)

        try:
            fp_account = FinancialPlanAccount.objects.get(client=self.client,
                                                          account=goal)
        except ObjectDoesNotExist:
            fp_account = None

        if fp_account is not None:
            fp_account.delete()

        return HttpResponse("null", content_type="application/json")


class FinancialPlansExternalAccountAdditionView(ClientView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(self.client.external_accounts,
                            content_type="application/json")

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body.decode('utf-8'))
        external_account = FinancialPlanExternalAccount(client=self.client)
        for k, v in payload.items():
            setattr(external_account, k, v)
        external_account.save()
        payload["id"] = external_account.id
        return HttpResponse(json.dumps(payload),
                            content_type="application/json")


class FinancialPlansExternalAccountDeletionView(ClientView):
    def put(self, request, *args, **kwargs):
        payload = json.loads(request.body.decode('utf-8'))
        del payload["client"]
        del payload["id"]
        pk = kwargs["pk"]
        fp_external = get_object_or_404(FinancialPlanExternalAccount,
                                        pk=pk,
                                        client=self.client)

        for k, v in payload.items():
            setattr(fp_external, k, v)

        payload["id"] = fp_external.pk
        return HttpResponse(json.dumps(payload),
                            content_type="application/json")

    def delete(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        fp_external = get_object_or_404(FinancialPlanExternalAccount,
                                        pk=pk,
                                        client=self.client)
        fp_external.delete()
        return HttpResponse("null", content_type="application/json")


class FinancialProfileView(ClientView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(self.client.get_financial_profile,
                            content_type="application/json")

    def post(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        payload = json.loads(request.body.decode('utf-8'))
        spouse_retired = payload.get("spouse_retired", None)
        if spouse_retired is None:
            payload["spouse_retired"] = False

        if hasattr(self.client, 'financial_profile'):
            profile = self.client.financial_profile
        else:
            profile = FinancialProfile(client=self.client)

        for k, v in payload.items():
            setattr(profile, k, v)
        profile.save()
        payload["id"] = profile.pk
        return HttpResponse(json.dumps(payload),
                            content_type="application/json")
