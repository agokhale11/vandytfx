"""
functions.py are the helper functions that contain code mostly used by main/views.py
"""

from main.models import Member, Team
from django.core.mail import send_mail, EmailMessage
import csv
import io


def authenticate_member(request, member):
    real_user = request.user
    real_username = real_user.get_username()
    return real_username == member.username


def get_user(request):
    user = request.user
    username = user.get_username()
    member = Member.objects.get(username=username)
    return member


def send_new_space_email(owner, space, email, already_registered):
    sender_email = 'teamformation.notify@gmail.com'
    if already_registered:
        participant = Member.objects.get(email=email)
        subject = owner.name + " added you to " + space.name
        message = participant.name + ",\n\nYou have been placed into " + space.name + " by " + owner.name
        message += ". Check the space out here: https://vandy-tfx.herokuapp.com/space/" + space.url + "/"
        message += "\n\nBest,\nThe Team Formation Team"
        send_mail(subject, message, sender_email, [email])
    else:
        subject = owner.name + " has invited you to join the Team Formation Platform."
        message = "Welcome to the Team Formation Platform!\n\n"
        message += owner.name + " has invited you to participate in the Team Formation Platform. In order to make an " \
                                "account, go to the following link: https://vandy-tfx.herokuapp.com/signup/" + email + "/"
        message += "\n\nBest,\nThe Team Formation Team"
        send_mail(subject, message, sender_email, [email])


def send_owner_spreadsheet(master_teams, space):
    owner = Member.objects.get(username=space.teacher)
    csvfile = io.StringIO()
    writer = csv.writer(csvfile)
    teams = Team.objects.filter(master=master_teams)
    number_of_members = master_teams.number_of_members

    # determining head row based on how many members a team can have (2 is default option)
    member_header = "Member 1,Member 2"
    if number_of_members == 3:
        member_header = "Member 1,Member 2,Member 3"
    elif number_of_members == 4:
        member_header = "Member 1,Member 2,Member 3,Member 4"
    elif number_of_members == 5:
        member_header = "Member 1,Member 2,Member 3,Member 4,Member 5"
    first_row_data = "Team #," + member_header
    first_row_list = first_row_data.split(",")

    writer.writerow(first_row_list)

    team_number = 1
    for team in teams:
        row_data = str(team_number) + ","
        members = Member.objects.filter(teams=team)
        for member in members:
            row_data += member.name + ","
        row_data = row_data[0:-1] # remove the extra "," at the end
        row_list = row_data.split(",")
        writer.writerow(row_list)

        team_number += 1
    email_body = owner.name + ", \n\n" + "Your teams for " + space.name + " have been formed, and the members have been notified"
    email_body += " of their teams.\nA csv file of the teams has been attached.\n\nBest,\nThe Team Formation Team"

    email = EmailMessage(subject=("Teams for " + space.name), body=email_body, from_email='teamformation.notify@gmail.com',
                         to=[owner.email])
    file_name = "teams_for_" + space.url + ".csv"
    email.attach(filename=file_name, content=csvfile.getvalue(), mimetype='text/csv')
    email.send()