"""
View.py contains all of the controller logic for this project which uses the MVC pattern
-   Each view is a function view that takes in an HTTP request and renders an html page with the appropriate data passed
    in the context dictionary.
-   Views are called by the urlconf in main/urls.py
-   To make the views more readable, code has been moved into helper methods in the main/functions.py file.
-   Any parameters in the function after 'request' are strings passed in by the Url which called the function
        -> Of these extra parameters, the most common is the username parameter used to identify the user
-   Author: Joshua Stafford (joshua.o.stafford@vanderbilt.edu) Contact with any questions
"""


from __future__ import division
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from main.forms import SignUpForm, EmailSignupForm, ChangePasswordForm
from django.shortcuts import render, redirect
from main.models import Space, Project, Member, Preferences, Team, MasterTeam
import json as simplejson
from main.functions import authenticate_member, get_user, send_new_space_email, send_owner_spreadsheet
from django.core.mail import send_mail
from subprocess import Popen, PIPE, STDOUT
import random


# View just displays a link to the login page if user is not logged in or redirects them to their
# profile page if they are
def home_view(request):
    msg = ""
    if request.user.is_active:
        member = get_user(request)
    else:
        member = None
    return render(request, 'home.html', {'member': member, 'msg': msg})


# View allows users to sign up and gain access to the site, entering them into our Member model. It is
# in this view where the user is determined to be an owner or regular user via the owner checkbox.
def signup_view(request):
    error_msg = ""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            login(request, user)
            is_registered = Member.objects.filter(email=request.POST['email']).exists()
            if is_registered:
                member = Member.objects.get(email__iexact=request.POST['email'])
                if member.name == "Account in Progress":
                    member.name = request.POST['full_name']
                    member.username = request.POST['username']
                    member.owner = False
                    member.save()
                    return redirect('/profile_redirect/')
                else:
                    error_msg = "Email is already registered with our site."
                    return render(request, 'registration/signup.html', {'form': form, 'errormsg': error_msg})
            else:
                member = Member(username=request.POST['username'],
                             name = request.POST['full_name'],
                             email=request.POST['email'],
                             owner= False)
                member.save()
            return redirect('/' + member.username + '/joinspace/')
    else:
        if request.user.is_active:
            return redirect('/profile_redirect/')
        else:
            form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form, 'errormsg': error_msg})


def email_signup_view(request, email_address):
    error_msg = email_address
    is_registered = Member.objects.filter(email__iexact=email_address).exists()
    if not is_registered:
        return redirect('/')
    if request.method == 'POST':
        form = EmailSignupForm(request.POST)
        username = request.POST['username']

        valid_username = True
        for letter in username:
            if not (letter.isalnum() or letter == '_'):
                valid_username = False
                error_msg = "Username can only contain letters, numbers, and underscores"
        if len(username) < 3 or len(username) > 16:
            valid_username = False
            error_msg = "Username must be between 3 to 16 characters"

        if not valid_username:
            return render(request, 'registration/email_signup.html',
                          {'form': form, 'error_msg': error_msg, 'email': email_address})

        if form.is_valid():
            form.save()
            user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            login(request, user)
            member = Member.objects.get(email=email_address)
            member.name = request.POST['full_name']
            member.username = request.POST['username']
            member.security_code = random.randint(100000, 999999)
            member.save()
            subject = "Your Team Formation account has been made!"
            message = member.name + "," + "\n\n"
            message += "Thanks for signing up with The Team Formation Platform! Log in to access your spaces and rank which projects you want to" \
                      " work on and which members you want to work with."
            message += "\n\nBest,\nThe Team Formation Team"
            sender_email = 'teamformation.notify@gmail.com'
            recipient_email = member.email
            send_mail(subject, message, sender_email, [recipient_email])
            return redirect('/profile_redirect/')
        else:
            error_msg = "Passwords did not match."
    form = EmailSignupForm()

    return render(request, 'registration/email_signup.html', {'form': form, 'error_msg': error_msg, 'email': email_address})


