# app/grps/test_client.py
import grpc
from app.grps.protos import detector_pb2, detector_pb2_grpc


def print_detection_response(response: "detector_pb2.DetectionResponse") -> None:
    """
    Выводит все поля DetectionResponse в удобочитаемом формате
    с учётом новой схемы: instance_info + bbox.
    """
    print("=" * 50)
    print("📄 DETECTION RESPONSE DETAILS")
    print("=" * 50)
    print(f"Query ID:        {response.query_id}")
    print(f"Result Path:     {response.result_path}")
    print(f"Success:         {response.success}")

    if not response.success:
        print(f"Error Message:   {response.error_message}")
        print("=" * 50)
        return

    print(f"Total Objects:   {response.total_objects}")

    # Детальная информация по каждому найденному объекту
    print("\nInstances:")
    if response.instance_info:
        for idx, inst in enumerate(response.instance_info, start=1):
            bbox_str = (
                f"[{', '.join(f'{v:.2f}' for v in inst.bbox)}]"
                if inst.bbox
                else "[]"
            )
            print(
                f"  #{idx}: class={inst.class_name}, "
                f"confidence={inst.confidience}, "
                f"bbox={bbox_str}"
            )
    else:
        print("  (no instance_info entries)")

    print("=" * 50)

def main():
    # Подключаемся к серверу
    channel = grpc.insecure_channel('localhost:50051')
    stub = detector_pb2_grpc.DetectorStub(channel)

    # Параметры запроса
    query_id = 3
    dir_path = "volume" # ← замените на реальный путь к папке или файлу!
    prompt = "Пропеллер, физюляж, рама, крыло"

    # Формируем запрос
    request = detector_pb2.DetectionRequest(
        query_id=query_id,
        dir_path=dir_path,
        prompt=prompt,
    )

    print(f"📤 Отправляю запрос:")
    print(f"   query_id: {request.query_id}")
    print(f"   dir_path: {request.dir_path}")
    print(f"   prompt:   {request.prompt}")

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
