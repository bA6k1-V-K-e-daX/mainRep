# app/grps/server.py
import logging
from concurrent import futures
import grpc
from app.scenaries.detect_image import ImageDetectionUseCase

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
        logger.info("DetectorService initialized")
        self.image_detection_usecase = ImageDetectionUseCase()
    def ImageDetection(self, request: detector_pb2.DetectionRequest, context) -> detector_pb2.DetectionResponse:
        """
        Новая реализация метода:
        - Принимает query_id, dir_path, targets
        - Запускает детекцию по директории (или файлу)
        - Возвращает result_path, query_id, статистику и статус
        """
        query_id = int(request.query_id)
        dir_path = request.dir_path
        targets = list(request.targets) 

        logger.info(f"[Query {query_id}] Received detection request: dir_path={dir_path}, targets={targets}")

        try:
            save_path,detection_result = self.image_detection_usecase.execute(query_id=query_id,
                                                             dir_path=dir_path,
                                                             targets=targets,
                                                             min_confidence=0.5
                                                             )
            # === Формирование ответа ===
            class_counts = []
            for cls, count in detection_result.items():
                # Приводим count к int, даже если он numpy
                class_counts.append(
                    detector_pb2.ClassCount(class_name=cls, count=int(count))
                )
            total_objects = sum(detection_result.values())
            
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