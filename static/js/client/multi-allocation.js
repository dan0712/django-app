define("views/advice/allocationRecommendationView", ["underscore", "common/slider", "models/v1/allocationChange", "models/v1/allocationChangeTaxImpact", "services/allocationService", "views/advice/baseRecommendationView", "views/taxImpact/taxImpactView", "components/common/scripts/analytics/analytics"], function(e, t, n, r, i, s, o, u) {
        return s.extend({
            template: "advice/allocationRecommendation",
            events: {
               // "keyup .current-value input": "changeAllocationFromTextBox",
               // "change .current-value input": "changeAllocationFromInput",
                //"blur .current-value input": "blurAllocationInput",
                "click .show-tax-impact": "showTaxImpact",
                "mouseup .ui-slider-handle": "allocationSliderDragged"
            },
            toolTips: {
                ".risk-help": {
                    position: {
                        my: "bottom center",
                        at: "top center"
                    }
                }
            },
            templateHelpers: {
                remainingGoalTerm: function() {
                    return this.self.term
                },
                stockAllocation: function() {
                    return this.pct(this.self.model.num("allocation"));
                },
                bondAllocation: function() {
                    return this.pct(1-this.self.model.num("allocation"));
                },
                satelliteAllocation: function(){
                    return this.pct(this.self.model.num("satelliteAlloc"));
                },
                coreAllocation: function(){
                    return this.pct(1-this.self.model.num("satelliteAlloc"));
                },
                showTaxImpactButton: function() {
                    return !this.self.model.isIRA() && this.self.model.getCurrentBalance() > 0
                }
            },
            onInitialize: function() {
                s.prototype.onInitialize.apply(this), this.term = this.options.termYears || this.model.remainingGoalTerm()
            },
            onRender: function() {
                this.$allocation_slider = this.createSlider()
                this.$satellite_slider = this.createSatelliteSlider()
                this.updateAllocationDisplay([this.model.num("allocation"), this.model.num("satelliteAlloc")])
            },
            onShow: function() {
                this.drawRecommendation(), this.updateAdvice([this.model.num("allocation"), this.model.num("satelliteAlloc")])
            },
            reset: function() {
                // labels
                var allocation = this.model.num("allocation");
                var satellite = this.model.num("satelliteAlloc");

                this.$(".existing-value .value").text((100 * allocation).round(0) + "%");
                this.$(".existing-bonds-value .value").text((100 * (1 - allocation)).round(0) + "%");

                this.$(".existing-satellite-value .value").text((100 * satellite).round(0) + "%");
                this.$(".existing-core-value .value").text((100 * (1 - satellite)).round(0) + "%");
                
                this.$allocation_slider.slider("value", allocation);
                this.$satellite_slider.slider("value", 1-satellite);

                this.taxImpactAnimation && this.taxImpactAnimation.stop(!0);
                this.$(".show-tax-impact").hide();
                this.updateAdvice([allocation, satellite]);
                this.trigger("valueChanged", {
                    allocation: allocation,
                    satelliteAlloc: satellite
                });
                this.trigger("valueReset")
            },
            getModel: function() {
                var values = this.getValue();
                var allocation = Number(values[0]);
                var satellite  = Number(values[1]);
                return this.model.num("allocation") !== e ? new n({
                    allocation: allocation,
                    satelliteAlloc: satellite,
                    account: this.model
                }) : null
            },
            getValue: function() {
                var allocation = this.$allocation_slider.slider("value");
                var satellite = 1-this.$satellite_slider.slider("value");
                return [allocation,  satellite];
            },
            refreshAdvice: function(t) {
                t.termYears && (this.term = t.termYears, this.drawRecommendation()), e.isUndefined(t.allocation) ? this.updateAdvice(this.getValue()) : this.updateAdvice([t.allocation, t.satelliteAlloc])
            },
            drawRecommendation: function() {
                t.drawSliderRecommendation(this.$allocation_slider, this.getRecommended())
            },
            allocationSliderDragged: function(e) {
               /* var t = this.getValue() * 100;
                u.track("ElementClicked", {
                    Name: "AllocationChange",
                    Location: "Advice",
                    Type: "Slider",
                    Value: t
                })*/
            },
            changeAllocationFromTextBox: function(e) {
                this.changeAllocationFromInput(e);
                var t = this.getValue() * 100;
                u.track("ElementClicked", {
                    Name: "AllocationChange",
                    Location: "Advice",
                    Type: "TextBox",
                    Value: t
                })
            },
            changeAllocationFromInput: function(e) {
                var t = $(e.target),
                    n = t.val(),
                    r = t.intVal() / 100;
                if (!r || r < 0) r = 0;
                n.length >= 3 && r.round(2) > 1 && (n.substring(0, 3) === "100" ? r = 1 : r = parseInt(n.substring(0, 2), 10) / 100), n !== "" && t.val((100 * r).round(0)), this.trigger("valueChanged", {
                    allocation: r
                }), r === this.model.num("allocation") ? (this.taxImpactAnimation && this.taxImpactAnimation.stop(!0), this.$(".show-tax-impact").hide(), this.trigger("valueReset")) : this.updateAllocationDisplay(r)
            },
            blurAllocationInput: function(e) {
                var t = $(e.target).intVal() / 100;
                t === this.model.num("allocation") && this.reset()
            },
            updateAllocationDisplay: function(values) {
                this.$(".show-tax-impact").is(":visible") || (this.$(".existing-value").is(":visible") && u.track("ElementViewed", {
                    Name: "TaxImpact",
                    Type: "Button",
                    Module: "AllocationChange",
                    Location: "Advice"
                }), this.taxImpactAnimation = this.$(".show-tax-impact").delay(250).slideDown(50)),
                this.$(".existing-value .value").text((100 * values[0]).round(0) + "%"),
                this.$(".existing-bonds-value .value").text((100 * ( 1 - values[0] )).round(0) + "%"),
                this.$(".existing-satellite-value .value").text((100 * values[1]).round(0) + "%"),
                this.$(".existing-core-value .value").text((100 * (1-values[1])).round(0) + "%")


            },
            updateAdvice: function(values) {
                var allocation = values[0];
                var t = this.getTolerance(allocation);
                this.$(".advice-value .risk-level").css("color", t.color).text(t.label), this.$(".advice-value .remaining-term").text(this.term)
            },
            createSlider: function() {
                var disabled=false;
                var allocation = this.model.num("allocation");
                var stocks_and_bonds = this.model.get("stocks_and_bonds");
                if (stocks_and_bonds != "both") {disabled=true};
                if(stocks_and_bonds=="bonds"){allocation = 0; this.model.set("allocation", 0)}
                if(stocks_and_bonds=="stocks"){allocation = 1; this.model.set("allocation", 1)}

                var allocation_slider = this.slider(".allocation-slider", {
                    min: 0,
                    max: 1,
                    step: .01,
                    disabled: disabled,
                    value: allocation,
                    slide: function(e, t) {
                        var values = values = [t.value, 1-this.$satellite_slider.slider("value")];
                        this.trigger("valueChanged", {
                            allocation: values[0],
                            satelliteAlloc: values[1]
                        });
                        this.updateAllocationDisplay(values);
                        (values[1].toFixed(2) === this.model.num("satelliteAlloc").toFixed(2)) && (values[0] === this.model.num("allocation")) && (this.trigger("valueReset"), this.taxImpactAnimation && this.taxImpactAnimation.stop(!0), this.$(".show-tax-impact").hide())
                    }.bind(this)
                });
                return this.bind("valueChanged", function(t) {
                    (t.allocation || t.allocation === 0) && allocation_slider.slider("value", t.allocation)
                }), allocation_slider
            },

            createSatelliteSlider: function() {
                // The value of the sat slider is actually the core percent. 
                var sat_slider = this.slider(".satellite-slider", {
                    min: 0,
                    max: 1,
                    step: .01,
                    value: 1-this.model.num("satelliteAlloc"),
                    slide: function(e, t) {
                        if (t.value < 0.7) {
                            $(this).slider( "value" , .7 );
                            return false;
                        }
                        var values = [this.$allocation_slider.slider("value"), 1-t.value];
                        this.trigger("valueChanged", {
                            allocation: values[0],
                            satelliteAlloc: values[1]
                        });
                        this.updateAllocationDisplay(values);
                        (values[1].toFixed(2) === this.model.num("satelliteAlloc").toFixed(2)) && (values[0] === this.model.num("allocation")) && (this.trigger("valueReset"), this.taxImpactAnimation && this.taxImpactAnimation.stop(!0), this.$(".show-tax-impact").hide())
                    }.bind(this)
                });
                return this.bind("valueChanged", function(t) {
                    (t.satelliteAlloc || t.satelliteAlloc === 0) && sat_slider.slider("value", 1-t.satelliteAlloc)
                }), sat_slider
            },
            getRecommended: function() {
                return i.getRecommendedAllocation(this.model, {
                    termYears: this.term
                })
            },
            getTolerance: function(e) {
                return i.getRiskTolerance(this.getRecommended(), e)
            },
            showTaxImpact: function(e) {
                u.track("ElementViewed", {
                    Name: "TaxImpact",
                    Location: "Advice"
                });
                var t = new r({
                    allocation: this.getValue(),
                    account: this.model
                });
                BMT.modal.show(new o({
                    model: t
                }))
            }
        })
    }),define("views/common/addGoalView", ["services/firmFetcher", "jquery", "underscore", "backbone", "common/betterment.views", "hbs!views/common/addGoal/cardRow", "modules/modelStrategyBuilder", "models/account", "models/rolloverFollowup", "views/common/addGoal/addGoalCardView", "views/common/addGoal/addGoalCardDefinitions", "views/profile/editBeneficiariesView", "views/advice/goalCompleteView", "components/account/scripts/services/retirementService", "components/account/scripts/services/goalService", "components/account/scripts/services/goalTypeService", "components/common/scripts/services/domainService", "components/portfolio/scripts/services/portfolioSetService", "components/common/scripts/analytics/analytics", "services/financialPlanUpdater", "views/common/termsOfServiceView", "components/account/scripts/constants/accountTypes"], function (firm, e, t, n, r, i, s, o, u, a, f, l, c, h, p, d, v, m, g, y, b, w) {
    var E = {
            fixed: !0,
            delay: 250
        },
        S = {
            my: "left center",
            at: "right center"
        },
        x = w.isInvesting,
        T = w.isIRA,
        N = r.ModalView.extend({
            template: "common/addGoal",
            className: "add-goal",
            regions: {
                termsOfServiceRegion: ".terms-of-service"
            },
            toolTips: {
                ".choose.help-icon": {
                    position: S,
                    hide: E
                },
                ".tax-advantage.help-text": {
                    position: S,
                    hide: E
                },
                ".essentials.help-text": {
                    position: S
                },
                ".major-savings.help-text": {
                    position: S
                },
                ".ethical-investing.help-text": {
                    position: S
                },
                ".legend .help-text": {
                    position: {
                        my: "top left",
                        at: "bottom center"
                    },
                    hide: E
                }
            },
            templateHelpers: {
                model: function () {
                    return this.self.model
                },
                header: function () {
                    return this.model() ? "Change Goal Type" : "Add Goal"
                },
                subheader: function () {
                    return "Choose one"
                },
                hideExit: function () {
                    return this.self.options.hideExit
                },
                accountTypeSelector: function () {
                    var e = {};
                    return e[w.INVESTING] = "Regular (Taxable)", t.each(w.getIRATypes(), function (t) {
                        (!this.model() || this.model().isNew()) && !BMT.accounts().hasAccountWithType(t) && BMT.accountGroup.isPersonal() && (e[t] = w.getDisplayName(t))
                    }, this), this.build_dropdown_menu(e, {
                        name: "accountType",
                        "class": "account-type-selector",
                        value: this.model() ? this.model().get("accountType") : w.INVESTING
                    })
                }
            },
            events: {
                "change .account-type-selector": "accountTypeChanged",
                "click .modal-buttons .back": "onBack",
                "click button.ok": "onOK"
            },
            validation: {
                labels: {
                    name: "Name your goal. You can change this any time."
                },
                model: function () {
                    return o.Model.buildGhost()
                }
            },
            allCardViews: [],
            onRender: function () {
                this.$nextStepInvesting = this.$(".next-step.investing"), this.$nextStepTerms = this.$(".next-step.terms"), this.$nameInput = this.$("input[name=name]"), this.$accountTypeRow = this.$(".account-type-row"), this.$goalNameRow = this.$(".goal-name-row"), this.$okButton = this.$(".modal-buttons button.ok"), this.createCards(), this.showOrHideAgreements()
            },
            onShow: function () {
                this.getSelectedCard() && this.getSelectedCard().onClick()
            },
            _isNew: function () {
                return !this.model || this.model.isNew()
            },
            _isRollover: function () {
                return this.options.isRollover
            },
            createCards: function () {
                var e = this.options.lists || this.defaultCardLists(),
                    n = this.options.cards || this.defaultCards();
                this.allCardViews = [], t.each(e, function (e) {
                    this.createCardList(e), t.each(n[e.key], function (t) {
                        var n = this.addCardToList(e.key, t);
                        this.model && !this._isRollover() && n.initFromAccount(this.model), this._isRollover() && n.isRollover() && n.setSelected(!0), this.listenTo(n, "click", this.selectCard)
                    }, this)
                }, this)
            },
            createCardList: function (e) {
                if(e.key==="ethical-investing"){
                     this.$(".second-card-list .next-step").before(i(e))
                }
                else{
                     this.$(".first-card-list").append(i(e))
                }

            },
            addCardToList: function (e, t) {
                var n = new a(t);
                return n.render(), this.$(".card-lists > li." + e).append(n.$el), this.allCardViews.push(n), n
            },
            getCards: function () {
                return this.allCardViews
            },
            getSelectedCard: function () {
                return t.find(this.getCards(), function (e) {
                    return e.isSelected()
                })
            },
            accountTypeChanged: function (t) {
                var n = e(t.currentTarget).val();
                this.showOrHideAgreements(n), T(n) ? this.$goalNameRow.slideUp() : this.$goalNameRow.slideDown()
            },
            selectCard: function (e, n) {
                if (!e.isEnabled()) return;
                var r = this.$("li"),
                    i = "";
                this.model && !this.model.isIRA() ? i = this.model.get("name") : n.goalName && (i = n.goalName), t.each(this.getCards(), function (t) {
                    t !== e && t.setSelected(!1)
                }), e.setSelected(!0), this.hideAllValidation(), this.$okButton.prop("disabled", !1), this.toggleAccountTypeSelector(!!n.accountType);
                var s = n.accountType ? n.accountType : this.$(".account-type-selector").val();
                this.showOrHideAgreements(s, n.rollover), g.track("GoalSelected", {
                    Module: "WebApp",
                    Location: "GoalModal",
                    GoalType: n.goalType,
                    IncomeGoal: n.income
                }), x(n.accountType) || !n.accountType ? (r.removeClass("highlight"), this.$nextStepInvesting.slideDown().addClass("highlight"), this.$nameInput.val(i), this.model && this.$nameInput.focus().select()) : (r.addClass("highlight"), this.$nextStepInvesting.slideUp())
            },
            toggleAccountTypeSelector: function (e) {
                this.$nextStepInvesting.is(":visible") ? this.$accountTypeRow[e ? "slideUp" : "slideDown"]() : this.$accountTypeRow.toggle(!e)
            },
            showOrHideAgreements: function (e, t) {
                if (!this._isNew() || this._isRollover() || !BMT.user.isFull()) {
                    this.$nextStepTerms.hide();
                    return
                }
                var n = x(e) && BMT.accounts().hasInvestingAccount();
                if (t || !e || n) {
                    this.$nextStepTerms.slideUp();
                    return
                }
                this.termsOfServiceRegion.show(new b({
                    showIraAgreement: !x(e),
                    showSEPAgreement: e === w.SEP_IRA
                })), this.$nextStepTerms.slideDown()
            },
            _highlightCard: function (e) {
                e.is(".selected") || (this.$(".goal-card").removeClass("selected"), e.addClass("selected"))
            },
            onBack: function (e) {
                e && e.preventDefault(), BMT.refreshAccounts(), BMT.modal.close(this)
            },
            onOK: function (e) {
                var n = this.getSelectedCard(),
                    r = n.isRollover(),
                    i = n.getAccountType();
                if (!this.model && r) {
                    BMT.router.navigate("rollover", !0), BMT.modal.close(this);
                    return
                }
                i || (i = this.$(".account-type-selector").val());
                var s = T(i),
                    u = this._isRollover() && r ? {} : {
                        goalType: n.getGoalType(),
                        name: s ? n.getGoalName() : this.$nameInput.val(),
                        accountType: i,
                        income: n.isIncome(),
                        rollover: !BMT.user.isFull() && r
                    };
                this.termsOfServiceRegion.currentView && t.extend(u, this.termsOfServiceRegion.currentView.getAgreementValues());
                var a = this.model || o.Model.buildGhost();
                if (a.validate(u)) {
                    this.termsOfServiceRegion.currentView && this.termsOfServiceRegion.currentView.checkAgreements(), this.triggerAllValidation();
                    return
                }
                if (!s && this._nameIsTaken(u.name)) {
                    this.updateFieldValidation(this.$nameInput, "Goal name exists. Choose a different name.");
                    return
                }
                n.onSelect(a), a.set("accountGroup", BMT.accountGroup, {
                    silent: !0
                }), a.isNew() ? this._processNewGoal(a, u, r) : a.get("goalType") === u.goalType && a.isIncome() === u.income ? BMT.modal.close(this) : this._processExistingGoal(a, u)
            },
            _continueAfterUpdate: function (e, t) {
                var n = !this.model,
                    r = t ? "rollover" : "goalSetup";
                n || BMT.currentPage !== r ? (BMT.selectedAccount = e, BMT.router.navigate(r, !0)) : this.options.callback && this.options.callback(), BMT.modal.close(this)
            },
            _nameIsTaken: function (e) {
                return BMT.accounts().reduce(function (t, n) {
                    return t || this.model !== n && e.toLowerCase() === n.get("name").toLowerCase()
                }, !1, this)
            },
            _processNewGoal: function (e, t, n) {
                e.set(t), this._getAfterProcessStrategy(n).execute(e)
            },
            _processExistingGoal: function (e, t) {
                this.block(), e.save(t, {
                    success: function () {
                        BMT.analytics.track("GoalUpdated", {
                            Location: "GoalModal",
                            GoalId: e.get("id"),
                            GoalType: e.get("goalType"),
                            IncomeGoal: e.is("income")
                        }), this._getAfterProcessStrategy(!1).execute(e)
                    }.bind(this),
                    complete: function () {
                        this.unblock()
                    }.bind(this)
                })
            },
            _getAfterProcessStrategy: function (e) {
                var t = function (t) {
                        this._continueAfterUpdate(t, e)
                    }.bind(this),
                    n = function (e, t) {
                        if (e.isNew()) {
                            var n = p.getDefaultTermForContext({
                                goalType: e.get("goalType"),
                                income: e.get("income"),
                                isRetired: BMT.user.isRetired(),
                                age: BMT.user.getAge(),
                                isPersonal: e.get("accountGroup").isPersonal()
                            });
                            e.setGoalTerm(n);
                            var r = this._createGoal(e).then(function () {
                                BMT.analytics.track("GoalAdded", {
                                    Location: "GoalModal",
                                    GoalId: e.get("id"),
                                    GoalType: e.get("goalType"),
                                    IncomeGoal: e.is("income")
                                })
                            });
                            t ? r.then(this._addAccountToSelectedPlan.bind(this, e)).then(function () {
                                this.unblock();
                                var t = "Your " + e.get("name") + " goal has been created " + "and added to your retirement plan.";
                                this._flashAndGoToAdvice(e, t)
                            }.bind(this)) : r.then(this._launchCompleteGoalModal.bind(this, e))
                        } else {
                            var i = "Your goal type has been updated to " + e.getGoalTypeLabel() + ".";
                            e.isRetirement() && h.canGiveRetireeAdvice(BMT.user) && (i += " Please review your goal strategy, allocation and plan-to age."), this._flashAndGoToAdvice(e, i)
                        }
                    }.bind(this);

                return (new s).when("goalType", ["BUILD_WEALTH", "BUILD_WEALTH_ETHICAL"], n).when("goalType", ["RETIREMENT", "RETIREMENT_ETHICAL"], function (r) {
                    this.getSelectedPlan().is("complete") && !r.isIncome() ? n(r, !0) : !e && (h.canGiveRetireeAdvice(BMT.user) || r.isIncome()) ? n(r) : t(r)
                }.bind(this)).otherwise(t)
            },
            _createGoal: function (e) {
                this.block();
                var t = e.allocationRecommendation(),
                    n = e.save({
                        allocation: t
                    }).then(function () {
                        return BMT.refreshAccounts()
                    }).then(function () {
                        return this.trigger("goalCreated", e), m.loadPortfolioSetForAccount(e)
                    }.bind(this));
                return n.always(this.unblock.bind(this)), n
            },
            _addAccountToSelectedPlan: function (e) {
                var t = this.getSelectedPlan();
                return this.block(), y.getStateSynchronizer({
                    account: e,
                    financialPlan: t,
                    enabled: !0
                }).save().then(function () {
                    return this.getSelectedPlan().fetch()
                }.bind(this))
            },
            _launchCompleteGoalModal: function (e) {
                this._goToDestination("advice", e), BMT.modal.replaceWith(new c({
                    isRollover: !1,
                    model: e
                }))
            },
            _flashAndGoToAdvice: function (e, t) {
                BMT.flash(t), this._goToDestination("advice", e), BMT.modal.close(this)
            },
            _goToDestination: function (e, t) {
                BMT.selectedAccount = t, BMT.vent.trigger("addGoal:saved", t), this.options.inPlace || BMT.router.navigate(e, {
                    trigger: !0
                })
            },
            getSelectedPlan: function () {
                return BMT.user.get("financialPlans").selected()
            },
            defaultCardLists: function () {
                var firmModel = firm.get();
                var e = [],
                    t = BMT.accountGroup.allowsIRAs() && (this._isNew() || this.model.isIRA() || !BMT.user.isFull()),
                    n = this.model && this.model.isInvestingAccount() || this._isNew() && !BMT.accounts().maxedOutInvestmentGoals(),
                    canUseEthical = firmModel.get("can_use_ethical_portfolio");

                return t && e.push({
                    key: "tax-advantage",
                    name: "Tax-advantaged Retirement",
                    tooltip: 'Individual Retirement Accounts (IRA) are given special tax advantages by the IRS. SMSF contributions are generally tax-free today and SMSFs are generally tax-free when you retire. If you&#39;re not sure which one is right for you, '
                }), n && (e.push({
                    key: "essentials",
                    name: "Essentials",
                    tooltip: "Everyone should have essential goals to help manage your money."
                }), e.push({
                    key: "major-savings",
                    name: "Major Savings",
                    tooltip: "If you plan to make a major purchase in the future, it&#39;s better to save for it through smart investing than buy it on credit."
                }), canUseEthical && e.push({
                    key: "ethical-investing",
                    name: "Ethical Investing",
                    tooltip: "If you plan to save or grow your wealth using only Ethical funds (companies with no exposure to tobacco and controversial weapons) to help manage your money."
                })), e
            },
            defaultCards: function () {
                var e = {
                    essentials: [f.get("EMERGENCY"), f.get("BUILD_WEALTH"), f.get("RETIREMENT"), f.get("RETIREMENT_INCOME")],
                    "major-savings": [f.get("HOUSE"), f.get("EDUCATION"), f.get("OTHER")]
                };
                var firmModel = firm.get();
                if (firmModel.get("can_use_ethical_portfolio")) {
                    e["ethical-investing"] = [f.get("EMERGENCY_ETHICAL"), f.get("BUILD_WEALTH_ETHICAL"), f.get("RETIREMENT_ETHICAL"), f.get("RETIREMENT_INCOME_ETHICAL")]
                }
                return e["tax-advantage"] = t.reduce(w.getIRATypes(), function (e, t) {
                    var n = !this._isRollover() && this.model && this.model.isAccountType(t) || !BMT.accounts().hasAccountWithType(t),
                        r = f.inherit(t, {
                            enabled: n,
                            checked: !n
                        });
                    return e.push(r), e
                }, [], this), e["tax-advantage"].push(f.get("ROLLOVER")), e
            }
        }),
        C = N.show;
    return N.show = function (e) {
        return e = e || {}, !e.model && BMT.accounts().maxedOutGoals() ? BMT.alert({
            title: "Cannot Create New Goal",
            icon: "warning",
            body: "Sorry, at this time you can only have a maximum of ten regular investing goals and two IRA goals. Let us know if you're interested in having more goals by sending an email to support@betasmartz.com."
        }) : C.call(N, e)
    }, N
}), define("models/withheldBonus", ["jquery", "underscore", "backbone", "common/betterment.models"], function (e, t, n, r) {
    return r.RelationalModel.extend({
        doesWithdrawalPushBonusBelowThreshold: function (e) {
            return e > this.num("maxWithdrawalToKeepBonus") && this.num("withholdingDaysRemaining") > 0
        }
    })
}), define("models/v2/externalAccount", ["underscore", "components/common/scripts/models/v2/baseModels"], function (e, t) {
    var n = {
            transaction_cheque_account: "Transaction / Cheque Account",
            savings_deposit_account: "Savings / Deposit Account",
            term_deposit_account: "Term Deposit Account",
            brokerage_account: "Brokerage Account",
            my_super: "MySuper",
            super_fund: "Super Fund",
            smsf: "SMSF"
        },
        r = {
            endpoint: "/external_accounts",
            isSpousal: function () {
                return this.get("accountOwner") === "spouse"
            },
            isEmployerPlan: function () {
                var t = ["401k", "roth_401k", "profit_sharing", "403b", "401a", "457b", "thrift_savings_plan"];
                return e.contains(t, this.get("accountType"))
            },
            hashKey: function () {
                return ["accountOwner", "accountType", "annualContributionCents", "balanceCents"].reduce(function (e, t) {
                    return e + t + ":" + this.get(t) + ";"
                }.bind(this), "")
            },
            displayAccountType: function () {
                return n[this.get("accountType")]
            }
        };
    r.validation = {
        institutionName: {
            required: !0
        },
        accountType: {
            required: !0
        },
        investmentType: {
            required: !0
        },
        accountOwner: {
            required: !0
        },
        balanceCents: {
            required: !0
        },
        annualContributionCents: {
            required: !0
        },
        advisorFeePercent: {
            range: [0, 100],
            required: !1
        }
    };
    var i = {
        VALID_ACCOUNT_TYPES: n
    };
    return t.RelationalModel.extend(r, i)
}), define("views/advice/multiAllocationModalView", ["jquery", "underscore", "common/betterment.views"], function ($, _, n) {
    return n.ModalView.extend({
            template: "advice/confirmMultiAllocationChanges",
            className: "multi-allocation-modal",
            events: {
                "click .ok": "saveChanges",
                "click .cancel": "closeModal"
            },
            templateHelpers: {
               optMode: function () {
                   var opt = this.self.options.multiAllocationController.optimization_mode;
                   if(opt == 1)return "Auto";
                   return "Custom Weights"
               },
               isAutoMode: function () {
                   return this.self.isAutoMode();
               },
            },
            isAutoMode: function () {
                   var opt = this.options.multiAllocationController.optimization_mode;
                   return (opt == 1);
            },
            onInitialize: function () {
                this.changes = this.options.multiAllocationController.getChanges();
            },
            onRender: function () {
                var i, row, market, m_size, currency_hedge;

                for (i in this.changes) {
                    market = this.options.multiAllocationController.$regions_dict[this.changes[i].key];

                    if(this.isAutoMode()){
                        if(this.changes[i].is_region_picked){
                            m_size = "Yes";
                        }
                        else{
                            m_size = "No";
                        }
                    }
                    else{
                        m_size = parseInt(this.changes[i].size);
                        if (m_size == null || m_size == undefined || isNaN(m_size)) {
                            m_size = "---"
                        }
                        else {
                            m_size = m_size + "% ";
                        }

                    }


                    if (this.changes[i].currency_hedge_value == null || this.changes[i].currency_hedge_value == undefined) {
                        currency_hedge = "---"
                    }
                    else {
                        currency_hedge = this.changes[i].currency_hedge_value ? "Yes" : "No";
                    }
                    row = '<tr><td>' + market + '</td><td>' + m_size + '</td><td>' + currency_hedge + '</td></tr>';
                    this.$('tbody').append(row);
                }

            },
            saveChanges: function () {
                this.closeModal();
                this.options.multiAllocationController.save();

            },
            closeModal: function () {
                this.options.modal.close(this);
            },

            onShow: function () {
            }
        }
    );
}), define("components/portfolio/scripts/services/portfolioSetService", ["underscore", "components/portfolio/scripts/models/portfolioSet", "components/common/scripts/models/appData", "components/account/scripts/constants/accountTypes", "jquery"], function (e, t, n, r, jquery) {
    var i = {},
        s = {};
    //var _ = e;
    return {
        loadPortfolioSet: function (e) {
            var n = i[e],
                r = s[e],
                o = new $.Deferred;
            if (n) o.resolve(n);
            else {
                var u = !!r;
                u || (r = s[e] = new $.Deferred), r.done(function (e) {
                    o.resolve(e)
                }).fail(function () {
                    o.reject()
                }), u || (n = t.findOrCreate({
                    id: e
                }), n.fetch().done(function () {
                    i[e] = n, r.resolve(n)
                }).fail(function () {
                    r.reject()
                }))
            }
            return o.promise()
        },
        loadPortfolioSetForAccount: function (e) {
            var key = "goal_" + e.get("id") + "_" + e.get("portfolioSetId");
            return this.loadPortfolioSet(key);

        },
        getPortfolioSet: function (e) {
            return i[e];
        },
        deletePortfolioSet: function (key) {
            delete i[key];
            delete s[key];
        },
        getPortfolioSetForAccount: function (e) {
            var key = "goal_" + e.get("id") + "_" + e.get("portfolioSetId");
            return i[key]

        },
        getDefaultInvestingPortfolioSetId: function () {
            return n.getInstance().get("defaultPortfolioSetID")
        },
        getDefaultIraPortfolioSetId: function () {
            return n.getInstance().get("defaultIraPortfolioSetID")
        },
        getDefaultPortfolioSetId: function (e) {
            return r.isIRA(e) ? this.getDefaultIraPortfolioSetId() : this.getDefaultInvestingPortfolioSetId()
        }
    }
}), define("views/advice/multiAllocationCardView", ["underscore", "common/slider", "services/allocationService", "common/betterment.views", "jquery", "tinyToggle"], function (_, slider, allocationService, bt, $, tinyToggle) {
    return bt.View.extend({
        template: "advice/multiAllocationCard",
        events: {
            "click .open-lg": "openCard",
            "click .close-lg": "closeCard"
        },
        toolTips: {
            ".currency-help": {
                position: {
                    my: "bottom center",
                    at: "top center"
                }
            }
        },
        templateHelpers: {
               canHedge: function () {
                   return this.self.canHedge();
               },
                isAutoMode:function(){
                    return this.self.options.parent.optimization_mode == 1;
                }

        },

        onInitialize: function () {
            this.size_slider_model = this.options.model_key + "_size";
            this.currency_hedge_model = this.options.model_key + "_currency_hedge";
        },
        canHedge: function () {
            return this.options.currency != "AUD";
        },
        currentHedge: function(){
            var hedges = this.model.get("hedges");
            if(!hedges){
                return false;
            }
            var region_hedge = hedges[this.options.model_key];
            var currency_hedge_value;

            if (!region_hedge) {
                currency_hedge_value = false;
            }
            else {
                currency_hedge_value = region_hedge;
            }
            return currency_hedge_value;

        },
        isRegionCurrentPicked: function(){
            var picked_regions = this.model.get("picked_regions");
            return picked_regions.indexOf(this.options.model_key)>=0;
        },
        onRender: function () {
            var self = this;
            this.$(".region-name").text(this.options.title);
            this.size_slider = this.createSlider();
            if (this.canHedge()) {
                this.currency_hedge_value = this.currentHedge();

                this.hedge_toggle = this.$(".hedge-toggle").tinyToggle({
                    onReady: function(){
                         if (self.currency_hedge_value) {
                                self.$(this).tinyToggle("check")
                         };
                    },
                    onChange: function (checkbox, value) {
                        if (this.currency_hedge_value == value)return;
                        this.currency_hedge_value = value;
                        this.options.parent.hasChanged();
                    }.bind(this),
                });

            }

            this.is_region_picked = this.isRegionCurrentPicked();

            this.region_toggle = this.$(".pick-toggle").tinyToggle({
                    onReady: function(){
                        if (self.is_region_picked) {
                                self.$(this).tinyToggle("check")
                         };

                    },
                    onChange: function (checkbox, value) {
                        if (this.is_region_picked == value)return;
                        this.is_region_picked = value;
                        this.options.parent.hasChanged();
                    }.bind(this),
                });

        },
        onShow: function () {
            this.drawSize();
            if (this.size_slider_value > 0) {
                this.openCard();
            }
        },
        createSlider: function () {
            var region = this.model.get("regions_allocation")[this.options.model_key];
            if (!region) {
                this.size_slider_value = 0;
            }
            else {
                this.size_slider_value = region["size"] * 100;
            }

            this.drawSize();
            var e = this.slider('.size-slider', {
                min: 0,
                max: 100,
                step: 1,
                value: this.size_slider_value,
                slide: function (e, t) {
                    var allocated = t.value - this.size_slider_value;
                    this.size_slider_value = t.value;
                    this.drawSize();
                    this.options.parent.resize(this.options.model_key, allocated);
                    this.options.parent.fixSize();
                    this.options.parent.hasChanged();
                }.bind(this)
            });
            return e
        },
        hasChanged: function () {
            var changeObject = {has_changed: false, changes: {key: this.options.model_key}};
            var old_size = 0;
            var region = this.model.get("regions_allocation")[this.options.model_key];
            if (region) {
                old_size = 100 * region["size"]
            }
            if (Math.abs(this.size_slider_value - old_size) > 1) {
                changeObject.has_changed = true;
                changeObject.changes.size = this.size_slider_value;
            }
            if (this.canHedge()) {
                var currency_hedge_value = this.currentHedge();

                if (this.currency_hedge_value != currency_hedge_value) {
                    changeObject.has_changed = true;
                    changeObject.changes.currency_hedge_value = this.currency_hedge_value;
                }
            }

            var is_region_picked = this.isRegionCurrentPicked();

            if(this.is_region_picked!=is_region_picked){
                changeObject.has_changed = true;
                changeObject.changes.is_region_picked = this.is_region_picked;
            }
            return changeObject
        },
        drawSize: function () {
            this.$(".size-pct").text(parseInt(this.size_slider_value) + "%");

        },
        reset: function () {
            var size_slider_value;
            var region = this.model.get("regions_allocation")[this.options.model_key];
            if (!region) {
                size_slider_value = 0;
            }
            else {
                size_slider_value = region["size"] * 100;
            }

            this.size_slider_value = size_slider_value;
            this.size_slider.slider("value", this.size_slider_value);
            if(this.canHedge()) {
                this.currency_hedge_value = this.currentHedge();
                if (this.currency_hedge_value) {
                    this.hedge_toggle.tinyToggle("check");
                }
                else {
                    this.hedge_toggle.tinyToggle("uncheck");
                }
            }

            this.is_region_picked = this.isRegionCurrentPicked();
            if (this.is_region_picked) {
                    this.region_toggle.tinyToggle("check");
                }
                else {
                    this.region_toggle.tinyToggle("uncheck");
                }


            this.drawSize();

        },
        save: function () {
            var picked_regions;
            var regions = $.extend({}, this.model.get("regions_allocation"));
            var hedges = $.extend({}, this.model.get("hedges"));


            if(this.is_region_picked){
                picked_regions = $.extend([], this.model.get("picked_regions"));
                if(picked_regions.indexOf(this.options.model_key)<0){
                    picked_regions.push(this.options.model_key);
                    this.model.set("picked_regions", picked_regions);
                }
            }
            else{
                picked_regions = $.extend([], this.model.get("picked_regions"));
                if(picked_regions.indexOf(this.options.model_key)>=0){
                    picked_regions.splice(picked_regions.indexOf(this.options.model_key), 1);
                    this.model.set("picked_regions", picked_regions);
                }
            }

            if(!regions[this.options.model_key]){
                regions[this.options.model_key] = {};
            }
            regions[this.options.model_key]["size"] = this.size_slider_value / 100;
            this.model.set("regions_allocation", regions);

            //save currency hedge
            hedges[this.options.model_key] = this.currency_hedge_value;
            this.model.set("hedges", hedges);


        },
        openCard: function (e) {
            var button = this.$('.open-lg');
            var card = this.$('.allocation-card');
            var content = card.find('.allocation-card-content');
            button.removeClass("open-lg");
            button.addClass("close-lg");
            content.removeClass("allocation-content-hide");
            content.addClass("allocation-content-show");
        },
        closeCard: function (e) {
            var button = this.$(e.currentTarget);
            var card = button.parents('.allocation-card');
            var content = card.find('.allocation-card-content');
            button.removeClass("close-lg");
            button.addClass("open-lg");
            content.removeClass("allocation-content-show");
            content.addClass("allocation-content-hide");
        }


    });

}),

    define("views/advice/multiAllocationView",
        ["underscore", "common/betterment.views", "views/advice/multiAllocationCardView", "components/portfolio/scripts/services/portfolioSetService", "views/advice/multiAllocationModalView"],
        function (_, bt, mac, pss, bsm) {
            return bt.View.extend({
                template: "advice/multiAllocation",
                events: {
                    "click .ma-reset-all": "reset",
                    "click .ma-set-all": "preSave"
                },
                toolTips: {
                    ".optimization-mode-help": {
                        position: {
                            my: "bottom center",
                            at: "top center"
                        }
                    }
                },
                onInitialize: function () {
                    this.optimization_mode = this.model.num("optimization_mode");

                    this.$regions_dict = {
                        AU: "Australia",
                        INT: "Developed Markets",
                        US: "United States",
                        UK: "United Kingdom",
                        EU: "Europe",
                        JAPAN: "Japan",
                        AS: "Asia (ex-Japan)",
                        CN: "China",
                        EM: "Emerging Markets"
                    };

                    _.each(this.model.get("regions_currencies"), function (value, key) {
                        this.addRegion(key + "Region", "#" + key + "-region");

                    }.bind(this));


                },
                onRender: function () {
                    var self = this;


                    this.mode_toggle = this.$(".tiny-toggle").tinyToggle({
                        onReady: function(){
                            var AUTO_MODE = 1;
                            if (self.optimization_mode==AUTO_MODE) {
                                    $(this).tinyToggle("check");
                            };
                        },
                        onChange: function (checkbox, value) {
                            var internal_value;
                            var AUTO_MODE = 1;
                            var WEIGHTS_MODE = 2;
                            if(value)internal_value = AUTO_MODE;
                            else internal_value = WEIGHTS_MODE;
                            if (this.optimization_mode == internal_value)return;
                            this.optimization_mode = internal_value;
                            this.reRender();
                            this.hasChanged();

                        }.bind(this),
                    });


                    var regions_currencies = this.model.get("regions_currencies");
                    _.each(this.$regions_dict, function ($value, key) {
                        if(key in regions_currencies){
                            var value = regions_currencies[key];
                            this.$("div#multiAllocationRegion").append("<div id='" + key + "-region'></div>");
                            this[key + "View"] = new mac({
                                model: this.model,
                                parent: this,
                                model_key: key,
                                title: this.$regions_dict[key],
                                "currency": value,
                            });
                            this[key + "Region"].show(this[key + "View"]);


                        }

                    }.bind(this));


                },
                hasChanged: function () {
                    this.changed = false;
                    var buttons = this.$(".ma-save-buttons");

                    _.each(this.model.get("regions_currencies"), function (value, key) {
                        var changeObject = this[key + "View"].hasChanged();
                        this.changed = this.changed || changeObject.has_changed;
                    }.bind(this));

                    if(this.optimization_mode!=this.model.get("optimization_mode")){
                        this.changed = true;
                    }

                    if (this.changed) {
                        buttons.removeClass("ma-hide");
                        buttons.addClass("ma-show");
                    }
                    else {
                        buttons.removeClass("ma-show");
                        buttons.addClass("ma-hide");
                    }
                    return this.changed;

                },
                onShow: function () {

                },
                reset: function () {
                    this.optimization_mode = this.model.get("optimization_mode");
                    _.each(this.model.get("regions_currencies"), function (value, key) {
                        this[key + "View"].reset();
                    }.bind(this));

                    this.reRender();


                    this.hasChanged();
                },
                getChanges: function () {
                    var changes = [];
                    _.each(this.model.get("regions_currencies"), function (value, key) {
                        var changeObject = this[key + "View"].hasChanged();
                        if (changeObject.has_changed) changes.push(changeObject.changes);
                    }.bind(this));
                    return changes;
                },
                fixSize: function () {
                    var market = [];
                    var total_size = 0;
                    _.each(this.model.get("regions_currencies"), function (value, key) {
                        var size_value = this[key + "View"].size_slider_value;
                        if (size_value == 0) return;
                        total_size += size_value;
                        market.push({key: key, size_value: size_value});
                    }.bind(this));

                    market = _.sortBy(market, function (o) {
                        return o.size_value;
                    });
                    market.reverse();
                    var dif = 100 - total_size;
                    if (dif == 0)return;

                    this[market[0].key + "View"].size_slider_value += dif;
                    this[market[0].key + "View"].size_slider.slider("value", this[market[0].key + "View"].size_slider_value);
                    this[market[0].key + "View"].drawSize();
                },
                resize: function (allocated_key, allocated) {
                    var market = [];
                    var default_key = "AU";
                    var left_allocation = 0;
                    var allocation_from_custom;
                    if (allocated_key == "AU")default_key = "INT";

                    if (allocated < 0) {
                        this[default_key + "View"].size_slider_value = this[default_key + "View"].size_slider_value - allocated;
                        if (this[default_key + "View"].size_slider_value > 1)this[default_key + "View"].size_slider_value = 100;
                        this[default_key + "View"].size_slider.slider("value", this[default_key + "View"].size_slider_value);
                        this[default_key + "View"].drawSize();
                        this[default_key + "View"].openCard();
                        return;
                    }

                    if (this[default_key + "View"].size_slider_value > 0) {
                        var allocation_from_main = this[default_key + "View"].size_slider_value - allocated;
                        if (allocation_from_main >= 0) {
                            left_allocation = 0;
                        }
                        else {
                            left_allocation = -1 * allocation_from_main;
                            allocation_from_main = 0;
                        }

                        this[default_key + "View"].size_slider_value = allocation_from_main;
                        this[default_key + "View"].size_slider.slider("value", this[default_key + "View"].size_slider_value);
                        this[default_key + "View"].drawSize();

                        if (left_allocation == 0)return;

                    }
                    else {
                        left_allocation = allocated;
                    }

                    _.each(this.model.get("regions_currencies"), function (value, key) {
                        if (key == allocated_key)return;
                        if (key == default_key)return;
                        var size_value = this[key + "View"].size_slider_value;
                        if (size_value == 0) return;
                        market.push({key: key, size_value: size_value});
                    }.bind(this));

                    market = _.sortBy(market, function (o) {
                        return o.size_value;
                    });
                    market.reverse();

                    for (var i in market) {
                        allocation_from_custom = this[market[i].key + "View"].size_slider_value - left_allocation;
                        if (allocation_from_custom >= 0) {
                            left_allocation = 0;
                        }
                        else {
                            left_allocation = -1 * allocation_from_custom;
                            allocation_from_custom = 0;
                        }
                        this[market[i].key + "View"].size_slider_value = allocation_from_custom;
                        this[market[i].key + "View"].size_slider.slider("value", this[market[i].key + "View"].size_slider_value);
                        this[market[i].key + "View"].drawSize();

                        if (left_allocation == 0)return;

                    }
                },
                preSave: function () {
                    var custom_size = 0;
                    _.each(this.model.get("regions_currencies"), function (value, key) {
                        custom_size = custom_size + this[key + "View"].size_slider_value;
                    }.bind(this));
                    if (custom_size != 100) {
                        BMT.alert({
                            title: "Error",
                            body: "Your portfolio allocation currently exceeds 100%, please adjust the allocation amounts to set your revised allocation.",
                            icon: "error"
                        });
                        return;
                    }
                    var e = new bsm({multiAllocationController: this, modal: BMT.modal});
                    BMT.modal.show(e);
                },
                save: function () {
                    this.model.set("optimization_mode", this.optimization_mode);
                    _.each(this.model.get("regions_currencies"), function (value, key) {
                        this[key + "View"].save();
                    }.bind(this));
                    this.options.parent.block();
                    this.model.save().fail(function () {
                        this.options.parent.unblock();
                    }.bind(this)).then(function () {
                        this.options.parent.unblock();
                        var portfolio_key = "goal_" + this.model.get("id") + "_" + this.model.get("portfolioSetId");
                        pss.deletePortfolioSet(portfolio_key);
                        pss.loadPortfolioSetForAccount(this.model).then(function () {
                            this.options.parent.reRender()
                        }.bind(this));
                    }.bind(this));
                },
            })
        }), define("views/advice/adviceView", ["jquery", "underscore", "common/betterment.views", "hbs!views/advice/advice", "hbs!views/advice/noTargetFlyover", "hbs!views/advice/targetFlyover", "components/common/scripts/constants/accountStatus", "services/accountService", "viewHelpers/accountViewHelpers", "views/common/tabHeaderView", "components/portfolio/scripts/views/targetPortfolioDonutView", "views/common/questionsView", "views/advice/batchSettingsController", "views/advice/allocationRecommendationView", "views/advice/autoTransactionRecommendationView", "views/advice/depositRecommendationView", "views/advice/termRecommendationView", "views/advice/planRetirementAgeView", "components/advice/scripts/adviceGraphView", "views/advice/marketPerformanceView", "models/notification", "models/v2/retirementPlan", "views/notifications/adviceRetirementIncomeView", "views/notifications/dismissibleFlyoverView", "views/advice/planStartSavingView", "views/advice/planHeaderView", "services/flyoverService", "components/common/scripts/modules/async", "views/advice/multiAllocationView"], function (e, t, n, r, i, s, o, u, a, f, l, c, h, p, d, v, m, g, y, b, w, E, S, x, T, N, C, k, mav) {
    return n.View.extend({
        template: r,
        id: "advice",
        regions: {
            planRegion: ".plan-region",
            headerRegion: ".header-region",
            allocationRegion: ".allocation-region",
            autoTransactionRegion: ".auto-transaction-region",
            oneTimeDepositRegion: ".one-time-deposit-region",
            termRegion: ".term-region",
            donutRegion: ".donut-region",
            multiAllocationRegion: ".multi-allocation-region",
            marketPerformanceRegion: ".market-performance-region",
            graphRegion: ".graph-region"
        },
        events: {
            "click .collapse-circle": "toggleRecommendations",
            "click .set-all": "saveSettings",
            "click .reset-all": "resetSettings"
        },
        onInitialize: function () {
            this.model = BMT.selectedAccount, this.listenTo(BMT.vent, "addGoal:saved", function () {
                this.reRender()
            })
        },
        onRender: function () {
            this.$settingsRow = this.$(".settings-row"), C.closeFlyover()
        },
        reRender: function () {
            this.block(), C.closeFlyover(), this.model = BMT.selectedAccount, this.loadAccountAndRender().then(this.unblock.bind(this))
        },
        onShow: function () {
            BMT.analytics.track("PageVisited", {
                Location: "Advice"
            }), this.preloadStart(), this.loadAccountAndRender().then(this.preloadComplete.bind(this))

        },
        onDestroy: function () {
            C.closeFlyover()
        },
        loadAccountAndRender: function () {
            var n = this,
                r = a.preloadSelectedAccount().then(function (t) {
                    var r = e.Deferred();
                    return n.model.isInPlan() ? E.create({
                        financialProfile: BMT.user.getFinancialProfile(),
                        financialPlan: n.model.get("financialPlan")
                    }).then(function (e) {
                        r.resolve(t, e)
                    }) : r.resolve(t), r.promise()
                });
            return r.then(function (e, n) {
                this.model = e, this.retirementPlan = n, this.renderSubViews(), this.toggleSaveButtons(), this.model.getCurrentBalanceWithPending() === 0 && t.defer(this.showFlyover.bind(this))
            }.bind(this))
        },
        renderSubViews: function () {
            this.renderPlanHeader(), this.renderHeader(), this.addAdviceBoxes(), this.renderDonut(), this.renderMultiAllocationRegion(), this.renderMarketPerformance(), this.renderGraph()
        },
        renderPlanHeader: function () {
            this.model.isInPlan() ? (this.planRegion.show(new N({
                retirementPlan: this.retirementPlan
            })), this.$el.addClass("in-plan")) : (this.planRegion.empty(), this.$el.removeClass("in-plan"))
        },
        renderHeader: function () {
            this.headerView = new f({
                model: this.model
            }), this.listenTo(this.headerView, "changeAccount", this.reRender), this.listenTo(this.headerView, "targetChanged", this.onValueChange), this.listenTo(this.headerView, "deleteAccount", this.reRender), this.listenTo(this.headerView, "goalStatusClicked", this.goalStatusClicked), this.listenTo(this.headerView, "autoTransactionChanged", this.reRender), this.headerRegion.show(this.headerView)
        },
        renderDonut: function () {
            this.donutView = new l({
                model: this.model
            }), this.donutRegion.show(this.donutView)
        },
        renderMultiAllocationRegion: function () {
            this.multiAllocationview = new mav({
                model: this.model,
                parent: this
            }), this.multiAllocationRegion.show(this.multiAllocationview)
        },
        renderMarketPerformance: function () {
            this.marketPerformanceView = new b, this.marketPerformanceRegion.show(this.marketPerformanceView)
        },
        renderGraph: function () {
            this.graphView = new y({
                model: this.model,
                age: BMT.user.getAge(),
                termYears: this.model.remainingGoalTerm(),
                totalCurrentBalance: BMT.accounts().totalCurrentBalance(),
                defaultFeeRate: BMT.accountGroup.defaultFeeRate()
            }), this.listenTo(this.graphView, "projectionChanged", function (e) {
                this.marketPerformanceView.update(e)
            }), this.graphRegion.show(this.graphView)
        },
        onValueChange: function (e) {
            t.extend(this.changes, e);
            this.notifyBoxes(this.changes);
        },
        showFlyover: function () {
            var e = this.retirementPlan,
                t = this.model,
                n;
            t.isIncome() ? n = new w({}, {
                view: S
            }) : this.model.isInPlan() && e.getRecommendedSavingsContributionForAccount(t) > 0 ? n = new w({}, {
                view: T,
                retirementPlan: e,
                account: t
            }) : !this.model.isInPlan() && !t.num("goalAmount") ? n = new w({}, {
                view: x,
                template: i
            }) : n = new w({}, {
                view: x,
                template: s
            }), C.showFlyover(n, {
                beforeShow: function (e) {
                    this.listenTo(e, "show", function () {
                        var t = this.oneTimeDepositRegion.$el,
                            n = t.offset(),
                            r = e.$el.parent().offset();
                        e.$el.css({
                            left: n.left - r.left - 40,
                            top: n.top - r.top + t.outerHeight() - 90
                        })
                    })
                }.bind(this)
            })
        },
        addAdviceBoxes: function () {
            this.adviceBoxes = [], this.changes = {}, this.addAdviceBox(this.allocationRegion, new p({
                modelKey: "allocationChangeTransaction",
                model: this.model,
                termYears: this.model.remainingGoalTerm()
            }), "allocationView"), this.addAdviceBox(this.autoTransactionRegion, new d({
                model: this.model
            }), "autoTransactionView"), this.addAdviceBox(this.oneTimeDepositRegion, new v({
                modelKey: "depositTransaction",
                model: this.model
            }), "oneTimeDepositView"), this.model.isInPlan() ? this.addAdviceBox(this.termRegion, new g({
                modelKey: "term",
                retirementAge: this.financialPlan().num("retirementAge")
            })) : this.addAdviceBox(this.termRegion, new m({
                modelKey: "term",
                model: this.model
            })), this.$settingsRow.addClass("no-animate"), this.autoToggleRecommendations()
        },
        addAdviceBox: function (e, t, n) {
            e.show(t), this.adviceBoxes.push(t), this.listenTo(t, "valueChanged", this.onValueChange), this.listenTo(t, "valueChanged valueReset", this.toggleSaveButtons), n && (this[n] = t)
        },
        notifyBoxes: function (e) {
            t.each(this.adviceBoxes, function (t) {
                t.refreshAdvice(e)
            }), this.$settingsRow.removeClass("no-animate"), this.autoToggleRecommendations(), this.donutView.update(e.allocation), this.graphView.update(e)
        },
        autoToggleRecommendations: function () {
            if (this.userHidRecommendationsLast) return;
            var e = t.chain(this.adviceBoxes).filter(function (e) {
                return e !== this.allocationView
            }, this).all(function (e) {
                return !e.hasRecommendation()
            }).value();
            e ? (this.hideRecommendations(), this.$(".collapse-circle").addClass("hidden")) : (this.showRecommendations(), this.$(".collapse-circle").removeClass("hidden"))
        },
        toggleRecommendations: function () {
            this.$settingsRow.removeClass("no-animate"), this.$settingsRow.hasClass("short") ? (this.userHidRecommendationsLast = !1, this.showRecommendations()) : (this.userHidRecommendationsLast = !0, this.hideRecommendations())
        },
        showRecommendations: function () {
            this.$settingsRow.removeClass("short"), this.$settingsRow.find(".collapse-label").text("Hide Recommendations")
        },
        hideRecommendations: function () {
            this.$settingsRow.addClass("short"), this.$settingsRow.find(".collapse-label").text("Show Recommendations")
        },
        goalStatusClicked: function (e) {
            e === o.OFF_TRACK && (this.showRecommendations(), this.showFlyover())
        },
        saveSettings: function () {
            if (!this.isAnythingDirty()) return;
            if (this.autoTransactionView.validate()) return;
            var e = {
                account: this.model,
                onSuccess: function () {
                    this.reRender()
                }.bind(this)
            };
            t.extend(e, this.getModelsForSave()), h.go(e);
        },
        resetSettings: function () {
            if (!this.isAnythingDirty()) return;
            t.each(this.adviceBoxes, function (e) {
                e.reset()
            })
        },
        toggleSaveButtons: function () {
            this.$(".save-buttons").toggle(this.isAnythingDirty());
            var e = "Set",
                t = "Reset";
            this.numberOfDirtySettings() > 1 && (e = "Set All", t = "Reset All"), this.$(".save-buttons .set-all").text(e), this.$(".save-buttons .reset-all").text(t)
        },
        getModelsForSave: function () {
            return t.reduce(this.adviceBoxes, function (e, n) {
                return t.extend(e, n.getModelForSave())
            }, {})
        },
        isAnythingDirty: function () {
            return t.any(this.adviceBoxes, function (e) {
                return e.isDirty()
            })
        },
        numberOfDirtySettings: function () {
            return t.filter(this.adviceBoxes, function (e) {
                return e.isDirty()
            }).length

        },
        financialPlan: function () {
            return BMT.user.get("financialPlans").selected()
        }
    })
}),define("views/profile/contactInfoView", ["jquery", "underscore", "backbone", "hbs!views/profile/contactInfo", "common/betterment.views", "views/profile/securityQuestionView", "models/user", "models/visitor", "views/profile/contactPreferencesView", "views/profile/changePasswordView", "views/common/flashView", "views/profile/changeDefaultAccountGroupView", "views/profile/externalAccountsView", "models/v1/defaultAccountGroupUpdater", "models/v1/quovoCredentials", "views/profile/retireGuidePreferencesView"], function(e, t, n, r, i, s, o, u, a, f, l, c, h, p, d, v) {
        var m = new d;
        return i.View.extend({
            template: r,
            tagName: "div",
            regions: {
                retireGuidePreferencesRegion: ".retire-guide-preferences"
            },
            templateHelpers: {
                statesDropdown: function() {
                    return this.build_dropdown_menu(o.states, {
                        "class": "state-selector",
                        name: "state",
                        value: this.self.model.get("state")
                    })
                },
                contactPreferencesStatus: function() {
                    return this.self.options.contactPreferences.hasDefaultPreferences() ? "Default" : "Custom"
                },
                defaultAccountGroupLabel: function() {
                    return BMT.user.getDefaultAccountGroup().get("name")
                },
                hasHnwConsultationFeature: function() {
                    return u.hasVariation("hnw_consultation_on")
                }
            },
            ui: {
                inputs: "input[name]:not([readonly])",
                updateButton: "button.update",
                phoneNumber: "[name=phoneNumber]"
            },
            events: {
                "keyup @ui.inputs": "inputChanged",
                "change .state-selector": "inputChanged",
                "click button#emailPreferences": "contactPreferences",
                "click button#changePassword": "changePassword",
                "click button.change-default-account": "changeDefaultAccount",
                "click button.link-external-accounts": "linkExternalAccounts",
                "click button.update": "update",
                "keydown input[name=zip]": function(e) {
                    return this.restrictLength(e, 5) && this.restrictNumeric(e)
                }
            },
            onInitialize: function() {
                this.defaultAccountGroupUpdater = new p({
                    user: BMT.user
                }), this.listenTo(this.defaultAccountGroupUpdater, "change", function() {
                    this.defaultAccountGroupUpdater.updateUser(), this.render()
                }), this.listenTo(this.options.contactPreferences, "change", function() {
                    this.render()
                })
            },
            getExternalAccountsCredentials: function() {
                var t = e.Deferred();
                return m.has("quovoKey") ? t.resolve(m) : m.fetch().done(function() {
                    t.resolve(m)
                }), t.promise()
            },
            onShow: function() {
                this.ui.phoneNumber.mask("999-999-9999"), this.ui.updateButton.prop("disabled", !0), this.applyValidation(), this.retireGuidePreferencesRegion.show(new v)
            },
            onDestroy: function() {
                this.defaultAccountGroupUpdater.trigger("destroy", this.defaultAccountGroupUpdater)
            },
            contactPreferences: function(e) {
                BMT.modal.show(new a({
                    model: this.options.contactPreferences
                }))
            },
            changePassword: function(e) {
                BMT.modal.show(new f({
                    model: BMT.user
                }))
            },
            changeDefaultAccount: function(e) {
                BMT.modal.show(new c({
                    model: this.defaultAccountGroupUpdater
                }))
            },
            linkExternalAccounts: function() {
                this.getExternalAccountsCredentials().done(function(e) {
                    BMT.modal.show(new h({
                        model: e
                    }))
                })
            },
            inputChanged: function(t) {
                var n = this,
                    r = !1,
                    i, s, o, u;
                for (o = 0; o < this.ui.inputs.length; o++) u = e(this.ui.inputs[o]), i = u.attr("name"), s = u.val(), r = r || n.model.get(i) !== s;
                this.ui.updateButton.prop("disabled", !r)
            },
            update: function(e) {
                var r = this,
                    i, o = n.Syphon.serialize(this);
                this.model.validate(o) || BMT.modal.show(i = new s(t.extend({
                    title: "Confirm Contact Info Update",
                    body: "To update your info please answer the following security question",
                    className: "confirm-update-modal securityQuestion",
                    handler: function(e) {
                        e && (i.block(), r.model.store(), r.model.save(t.extend(o, e), {
                            success: function() {
                                BMT.modal.close(i), BMT.flash("Your info was updated successfully."), s.removeResults(r.model)
                            },
                            error: function() {
                                r.model.restart()
                            },
                            complete: function() {
                                i.unblock()
                            }
                        }))
                    }
                }, this.model.randomSecurityQuestion())))
            }
        })
    }),  define("hbs!views/profile/accountAdministration", ["hbs", "hbs/handlebars", "components/common/scripts/templateHelpers/link"], function(e, t) {
        var n = t.template(function(e, t, n, r, i) {
            this.compilerInfo = [4, ">= 1.0.0"], n = this.merge(n, e.helpers);
            var s = "",
                o, u, a, f = "function",
                l = this.escapeExpression,
                c = n.helperMissing;
            return s += '<ul>\n    <li>\n        <label>Bank Account</label>\n\n        <span class="item-content">', (u = n.bankAccountDescription) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.bankAccountDescription, o = typeof u === f ? u.call(t, {
                hash: {}
            }) : u), s += l(o) + '</span>\n\n        <button class="change-bank-account">Change</button>\n        <div class="clearfix"></div>\n    </li>\n\n    <li>\n        <label>Pricing Plan</label>\n        <span class="advised-user-only item-content">\n            ', (u = n.advisedFeeTypeDisplayAmount) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.advisedFeeTypeDisplayAmount, o = typeof u === f ? u.call(t, {
                hash: {}
            }) : u), s += l(o) + '\n            <div id="advisedFeeHelp" class="help-icon">\n                This is the combined fee for Betasmartz and your Investment Advisor. For more details, please see your respective customer agreements. Your Betasmartz customer agreements can be found <a href="https://www.betterment.com/advisedcustomeragreement">here</a>.\n            </div>\n        </span>\n        <span class="unadvised-user-only">\n            <span class="item-content">', (u = n.feeTypeDisplayName) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.feeTypeDisplayName, o = typeof u === f ? u.call(t, {
                hash: {}
            }) : u), s += l(o) + '</span>\n            <button data-track-event="ElementClicked" data-track-location="Profile" data-track-name="ChangePricing" class="review-pricing-plan">Review</button>\n        </span>\n\n        <div class="clearfix"></div>\n    </li>\n\n    <li>\n        <label>Account Status</label>\n        <span class="item-content">', (u = n.accountStatus) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.accountStatus, o = typeof u === f ? u.call(t, {
                hash: {}
            }) : u), s += l(o) + '</span>\n        <button data-track-event="ElementClicked" data-track-location="Profile" data-track-name="CloseAccount" href="#" class="close-account blue">Change</button>\n\n        <section class="info-tip clearfix hide close-info">\n            <div class="arrow"></div>\n            <div class="text trust-ag-only">\n                To close your trust account, amend the trust, or add or remove a trustee, please call our support team at ', (u = n.supportPhoneNumber) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.supportPhoneNumber, o = typeof u === f ? u.call(t, {
                hash: {}
            }) : u), s += l(o) + '.\n            </div>\n            <div class="text joint-ag-only">\n                To close your joint account, please call our support team at ', (u = n.supportPhoneNumber) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.supportPhoneNumber, o = typeof u === f ? u.call(t, {
                hash: {}
            }) : u), s += l(o) + '.\n            </div>\n        </section>\n\n        <div class="clearfix"></div>\n    </li>\n</ul>\n', s
        });
        return t.registerPartial("views/profile/accountAdministration", n), n
    }),define("hbs!views/profile/retireGuidePreferences", ["hbs", "hbs/handlebars"], function(e, t) {
        var n = t.template(function(e, t, n, r, i) {
            this.compilerInfo = [4, ">= 1.0.0"], n = this.merge(n, e.helpers);
            var s = "",
                o, u, a = "function",
                f = this.escapeExpression;
            return s += '<label>RetireGuide</label>\n<span class="item-content retire-guide-status"> ', (u = n.retireGuideState) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.retireGuideState, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '\n    <span class="retire-guide-help help-icon">\n            RetireGuide is a retirement planning tool available on the Advice tab.\n            RetireGuide requires entering details about your financial profile in order\n            to provide retirement advice.  Once you set up RetireGuide, you have the option to clear\n            your profile. Clearing your profile cannot be undone. If RetireGuide is cleared or has\n            not been set up, you can also hide RetireGuide from your account.\n    </span>\n</span>\n<button data-track-event="ElementClicked" data-track-location="Profile" data-track-name="ChangeRetireGuidePrefs" class="blue clear-retire-guide ', (u = n.clearButtonDisplay) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.clearButtonDisplay, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '">Clear</button>\n<button data-track-event="ElementClicked" data-track-location="Profile" data-track-name="ChangeRetireGuidePrefs" class="blue hide-retire-guide ', (u = n.hideButtonDisplay) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.hideButtonDisplay, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '">Hide</button>\n<button data-track-event="ElementClicked" data-track-location="Profile" data-track-name="ChangeRetireGuidePrefs" class="blue show-retire-guide ', (u = n.showButtonDisplay) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.showButtonDisplay, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '">Show</button>\n<div class="clearfix"></div>\n', s
        });
        return t.registerPartial("views/profile/retireGuidePreferences", n), n
    }), define("views/profile/retireGuidePreferencesView", ["jquery", "underscore", "backbone", "hbs!views/profile/retireGuidePreferences", "common/betterment.views"], function(e, t, n, r, i) {
        return i.View.extend({
            template: r,
            templateHelpers: {
                retireGuideState: function() {
                    return this.self.currentState()
                },
                clearButtonDisplay: function() {
                    return this.self.currentState() === "Active" ? "show" : "hidden"
                },
                showButtonDisplay: function() {
                    return this.self.currentState() === "Hidden" ? "show" : "hidden"
                },
                hideButtonDisplay: function() {
                    return this.self.currentState() === "Not Active" ? "show" : "hidden"
                }
            },
            tagName: "span",
            toolTips: {
                ".retire-guide-help": {
                    position: {
                        my: "bottom center",
                        at: "top center"
                    }
                }
            },
            events: {
                "click button.clear-retire-guide": "clearRetireGuide",
                "click button.show-retire-guide": "showRetireGuide",
                "click button.hide-retire-guide": "hideRetireGuide"
            },
            onInitialize: function() {
                this.listenTo(BMT.user, "change:retireGuideEnabled", function() {
                    BMT.user.is("retireGuideEnabled") ? BMT.flash("RetireGuide has been hidden from your account. Click Show RetireGuide to bring it back at any time.") : BMT.flash('RetireGuide is now available in your account. <a href="#retireGuideSetup"><u>Set up RetireGuide</u></a>.'), this.render()
                })
            },
            currentState: function() {
                var e = !BMT.user.get("financialPlans").selected().isNew(),
                    t = BMT.user.is("retireGuideEnabled");
                if (e && t) return "Active";
                if (!e && t) return "Not Active";
                if (!t) return "Hidden"
            },
            clearRetireGuide: function() {
                var e = this;
                BMT.alert({
                    body: "You are about to clear the personal data you entered when setting up RetireGuide. This cannot be undone.",
                    title: "Clear RetireGuide Profile",
                    buttons: [{
                        id: "clear-retire-guide-button",
                        title: "Clear"
                    }],
                    handler: function() {
                        BMT.user.get("financialPlans").selected().destroy({
                            success: function() {
                                BMT.flash("RetireGuide profile has been cleared.  <a href=#retireGuideSetup><u>Start your profile over</u></a>, or visit the Advice tab later to set up RetireGuide again."), e.render()
                            }
                        })
                    }
                })
            },
            hideRetireGuide: function() {
                BMT.user.disableRetireGuide()
            },
            showRetireGuide: function() {
                BMT.user.enableRetireGuide()
            }
        })
    }), define("hbs!views/profile/contactInfo", ["hbs", "hbs/handlebars"], function(e, t) {
        var n = t.template(function(e, t, n, r, i) {
            function c(e, t) {
                return '\n        <li>\n            <label>External Accounts</label>\n            <span class="item-content"></span>\n            <button class="blue link-external-accounts">Link</button>\n            <div class="clearfix"></div>\n        </li>\n    '
            }
            this.compilerInfo = [4, ">= 1.0.0"], n = this.merge(n, e.helpers);
            var s = "",
                o, u, a = "function",
                f = this.escapeExpression,
                l = this;
            s += '<form method="POST" action="#">\n    <section>\n        <label>Name</label>\n        <input type="text" name="firstName" value="', (u = n.firstName) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.firstName, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '" readonly />\n        <input type="text" name="middleName" class="middleName" value="', (u = n.middleName) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.middleName, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '" maxlength="1" readonly />\n        <input type="text" name="lastName" class="lastName" value="', (u = n.lastName) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.lastName, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '" readonly />\n    </section>\n\n    <section>\n        <label>Address 1</label>\n        <input type="text" class="long" name="address1" value="', (u = n.address1) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.address1, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '" />\n    </section>\n\n    <section>\n        <label>Address 2</label>\n        <input type="text" class="long" name="address2" value="', (u = n.address2) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.address2, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '" />\n    </section>\n\n    <section>\n        <label>City/State</label>\n        <input type="text" name="city" value="', (u = n.city) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.city, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '" />\n        ', (u = n.statesDropdown) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.statesDropdown, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '\n        <input type="text" class="zip" name="zip" value="', (u = n.zip) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.zip, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '" maxlength="5" />\n    </section>\n\n    <section>\n        <label>Phone</label>\n        <input type="tel" class="long" name="phoneNumber" value="', (u = n.phoneNumber) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.phoneNumber, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '" />\n    </section>\n\n    <section>\n        <label>Email</label>\n        <input type="email" class="long" name="userName" value="', (u = n.userName) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.userName, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '" />\n    </section>\n</form>\n\n<button class="update" disabled="disabled">Update info</button>\n\n<hr />\n\n<ul class="stacked-items">\n\n    <li>\n        <label>Password</label>\n        <span class="item-content">**********</span>\n        <button id="changePassword" class="blue">Change</button>\n        <div class="clearfix"></div>\n    </li>\n\n    <li>\n        <label>Email Preferences</label>\n        <span class="item-content">', (u = n.contactPreferencesStatus) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.contactPreferencesStatus, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '</span>\n        <button data-track-event="ElementClicked" data-track-location="Profile" data-track-name="ChangeEmailPrefs" id="emailPreferences" class="blue">Change</button>\n        <div class="clearfix"></div>\n    </li>\n\n    <li class="multi-ag-only">\n        <label>Default Account</label>\n        <span class="item-content">', (u = n.defaultAccountGroupLabel) ? o = u.call(t, {
                hash: {}
            }) : (u = t && t.defaultAccountGroupLabel, o = typeof u === a ? u.call(t, {
                hash: {}
            }) : u), s += f(o) + '</span>\n        <button data-track-event="ElementClicked" data-track-location="Profile" data-track-name="ChangeDefaultAccountPrefs" class="blue change-default-account">Change</button>\n        <div class="clearfix"></div>\n    </li>\n\n    ', o = n["if"].call(t, t && t.hasHnwConsultationFeature, {
                hash: {},
                inverse: l.noop,
                fn: l.program(1, c, i)
            });
            if (o || o === 0) s += o;
            return s += '\n    <li class="retire-guide-preferences"></li>\n</ul>\n', s
        });
        return t.registerPartial("views/profile/contactInfo", n), n
    });