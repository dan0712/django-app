# Activity

Actions are managed by open source package
that is based on ([ActivityStrea.ms](http://activitystrea.ms/specs/atom/1.0/)),
well-elaborated format to handle complex and multi-purposed action logs. 
Format is so powerfull, that it perfectly handle actions with all possibly 
needed relation objects, such as who acts (`actor`), who is acted (`target`),
what else (`action_object`). 

For example, action record can carry information
for: advisor (`actor`) sends document (`action_object`)
to client (`target`) to be signed (`verb`). 
It lets easily to notify users and call them to action in response. 
More general descriptions and examples could be found in the package 
[readme](https://github.com/django-notifications/django-notifications).


### Examples

**Create action/notification record**  
```python
@receiver(user_logged_in)
def advisor__user_logged_in__test(sender, user, request, **kwargs):
    if hasattr(user, 'advisor'):
        notify.send(user.advisor, recipient=user, verb='logged in')

```

**Create abstract action with "full" payload**  
```python
notify.send(
  follow_instance.user,
  recipient=follow_instance.follow_object,
  verb=u'has followed you',
  action_object=instance,
  description=u'',
  target=follow_instance.follow_object,
  level='success', # by default 'info'
)
```


[RESERVED]  
**Api response with the list of actions**  
/api/me/activity  
```js
"data": {
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 11,
      "level": "warn",
      "unread": true,
      "actor_object_id": "11",
      "verb": "out of balance. do something",
      "description": null,
      "target_object_id": null,
      "action_object_object_id": null,
      "timestamp": "2015-11-28T04:31:29.869705Z",
      "public": true,
      "deleted": false,
      "emailed": false,
      "data": null,
      "recipient": 11,
      "actor_content_type": 5,
      "target_content_type": null,
      "action_object_content_type": null
    },
    {
      "id": 1,
      "level": "info",
      "unread": true,
      "actor_object_id": "11",
      "verb": "was saved",
      "description": null,
      "target_object_id": null,
      "action_object_object_id": null,
      "timestamp": "2015-11-28T04:31:28.059969Z",
      "public": true,
      "deleted": false,
      "emailed": false,
      "data": null,
      "recipient": 11,
      "actor_content_type": 24,
      "target_content_type": null,
      "action_object_content_type": null
    }
  ]
}
```