def forgot_password_view(request):
    msg = ""
    if request.method == 'POST':
        email = request.POST['email']
        if Member.objects.filter(email__iexact=email).exists():
            member = Member.objects.get(email__iexact=email)
            subject = "New password for Team Formation Account"
            message = "Hi " + member.name + ", \n\nPlease use the security code and link below to change the password of " + member.username + ".\n\n"
            message += "Security code: " + str(member.security_code) + "\n\nhttps://vandy-tfx.herokuapp.com/change_password/" + member.username + "/"
            message += "\n\nBest,\nThe Team Formation Team"
            sender_email = 'teamformation.notify@gmail.com'
            send_mail(subject, message, sender_email, [email])
            msg = "Your password has been sent to " + email
        else:
            msg = "The email you entered is not registered with our site."
    return render(request, "forgot_password.html", {'msg': msg})


def change_password_view(request, username):
    msg = ""
    if request.user.is_active:
        member = get_user(request)
        msg = "Your security code is " + str(member.security_code)
    error_msg = ""
    if not Member.objects.filter(username=username).exists():
        return redirect('/')

    if request.method == 'POST':
        security_code = int(request.POST['security_code'])
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        member = Member.objects.get(username=username)
        if security_code == member.security_code:
            if password1 == password2:
                user = User.objects.get(username=username)
                user.set_password(password1)
                user.save()
                msg = "Your password has been changed."
            else:
                error_msg = "Passwords were not the same."
                form = ChangePasswordForm()
                return render(request, "change_password.html",
                              {'form': form, 'error_msg': error_msg, 'member': member, 'msg': msg})
        else:
            error_msg = "Invalid security code."
            form = ChangePasswordForm()
            return render(request, "change_password.html",
                          {'form': form, 'error_msg': error_msg, 'member': member, 'msg': msg})
        return render(request, "home.html", {'msg': msg})
    form = ChangePasswordForm()
    member = Member.objects.get(username=username)
    return render(request, "change_password.html", {'form': form, 'error_msg': error_msg, 'member': member, 'msg': msg})


# View shows all the most pertinent information for the user, including links to all of the spaces they
# are already in and a link to either create a new space or join an existing one
@login_required(login_url="login/")
def profile_view(request, username):
    if username == "" or not Member.objects.filter(username=username).exists():
        return redirect('/profile_redirect/')
    member = Member.objects.get(username= username)
    if authenticate_member(request, member):
        if member.owner:
            spaces = Space.objects.filter(teacher=username)
        else:
            spaces = member.spaces.all()
        return render(request, 'profile.html', {'member': member, 'spaces': spaces})
    else:
        return redirect('/profile_redirect/')


# View redirects lost users to their profile
@login_required(login_url="/login/")
def profile_redirect_view(request):
    member = get_user(request)
    string = '/profile/' + member.username
    return redirect(string)


# View allows for owners to create a new space with a password. They are then redirected to that page
@login_required(login_url="/login/")
def create_space_view(request, username):
    member = Member.objects.get(username = username)
    if not authenticate_member(request, member):
        return redirect('/profile_redirect/')
    error_msg = ""
    if request.method == 'POST':
        space_name = request.POST['Space']
        if len(space_name) > 16 or len(space_name) < 3:
            error_msg = "The name of your space must be between 3 and 16 characters."
            return render(request, 'createspace.html', {'username': username, 'member': member, 'errormsg': error_msg})

        existing_space_name = Space.objects.filter(name = space_name).exists()
        if existing_space_name: # space name is taken, so error message is shown
            error_msg = "That name is already being used for an existing space, please choose another."
            return render(request, 'createspace.html', {'username': username, 'member': member, 'errormsg': error_msg})

        else:   # space name is unique, so the space is made
            url_catcher = ""
            url_name = ""
            words_list = space_name.split(" ")
            for word in words_list:
                url_catcher += word + "_"
                url_name = url_catcher[:-1]

            space = Space(name=space_name, teacher=username, description=request.POST['Description'],
                          password=request.POST.get('password', False), url=url_name)

            space.save()
            space_page = '/space/' + url_name
            return redirect(space_page)
    return render(request, 'createspace.html', {'username': username, 'member': member, 'errormsg': error_msg})


