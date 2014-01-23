# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from copy import copy
from django import forms
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from thecut.emailform import settings


class BaseEmailForm(forms.Form):
    """Base email form.

    Extends a standard Django :py:class:`~django.forms.Form` class with methods
    to send valid form data as an email.

    """

    from_email = settings.DEFAULT_FROM_EMAIL
    to_emails = settings.DEFAULT_TO_EMAILS
    cc_emails = []
    email_context_data = {}
    email_headers = {}
    email_subject = 'Enquiry'
    email_subject_prefix = settings.EMAIL_SUBJECT_PREFIX
    email_template_name = 'emailform/email.txt'
    error_css_class = 'error'
    label_suffix = ''
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(BaseEmailForm, self).__init__(*args, **kwargs)

        # HTML5 input types and attributes
        for field in self.fields.values():
            if isinstance(field, forms.EmailField):
                field.widget.input_type = 'email'
            if field.required:
                field.widget.attrs.update({'required': 'required'})

    def get_email_context_data(self, **kwargs):
        """Returns a data dictionary for use when rendering the email context.

        :returns: A dictionary.
        :rtype: :py:class:`dict`

        """

        context_data = copy(self.email_context_data)
        context_data.update(form=self, **kwargs)
        return context_data

    def get_email_headers(self):
        """Returns a dictionary of values for use as extra email headers.

        :returns: A dictionary of extra email headers.
        :rtype: :py:class:`dict`

        """

        return copy(self.email_headers)

    def get_email_kwargs(self, **kwargs):
        return kwargs

    def get_email_subject(self, subject=None):
        """Returns a string for use as an email's ``subject`` value.

        :keyword unicode subject: A string to join to the subject prefix.
        :returns: An email subject.
        :rtype: :py:class:`unicode`

        """

        if subject is None:
            subject = self.email_subject

        return '{prefix}{subject}'.format(prefix=self.email_subject_prefix,
                                          subject=subject)

    def get_email_template_name(self):
        """Returns a template name which will be used when rendering the email.

        :returns: A template name.
        :rtype: :py:class:`unicode`

        """

        return self.email_template_name

    def get_from_email(self):
        """Returns an email address for use as an email's ``from`` value.

        :returns: An email address.
        :rtype: :py:class:`unicode`

        """

        return self.from_email

    def get_to_emails(self):
        """Returns a list of email addresses for use as an email's ``to``
        value.

        :returns: List of email address strings.
        :rtype: :py:class:`list`

        """

        return copy(self.to_emails)

    def get_cc_emails(self):
        """Returns a list of email addresses for use as an email's ``cc``
        value.

        :returns: List of email address strings.
        :rtype: :py:class:`list`

        """

        return copy(self.cc_emails)

    def render_email_body(self, context):
        """Renders and returns content for use as an email's body text.

        :argument dict context: Context data dictionary to be used when
            rendering the template.
        :returns: Rendered body copy.
        :rtype: :py:class:`unicode`

        """

        template = get_template(self.get_email_template_name())
        return template.render(context)

    def send_email(self):
        """Construct and send an email for a valid form."""

        assert self.is_valid()

        context = Context(self.get_email_context_data())
        email_kwargs = self.get_email_kwargs(
            subject=self.get_email_subject(),
            body=self.render_email_body(context),
            from_email=self.get_from_email(),
            to=self.get_to_emails(),
            cc=self.get_cc_emails(),
            headers=self.get_email_headers()
        )
        mail = EmailMultiAlternatives(**email_kwargs)
        return mail.send()
