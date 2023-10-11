from callable_tracing import callable_tracer
from sys import settrace


class David:
    def plays_video_games(self):
        return True

    def watches_movies(self):
        return True

    def return_name(self):
        return "David"


david = David()


def who_is_this(person: David, age=53):
    return person


# set tracing function
settrace(callable_tracer)

who_is_this(david)