# View allows for owners to create new projects in a space, which will be visible by everyone in the space.
@login_required(login_url="/login/")
def create_project_view(request, space_url):
    errormsg = ""
    member = get_user(request)
    owning_space = Space.objects.get(url=space_url)
    if member.username != owning_space.teacher:
        return redirect('/profile_redirect/')

    if request.method == 'POST':
        name = request.POST['Project']
        description = request.POST['Description']
        qualifications = request.POST['Qualifications']
        url = name.replace(' ', '_')
        if Project.objects.filter(name = name).exists():
            errormsg = "That project name has already been used."
            return render(request, 'createproject.html', {'member': member, 'errormsg': errormsg})

        if len(url) > 30 or len(description) > 500 or len(qualifications) > 300:
            errormsg = "Too long. The project's name cannot be more than 30 characters"
            return render(request, 'createproject.html', {'member': member, 'errormsg': errormsg})

        new_project = Project(name = name, url = url, description=description, qualifications=qualifications,
                            space = owning_space)
        new_project.save()
        return redirect('/space/' + space_url)
    return render(request, 'createproject.html', {'member': member, 'errormsg': errormsg})


# View displays all of the spaces that the active user is a part of as links to the space's page
@login_required(login_url="/login/")
def space_view(request, url):
    msg = ""
    space = Space.objects.get(url=url)
    teamsformed = Team.objects.filter(space=space).exists()
    member = get_user(request)
    if member.spaces.filter(url=url).exists() or member.username == space.teacher: # makes sure user is in the space
        projects = Project.objects.filter(space__url__exact=url)
        ordered_projects = projects.order_by('name')
        participants = space.member_set.exclude(name = 'Account in Progress')
        ordered_participants = participants.order_by('name')
        participants_prefs = []
        for participant in ordered_participants:
            if Preferences.objects.filter(member=participant, space=space).exists():
                preference = Preferences.objects.get(member=participant, space=space)
                prefs = preference.preferences_as_names()
            else:
                prefs = "No partner preferences submitted"
            participants_prefs.append(prefs)

        non_registered_members = space.member_set.filter(name='Account in Progress')
        non_registered_members = non_registered_members.order_by('email')
        if request.method == 'POST':
            msg = "The password for this space is " + space.password
        zipped = zip(ordered_participants, participants_prefs)
        return render(request, 'space.html', {'projects': ordered_projects, 'space': space, 'member': member,
                                              'zipped_students': zipped, 'msg': msg, 'teamsformed': teamsformed,
                                              'non_registered_members': non_registered_members, 'total_students':
                                              participants.count()})
    else:
        return redirect('/profile_redirect/')


