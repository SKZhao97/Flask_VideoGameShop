# VideoGameShoppingApp

Distributed System Programming Assignment #1

## Video Game Shop based on Flask and Google Datastore

### Project Structure:
- /Static: including js file, css file and favicon.
- /templates: including all html files, based on base.html to extend
- main.py: define all the routers and middlewares
- app.yaml: configuration 

### Features:
- REST-ful implementation
- Use **Google Cloud Platform Datastore** as storage
- Use **Google Oauth2** to implement user authentication to login and logout
- Show video games in **generes** respectively
- Add video games with properties of *titel, RSDB rating, platform, developer, year of release* and *price*, also support genre adding
- Search vidoe games in specific genere with any one or combinations of the properties
- **Case insensitive** and **err-input handling**
- Returning to the homepage or other pages conveniently
- Navigation bar added and basic styling using Bootstrap
- Faiure search or unauthorized access notification
- Implemented cart operations, such as *add to cart* and *remove*
- Implemented **checkout** operations
- Maintaining the **cart** list and **purchase history** list for specific user
- Deploy on **Google Cloud Platform AppEngine**

### Run:
1. To run locally: first open the /templates/index.html file, comment out the line24 and cancell the comment of line23, and then type in terminal:

  $ cd videoGameShopApp  
  $ pip install --upgrade google-cloud-datastore (Optional)  
  $ pip install --upgrade google-api-python-client(Optional)  

  $ export GOOGLE_APPLICATION_CREDENTIALS="[Path to the account .json file]/[projectCredentials].json"  
  $ python3 main.py  

then visit http://localhost:8080

2. To visit on cloud: visit http://video-game-shop-sikai-zhao.appspot.com/
3. To deploy on cloud: first confirm the line24 is using rather than line23 in /templates/index.html. Then run:
$ gcloud app deploy
input y when prompt if continue.

