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



import json
from collections import OrderedDict
from datetime import datetime
from functools import partial, wraps

from django.contrib.auth.models import Group
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.contrib.auth import authenticate, get_user_model, login as django_login, logout as django_logout
from django.template.defaulttags import register
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.forms.formsets import formset_factory

from footprint.main.publishing.user_initialization import update_or_create_user
from footprint.main.user_management.forms import UserForm, UserGroupsForm, UserGroupsFormSet
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.config.project import Project
from footprint.main.models.config.region import Region
from footprint.main.models.keys.keys import Keys


__author__ = 'calthorpe_analytics'

USER_MODEL = get_user_model()

USER_EDIT_PERMISSIONS_MAP = {
    UserGroupKey.SUPERADMIN: [UserGroupKey.SUPERADMIN, UserGroupKey.ADMIN, UserGroupKey.MANAGER, UserGroupKey.USER],
    UserGroupKey.ADMIN: [UserGroupKey.MANAGER, UserGroupKey.USER],
    UserGroupKey.MANAGER: [UserGroupKey.USER],
    UserGroupKey.USER: []
}

ROLE_CHOICES_MAP = {
    UserGroupKey.SUPERADMIN: [UserGroupKey.SUPERADMIN, UserGroupKey.ADMIN, UserGroupKey.MANAGER, UserGroupKey.USER],
    UserGroupKey.ADMIN: [UserGroupKey.ADMIN, UserGroupKey.MANAGER, UserGroupKey.USER],
    UserGroupKey.MANAGER: [UserGroupKey.MANAGER, UserGroupKey.USER],
    UserGroupKey.USER: [UserGroupKey.USER]
}

ROLE_SUBCLASSES_MAP = {
    UserGroupKey.SUPERADMIN: [GlobalConfig, Region, Project],
    UserGroupKey.ADMIN: [Region, Project],
    UserGroupKey.MANAGER: [Project],
    UserGroupKey.USER: [Project]
}

# A map of role keys to integers to preserve drop down option ordering
ROLE_ID_MAP = {
    UserGroupKey.SUPERADMIN: 0,
    UserGroupKey.ADMIN: 1,
    UserGroupKey.MANAGER: 2,
    UserGroupKey.USER: 3
}


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def sort_items(dictionary):
    return sorted(dictionary.items())


@register.filter
def user_display_string(user):
    if user.first_name and user.last_name:
        return "{} {}".format(user.first_name, user.last_name)
    elif user.email:
        return user.email
    return user.username


def get_role_key_for_user(user):
    """Get the role key corresponding to a user's groups. The role key represents the
    user's group's perission levels normalized by config entity. Because a user may only
    have one role, we can just get the role key from the first group."""

    return get_role_key_for_group(user.groups.all()[0])


def get_role_key_for_group(group):
    """
    Returns the role key corresponding to a Group object's name. Group names
    are a concatenation of the corresponding ConfigEntity key and a user role, e.g.:
    'scag__or_cnty__lgnhls__manager'. For groups belonging to the global config, the group
    name is simply the role key, e.g.: 'admin'. The role key represents a group's
    perission levels normalized by config entity.
    """

    return group.name.split('__')[-1]


def user_has_permission_for_config_entity(user, config_entity):
    """
    Returns True if any of a user's groups are associated with the
    config entity or any of its descendants.
    """

    # Previously we had checked if `config_entity` was a descendant of the
    # config entities of `user`. Some profiling determined that the call to
    # `descendants()` was the primary cause of poor page load performance

    # An example branch of the hierarchy tree looks like:
    # SCAG DM (Region) -> SCAG (Region) -> Aliso Viejo (Project) -> Aliso Viejo (Scenario)

    # This hierarchy is also represented via `schema()` method on the ConfigEntity
    # class, e.g. the schema of Aliso Viejo the scenario is scag_dm__scag__lsvj__lsvj_s
    # so we can use string comparison as a test for ancestry

    for user_config_entity in get_config_entities_for_user(user):

        # User has permission to view their own config entity
        if user_config_entity.id == config_entity.id:
            return True

        # Users belonging to the global config have permission to view users of any config entity
        if isinstance(user_config_entity, GlobalConfig):
            return True

        if config_entity.schema().startswith(user_config_entity.schema()):
            return True


