import os

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session


# Переименовать файл
router_rename_file_read = APIRouter(
    prefix="/v1/RenameFileReader",
    tags=["Reader"]
)


@router_rename_file_read.post("/")
async def rename_file_read(data: dict, session: AsyncSession = Depends(get_async_session)):

    print(f'{data=}')

    old_file_name: str = data["old_file_name"]
    new_file_name: str = data["new_file_name"]
    path: str = data["path"]

    if new_file_name == '':
        return {
            "status": "error",
            "data": None,
            "details": "Новое название файла не предоставлено"
        }

    try:
        # Обработанный файл переименовывается в соответствии с извлеченной информацией
        file_oldname = os.path.join(path, old_file_name)

        # Для ФНС
        file_newname = os.path.join(path, new_file_name)

        os.rename(file_oldname, file_newname)

        base_name = os.path.basename(file_newname)
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f'Не удалось изменить название файла. {ex}'
        }

    return {
        'status': 'success',
        'data': None,
        'details': f'Файл переименован. Новое имя файла {base_name}'
    }
