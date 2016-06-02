# User account management

User model/profiles management based on conventional Django/Userena approach. 
We have one common user model with different related profiles for each user type. 
That's the way Django and Userena recommend to do it. 
That approach let's to use all standard Django, Userena and DRF authentication 
features, without workarounds and so on. 


## User types 
User type (also could be called "profile") defined and assigned by adding user
to the correspoding user group (standard Django Group model).  

Using custom helpers, it looks like that:

```sh
# add and remove user to group (aka assign user type)
user.groups_add(User.GROUP_ADVISOR)
user.groups_remove(User.GROUP_CLIENT)
```

To manage available user types check this self-explaind module: ``account/models.py`` 
and update it to add/remove/change user types and related helper functions.
Don't forget also to add new user profile model (see below).



## User profiles
User have one default profile (Userena requires that) and extra optinal profiles 
for user types (Advisor, Invesor, ...). After setting user type (see above),
user profile object will be created automatically.

Use this example to add new user profile models 
(it's assumed that the corresponding user type is also creted - see above):
```sh
# advisor.models
class Advisor(models.Model):
    user = models.OneToOneField(User, related_name='advisor')
```



## Working with user types/profiles 
Please, check the snipppets:
```sh
# to check user type in a view
user = self.request.user
if user.is_advisor:
    print "Look Ma, I'm advisor"

# access to profile from user and back
user = self.request.user
if user.is_advisor:
    advisor = user.advisor
    user = advisor.user
```
