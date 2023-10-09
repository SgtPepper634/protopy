from typing import Protocol, runtime_checkable
from callable_tracing import callable_tracer
from sys import settrace

# @runtime_checkable
# class PlaysVideoGames(Protocol):
#   def plays_video_games(self):
#     ...

# @runtime_checkable
# class WatchesMovies(Protocol):
#   def watches_movies(self):
#     ...
 
class David:
  def plays_video_games(self):
    return True

  def watches_movies(self):
    return True

  def return_name(self):
    return 'David'


david = David()

def who_is_this(person: David, age=53):
  return person

# set tracing function
settrace(callable_tracer)

who_is_this(david)

