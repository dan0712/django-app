from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, _, validators, UserManager, timezone,\
    send_mail
from django.core.validators import RegexValidator
from .fields import ColorField
from django_localflavor_au.models import AUPhoneNumberField
from main.slug import unique_slugify
from django.conf import settings


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
    firm_logo_url = models.ImageField(null=False, blank=False)
    firm_knocked_out_logo_url = models.ImageField(null=False, blank=False)
    firm_client_agreement_url = models.FileField(null=True, blank=True)
    firm_form_adv_part2_url = models.FileField(null=True, blank=True)
    firm_client_agreement_token = models.CharField(max_length=36, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if not self.firm_slug:
            unique_slugify(self, self.firm_name, slug_field_name="firm_slug")
        else:
            unique_slugify(self, self.firm_slug, slug_field_name="firm_slug")

        super(Firm, self).save(force_insert, force_update, using, update_fields)

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
    date_of_birth = models.DateField()


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
