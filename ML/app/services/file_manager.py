import os
from pathlib import Path
from typing import List, Optional

class FileManager:
    """
    Работа с файлами через директории:
    - чтение всех (или N) файлов из папки
    - запись файлов в папку с автоматической нумерацией
    """

    def __init__(self):
        pass

    def read_from_dir(
        self,
        input_dir: str,
        max_files: Optional[int] = None,
        extensions: Optional[List[str]] = None
    ) -> List[bytes]:
        """
        Читает файлы из директории.
        
        Args:
            input_dir: Путь к входной директории
            max_files: Максимальное количество файлов для чтения (None = все)
            extensions: Список расширений для фильтрации, например ['.jpg', '.png']
            
        Returns:
            Список содержимого файлов в байтах [b'...', b'...', ...]
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Директория не найдена: {input_dir}")
        
        # Получаем все файлы (не папки)
        all_files = [f for f in input_path.iterdir() if f.is_file()]
        
        # Фильтруем по расширению (если указано)
        if extensions:
            ext_set = {ext.lower() for ext in extensions}
            all_files = [
                f for f in all_files
                if f.suffix.lower() in ext_set
            ]
        
        # Сортируем для предсказуемости
        all_files.sort()
        
        # Ограничиваем количество
        if max_files is not None:
            all_files = all_files[:max_files]
        
        # Читаем содержимое
        file_contents = []
        for file_path in all_files:
            with open(file_path, "rb") as f:
                file_contents.append(f.read())
        
        return file_contents

    def write_to_dir(
        self,
        output_dir: str,
        file_contents: List[bytes],
        base_name: str = "output",
        extension: str = ".bin"
    ) -> List[str]:
        """
        Записывает список файлов в директорию с автоматической нумерацией.
        
        Имена файлов: {base_name}_001{extension}, {base_name}_002{extension}, ...
        
        Args:
            output_dir: Путь к выходной директории
            file_contents: Список данных в байтах [b'...', b'...', ...]
            base_name: Базовое имя файла (по умолчанию "output")
            extension: Расширение (по умолчанию ".bin")
            
        Returns:
            Список путей сохранённых файлов
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        for i, data in enumerate(file_contents, start=1):
            # Формат: output_001.jpg, output_002.jpg, ...
            filename = f"{base_name}_{i:03d}{extension}"
            file_path = output_path / filename
            
            with open(file_path, "wb") as f:
                f.write(data)
            
            saved_paths.append(str(file_path.resolve()))
        
        return saved_paths