# View shows the user all available spaces they could join (one's they aren't already in) and allows them to join
# multiple at one time by entering the password and checking a box. If a space is joined and no password is wrong,
# the view redirects to their profile with the newly added spaces
@login_required(login_url="/login/")
def join_space_view(request, username):
    member = Member.objects.get(username=username)
    if not authenticate_member(request, member):
        return redirect('/profile_redirect/')
    msg = ""
    are_spaces = True
    success = False  # flag for if a user has successfully joined
    fail = False    # flag for if user entered the wrong password for any space

    spaces = Space.objects.all()
    spaces = spaces.order_by('name')    # orders spaces alphabetically

    # for loop checks for which spaces a member is already a part of and prevents showing those spaces on JoinSpace
    for space in spaces:
        already_member = member.spaces.filter(name= space.name).exists()
        if already_member:
           spaces = spaces.exclude(name = space.name)

    if spaces.count() == 0:
        are_spaces = False
    if request.method == 'POST':
        for space in spaces:
            check = request.POST.get(space.url, False) == "on"
            if check: # if they indicated they wanted to join space

                password_input = space.url + "Password"
                password_try = request.POST.get(password_input, "")
                if space.password == password_try: # if the password was correct
                    member.spaces.add(space)
                    member.save()
                    success = True
                    msg += "You have been added to " + space.name + ". "
                else:
                    msg += "You entered the wrong password for " + space.name + ". "
                    fail = True
        if fail:
            return render(request, 'joinspace.html', {'msg': msg, 'member': member, "spaces": spaces, "are_spaces": are_spaces})
        if success:
            return redirect("/profile/" + username + '/')
    return render(request, 'joinspace.html', {'msg': msg, 'member': member, "spaces": spaces, "are_spaces": are_spaces})


# View allows for users to edit their profile and add skills or a bio
@login_required(login_url="/login/")
def edit_profile_view(request, username):
    error = False
    member = Member.objects.get(username=username)
    msg = ""
    if not authenticate_member(request, member):
        return redirect('/profile_redirect/')
    if request.method == 'POST':
        skills = request.POST['skills']
        if len(skills) < 300:
            member.skills = skills
            member.save()
        else:
            error = True
            msg = "The skills you entered were too long. They have to be under 300 characters."
    return render(request, "editprofile.html", {'member': member, 'msg': msg, 'error': error})


# View shows the about page
def about_view(request):
    return render(request, "about.html", context=None)


# View allows the owner of a space to delete the space after receiving a message alerting them to what they
# are about to do
@login_required(login_url="/login/")
def delete_space_view(request, spaceurl):
    msg = ""
    deleted = False
    member = get_user(request)
    space = Space.objects.get(url=spaceurl)
    if space.teacher != member.username:
        return redirect('/profile_redirect/')
    if request.method == 'POST':
        if space.teacher == member.username:
            space.delete()
            return redirect("/profile/" + member.username)
        else:
            msg = "You do not have the ability to delete this space"

    return render(request, "deletespace.html", {'msg': msg, 'spaceurl': spaceurl, 'member': member, 'deleted': deleted})


