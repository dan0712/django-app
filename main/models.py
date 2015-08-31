from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, _, validators, UserManager, timezone,\
    send_mail
from django.core.validators import RegexValidator
from .fields import ColorField
from django_localflavor_au.models import AUPhoneNumberField, AUStateField, AUPostCodeField
from main.slug import unique_slugify
from django.conf import settings
import uuid
import datetime


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """

    first_name = models.CharField(_('first name'), max_length=30)
    middle_name = models.CharField(_('middle name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30)
    username = models.CharField(max_length=30, editable=False, default='')
    email = models.EmailField(_('email address'), unique=True,
                              error_messages={
                                  'unique': _("A user with that email already exists."),
                                  })

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        " Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Firm(models.Model):
    firm_name = models.CharField(max_length=255)
    firm_slug = models.CharField(max_length=255, editable=False, unique=True)
    firm_logo_url = models.ImageField(verbose_name="White logo", null=False, blank=False)
    firm_knocked_out_logo_url = models.ImageField(verbose_name="Colored logo", null=False, blank=False)
    firm_client_agreement_url = models.FileField(verbose_name="Client Agreement (PDF)", null=True, blank=True)
    firm_form_adv_part2_url = models.FileField(verbose_name="Form Adv", null=True, blank=True)
    firm_client_agreement_token = models.CharField(max_length=36, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if self.pk is None:
            self.firm_client_agreement_token = str(uuid.uuid4())

        if not self.firm_slug:
            unique_slugify(self, self.firm_name, slug_field_name="firm_slug")
        else:
            unique_slugify(self, self.firm_slug, slug_field_name="firm_slug")

        super(Firm, self).save(force_insert, force_update, using, update_fields)

    def white_logo(self):
        if self.firm_logo_url is None:
            return settings.STATIC_URL + 'images/white_logo.png'

        return settings.MEDIA_URL + self.firm_logo_url.name

    def __str__(self):
        return self.firm_name


class Advisor(models.Model):
    user = models.OneToOneField(User, related_name="advisor")
    work_phone = AUPhoneNumberField()
    confirmation_key = models.CharField(max_length=36, null=True, blank=True, editable=False)
    token = models.CharField(max_length=36, null=True, editable=False)
    is_accepted = models.BooleanField(default=False, editable=False)
    is_confirmed = models.BooleanField(default=False, editable=False)
    firm = models.ForeignKey(Firm)
    date_of_birth = models.DateField()
    is_supervisor = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name + " - " + self.firm.firm_name

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def phone(self):
        return self.work_phone[0:4] + "-" + self.work_phone[4:7] + "-" + self.work_phone[7:10]
    
    @property
    def email(self):
        return self.user.email


    @property
    def firm_colored_logo(self):
        return self.firm.firm_knocked_out_logo_url

    @property
    def invite_url(self):
        return settings.SITE_URL + "/" + self.firm.firm_slug + "/client/signup/" + self.token

    def save(self, *args, **kw):
        send_confirmation_mail = False
        if self.pk is not None:
            orig = Advisor.objects.get(pk=self.pk)
            if (orig.is_accepted != self.is_accepted) and (self.is_accepted is True):
                send_confirmation_mail = True

        super(Advisor, self).save(*args, **kw)
        if send_confirmation_mail and (self.confirmation_key is not None):
            self.user.email_user("BetaSmartz advisor account confirmation",
                                 "You advisor account have been approved, "
                                 "please confirm your email here: "
                                 "{site_url}/advisor/confirm_email/{confirmation_key}/"
                                 " \n\n\n  The BetaSmartz Team"
                                 .format(confirmation_key=self.confirmation_key,
                                         site_url=settings.SITE_URL))


TFN_YES = 0
TFN_NON_RESIDENT = 1
TFN_CLAIM = 2
TFN_DONT_WANT = 3

TFN_CHOICES = ((TFN_YES, "Yes"),
               (TFN_NON_RESIDENT, "I am a non-resident of Australia"),
               (TFN_CLAIM, "I want to claim an exemption"),
               (TFN_DONT_WANT, "I do not want to quote a Tax File Number or exemption"),)

Q1 = "What was the name of your elementary school?"
Q2 = "What was the name of your favorite childhood friend?"
Q3 = "What was the name of your childhood pet?"
Q4 = "What street did you live on in third grade?"
Q5 = "What is your oldest sibling's birth month?"
Q6 = "In what city did your mother and father meet?"

QUESTION_1_CHOICES = ((Q1, Q1),
                      (Q2, Q2),
                      (Q3, Q3))

QUESTION_2_CHOICES = ((Q4, Q4),
                      (Q5, Q5),
                      (Q6, Q6))


YES_NO = ((False, "No"), (True, "Yes"))


class Client(models.Model):
    is_confirmed = models.BooleanField()
    confirmation_key = models.CharField(max_length=36)
    advisor = models.ForeignKey(Advisor)
    user = models.OneToOneField(User)
    accepted = models.BooleanField(default=False, editable=False)
    date_of_birth = models.DateField(verbose_name="Date of birth")
    gender = models.CharField(max_length=20, default="Male",  choices=(("Male", "Male"), ("Female", "Female")))
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = AUStateField()
    post_code = AUPostCodeField()
    phone_number = AUPhoneNumberField()
    medicare_number = models.CharField(max_length=50)
    tax_file_number = models.CharField(max_length=50)
    provide_tfn = models.IntegerField(verbose_name="Provide TFN?", choices=TFN_CHOICES, default=TFN_YES)
    security_question_1 = models.CharField(max_length=255, choices=QUESTION_1_CHOICES)
    security_question_2 = models.CharField(max_length=255, choices=QUESTION_2_CHOICES)
    security_answer_1 = models.CharField(max_length=255, verbose_name="Answer")
    security_answer_2 = models.CharField(max_length=255, verbose_name="Answer")
    associated_to_broker_dealer = models.BooleanField(verbose_name="You are employed by or associated with "
                                                                   "a broker dealer.",
                                                      default=False,
                                                      choices=YES_NO)
    ten_percent_insider = models.BooleanField(verbose_name="You are a 10% shareholder, director, or"
                                                           " policy maker of a publicly traded company.",
                                              default=False,
                                              choices=YES_NO)


INVESTMENT_TYPES = (("BONDS", "BONDS"), ("STOCKS", "STOCKS"))


SUPER_ASSET_CLASSES = (
    # EQUITY
    ("EQUITY_AU", "EQUITY_AU"), ("EQUITY_US", "EQUITY_US"), ("EQUITY_EU", "EQUITY_EU"), ("EQUITY_EM", "EQUITY_EM"),
    ("EQUITY_INT", "EQUITY_INT"),
    # FIXED_INCOME
    ("FIXED_INCOME_AU", "FIXED_INCOME_AU"), ("FIXED_INCOME_US", "FIXED_INCOME_US"),
    ("FIXED_INCOME_EU", "FIXED_INCOME_EU"), ("FIXED_INCOME_EM", "FIXED_INCOME_EM"),
    ("FIXED_INCOME_INT", "FIXED_INCOME_INT")

)


class AssetClass(models.Model):
    name = models.CharField(max_length=255, validators=[RegexValidator(regex=r'^[0-9a-zA-Z_]+$',
                                                        message="Invalid character only accept (0-9a-zA-Z_) ")])
    display_order = models.PositiveIntegerField()
    primary_color = ColorField()
    foreground_color = ColorField()
    drift_color = ColorField()
    asset_class_explanation = models.TextField(blank=True, default="", null=False)
    tickers_explanation = models.TextField(blank=True, default="", null=False)
    display_name = models.CharField(max_length=255, blank=False, null=False)
    investment_type = models.CharField(max_length=255, choices=INVESTMENT_TYPES,  blank=False, null=False)
    super_asset_class = models.CharField(max_length=255, choices=SUPER_ASSET_CLASSES)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        self.name = self.name.upper()

        super(AssetClass, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Ticker(models.Model):
    symbol = models.CharField(max_length=10, blank=False, null=False, validators=[RegexValidator(regex=r'^[^ ]+$',
                                                                                  message="Invalid symbol format")])
    display_name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, default="", null=False)
    ordering = models.IntegerField(blank=True, default="", null=False)
    url = models.URLField()
    unit_price = models.FloatField(default=1, editable=False)
    asset_class = models.ForeignKey(AssetClass, related_name="tickers")

    def __str__(self):
        return self.symbol

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        self.symbol = self.symbol.upper()

        super(Ticker, self).save(force_insert, force_update, using, update_fields)


class ClientInvite(models.Model):
    client_email = models.EmailField(unique=True)
    advisor = models.ForeignKey(Advisor, related_name="client_invites")
    sent_date = models.DateTimeField(auto_now=True)
    is_user = models.BooleanField(default=False)

    def send(self):
        # TODO : when create an user check if is in the invite table and put is_user as True
        # TODO: SEND EMAIl

        if self.is_user:
            return

        if User.objects.filter(email=self.client_email):
            self.is_user = True
            self.save()
            return

        self.sent_date = datetime.datetime.now()
        self.save()