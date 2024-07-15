from typing import TypedDict, Set, List

from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import SwitchTo, ScrollingGroup, Select, Cancel, Group, Back, Button
from aiogram_dialog.widgets.text import Const, Format

from src.db.database import add_link, get_links, delete_link, update_link, get_tags


class GetLinksStateGroup(StatesGroup):
    choose_tag = State()

    show_links = State()
    show_link = State()

    edit_link = State()
    link_edited = State()

    delete_link = State()
    link_deleted = State()


class TagsWindowGetterData(TypedDict):
    tags: List[tuple[int, str]]


class LinksWindowGetterData(TypedDict):
    links: List[tuple[int, dict]]


class LinkWindowGetterData(TypedDict):
    url: str
    description: str
    tag: str


async def tags_getter(dialog_manager: DialogManager, **_) -> TagsWindowGetterData:
    tags = await get_tags()
    dialog_manager.dialog_data["tags"] = tags
    tags = [(element["id"], element["name"]) for element in tags]
    dialog_manager.dialog_data["tags"] = tags
    return TagsWindowGetterData(tags=tags)


async def tag_selected(query: CallbackQuery, widget: Select, dialog_manager: DialogManager, tag_id: int):
    links = await get_links(int(tag_id))
    dialog_manager.dialog_data["links"] = links
    await dialog_manager.switch_to(GetLinksStateGroup.show_links)


async def links_getter(dialog_manager: DialogManager, **_) -> LinksWindowGetterData:
    return LinksWindowGetterData(links=(dialog_manager.dialog_data["links"]))


async def link_selected(query: CallbackQuery, widget: Select, dialog_manager: DialogManager, link_: str):
    for link in dialog_manager.dialog_data["links"]:
        if link["url"][:25] == link_:
            dialog_manager.dialog_data["link"] = link
            await dialog_manager.switch_to(GetLinksStateGroup.show_link)


async def link_data_getter(dialog_manager: DialogManager, **_) -> LinkWindowGetterData:
    tag = await get_tags(dialog_manager.dialog_data["link"]["tag_id"])
    tag_name = tag[0]["name"]
    return LinkWindowGetterData(
        url=dialog_manager.dialog_data["link"]["url"],
        description=dialog_manager.dialog_data["link"]["description"],
        tag=tag_name,
    )


async def on_edit_link(
        message: Message,
        widget: ManagedTextInput[str],
        dialog_manager: DialogManager,
        description: str):
    await update_link(
        link_id=dialog_manager.dialog_data["link"]["id"],
        description=description
    )
    await dialog_manager.switch_to(GetLinksStateGroup.link_edited)


async def on_delete_link(query: CallbackQuery, widget: Button, dialog_manager: DialogManager, **_):
    await delete_link(dialog_manager.dialog_data["link"])
    await dialog_manager.switch_to(GetLinksStateGroup.link_deleted)


get_links_window = Dialog(
    Window(
        Const("Выберите тег"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                item_id_getter=lambda item: item[0],
                on_click=tag_selected,
                items="tags",
                id="tags"
            ),
            id="select_tag",
            width=3,
            height=2,
        ),
        Cancel(Const("Назад")),
        getter=tags_getter,
        state=GetLinksStateGroup.choose_tag,
        parse_mode=ParseMode.MARKDOWN
    ),
    Window(
        Const("Выберите ссылку"),
        ScrollingGroup(
            Select(
                Format("{item[url]}"),
                item_id_getter=lambda item: item["url"][:25],
                on_click=link_selected,
                items="links",
                id="links"
            ),
            id="select_link",
            width=1,
            height=10,
        ),
        Cancel(Const("Назад")),
        getter=links_getter,
        state=GetLinksStateGroup.show_links,
        parse_mode=ParseMode.MARKDOWN
    ),
    Window(
        Format(
            "Ссылка: {url}\n"
            "Описание: {description}\n"
            "Тэг: {tag}\n"
        ),
        Group(
            SwitchTo(
                text=Const("Редактировать"),
                id="edit_selected_link",
                state=GetLinksStateGroup.edit_link
            ),
            Button(
                text=Const("Удалить"),
                id="delete_selected_link",
                on_click=on_delete_link
            ),
            Back(Const("Назад")),
            width=2
        ),
        getter=link_data_getter,
        state=GetLinksStateGroup.show_link
    ),
    Window(
        Const("Ссылка успешно удалена!"),
        Cancel(Const("Назад")),
        state=GetLinksStateGroup.link_deleted
    ),
    Window(
        Const("Введите новое значение описания"),
        TextInput(
            id="edit_selected_link",
            on_success=on_edit_link
        ),
        state=GetLinksStateGroup.edit_link
    ),
    Window(
        Const("Ссылка успешно изменена!"),
        Cancel(Const("Назад")),
        state=GetLinksStateGroup.link_edited
    ),
)