# View allows the owner of a space to make a semi-complete user account and put them in their space, so when the user
# joins with the email the admin put in, they will already be in the right space
@login_required(login_url="/login/")
def add_members_view(request, spaceurl):
    were_reg_adds = were_unreg_adds = were_dup_adds = False
    counter = 0
    non_registered_adds = []
    registered_adds = []
    already_added = []
    total_added = 0
    were_adds = False
    member = get_user(request)
    space = Space.objects.get(url = spaceurl)
    msg = ""
    if request.FILES and request.method == 'POST':
        were_adds = True
        file = request.FILES['csv_file']
        file_data = file.read().decode("utf-8")
        lines = file_data.split("\n")
        for i, entry in enumerate(lines):
            lines[i] = lines[i].replace('\r', '')
            if lines[i] == '':
                counter += 1
        lines = list(filter(None, lines))
        if counter == len(lines):
            msg = "Error, no file submitted."
            return render(request, "addmembers.html", {'space': space, 'msg': msg, 'member': member})
        for line_input in lines:
            email = line_input
            already_member = Member.objects.filter(email__iexact=email).exists()
            if already_member:
                already_invited_to_space = False
                added_member = Member.objects.get(email__iexact=email)
                if space.member_set.filter(email__iexact=email).exists():
                    already_invited_to_space = True
                    were_dup_adds = True
                    already_added.append(added_member.email)
                if not already_invited_to_space:
                    were_reg_adds = True
                    added_member.spaces.add(space)
                    added_member.save()
                    registered_adds.append(added_member.name)
                    #send_new_space_email(member, space, email, already_member)
            else:
                new_member = Member(email=email)
                new_member.save()
                new_member.spaces.add(space)
                new_member.save()
                non_registered_adds.append(new_member.email)
                were_unreg_adds = True
                #send_new_space_email(member, space, email, already_member)
        total_added = non_registered_adds.__len__() + registered_adds.__len__() + already_added.__len__()
    elif request.method == 'POST':
        email = request.POST['Email']
        if email == "":
            msg = "Error, no file submitted."
            return render(request, "addmembers.html", {'space': space, 'msg': msg, 'member': member})
        already_member = Member.objects.filter(email__iexact=email).exists()
        if already_member:
            already_invited_to_space = False
            added_member = Member.objects.get(email__iexact=email)
            if space.member_set.filter(email__iexact=email).exists():
                already_invited_to_space = True
            if not already_invited_to_space:
                added_member.spaces.add(space)
                added_member.save()
                msg = added_member.name + " has been successfully added to " + space.name \
                     + ". Enter another email to add another member to the space."
                #send_new_space_email(member, space, email, already_member)
        else:
            new_member = Member(email=email)
            new_member.save()
            new_member.spaces.add(space)
            new_member.save()
            msg = email + " has been successfully added to " + space.name \
                   + ". Enter another email to add another member to the space."
            #send_new_space_email(member, space, email, already_member)
    return render(request, "addmembers.html", {'space':space, 'msg': msg, 'member': member, 'non_registered_adds':
                                               non_registered_adds, 'registered_adds': registered_adds,
                                               'were_adds': were_adds, 'total_added': total_added, 'already_added':
                                               already_added, 'ra': were_reg_adds, 'ura': were_unreg_adds, 'aa':
                                               were_dup_adds})


# View allows students to rank the students the would like to work with and projects they would like to work on
@login_required(login_url="/login/")
def rank_preferences_view(request, spaceurl, username):
    success = False
    member = Member.objects.get(username=username)
    if not authenticate_member(request, member):
        return redirect('/profile_redirect/')

    space = Space.objects.get(url=spaceurl)
    projects = Project.objects.filter(space__url__exact=spaceurl)
    projects = projects.order_by('name')
    participants = space.member_set.exclude(name='Account in Progress')
    participants = participants.exclude(username = username)
    participants = participants.order_by('name')

    if request.is_ajax():
        category = request.POST.get('category')
        if Preferences.objects.filter(member=member, space=space).exists():
            preference = Preferences.objects.get(member=member, space=space)
            preference.delete()
        preference = Preferences(member=member, space=space)
        preference.id = preference.id
        if category == 'project':
            project_ranking_JSON = request.POST.get('project_ranking')
            project_preferences = simplejson.loads(project_ranking_JSON)
            preference.projects_ranking = ""
            for project in project_preferences:
                preference.projects_ranking += project + ', '
            preference.projects_ranking = preference.projects_ranking[:-2]
            success = True

        if category == 'peer':
            peer_ranking_JSON = request.POST.get('peer_ranking')
            peer_preferences = simplejson.loads(peer_ranking_JSON)
            preference.members_ranking = ""
            for peer in peer_preferences:
                raw_list = peer.split(" ")
                username = raw_list[len(raw_list) - 1]
                if username == "Myself":
                    preference.members_ranking += "@myself@ "
                elif username == 'Team':
                    preference.members_ranking += "@team@ "
                else:
                    username = username[1:-1]
                    preference.members_ranking += username + ' '

        preference.save()
    return render(request, "rankpreferences.html", {'member': member, 'projects': projects, 'participants': participants,
                                                    'success': success, 'space': space})


# View quickly changes view and back to the old view, running code to delete the project in the meantime
@login_required(login_url="/login/")
def delete_project_view(request, space_url, project_url):
    member = get_user(request)
    space = Space.objects.get(url=space_url)
    if space.teacher == member.username:
        project_name = project_url.replace('_', ' ')
        project = Project.objects.get(name=project_name, space=space)
        project.delete()
    return redirect("/space/" + space_url)