def get_allowed_groups(user, config_entity):
    """
    Returns a list of groups associates with the config entity
    that the user has permission to access according to ROLE_CHOICES_MAP.
    """

    user_role_key = get_role_key_for_user(user)

    allowed_groups = []

    if user_has_permission_for_config_entity(user, config_entity):
        if config_entity.key == Keys.GLOBAL_CONFIG_KEY:
            for allowed_role in ROLE_CHOICES_MAP[user_role_key]:
                allowed_groups.append(Group.objects.get(name=allowed_role))
        else:
            for gh in config_entity.group_hierarchies.all():
                if gh.group:
                    group_role_key = get_role_key_for_group(gh.group)
                    if group_role_key in ROLE_CHOICES_MAP[user_role_key]:
                        allowed_groups.append(gh.group)

    return allowed_groups


def get_config_entity_and_role_choices_for_user(user):
    """
    Collect the config entities and groups a user is permittted
    to access as defined by ROLE_SUBCLASSES_MAP and ROLE_CHOICES_MAP.
    """

    role_choices = set()
    config_entity_choices = {}

    user_role_key = get_role_key_for_user(user)

    for subclass in ROLE_SUBCLASSES_MAP[user_role_key]:
        for config in subclass.objects.all().order_by('name'):

            for group in get_allowed_groups(user, config):

                group_role_key = get_role_key_for_group(group)
                group_role_id = ROLE_ID_MAP[group_role_key]
                role_choices.add((group_role_id, group_role_key.capitalize()))

                if group_role_id not in config_entity_choices:
                    config_entity_choices[group_role_id] = [('--------', '--------')]

                config_entity_choices[group_role_id].append((group.id, config.name))

    return sorted(role_choices), config_entity_choices


def get_config_entities_for_user(user):
    """Returns the ConfigEntity objects corresponding to the group a user belongs to."""

    global_config_group_names = [UserGroupKey.SUPERADMIN, UserGroupKey.ADMIN, UserGroupKey.MANAGER, UserGroupKey.USER]

    user_config_entities = []

    for group in user.groups.all():
        if group.group_hierarchy:

            if group.group_hierarchy.config_entity:
                user_config_entities.append(group.group_hierarchy.config_entity)

            elif group.id in Group.objects.filter(name__in=global_config_group_names).values_list('id', flat=True):
                user_config_entities.append(GlobalConfig.objects.get())

    return user_config_entities


def get_group_formset_class(config_entity_choices):
    """
    Generate the formset class that supports a user belonging
    to multiple groups.
    """

    all_config_choices = []
    for choice_list in config_entity_choices.values():
        for choice in choice_list:
            # using a list (and not a set) b/c ordering is important
            # to keep the default placeholder option at the top
            if choice not in all_config_choices:
                all_config_choices.append(choice)

    # A workaround for assinging formset forms with custom kwargs in pre-1.9 Django versions. From
    # http://stackoverflow.com/questions/622982/django-passing-custom-form-parameters-to-formset
    formset_class = formset_factory(
        wraps(UserGroupsForm)(
            partial(
                UserGroupsForm,
                config_entity_choices=all_config_choices
            )
        ),
        formset=UserGroupsFormSet
    )

    return formset_class


def get_group_names_from_formset(group_formset):
    """Extract the group names """

    group_names = []
    for formset_form in group_formset:
        if formset_form.cleaned_data.get('config_entity').isdigit():
            group = Group.objects.get(id=formset_form.cleaned_data['config_entity'])
            group_names.append(group.name)

    return group_names


