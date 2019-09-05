# off
This libraries pack is meant to be used along with the applications taht are build for the off (Open Free Federation). This federation is intended as a social network and an application repository available to people that willingly subscribe to the Federation.

## Settings.py ##
* **``BASE_PAGE``** the path to the base page template 
* **``SITE_NAME``** the name of the website
* **``VERSION``** the current version of the application
* **``DEFAULT_EMAIL_DOMAIN_NAME``** the default domain name of the user if none provided (usernames are emails, except for admin)
* **``USER_PROFILE_PATTERN_NAME``** the django styled url to the user profile page (such as ``off.identity:identity``)
* **``NEW_USER_PATTERN_NAME``** the django styled url to the user creation page (such as ``off.identity:create``)

## Documentation basics ##
Always use the **``ContextBuilder``** to serve the django page context, as it adds various element in it:
* ``global.base_page`` the settings.BASE_PAGE
* ``global.now`` the current time according to the setup timezone
* ``global.version`` the settings.VERSION
* ``global.site_name`` the settings.SITE_NAME
* ``global.context_build_duration`` the time it took to build the context (most of the time, it correspond to the time it took to gather all the data needed to show the page).
* ``pagination.querystring`` the querystring of the current page. This is mainly used by the pagination system, thus the value is stored under the ``pagination`` object.

## off.infrastructure ##
This is the main library for common operations such as 
* Better page context
    * ``ContextBuilder``
* Page redirection
    * ``RedirectNextMixin``
    * ``RedirectNextFormMixin``
* Views filters
    * ``FilteredViewMixin``
    * ``FilterForm``
* Activities
    * ``ActivityView``
    * ``ActivityStep``
    * ``ActivityParameter``
    * ``ActivityNavigationMixin``
* Navigation
    * ``GenericNavigationMixin``
    * ``Navigation``
    * ``NavItem``
* User services
    * ``user_services.Services``

## off.identity ##
This module presents what we are calling an identity. Every user of the platform has one if authenticated. The identity contains a key field which contains a unique ID (NFC tag for exemple) that allows identification of users (not authentification) in an anonymised manner and with a physical support (NFC card, phone, etc...)

## off.account ##
This module contains the "credit" logic for the system. Each Identity is connected to an Account that can be receiver or emmiter of Transaction objects.
