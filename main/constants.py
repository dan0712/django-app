SUCCESS_MESSAGE = "Your application has been submitted successfully, " \
                  "you will receive a confirmation email" \
                  " following a BetaSmartz approval."
INVITATION_PENDING = 0
INVITATION_SUBMITTED = 1
INVITATION_ACTIVE = 3
INVITATION_CLOSED = 4
EMAIL_INVITATION_STATUSES = (
    (INVITATION_PENDING, 'Pending'), (INVITATION_SUBMITTED, 'Submitted'),
    (INVITATION_ACTIVE, 'Active'), (INVITATION_CLOSED, 'Closed'))
EMPLOYMENT_STATUS_FULL_TIME = 0
EMPLOYMENT_STATUS_PART_TIME = 1
EMPLOYMENT_STATUS_SELF_EMPLOYED = 2
EMPLOYMENT_STATUS_STUDENT = 3
EMPLOYMENT_STATUS_RETIRED = 4
EMPLOYMENT_STATUS_HOMEMAKER = 5
EMPLOYMENT_STATUS_UNEMPLOYED = 6
EMPLOYMENT_STATUSES = (
    (EMPLOYMENT_STATUS_FULL_TIME, 'Employed (full-time)'),
    (EMPLOYMENT_STATUS_PART_TIME, 'Employed (part-time)'),
    (EMPLOYMENT_STATUS_SELF_EMPLOYED, 'Self-employed'),
    (EMPLOYMENT_STATUS_STUDENT, 'Student'),
    (EMPLOYMENT_STATUS_RETIRED, 'Retired'),
    (EMPLOYMENT_STATUS_HOMEMAKER, 'Homemaker'),
    (EMPLOYMENT_STATUS_UNEMPLOYED, "Not employed"),
)
INVITATION_ADVISOR = 0
AUTHORIZED_REPRESENTATIVE = 1
INVITATION_SUPERVISOR = 2
INVITATION_CLIENT = 3
INVITATION_TYPE_CHOICES = (
    (INVITATION_ADVISOR, "Advisor"),
    (AUTHORIZED_REPRESENTATIVE, 'Authorised representative'),
    (INVITATION_SUPERVISOR, 'Supervisor'),
    (INVITATION_CLIENT, 'Client'),
)
INVITATION_TYPE_DICT = {
    str(INVITATION_ADVISOR): "advisor",
    str(AUTHORIZED_REPRESENTATIVE): "authorised_representative",
    str(INVITATION_CLIENT): "client",
    str(INVITATION_SUPERVISOR): "supervisor"
}
TFN_YES = 0
TFN_NON_RESIDENT = 1
TFN_CLAIM = 2
TFN_DONT_WANT = 3
TFN_CHOICES = (
    (TFN_YES, "Yes"),
    (TFN_NON_RESIDENT, "I am a non-resident of Australia"),
    (TFN_CLAIM, "I want to claim an exemption"),
    (TFN_DONT_WANT, "I do not want to quote a Tax File Number or exemption"),)
PERSONAL_DATA_FIELDS = ('date_of_birth', 'gender',
                        'phone_num', 'medicare_number')
ASSET_FEE_EVENTS = ((0, 'Day End'),
                    (1, 'Complete Day'),
                    (2, 'Month End'),
                    (3, 'Complete Month'),
                    (4, 'Fiscal Month End'),
                    (5, 'Entry Order'),
                    (6, 'Entry Order Item'),
                    (7, 'Exit Order'),
                    (8, 'Exit Order Item'),
                    (9, 'Transaction'))
ASSET_FEE_UNITS = ((0, 'Asset Value'),  # total value of the asset
                   (1, 'Asset Qty'),  # how many units of an asset
                   (2, 'NAV Performance'))  # % positive change in the NAV
ASSET_FEE_LEVEL_TYPES = (
    (0, 'Add'),  # Once the next level is reached, the amount form that band is added to lower bands
    (1, 'Replace')  # Once the next level is reached, the value from that level is used for the entire amount
)
SUPER_ASSET_CLASSES = (
    # EQUITY
    ("EQUITY_AU", "EQUITY_AU"),
    ("EQUITY_US", "EQUITY_US"),
    ("EQUITY_EU", "EQUITY_EU"),
    ("EQUITY_EM", "EQUITY_EM"),
    ("EQUITY_INT", "EQUITY_INT"),
    ("EQUITY_UK", "EQUITY_UK"),
    ("EQUITY_JAPAN", "EQUITY_JAPAN"),
    ("EQUITY_AS", "EQUITY_AS"),
    ("EQUITY_CN", "EQUITY_CN"),
    # FIXED_INCOME
    ("FIXED_INCOME_AU", "FIXED_INCOME_AU"),
    ("FIXED_INCOME_US", "FIXED_INCOME_US"),
    ("FIXED_INCOME_EU", "FIXED_INCOME_EU"),
    ("FIXED_INCOME_EM", "FIXED_INCOME_EM"),
    ("FIXED_INCOME_INT", "FIXED_INCOME_INT"),
    ("FIXED_INCOME_UK", "FIXED_INCOME_UK"),
    ("FIXED_INCOME_JAPAN", "FIXED_INCOME_JAPAN"),
    ("FIXED_INCOME_AS", "FIXED_INCOME_AS"),
    ("FIXED_INCOME_CN", "FIXED_INCOME_CN"))
YES_NO = ((False, "No"), (True, "Yes"))
ACCOUNT_TYPE_PERSONAL = 0
ACCOUNT_TYPE_JOINT = 1
ACCOUNT_TYPE_TRUST = 2
ACCOUNT_TYPE_SMSF = 3
ACCOUNT_TYPE_CORPORATE = 4
ACCOUNT_TYPES = (
    (ACCOUNT_TYPE_PERSONAL, "Personal Account"),
    (ACCOUNT_TYPE_JOINT, "Joint Account"),
    (ACCOUNT_TYPE_TRUST, "Trust Account"),
    (ACCOUNT_TYPE_SMSF, "Self Managed Superannuation Fund"),
    (ACCOUNT_TYPE_CORPORATE, "Corporate Account"),
)
YAHOO_API = "YAHOO"
GOOGLE_API = "GOOGLE"
API_CHOICES = ((YAHOO_API, "YAHOO"), (GOOGLE_API, 'GOOGLE'))
_asset_fee_ht = "List of level transition points and the new values after that transition. Eg. '0: 0.001, 10000: 0.0'"
PERFORMER_GROUP_STRATEGY = "PERFORMER_GROUP_STRATEGY"
PERFORMER_GROUP_BENCHMARK = "PERFORMER_GROUP_BENCHMARK"
PERFORMER_GROUP_BOND = "PERFORMER_GROUP_BOND"
PERFORMER_GROUP_STOCK = "PERFORMER_GROUP_STOCK"
PERFORMER_GROUP_CHOICE = (
    (PERFORMER_GROUP_STRATEGY, "PERFORMER_GROUP_STRATEGY"),
    (PERFORMER_GROUP_BENCHMARK, "PERFORMER_GROUP_BENCHMARK"),
    (PERFORMER_GROUP_BOND, "PERFORMER_GROUP_BOND"),
    (PERFORMER_GROUP_STOCK, "PERFORMER_GROUP_STOCK")
)