@login_required(login_url='/footprint/login')
def users(request):
    users = OrderedDict()
    config_keys = {}

    user_role = get_role_key_for_user(request.user)
    for subclass in ROLE_SUBCLASSES_MAP[user_role]:
        for config in subclass.objects.all().order_by('name'):

            if not user_has_permission_for_config_entity(request.user, config):
                continue

            if config.key == Keys.GLOBAL_CONFIG_KEY:
                for group in Group.objects.filter(name__in=USER_EDIT_PERMISSIONS_MAP[user_role]):
                    if group.user_set.count():

                        if config.name not in users:
                            users[config.name] = []
                            config_keys[config.name] = config.key

                        for user in group.user_set.all():
                            users[config.name].append({
                                'user': user,
                                'role': get_role_key_for_user(user).capitalize()
                            })

            else:
                for group_hierarchy in config.group_hierarchies.all():
                    if group_hierarchy.group:
                        _role_key = get_role_key_for_group(group_hierarchy.group)

                        if _role_key not in USER_EDIT_PERMISSIONS_MAP[user_role]:
                            continue

                        if group_hierarchy.group.user_set.count():
                            if config.name not in users:
                                users[config.name] = []
                                config_keys[config.name] = config.key

                            for user in group_hierarchy.group.user_set.all():
                                users[config.name].append({
                                    'user': user,
                                    'role': _role_key.capitalize()
                                })

    return render(
        request,
        'footprint/users.html',
        {
            'users': users,
            'config_keys': config_keys,
            'admin_user': request.user,
            'requesting_user_role': user_role
        }
    )


@login_required(login_url='/footprint/login')
def user(request, user_id):
    user = get_object_or_404(USER_MODEL, id=user_id)

    if request.user.id != user.id:
        if get_role_key_for_user(user) not in USER_EDIT_PERMISSIONS_MAP[get_role_key_for_user(request.user)]:
            return HttpResponse('Unauthorized', status=401)

    role_choices, config_entity_choices = get_config_entity_and_role_choices_for_user(request.user)

    form = UserForm(
        request.POST or None,
        instance=user,
        role_choices=role_choices,
        initial_role=ROLE_ID_MAP[get_role_key_for_user(user)]
    )

    group_formset_class = get_group_formset_class(config_entity_choices)

    initial_group_values = [{'config_entity': g.id} for g in user.groups.all()]

    group_formset = group_formset_class(request.POST or None, initial=initial_group_values)

    if form.is_valid() and group_formset.is_valid():

        update_or_create_user(
            username=user.username,
            password=form.cleaned_data.get('password') or form.cleaned_data.get('new_password'),
            email=form.cleaned_data.get('email'),
            first_name=form.cleaned_data.get('first_name'),
            last_name=form.cleaned_data.get('last_name'),
            api_key=None,
            groups=get_group_names_from_formset(group_formset)
        )

        messages.add_message(request, messages.SUCCESS, 'User successfully updated.')

        return HttpResponseRedirect('/footprint/users/')

    if form.errors:
        for error in form.errors:
            messages.add_message(request, messages.ERROR, error)

    if group_formset.non_form_errors():
        for error in group_formset.non_form_errors():
            messages.add_message(request, messages.ERROR, error)

    return render(
        request,
        'footprint/user.html',
        {
            'form': form,
            'group_formset': group_formset,
            'user_id': user.id,
            'requesting_user_role': get_role_key_for_user(request.user),
            'config_entity_choices': json.dumps(config_entity_choices),
            'admin_user': request.user
        }
    )


