django-choicer
=============================

.. image:: https://travis-ci.org/tonimichel/django-choicer.svg?branch=master
    :target: https://travis-ci.org/tonimichel/django-choicer

Simplify dealing with (large) choices.

Getting started
----------------

models:

..code-block:: python

    from django.db import models
    import choicer

    sub_choicer = choicer.Choicer([
        dict(
            name='started',
            value=0,
            verbose_name='Approved'
        ),
        dict(
            name='inprogress',
            value=1,
            verbose_name='In progress'
        ),
        dict(
            name='completed',
            value=2,
            verbose_name='Completed'
        ),
        dict(
            name='approved',
            value=3,
            verbose_name='Approved'
        ),
        dict(
            name='dismissed',
            value=4,
            verbose_name='Dismissed'
        ),
        dict(
            name='wartinglist',
            value=5,
            verbose_name='On waiting list'
        ),
    ])

    @subscription_choicer.apply(field_name='state')
    class Subscription(models.Model):
        # some fields
        state = models.IntegerField(choices=sub_choicer.get_choices())


After we defined our model and applied our choicer, we now want to play with the api:

code::

    s = Subscription()
    s.set_state_started()
    s.save()

    print(s.is_state_started())
    # True

    s.set_state_inprogress()
    print(s.is_state_approved())
    # False
    print (s.is_state_started())
    # True

    choice = s.STATE_CHOICER.get_by_name('dismissed')
    print(choice)
    # {'name': 'dismissed', 'value': 4, verbose_name='Dismissed'}

    choice = s.STATE_CHOICER.get_by_value(5)
    print(choice)
    # {'name': 'waitinglist', 'value': 5, verbose_name='On waiting list'}

    s.set_state_waitinglist()
    print(s.state)
    # 5
    print(s.get_state())
    # {'name': 'waitinglist', 'value': 5, verbose_name='On waiting list'}







Installation
----------------

code::

    pip install git+https://github.com/tonimichel/django-choicer.git

As django-choicer neither provides models, nor templates, nor static files we dont
neet to add it to our project's INSTALLED_APPS.


Motivation
---------------

Sometimes models need to provide a large set of choices.
This may bring the following issues to deal with:

* Querying
Actually we dont want to query our model by integer or string values which are not human-readable.
So, instead of doing

code:: python

    MyModel.objects.filter(type=0)

its better to do something like this

code:: python
    MyModel.objects.filter(state=STATES.approved)

Furthermore it is sometimes necessary to provide instance methods that check for a certain model state.
So instead of doing

code:: python

    if obj.state == 0:
        # do something

or a little better

    if obj.state == STATES.approved

we actually want to do

code:: python

    if obj.is_state_approved():
        pass

which is the way to go as our model provide an explicit api check for a given state.
Considering assignment of a choice, we got similar issues:

code::

    obj.state = 0

is worse than

    obj.state = STATES.approved

But what we actually want to do is

code::

    obj.set_state_approved()

So, now imagine the following scenario.
We got 8 different choices, so the naive way of checkin against the integers or strings defined in our choices
is inacceptable. But also the way of constructing a "STATE" class for doing enum-like checks (``obj.state == STATES.approved``)
is no that cool, as we actually want to do ``obj.is_state_approved``. But, it would also be totally unacceptable to
write 8 getters and 8 setters each providing the same code, especially when we need to change the naming of a choice
during early development, which actually happend quite often after Phil Karlton's
"There are only two hard things in Computer Science: cache invalidation and naming things".
