README
======

|ci| |cov|

.. |ci| image:: https://github.com/audrow/now-and-later/workflows/Continuous%20Integration/badge.svg
.. |cov| image:: https://codecov.io/gh/audrow/now-and-later/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/audrow/now-and-later

There are many things that I should do regularly (say, every two weeks) and it is hard to keep track of them: cleaning, calling loved ones, ect. My thinking is that I can commit to doing one of these actions a day and, if I do so, I won't have a backlog of them to do. Regular todo lists fail me here, as I can make repeating todos but several of them may be due at the same time and from there I must prioritize what to do. Also, the repeating todo interface is often cumbersome to work with, especially if you're not completing all of the events within the due date.

What I am aiming to make here is a way of prioritizing a repeated set of todos that takes into account how many items a user wants to do on any given day.  Items that are due but not completed will gradually have their priority increased so that they are recommended for completion sooner.

The intention is to take a list of todo list items, as well as some information about how frequently they should occur and their starting priority, and output a schedule for the todos that takes into account how many todo list items the user wants to complete on any given day.



