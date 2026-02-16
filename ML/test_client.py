# app/grps/test_client.py
import grpc
from app.grps.protos import detector_pb2, detector_pb2_grpc

def main():
    # Подключаемся к серверу
    channel = grpc.insecure_channel('localhost:50051')
    stub = detector_pb2_grpc.DetectorStub(channel)

    # Параметры запроса
    query_id = 3
    dir_path = "volume"  # ← замените на реальный путь к папке или файлу!
    targets = ['bus','apple']       # ← классы, которые нужно искать (оставьте [] для всех)

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
            print("\n✅ Успех!")
            print(f"   query_id:     {response.query_id}")
            print(f"   result_path:  {response.result_path}")
            print(f"   Всего объектов: {response.total_objects}")
            for item in response.class_counts:
                print(f"   • {item.class_name}: {item.count}")
        else:
            print(f"\n❌ Ошибка: {response.error_message}")
            
    except grpc.RpcError as e:
        print(f"\n❌ gRPC ошибка: {e.code().name} — {e.details()}")
    finally:
        channel.close()

if __name__ == '__main__':
    main()