@login_required(login_url='/footprint/login')
def add_user(request):
    if get_role_key_for_user(request.user) not in [UserGroupKey.SUPERADMIN, UserGroupKey.ADMIN, UserGroupKey.MANAGER]:
        return HttpResponse('Unauthorized', status=401)

    role_choices, config_entity_choices = get_config_entity_and_role_choices_for_user(request.user)

    form = UserForm(
        request.POST or None,
        initial={'is_active': True},
        role_choices=role_choices
    )

    group_formset_class = get_group_formset_class(config_entity_choices)

    group_formset = group_formset_class(request.POST or None)

    if form.is_valid() and group_formset.is_valid():

        update_or_create_user(
            # TODO:
            #  Unfortunately, it appears that changing the length of the username in Django get complicated
            #  quickly so we're leaving this to 30 characters for now.
            #  See http://stackoverflow.com/questions/2610088/can-djangos-auth-user-username-be-varchar75-how-could-that-be-done
            username=form.cleaned_data.get('email')[:30],
            password=form.cleaned_data.get('password'),
            email=form.cleaned_data.get('email'),
            first_name=form.cleaned_data.get('first_name'),
            last_name=form.cleaned_data.get('last_name'),
            api_key=None,
            groups=get_group_names_from_formset(group_formset)
        )

        messages.add_message(request, messages.SUCCESS, 'User successfully added.')
        return HttpResponseRedirect('/footprint/users/')

    if form.errors:
        for error in form.errors:
            messages.add_message(request, messages.ERROR, error)

    if group_formset.non_form_errors():
        for error in group_formset.non_form_errors():
            messages.add_message(request, messages.ERROR, error)

    return render(
        request,
        'footprint/user.html',
        {
            'form': form,
            'group_formset': group_formset,
            'requesting_user_role': get_role_key_for_user(request.user),
            'config_entity_choices': json.dumps(config_entity_choices),
            'admin_user': request.user
        }
    )


def logout(request):
    django_logout(request)
    response = HttpResponseRedirect('/footprint/login')
    response.set_cookie(key=settings.SPROUTCORE_COOKIE_KEY, expires=datetime.utcnow())
    messages.add_message(request, messages.SUCCESS, "Successfully logged out.")

    return response


@csrf_exempt  # This is safe because if the user wasn't already logged in, the CSRF isn't protecting anything
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        output = request.REQUEST.get('output')

        if not email or not password:
            if output == 'json':
                return HttpResponseBadRequest()
            messages.add_message(request, messages.WARNING, "Please enter an email and password.")
            return render(request, 'footprint/login.html', {'exclude_navbar': True})

        try:
            user = USER_MODEL.objects.get(email__iexact=email)
        except USER_MODEL.DoesNotExist:
            if output == 'json':
                return HttpResponseNotFound()
            messages.add_message(request, messages.WARNING, "The email does not match any users.")
            return render(request, 'footprint/login.html', {'exclude_navbar': True})
        except USER_MODEL.MultipleObjectsReturned:
            if output == 'json':
                return HttpResponseNotFound()
            messages.add_message(request, messages.WARNING, "There are mulitple users with this email account.")
            return render(request, 'footprint/login.html', {'exclude_navbar': True})

        authenticated_user = authenticate(username=user.username, password=password)
        if authenticated_user is not None:
            if authenticated_user.is_active:
                django_login(request, authenticated_user)
                # output=json means to treat this like an API rather than a redirect
                if output == 'json':
                    return _render_login_info(user)
                return HttpResponseRedirect('/footprint/users')
            else:
                if output == 'json':
                    return HttpResponseForbidden()
                messages.add_message(request, messages.WARNING, "This user account is disabled.")
        else:
            if output == 'json':
                return HttpResponseForbidden()
            messages.add_message(request, messages.WARNING, "The email or password is incorrect.")

    else:
        users = USER_MODEL.objects.filter(id=request.user.id)
        user = users and users[0]
        if user and user.is_authenticated:
            return HttpResponseRedirect('/footprint/users')

    return render(request, 'footprint/login.html', {'exclude_navbar': True})


def _render_login_info(user):
    """Returns json information that matches what sproutcore expects.

    When the user logs in, the response needs to look like a tastypie response, because
    sproutcore is treating it like the results of a record retrieval."""

    fake_tastypie_user = {
        "meta": {
            "limit": 1000,
            "next": None,
            "offset": 0,
            "previous": None,
            "total_count": 1
        },
        "objects": [{
            "api_key": user.api_key.key,
            "email": user.email,
            "first_name": user.first_name,
            "id": user.id,
            "is_active": user.is_active,
            "last_name": user.last_name,
            "username": user.username,
            "groups": [group.id for group in user.groups.all()],
        }]
    }

    return HttpResponse(json.dumps(fake_tastypie_user), content_type="application/json")
