# RevUp
[visit RevUp online!](https://revup.onrender.com/)

## Important Models
- User: An account created by a user which has a location, username, email, and password.
- Meet: A meet has a location, a title, a description, and a datetime as well as an association with the user who created it.
- Car: A car has a year, make, and model. Cars can be added to a users "garage" so that users can use them to rsvp to meets.
- RSVP: An RSVP allows a user to state that they are attending a meet and add which car they are bringing.

## Main pages/routes
- /: The homepage, this page will show 50 of the most recent meets within 50 miles of the users location; if not location is set it will show all meets on the site.
- /users/user-id: This will show a users info inluding their location, username, garage, meets attended, and meets created. If the user is on their own page it will allow then to edit their profile, delete their profile, and add/remove cars from their garage.
- /meets/meet-id: This page will show the meet with the id specified. It will show the title, who made the meet, the description, the address, the date, the users attending as well as their cars being brought, and a map showing the address which is generated using the mapquest api.
- /meets/search: This page allows the user to search for meets within a specific range of their area or view all meets.

## User Flows
Typically a user flow will look like this for a first time user:   
1. User visits homepage which will prompt them to make an account, which they click the link.   
2. User fills out the form and is redirected to the homepage which will show them meets within 50 miles of their area.  
3. User will then click on their profile to view their info.  
4. User will add their cars to their garage.  
5. User will visit the search meets page which they will use to search for meets in their range.  
6. User finds a meet which fits their personal criteria and clicks the meet link.  
7. The user looks over the info and rsvps to the meet with their car of choice.

## API
For this project I used the mapquest api for multiple implementations.

- The signup page as well as the edit profile page have an input for a location. This input will suggest options based on what the user has typed so far. This is done using the mapquest api which uses the users already typed characters to determine what is being typed and returns suggestions.
- On the create and edit meets pages there is an input for an address this uses the mapquest api in a similar manner as the location input on the user pages except it requests addresses from the api instead of cities, states, areas, etc.
- The api is also used in the get_meets_in_range function. The api is used to get the distance from the users location a meet is which is used to determine whether to display it to the user.
- The final usage of the api is in order to get a map showing where the location is to display on the meet info page.

## Tech Stack
-Frontend: Javascript, Html, CSS, JQuery, axios
-Backend: Python, Flask, Jinja, WTForms, SQLAlchemy, Postgresql
-Tools: git, GitHub, VSCode