# View quickly changes view and back to the old view, running code to remove a member from the space
@login_required(login_url="/login/")
def remove_member_view(request, space_url, username):
    space = Space.objects.get(url=space_url)
    member = get_user(request)
    removed_member = Member.objects.get(username=username)
    if member.username != space.teacher:
        return redirect("/space/" + space_url)
    if request.POST:
        removed_member.spaces.remove(space)
        if Preferences.objects.filter(member=removed_member, space=space).exists():
            preferences = Preferences.objects.get(member=removed_member, space=space)
            preferences.delete()
        return redirect("/space/" + space_url)
    return render(request, 'remove_member.html', {'space': space, 'member': member, 'removed_member': removed_member})


@login_required(login_url="/login/")
def preferences_view(request, username):
    member = Member.objects.get(username = username)
    if not authenticate_member(request, member):
        return redirect('/profile_redirect/')

    if member.owner:
        spaces = Space.objects.filter(teacher = member.username)
        percentages = []
        for space in spaces:
            submitted = 0
            participants = space.member_set.exclude(name='Account in Progress')
            preferences = Preferences.objects.filter(space = space)
            for preference in preferences:
                if preference.members_ranking != '' and preference.members_ranking != 'Not Submitted Yet':
                    submitted += 1
            if participants.count() == 0:
                percent = 0.0
            else:
                percent = submitted / participants.count() * 100
            percent = round(percent, 2)
            percentages.append(percent)
            percentages.append(percent)
            percentages.append(percent)
        percentages.reverse()
        return render(request, 'ownerviewpreferences.html', {'member': member, 'spaces': spaces,
                                                             'percentages': percentages})

    preferences = Preferences.objects.filter(member=member)
    return render(request, 'preferences.html', {'member': member, 'preferences': preferences})


@login_required(login_url="/login/")
def space_preferences_view(request, username, spaceurl):
    member = Member.objects.get(username=username)
    if not authenticate_member(request, member):
        return redirect('/profile_redirect/')

    space = Space.objects.get(url=spaceurl)
    if member.username != space.teacher:
        return redirect('/profile_redirect/')

    preferences = Preferences.objects.filter(space = space)
    preferences.order_by('member')
    return render(request, 'spacepreferences.html', {'member': member, 'preferences': preferences})


