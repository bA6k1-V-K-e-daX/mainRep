# app/grps/test_client.py
import grpc
from app.grps.protos import detector_pb2, detector_pb2_grpc
def print_detection_response(response: 'detector_pb2.DetectionResponse') -> None:
    """
    Выводит все поля DetectionResponse в удобочитаемом формате.
    Полезно для отладки или логирования.
    """
    print("=" * 50)
    print("📄 DETECTION RESPONSE DETAILS")
    print("=" * 50)
    print(f"Query ID:        {response.query_id}")
    print(f"Result Path:     {response.result_path}")
    print(f"Success:         {response.success}")

    if not response.success:
        print(f"Error Message:   {response.error_message}")
    else:
        print(f"Total Objects:   {response.total_objects}")
        print("Class Counts:")
        if response.class_counts:
            for item in response.class_counts:
                print(f"  - {item.class_name}: {item.count}")
        else:
            print("  (no objects detected)")

    print("=" * 50)
def main():
    # Подключаемся к серверу
    channel = grpc.insecure_channel('localhost:50051')
    stub = detector_pb2_grpc.DetectorStub(channel)

    # Параметры запроса
    query_id = 3
    dir_path = "volume"  # ← замените на реальный путь к папке или файлу!
    targets = []       # ← классы, которые нужно искать (оставьте [] для всех)

    # Формируем запрос
    request = detector_pb2.DetectionRequest(
        query_id=query_id,
        dir_path=dir_path,
        targets=targets
    )

    print(f"📤 Отправляю запрос:")
    print(f"   query_id: {request.query_id}")
    print(f"   dir_path: {request.dir_path}")
    print(f"   targets:  {list(request.targets)}")

    try:
        response = stub.ImageDetection(request)
        
        if response.success:
            print_detection_response(response)
        else:
            print(f"\n❌ Ошибка: {response.error_message}")
            
    except grpc.RpcError as e:
        print(f"\n❌ gRPC ошибка: {e.code().name} — {e.details()}")
    finally:
        channel.close()

if __name__ == '__main__':
    main()