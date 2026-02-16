# app/grps/server.py
import os
import logging
from pathlib import Path
from concurrent import futures
from app.scenaries.detect_image import detect_image
from app.core.di_container import ServiceContainer
from app.utils.names_to_ids import class_names_to_ids
import grpc

# Импортируем сгенерированные protobuf-модули
from app.grps.protos import detector_pb2, detector_pb2_grpc

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DetectorService(detector_pb2_grpc.DetectorServicer):
    """Реализация сервиса Detector из обновлённого detector.proto"""

    def __init__(self):
        container = ServiceContainer()
        self.model_loader = container.model_loader
        logger.info("DetectorService initialized")

    def ImageDetection(self, request: detector_pb2.DetectionRequest, context) -> detector_pb2.DetectionResponse:
        """
        Новая реализация метода:
        - Принимает query_id, dir_path, targets
        - Запускает детекцию по директории (или файлу)
        - Возвращает result_path, query_id, статистику и статус
        """
        query_id = int(request.query_id)
        dir_path = request.dir_path
        targets = list(request.targets)  # repeated string → list[str]

        logger.info(f"[Query {query_id}] Received detection request: dir_path={dir_path}, targets={targets}")

        # === Валидация входных данных ===
        if not dir_path:
            return self._error_response(query_id, "dir_path cannot be empty")

        if not os.path.exists(dir_path):
            return self._error_response(query_id, f"Path does not exist: {dir_path}")

        # === Подготовка путей для чтения и сохранения результатов ===
        results_base = Path(request.dir_path)
        source_path = str(results_base / "detect" / f"query_{query_id}" / "source")
        save_path = str(results_base / "detect" / f"query_{query_id}" / "result")

        try:
            model = self.model_loader.get_model()
            target_ids = class_names_to_ids(targets) if targets else None

            detection_result = detect_image(source_path=source_path,
                                            save_path=save_path,
                                            target_ids=target_ids,
                                            min_confidence=0.5,
                                            model=model)

            # === Формирование ответа ===
            class_counts = []
            for cls, count in detection_result.items():
                # Приводим count к int, даже если он numpy
                class_counts.append(
                    detector_pb2.ClassCount(class_name=cls, count=int(count))
                )

            total_objects = int(sum(detection_result.values()))

            logger.info(f"[Query {query_id}] Detection successful. Found {total_objects} objects. Results saved to {save_path}")

            return detector_pb2.DetectionResponse(query_id=query_id,
                                                  result_path=save_path,
                                                  success=True,
                                                  class_counts=class_counts,
                                                  total_objects=total_objects)

        except Exception as e:
            logger.exception(f"[Query {query_id}] Error during detection")
            return self._error_response(query_id, f"Detection failed: {str(e)}")

    @staticmethod
    def _error_response(query_id: int, message: str) -> detector_pb2.DetectionResponse:
        """Вспомогательный метод для формирования ошибки с query_id"""
        logger.error(f"[Query {query_id}] Returning error: {message}")
        return detector_pb2.DetectionResponse(
            query_id=query_id,
            result_path="",
            success=False,
            error_message=message,
            total_objects=0
        )

def serve(port: int = 50051) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    detector_pb2_grpc.add_DetectorServicer_to_server(DetectorService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"Detector gRPC server started on port {port}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()