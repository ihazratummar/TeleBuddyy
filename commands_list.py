from commands.utils import Utils
from commands.general_commnads import General
from functools import partial


def get_handlers(database, commands):
    general = General(db=database)
    utils = Utils()
    commands = [
        ("start", partial(utils.start)),
        ("calculate_age", partial(utils.calculate_age)),
        ("echo", partial(utils.echo)),
        ("quotes", partial(general.quotes)),
        ("weather", partial(general.weather)),
        ("joke", partial(general.joke)),
        ("facts", partial(general.facts)),
        ("reminder", partial(general.reminder)),
        ("poll", partial(general.poll)),
        ("todo", partial(general.todo)),
        ("todo_list", partial(general.todo_list)),
        ("complete_todo", partial(general.complete_todo)),
        ("delete_todo", partial(general.delete_todo)),
        ("define", partial(general.define)),
        ("help", partial(utils.help))
    ]

    button_handles = [
        partial(general.poll_button)
    ]

    return commands, button_handles