@login_required(login_url="/login/")
def form_teams_view(request, spaceurl):
    member = get_user(request)
    space = Space.objects.get(url=spaceurl)
    msg = ""
    user_preferences = ""
    if member.username != space.teacher:
        return redirect('/profile_redirect/')
    setup_data = ""
    if request.method == 'POST':
        group_size_raw = request.POST.get('Group_Options', None)
        iterative_soulmates_raw = '1'
        algorithm_index_raw = request.POST.get('optradio', None)
        alpha_raw = request.POST.get('alpha')
        alpha_adjusted = float(alpha_raw) * 1000000
        alpha_adjusted = int(alpha_adjusted)
        theta_raw = request.POST.get('theta')
        theta_adjusted = float(theta_raw) * 100
        theta_adjusted = int(theta_adjusted)
        members = space.member_set.exclude(name='Account in Progress')
        number_members = members.count()

        setup_data = str(number_members) + " " + group_size_raw + " " + iterative_soulmates_raw + " " \
                     + algorithm_index_raw + " " + str(alpha_adjusted) + " " + str(theta_adjusted)

        # get input in format to store in team model
        algorithm_index = int(algorithm_index_raw)
        iterative_soulmates = iterative_soulmates_raw == "1"
        group_size = int(group_size_raw)

        # Assigns each member a rank and sets up easy lookup between usernames and rankings
        rank_to_user_dict = {}
        user_to_rank_dict = {}
        random_array = random.sample(range(0, members.count()), members.count())
        count = 0
        for member in members:
            rank = random_array[count]
            rank_to_user_dict[rank] = member.username
            user_to_rank_dict[member.username] = rank
            count += 1

        # Gets member preferences ready for the java program
        user_preferences = ""
        for member in members:
            member_data = member.username + " " + str(user_to_rank_dict[member.username]) + " "
            wants_any_team = False
            if Preferences.objects.filter(member=member, space=space).exists():
                finished = False
                pref_data = ""
                preferences = Preferences.objects.get(member=member, space=space)
                preferenceArray = preferences.members_ranking.split(' ')
                for preference in preferenceArray:
                    if preference == "@myself@":
                        finished = True
                    elif preferences == "@team@":
                        wants_any_team = True
                    if preference in user_to_rank_dict and not finished:
                        pref_data += str(user_to_rank_dict[preference]) + " "
                if wants_any_team:
                    pref_data = "team " + pref_data
                else:
                    pref_data = "alone " + pref_data
                member_data += " " + pref_data
            else:
                member_data += "alone "
            user_preferences += member_data

        # Runs the team formation algorithms by passing in setup data and preference data to the Java executable
        p = Popen(['java', '-jar', 'JavaCode/TeamFormationAlgorithms.jar', setup_data, user_preferences],
                  stdout=PIPE, stderr=STDOUT)

        # Adds teams to the database by parsing the console output of the Java executable
        master_team = MasterTeam(space=space, iterative_soulmates=iterative_soulmates,
                                 number_of_members=group_size, algorithm_index=algorithm_index)
        master_team.save()
        space.teams_decided = False
        space.save()

        for raw_line in p.stdout:
            line = raw_line.decode("utf-8")
            if line[0:2] == 'T:':
                teammates = line[3:]
                user_list = teammates.split(" ")
                team = Team(space=space, master=master_team)
                team.save()
                for username in user_list:
                    if Member.objects.filter(username=username).exists():
                        user = Member.objects.get(username=username)
                        user.teams.add(team)
                        user.save()
                team.save()
            if line[0:2] == 'S:':
                solo_names = line[3:]
                solo_list = solo_names.split(" ")
                for username in solo_list:
                    if not username == '':
                        user = Member.objects.get(username=username)
                        team = Team(space=space, master=master_team)
                        team.save()
                        user.teams.add(team)
        master_team.save()

        return redirect("/choose_teams/" + space.url + "/")

    return render(request, "TeamFormation.html", {'member': member, 'msg': "\"" + setup_data + "\" \"" + user_preferences + "\""})


@login_required(login_url="/login/")
def teams_view(request, username):
    member = get_user(request)
    if member.owner:
        spaces = Space.objects.filter(teacher = member.username)
        return render(request, "ownerviewteams.html", {'member': member, 'spaces': spaces})
    else:
        teams = []
        no_teams = True
        for space in member.spaces.all():
            if space.teams_decided:
                if member.teams.filter(space=space).exists():
                    team = member.teams.get(space=space)
                    teams.append(team)
                    no_teams = False
        return render(request, "ViewTeams.html", {'member': member, 'teams': teams, 'noteams': no_teams})


@login_required(login_url="/login/")
def all_teams_view(request, spaceurl):
    member = get_user(request)
    if Space.objects.filter(url=spaceurl).exists():
        space = Space.objects.get(url = spaceurl)
    else:
        return redirect('/profile_redirect/')
    if not member.owner:
        return redirect('/profile_redirect/')
    no_teams = not space.teams_decided
    if space.teams_decided:
        master_team = MasterTeam.objects.get(space=space)
        teams = Team.objects.filter(space=space, master=master_team)
    else:
        teams = None
    return render(request, "ViewTeams.html", {'member': member, 'teams': teams, 'noteams': no_teams, 'space': space})


