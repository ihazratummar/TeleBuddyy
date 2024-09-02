import commands.utils as utils
from commands.general_commnads import General
from functools import partial


def get_handlers(database):
    general = General(db=database)

    commands = [
        ("quotes", partial(general.quotes)),
        ("weather", partial(general.weather)),
        ("joke", partial(general.joke)),
        ("facts", partial(general.facts)),
        ("reminder", partial(general.remind)),
        ("poll", partial(general.poll)),
        ("todo", partial(general.todo)),
        ("todo_list", partial(general.todo_list)),
        ("complete_todo", partial(general.complete_todo)),
        ("delete_todo", partial(general.delete_todo))
    ]

    button_handles = [
        partial(general.poll_button)
    ]

    return commands, button_handles