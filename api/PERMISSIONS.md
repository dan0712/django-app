# Permissions

To set permisions for api views/viewsets the next custom Django Rest Framework 
permission classes are used.

**Non-object oriented classes**  
```python
IsClient
IsAdvisor
IsAdvisorManager
...
```

**Object-oriented classes**  
Could be used for non-object oriented endpoints/methods (such as "list" or "create"),
they are just passed in that case.
```python
...should be created. example:
IsMyAdvisorCompany
...
```

**Object-oriented classes with custom objects**  
Used for custom objects (that cannot be fetched by self.get_object). Such objects
should be get and passed to permission class explicitly in viewset get_permission method 
(but some of them, such as IsMyAdvisorCompanyNestedInit, could be set usual way).
```python
...should be created. example:
IsMyAdvisorCompanyCustomInit(object)
...
```
