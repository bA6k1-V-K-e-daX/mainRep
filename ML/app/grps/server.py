# app/grps/server.py
import os
import logging
from concurrent import futures
from app.scenaries.detect_image import detect_image
from app.core.di_container import ServiceContainer
import grpc
from app.core.coco_classes import COCO_CLASS_NAMES_TO_IDS

# Импортируем сгенерированные protobuf-модули
from app.grps.protos import detector_pb2, detector_pb2_grpc

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DetectorService(detector_pb2_grpc.DetectorServicer):
    """Реализация сервиса Detector из detector.proto"""

    def __init__(self):
        container = ServiceContainer()
        self.model_loader = container.model_loader
        logger.info("DetectorService initialized")
        
    def ImageDetection(self, request: detector_pb2.DetectionRequest, context) -> detector_pb2.DetectionResponse:
        """
        Реализация метода ImageDetection согласно контракту.
        Валидирует запрос, эмулирует детекцию объектов и возвращает структурированный ответ.
        """
        image_path = request.image_path
        target_classes = request.target_classes
        min_confidence = request.min_confidence
        logger.info(f"Received detection request: image_path={image_path}, "
                    f"target_classes={target_classes}, min_confidence={min_confidence}")
       
        # Валидация входных данных
        if not image_path:
            return self._error_response("Image path cannot be empty")

        if not os.path.exists(image_path):
            return self._error_response(f"File not found: {image_path}")

        if not (0.0 <= min_confidence <= 1.0):
            return self._error_response(f"min_confidence must be between 0.0 and 1.0, got {min_confidence}")
        
        try:
            target_ids = self._class_names_to_ids(target_classes)
            model = self.model_loader.get_model()
            result = detect_image(image_path=image_path,min_confidence=min_confidence,target_ids=target_ids, model=model)

            #Приведение к полям response
            class_counts = [
                detector_pb2.ClassCount(class_name=cls_name, count=count)
                for cls_name, count in result.items()
            ]

            total = sum(result.values())

            logger.info(f"Detection successful: found {total} objects")

            return detector_pb2.DetectionResponse(
                success=True,
                class_counts=class_counts,      # ← список объектов ClassCount
                total_objects=total
            )
            
        except Exception as e:
            logger.exception("Error during detection")
            return self._error_response(f"Detection failed: {str(e)}")

    @staticmethod
    def _error_response(message: str) -> detector_pb2.DetectionResponse:
        """Вспомогательный метод для формирования ошибки"""
        logger.error(f"Returning error: {message}")
        return detector_pb2.DetectionResponse(
            success=False,
            error_message=message,
            total_objects=0
        )


    def _class_names_to_ids(self,target_classes):
        """
        Преобразует список имён классов в список ID классов COCO.
        
        Args:
            target_classes (List[str]): Список имён классов, например ["bus", "car"]
            
        Returns:
            List[int]: Список ID, например [5, 2]
            None: если target_classes пустой или None
        """
        if not target_classes:
            return None
        
        class_ids = []
        for cls_name in target_classes:
            if cls_name in COCO_CLASS_NAMES_TO_IDS:
                class_ids.append(COCO_CLASS_NAMES_TO_IDS[cls_name])
            else:
                # Опционально: можно игнорировать неизвестные классы
                # или вызывать ошибку — здесь просто пропускаем
                pass
        
        return class_ids if class_ids else None


def serve(port: int = 50051) -> None:
    """
    Запуск gRPC сервера
    
    Args:
        port: Порт для прослушивания (по умолчанию 50051)
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    detector_pb2_grpc.add_DetectorServicer_to_server(DetectorService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"Detector gRPC server started on port {port}")
    server.wait_for_termination()
if __name__ == '__main__':
    serve()