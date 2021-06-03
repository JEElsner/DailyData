if __name__ == '__main__':
    # Redirect the execution of the module to to the entry point for timelog
    # This will then parse system arguments and do magic in general
    from .timelog import timelog_entry_point

    timelog_entry_point()
