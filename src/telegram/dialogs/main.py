from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Start, Group
from aiogram_dialog.widgets.text import Const

from src.telegram.dialogs.add_post import AddLinkStateGroup
from src.telegram.dialogs.get_posts import GetLinksStateGroup


class MainStateGroup(StatesGroup):
    main = State()


main_window = Dialog(
    Window(
        Const(
            "Добро пожаловать!\n"
            "Я бот, который поможет вам удобно хранить ваши ссылки.\n"
            "Чтобы добавить ссылку, воспользуйтесь командой /add или кнопкой ниже"),
        Group(
            Start(
                Const("Добавить ссылку"),
                id="start_add_link",
                state=AddLinkStateGroup.add_url,
            ),
            Start(
                Const("Посмотреть ссылки"),
                id="start_get_links",
                state=GetLinksStateGroup.choose_tag
            ),
            width=2
        ),
        state=MainStateGroup.main,
        parse_mode="Markdown",
    )
)
