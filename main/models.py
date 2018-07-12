"""
Models.py explains the data for this project and is the Model part of the MVC pattern
-   The database on the Heroku server is a Postgres database with tables for each of the classes you see
-   To understand what each class is used for and how it works, read the comments above the class and look at the
-   variables of the class
-   Author: Joshua Stafford (joshua.o.stafford@vanderbilt.edu) Contact with any questions
"""

from django.db import models


#   Spaces are virtual classrooms created by owner members and filled with non-owner members, all stored in
#   space.member_set()
#   -   Spaces are identified by a name and url, and require a password to join unless the owner of the space personally
#       invites a member through their email
#   -   Spaces are created by a form passed to the create_space_view that can be filled out by any owner member
#   -   Members see a portal to all of their spaces on the home page
#   -   The space.html file was created around making each space a virtual classroom, & presents the members & projects
#       of the space to all members to be viewed
#   -   Members and projects can be deleted from a space from the space url by the owner of the space
#   -   To check if a member is the owner of a space, you would use member.username == space.teacher
class Space(models.Model):
    name = models.CharField(max_length=16)
    teacher = models.CharField(max_length=30)  # this is the owner of the space's username
    description = models.CharField(max_length=300)
    password = models.CharField(max_length=16, default='')
    url = models.CharField(max_length=16, default=name)  # needed to access the space via url
    teams_decided = models.BooleanField(default=False)  # if true, the owner has already decided the teams for the space

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

#   MasterTeams hold all the teams for a space and the characteristics of the algorithm used to make the teams
#   -   MasterTeams are created by form_teams_view in main/views.py and are then compared in choose_teams.html
#   -   When the owner of a space chooses a team in choose_teams.html, compare_teams_view will delete all the other
#   -   MasterTeams for that space and alert the members of the space of the teams via email
class MasterTeam(models.Model):
    space = models.ForeignKey(Space)
    number_of_members = models.IntegerField(default=2)
    iterative_soulmates = models.BooleanField(default=False)
    algorithm_index = models.IntegerField(default=0)

    def algorithm_type(self):
        info = ""
        if self.algorithm_index == 0:
            info = "Random Serial Dictatorship"
        elif self.algorithm_index == 1:
            info = "Heuristic"
        elif self.algorithm_index == 2:
            info = "Rotational Proposer Mechanism"
        return info


#   Each team object is identified by its space and it's MasterTeam
#   -   To get the teams of a member, use member.teams
#   -   Team instances are made by the form_teams_view in main/views.py by reading the Jar file output
class Team(models.Model):
    space = models.ForeignKey(Space)
    master = models.ForeignKey(MasterTeam, default=None)

    def __str__(self):
        members = Member.objects.filter(teams=self)
        temp = ""
        for member in members:
            temp += member.name + ", "
        temp = temp[:-2]
        return temp


#   Projects are able to be created by Members that own a space. Each project is made via a form in the
#   create_project_view method in main/views.py. Projects are displayed in the space.html page for all members of the
#   space to view
class Project(models.Model):
    name = models.CharField(max_length=30)
    url = models.CharField(max_length=30, default=name)  # needed to have a url that called the delete_project_view
    description = models.CharField(max_length=500)
    qualifications = models.CharField(max_length=300)
    space = models.ForeignKey(Space)  # each project is associated with one space

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


#   Instead of extending the User model of Django, a new Member class was created. To link the User to their member
#   instance, get the User's username with the_username = request.user.get_username() and then get the member object
#   with Member.objects.get(username=the_username)
class Member(models.Model):
    name = models.CharField(max_length=30, default='Account in Progress')
    username = models.CharField(max_length=30)
    email = models.EmailField(max_length=60, default='empty@gmail.com')
    spaces = models.ManyToManyField(Space)
    skills = models.CharField(max_length=300, default="No bio has been added yet.")
    owner = models.BooleanField(default=False)  # if true, member is able to create spaces & have admin functionality
    teams = models.ManyToManyField(Team)
    security_code = models.IntegerField(default=972124)  # hacked this on late to allow changing passwords

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.username


#   Each preference instance is tied to a single member and a single space, and the member can have only one preference
#   for each space they are in.
#   -   Preferences hold project_rankings and member_rankings, which are strings that hold their preferences
#       and are parsed by preferences_as_names to display a nice format for users to see
#   -   The form_teams_view in main/views.py also parses the preferences and passes them into the Jar file to form teams
#   -   Preferences are created in the rank_preferences_view in main/views.py
class Preferences(models.Model):
    member = models.ForeignKey(Member)
    space = models.ForeignKey(Space)
    projects_ranking = models.CharField(max_length=1000, default='')
    members_ranking = models.CharField(max_length=1000, default='')

    def __unicode__(self):
        return self.member.username + ": " + self.space.name

    def __str__(self):
        return self.member.username + ": " + self.space.name

    def preferences_as_names(self):
        all_preferences = str(self.members_ranking)
        pref_user_names = all_preferences.split(" ")
        names_string_raw = ""
        for pref_username in pref_user_names:
            if len(pref_username) >= 3:
                if Member.objects.filter(username=pref_username).exists():
                    preferred_user = Member.objects.get(username=pref_username)
                    name = preferred_user.name
                elif pref_username == "@myself@":
                    name = "Rather be by Myself"
                elif pref_username == "@team@":
                    name = "Rather be on any Team"
                else:
                    name = "Invalid User"
                names_string_raw += name + ", "

        if len(names_string_raw) > 3:
            names_string = names_string_raw[0:-2]
        else:
            names_string = "No preferences submitted."
        return names_string

    def project_preferences_as_names(self):
        all_preferences = str(self.projects_ranking)
        pref_projects = all_preferences.split(" ")
        pref_projects = pref_projects[:-1]
        counter = 1
        project_points = {}
        for pref_project in pref_projects:
            if Project.objects.filter(name=pref_project).exists():
                    preferred_project = Project.objects.get(name=pref_project)
                    project_points[preferred_project.name] = counter
                    counter += 1
        return project_points


class TeamProject(models.Model):
    space = models.ForeignKey(Space)
    project = models.ForeignKey(Project, default=None)
    team = models.ForeignKey(Team)


