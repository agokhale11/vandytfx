"""
main/urls.py routes each url that a user could visit to the appropriate view function in main/views.py
-   All parts of the regular expressions that are in parenthesis are parameters that are passed to the view function
-   Most of the ([a-zA-Z0-9_-]{3,16}) are usernames of members or urls of spaces in order to determine which page to
    render or who is visiting the page.
-   Author: Joshua Stafford (joshua.o.stafford@vanderbilt.edu) Contact with any questions
"""

from django.conf.urls import url
from django.contrib.auth import views as auth_views
from main.forms import LoginForm
from main import views

urlpatterns = [
    url(r'^$', views.home_view, name='home'),
    # url(r'^signup/$', views.signup_view, name ='signup'),
    url(r'^signup/(.*)/$', views.email_signup_view, name='signup_email'),
    url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html', 'authentication_form': LoginForm}),
    url(r'^logout/$', auth_views.logout, {'template_name': 'registration/logout.html'}),
    url(r'^forgot_password/$', views.forgot_password_view, name='forgot_password'),
    url(r'^change_password/([a-zA-Z0-9_-]{3,16})/$', views.change_password_view, name='change_password'),
    url(r'^profile_redirect/$', views.profile_redirect_view, name='profile_redirect'),
    url(r'^profile/([a-zA-Z0-9_-]{3,16})/$', views.profile_view, name='profile'),
    url(r'([a-zA-Z0-9_-]{3,16})/space/$', views.create_space_view, name='create_space'),
    url(r'^space/([a-zA-Z0-9_-]{3,16})/$', views.space_view, name='space'),
    url(r'([a-zA-Z0-9_-]{3,16})/createproject/$', views.create_project_view, name='create_project'),
    url(r'([a-zA-Z0-9_-]{3,16})/joinspace/$', views.join_space_view, name='join_space'),
    url(r'([a-zA-Z0-9_-]{3,16})/editprofile/$', views.edit_profile_view, name='edit_profile'),
    url(r'([a-zA-Z0-9_-]{3,16})/delete/$', views.delete_space_view, name='delete_space'),
    url(r'^about/$', views.about_view, name='about'),
    url(r'^([a-zA-Z0-9_-]{3,16})/addmembers', views.add_members_view, name='add_members'),
    url(r'^([a-zA-Z0-9_-]{3,16})/([a-zA-Z0-9_-]{3,16})/rank/', views.rank_preferences_view, name='rank_preferences'),
    url(r'^([a-zA-Z0-9_-]{3,16})/delete/([a-zA-Z0-9_"-]{1,30})/$', views.delete_project_view, name='delete_project'),
    url(r'^([a-zA-Z0-9_-]{1,30})/remove/([a-zA-Z0-9_"-]{3,16})/$', views.remove_member_view, name='remove_member'),
    url(r'^([a-zA-Z0-9_-]{3,16})/preferences', views.preferences_view, name='view_preferences'),
    url(r'^([a-zA-Z0-9_-]{3,16})/form_teams/$', views.form_teams_view, name='team_formation'),
    url(r'^([a-zA-Z0-9_-]{3,16})/view_assignments/$', views.view_assignments, name='view_assignments'),
    url(r'^([a-zA-Z0-9_-]{3,16})/assign_teams/$', views.assign_teams_view, name='assign_teams'),
    url(r'^([a-zA-Z0-9_-]{3,16})/teams/$', views.teams_view, name='view_groups'),
    url(r'^([a-zA-Z0-9_-]{3,16})/all_teams/$', views.all_teams_view, name='view_groups'),
    url(r'^([a-zA-Z0-9_-]{3,16})/([a-zA-Z0-9_-]{3,16})/preferences', views.space_preferences_view,
        name='space_view_preferences'),
    url(r'^choose_teams/([a-zA-Z0-9_-]{3,16})/', views.compare_teams_view, name='compare_teams'),
    url(r'^([a-zA-Z0-9_-]{3,16})/send_reminders/$', views.send_reminders_view, name='send_reminders'),
]