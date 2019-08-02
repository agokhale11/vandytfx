# Web Platform for forming teams

TFx (Team Formation Exchange) is a web platform that will form teams of users based off these users' preferences.

<h2>Overview</h2>

<b>Examples of situations for this application:</b>
- Choosing groups for projects in school<br>
- Forming groups for work assignments<br>
- Picking roommates on trips<br>

<b>How it works:</b>
- There are two different types of accounts - owners and members.<br>
- Owners can create spaces and invite members to join.<br> 
- Members can join spaces and submit their preferences of which other members of the space they want to work with. <br>
- Owners then pick which team formation algorithm to run and the maximum group size allowed.<br>
- Teams are formed based off the algorithm and the owner is notified.<br>
- The owner can either finalize these teams or run a different algorithm.<br>
- When the owner finalizes teams, all members in that space get a notification.

<h2>Documentation</h2>

<b>High Level</b>
- The web platform is written in the python framework Django (python 3.6, Django 1.11).<br>
- The algorithms which determine teams are written in Java as a .jar file and are run with Popen from the python library subprocess.<br>
- User information, user preferences, space information, and teams are kept in a Postgres database.<br>
- You can view the tables for these databases by looking at the main.models file.<br>
- The frontend of the platform is written with Django's template framework and very little javascript.

<b>Lower Level</b>
- The project can be best thought of through the Model View Controller (MVC) pattern
- The most important files to investigate to get an understanding of the code are the following. They are all well commmented.
    - main/urls.py: This file routes all the possible urls a user could visit to functions that render what the user sees
    - main/views.py: This file contains all those functions called by urls.py that render the html
    - main/models.py: This file describes how the data for this project is stored and used
    - main/templates: This folder holds all the html pages the user sees written with Django's template framework. 


<h1>Algorithms Used</h1>
<b>Algorithms Currently Offered</b>
<ul>
<li>Iterative Soulmates*</li>
<li>Random Serial Dictatorship</li>
<li>Heuristic Approach</li>
<li>Rotational Proposer Mechanism</li>
</ul>
* - (pre-processing algorithm, normally used along with one of the algorithms below)
<h5>Iterative Soulmates</h5>
<p>This preprocessing algorithm will find any groups of members of a specified size that meet the Soulmates Criteria</p>
<p>Soulmates Criteria:A team of <i>n</i> users is meets the soulmates criteria iff each member of the team considers every other member to be in their top <i>n-1</i> available choices.</p>
<h5>Random Serial Dictatorship</h5>
<p>Users are given a random rank for when they get to propose teams. The member currently proposing is the dictator and gets to form their team without taking into consideration any other user's preferences. Then the next dictator gets to go until all the members have teams.
<h5>Heuristics Approach</h5>
<p>The proposer invites their best available options to join their team. If the average of the available options for the user being invited is better than the team being proposed, that user declines the offer. If all players agree to the team, the team is formed and the next player still teamless proposes a team. Users take turns proposing teams for a finite number of rounds.</p>
<h5>Rotational Proposer Mechanism</h5>


<h2>Support</h2>
Contact Aditya Gokhale (aditya.p.gokhale@vanderbilt.edu) or Joshua Stafford (joshua.o.stafford@vanderbilt.edu) with any questions about this project.

<b>Extra Files</b>
- Procfile: used for hosting with Heroku (Needed for Django Application)
- System.properties: used for hosting with Heroku (Needed for Java Runtime Environment)
- requirements.txt: Python dependencies for running the application