@login_required(login_url="/login/")
def compare_teams_view(request, space_url):
    space = Space.objects.get(url=space_url)
    member = get_user(request)
    if space.teacher != member.username:
        return redirect('/profile_redirect/')
    if request.method == 'POST':
        master_teams = MasterTeam.objects.filter(space=space)
        was_finalized = False
        finalized_team = None
        for master_team in master_teams:
            finalized_team_id = request.POST.get(str(master_team.id), False)
            if finalized_team_id:
                finalized_team = master_team
                was_finalized = True
        if was_finalized:
            for master_team in master_teams:
                if master_team != finalized_team:
                    master_team.delete()
            space.teams_decided = True
            space.save()

            # tell all the members about their new team
            master_teams = MasterTeam.objects.get(space=space)
            send_owner_spreadsheet(master_teams, space)
            participants = space.member_set.exclude(name='Account in Progress')
            for participant in participants:
                if member.teams.filter(space=space).exists():
                    team = member.teams.get(space=space)
                    subject = "You have been added to a Team in " + space.name
                    message = participant.name + ",\n\nCongratulations, you have been added to a team in " + space.name
                    message += ". Your team consists of " + str(team) + ". "
                    message += "\n\nBest,\nThe Team Formation Team"
                    sender_email = 'teamformation.notify@gmail.com'
                    recipient_email = participant.email
                    send_mail(subject, message, sender_email, [recipient_email])
                else:
                    subject = "You have been added to a Team in " + space.name
                    message = participant.name + ",\n\nCongratulations, you have been added to a team in " + space.name
                    message += ". Check out the team at https://vandy-tfx.herokuapp.com/" + participant.username + "/teams/"
                    message += "\n\nBest,\nThe Team Formation Team"
                    sender_email = 'teamformation.notify@gmail.com'
                    recipient_email = participant.email
                    send_mail(subject, message, sender_email, [recipient_email])

    master_teams = MasterTeam.objects.filter(space=space)
    return render(request, "choose_teams.html", {'member': member, 'space': space, 'master_teams': master_teams})


@login_required(login_url="/login/")
def send_reminders_view(request, space_url):
    space = Space.objects.get(url=space_url)
    member = get_user(request)
    if member.username != space.teacher:
        return redirect('/profile_redirect/')
    emails = []
    non_registered_members = space.member_set.filter(name='Account in Progress')
    for non_registered_member in non_registered_members:
        receiver_email = non_registered_member.email
        send_new_space_email(member, space, receiver_email, False)
        emails.append(receiver_email)
    return render(request, 'send_reminders.html', {'member': member, 'emails': emails, 'space': space})


@login_required(login_url="/login/")
def assign_teams_view(request, spaceurl):
    space = Space.objects.get(url=spaceurl)
    preferences = Preferences.objects.filter(space=space)
    teams = Team.objects.filter(space=space)
    projects = Project.objects.filter(space=space)

    for team in teams:
        team_rank = {}
        for project in projects:
            team_rank[project.name] = 0

        members = Member.objects.filter(teams=team)
        for member in members:
            member_preferences = preferences.filter(member=member, space=space)
            member_rankings = member_preferences.project_preferences_as_names
            for project in member_rankings:
                team_rank[project.name] += member_rankings[project.name]

        max_value = -1
        max_project = None
        for project.name in team_rank:
            if team_rank[project.name] > max_value:
                max_value = team_rank[project.name]
                max_project = project.name

        team_project = Project.objects.filter(name=max_project)
        team_project.team = team
        team_project.save()
    return render(request, 'view_assignments.html', {'member': get_user(request), 'list': Project.objects.filter(space=space), 'space': space})


@login_required(login_url="/login/")
def view_assignments(request, spaceurl):
    space = Space.objects.get(url=spaceurl)
    return render(request, 'view_assignments.html', {'member': get_user(request), 'list': Project.objects.filter(space=space), 'space': space})

