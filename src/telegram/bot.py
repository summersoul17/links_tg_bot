import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, setup_dialogs

from src.config import settings
from src.telegram.dialogs.get_posts import get_links_window
from src.telegram.dialogs.main import MainStateGroup, main_window
from src.telegram.dialogs.add_post import AddLinkStateGroup, add_link_dialog

logger = logging.getLogger(__name__)

storage = MemoryStorage()

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN_)
dp = Dispatcher(storage=storage)
dp.include_router(add_link_dialog)
dp.include_router(main_window)
dp.include_router(get_links_window)
setup_dialogs(dp)


@dp.message(CommandStart())
async def start(_: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainStateGroup.main, mode=StartMode.RESET_STACK)


@dp.message(Command("add"))
async def add(_: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AddLinkStateGroup.add_url, mode=StartMode.RESET_STACK)
