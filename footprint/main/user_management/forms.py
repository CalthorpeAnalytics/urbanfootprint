# coding=utf-8

# UrbanFootprint v1.5
# Copyright (C) 2016 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.



from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, is_password_usable
from django.forms.formsets import BaseFormSet

from footprint.main.models.keys.user_group_key import UserGroupKey


USER_ROLES = [
    (UserGroupKey.SUPERADMIN, ''),
    (UserGroupKey.ADMIN, ''),
    (UserGroupKey.MANAGER, ''),
    (UserGroupKey.USER, '')
]


class UserGroupsForm(forms.Form):

    config_entity = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):

        if 'config_entity_choices' in kwargs:
            config_entity_choices = kwargs.pop('config_entity_choices')
        else:
            config_entity_choices = []

        super(UserGroupsForm, self).__init__(*args, **kwargs)

        self.fields['config_entity'] = forms.ChoiceField(
            choices=config_entity_choices,
            widget=forms.Select(attrs={'class': 'form-control config-entity-select'})
        )


class UserGroupsFormSet(BaseFormSet):

    def clean(self):

        if any(self.errors):
            return

        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            group_id = form.cleaned_data['config_entity']
            if group_id.isdigit():
                return

        raise forms.ValidationError("You must assign at least one project.")


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        initial_role = None
        role_choices = []

        if 'initial_role' in kwargs:
            initial_role = kwargs.pop('initial_role')
        if 'role_choices' in kwargs:
            role_choices = kwargs.pop('role_choices')

        super(UserForm, self).__init__(*args, **kwargs)

        self.fields['role'] = forms.ChoiceField(choices=role_choices, widget=forms.Select(attrs={'class': 'form-control'}))

        if initial_role:
            self.fields['role'].initial = initial_role

    role = forms.ChoiceField()
    raw_password = forms.CharField(required=False, widget=forms.PasswordInput())
    confirm_password = forms.CharField(required=False, widget=forms.PasswordInput())
    raw_new_password = forms.CharField(required=False, widget=forms.PasswordInput())
    confirm_new_password = forms.CharField(required=False, widget=forms.PasswordInput())
    email = forms.CharField(max_length=75, widget=forms.TextInput(attrs={'size': '40', 'class': 'form-control'}))

    class Meta:
        model = get_user_model()

        fields = (
            'role',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'raw_password',
            'confirm_password',
            'raw_new_password',
            'confirm_new_password'
        )

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self, *args, **kwargs):
        data = super(UserForm, self).clean(*args, **kwargs)

        if 'user_id' not in self.data:  # we're trying to create a new user

            if not data.get('raw_password'):
                self._errors['raw_password'] = self.error_class(['This field is required'])

            if not data.get('confirm_password'):
                self._errors['confirm_password'] = self.error_class(['This field is required'])

            if data.get('raw_password') != data.get('confirm_password'):
                self._errors['confirm_password'] = self.error_class(['The passwords do not match'])

            data['password'] = data.get('raw_password')
            if not is_password_usable(make_password(data['password'])):
                self._errors['raw_password'] = self.error_class(['Please enter a different password'])

            user_model = get_user_model()
            if data.get('email'):
                try:
                    user_model.objects.get(email__iexact=data['email'])
                    user_model.objects.get(username__iexact=data['email'][:30])
                    self._errors['email'] = self.error_class(['This email address is already in use'])
                except user_model.DoesNotExist:
                    pass

        else:
            if data.get('raw_new_password'):
                if data['raw_new_password'] != data.get('confirm_new_password'):
                    self._errors['confirm_new_password'] = self.error_class(['The passwords do not match'])

                data['new_password'] = data.get('raw_new_password')
                if not is_password_usable(make_password(data['new_password'])):
                    self._errors['raw_new_password'] = self.error_class(['Please enter a different password'])

        return data
