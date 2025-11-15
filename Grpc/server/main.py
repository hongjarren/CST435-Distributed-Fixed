from concurrent import futures
import time
import grpc
import os


# generated modules (will be created during Docker build)
import compute_pb2
import compute_pb2_grpc


SERVICE_NAME = os.environ.get("SERVICE_NAME", "Unknown")
PORT = int(os.environ.get("PORT", "50051"))


class ComputeServicer(compute_pb2_grpc.ComputeServicer):
    """Service that implements the pipeline: Compute -> Transform -> Aggregate"""
    
    def Compute(self, request, context):
        """Service A: multiply input by 2"""
        work_ms = request.work_ms if request.work_ms else 0
        time.sleep(work_ms / 1000.0)
        
        # Compute: value * 2
        result = request.value * 2
        timestamp_ms = int(time.time() * 1000)
        
        return compute_pb2.ComputeResponse(
            result=result,
            service_name=SERVICE_NAME,
            timestamp_ms=timestamp_ms
        )
    
    def Transform(self, request, context):
        """Service B: add 10 to the computed value"""
        work_ms = request.work_ms if request.work_ms else 0
        time.sleep(work_ms / 1000.0)
        
        # Transform: computed_value + 10
        result = request.computed_value + 10
        timestamp_ms = int(time.time() * 1000)
        
        return compute_pb2.TransformResponse(
            result=result,
            service_name=SERVICE_NAME,
            timestamp_ms=timestamp_ms
        )
    
    def Aggregate(self, request, context):
        """Service C: multiply by 3 and return final result"""
        work_ms = request.work_ms if request.work_ms else 0
        time.sleep(work_ms / 1000.0)
        
        # Aggregate: transformed_value * 3
        result = request.transformed_value * 3
        timestamp_ms = int(time.time() * 1000)
        
        return compute_pb2.AggregateResponse(
            final_result=result,
            pipeline="A->B->C",
            timestamp_ms=timestamp_ms
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    compute_pb2_grpc.add_ComputeServicer_to_server(ComputeServicer(), server)
    listen_addr = f"0.0.0.0:{PORT}"
    server.add_insecure_port(listen_addr)
    print(f"{SERVICE_NAME} starting on {listen_addr}")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()