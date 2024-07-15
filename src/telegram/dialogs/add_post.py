import re
from typing import TypedDict

from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import SwitchTo, Back, Cancel, Group
from aiogram_dialog.widgets.text import Const, Format

from src.db.database import add_link, add_tag


class AddLinkStateGroup(StatesGroup):
    add_url = State()
    add_description = State()
    add_tag = State()
    done = State()


class LinkWindowGetterData(TypedDict):
    url: str
    description: str | None
    tag_id: str | None


class MessageWindowGetterData(TypedDict):
    message: str


async def on_input_add_url_success(
        message: Message,
        widget: ManagedTextInput[str],
        dialog_manager: DialogManager,
        url: str):
    if re.match(r"^https?://", url) is None:
        await message.answer(
            "URL-адрес должен начинаться с *http://* или *https://*",
            parse_mode=ParseMode.MARKDOWN
        )
        await dialog_manager.switch_to(AddLinkStateGroup.add_url)
    else:
        dialog_manager.dialog_data["url"] = url.lower()
        await dialog_manager.switch_to(AddLinkStateGroup.add_description)


async def on_input_add_description_success(
        message: Message,
        widget: ManagedTextInput[str],
        dialog_manager: DialogManager,
        description: str):
    dialog_manager.dialog_data["description"] = description
    await dialog_manager.switch_to(AddLinkStateGroup.add_tag)


async def on_input_add_tag_success(
        message: Message,
        widget: ManagedTextInput[str],
        dialog_manager: DialogManager,
        tag: str):
    if not tag.startswith("#"):
        await message.answer("Тег должен начинаться со знака *#*", parse_mode=ParseMode.MARKDOWN)
        await dialog_manager.switch_to(AddLinkStateGroup.add_tag)
    else:
        dialog_manager.dialog_data["tag"] = tag.lower()
        await dialog_manager.switch_to(AddLinkStateGroup.done)
        tag_id = await add_tag(tag)
        await add_link(
            LinkWindowGetterData(
                url=dialog_manager.dialog_data["url"],
                description=dialog_manager.dialog_data.get("description", ""),
                tag_id=tag_id,
            )
        )


async def message_getter(dialog_manager: DialogManager, **_):
    message = (f'Отлично! Ваша ссылка добавлена в базу данных!\n\n'
               f'Ссылка: {dialog_manager.dialog_data.get("url", "")}\n'
               f'Описание: {dialog_manager.dialog_data.get("description", "Отсутствует")}\n'
               f'Тег: {dialog_manager.dialog_data.get("tag", "Отсутствует")}'
               )
    return MessageWindowGetterData(
        message=message
    )


add_link_dialog = Dialog(
    Window(
        Const("Ведите ссылку"),
        TextInput(
            id="add_url_input",
            on_success=on_input_add_url_success
        ),
        Cancel(Const("Назад")),
        state=AddLinkStateGroup.add_url,
    ),
    Window(
        Const("Введите описание"),
        Group(
            SwitchTo(
                Const("Пропустить"),
                id="switch_to_add_tag",
                state=AddLinkStateGroup.add_tag
            ),
            Back(Const("Назад")),
            width=2
        ),
        TextInput(
            id="add_description_input",
            on_success=on_input_add_description_success
        ),
        state=AddLinkStateGroup.add_description,
    ),
    Window(
        Const("Введите тег"),
        TextInput(
            id="add_tag_input",
            on_success=on_input_add_tag_success
        ),
        state=AddLinkStateGroup.add_tag
    ),
    Window(
        Format("{message}"),
        Cancel(Const("Назад")),
        getter=message_getter,
        state=AddLinkStateGroup.done
    )
)
