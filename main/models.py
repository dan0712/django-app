from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, _, validators, UserManager, timezone,\
    send_mail
from django.core.validators import RegexValidator
from .fields import ColorField
from django_localflavor_au.models import AUPhoneNumberField, AUStateField, AUPostCodeField
from main.slug import unique_slugify
from django.conf import settings
import uuid
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist


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
    name = models.CharField(max_length=255)
    dealer_group_number = models.CharField(max_length=50, null=True, blank=True)
    slug = models.CharField(max_length=100, editable=False, unique=True)
    logo_url = models.ImageField(verbose_name="White logo", null=True, blank=True)
    knocked_out_logo_url = models.ImageField(verbose_name="Colored logo", null=True, blank=True)
    client_agreement_url = models.FileField(verbose_name="Client Agreement (PDF)", null=True, blank=True)
    form_adv_part2_url = models.FileField(verbose_name="Form Adv", null=True, blank=True)
    token = models.CharField(max_length=36, editable=False)
    fee = models.FloatField(default=0)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        if self.pk is None:
            self.token = str(uuid.uuid4())

        # reset slug with name changes
        if self.pk is not None:
            orig = Firm.objects.get(pk=self.pk)
            if orig.name != self.name:
                self.slug = None

        if not self.slug:
            unique_slugify(self, self.name, slug_field_name="slug")
        else:
            unique_slugify(self, self.slug, slug_field_name="slug")

        super(Firm, self).save(force_insert, force_update, using, update_fields)

    def white_logo(self):
        if self.logo_url is None:
            return settings.STATIC_URL + 'images/white_logo.png'

        return settings.MEDIA_URL + self.logo_url.name

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self).pk

    @property
    def legal_representative_form_url(self):
        if self.token is None:
            return None
        return settings.SITE_URL + "/" + self.token + "/legal_signup"

    def __str__(self):
        return self.name


class FirmData(models.Model):
    afsl_asic = models.CharField(default="", max_length=50)
    afsl_asic_document = models.FileField()
    office_address_line_1 = models.CharField(max_length=255)
    office_address_line_2 = models.CharField(max_length=255)
    office_state = AUStateField()
    office_city = models.CharField(max_length=255)
    office_post_code = AUPostCodeField()
    postal_address_line_1 = models.CharField(max_length=255)
    postal_address_line_2 = models.CharField(max_length=255)
    postal_state = AUStateField()
    postal_city = models.CharField(max_length=255)
    postal_post_code = AUPostCodeField()
    daytime_phone_number = AUPhoneNumberField()
    mobile_phone_number = AUPhoneNumberField()
    fax_number = AUPhoneNumberField()
    alternate_email_address = models.EmailField(null=True, blank=True)
    last_change = models.DateField(auto_now=True)
    fee_bank_account_name = models.CharField(max_length=100)
    fee_bank_account_branch_name = models.CharField(max_length=100)
    fee_bank_account_bsb_number = models.CharField(max_length=20)
    fee_bank_account_number = models.CharField(max_length=20)
    fee_bank_account_holder_name = models.CharField(max_length=100)
    australian_business_number = models.CharField(max_length=20)
    investor_transfer = models.BooleanField(default=False, choices=YES_NO)
    previous_adviser_name = models.CharField(max_length=100, null=True, blank=True)
    previous_margin_lending_adviser_number = models.CharField(max_length=100, null=True, blank=True)
    previous_bt_adviser_number = models.CharField(max_length=100, null=True, blank=True)


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
        return self.user.first_name + " - " + self.firm.name

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
        return self.firm.knocked_out_logo_url

    @property
    def invite_url(self):
        return settings.SITE_URL + "/" + self.firm.slug + "/client/signup/" + self.token

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


INVITATION_PENDING = 0
INVITATION_SUBMITTED = 1
INVITATION_ACTIVE = 3
INVITATION_CLOSED = 4

EMAIL_INVITATION_STATUSES = ((INVITATION_PENDING, 'Pending'),
                             (INVITATION_SUBMITTED, 'Submitted'),
                             (INVITATION_ACTIVE, 'Active'),
                             (INVITATION_CLOSED, 'Closed'))


INVITATION_ADVISOR = 0
INVITATION_LEGAL_REPRESENTATIVE = 1
INVITATION_SUPERVISOR = 2
INVITATION_CLIENT = 3
INVITATION_TYPE_CHOICES = ((INVITATION_ADVISOR, "Advisor"),
                           (INVITATION_LEGAL_REPRESENTATIVE, 'Legal representative'),
                           (INVITATION_CLIENT, 'Client'),
                           (INVITATION_SUPERVISOR, 'Supervisor'))

INVITATION_TYPE_DICT = {str(INVITATION_ADVISOR): "advisor",
                        str(INVITATION_LEGAL_REPRESENTATIVE): "legal_representative",
                        str(INVITATION_CLIENT): "client",
                        str(INVITATION_SUPERVISOR): "supervisor"}


class EmailInvitation(models.Model):

    email = models.EmailField()
    inviter_type = models.ForeignKey(ContentType)
    inviter_id = models.PositiveIntegerField()
    inviter_object = generic.GenericForeignKey('inviter_type', 'inviter_id')
    send_date = models.DateTimeField(auto_now=True)
    send_count = models.PositiveIntegerField(default=0)
    status = models.PositiveIntegerField(choices=EMAIL_INVITATION_STATUSES, default=INVITATION_PENDING)
    invitation_type = models.PositiveIntegerField(choices=INVITATION_TYPE_CHOICES, default=INVITATION_CLIENT)

    @property
    def get_status(self):
        for i in EMAIL_INVITATION_STATUSES:
            if self.status == i[0]:
                return i[1]

    def send(self):
        # TODO: SEND EMAIl

        if self.status != INVITATION_PENDING:
            return

        try:
            user = User.objects.get(email=self.email)
        except ObjectDoesNotExist:
            user = None

        if user is not None:
            if not user.is_active:
                self.status = INVITATION_CLOSED
                self.save()
                return

            for it in INVITATION_TYPE_CHOICES:
                if self.invitation_type == it[0]:
                    model = INVITATION_TYPE_DICT[it[0]]
                    if hasattr(user, model):
                        if getattr(user, model).is_confirmed:
                            self.status = INVITATION_ACTIVE
                            self.save()
                            return
                        else:
                            self.status = INVITATION_SUBMITTED
                            self.save()
                            return

        self.send_count += 1
        self.save()