# app/grps/test_client.py
import grpc
from app.grps.protos import detector_pb2, detector_pb2_grpc

def main():
    # Подключаемся к серверу
    channel = grpc.insecure_channel('localhost:50051')
    stub = detector_pb2_grpc.DetectorStub(channel)

    # Формируем запрос
    request = detector_pb2.DetectionRequest(
        image_path="data/test.jpg",          # ← замените на реальный путь к изображению!
        target_classes=None,
        min_confidence=0.5
    )

    print(f"📤 Отправляю запрос: {request.image_path}, ищу: {request.target_classes}")

    try:
        response = stub.ImageDetection(request)
        
        if response.success:
            print("✅ Успех!")
            print(f"   Всего объектов: {response.total_objects}")
            for item in response.class_counts:
                print(f"   • {item.class_name}: {item.count}")
        else:
            print(f"❌ Ошибка: {response.error_message}")
            
    except grpc.RpcError as e:
        print(f"❌ gRPC ошибка: {e.code().name} — {e.details()}")
    finally:
        channel.close()

if __name__ == '__main__':
    main()