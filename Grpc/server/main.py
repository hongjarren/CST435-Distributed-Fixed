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
        """Service A: Inventory Check - add incoming stock to base inventory"""
        work_ms = request.work_ms if request.work_ms else 0
        time.sleep(work_ms / 1000.0)
        
        # Inventory: base_inventory (100) + incoming stock
        result = request.value + 100
        timestamp_ms = int(time.time() * 1000)
        
        return compute_pb2.ComputeResponse(
            result=result,
            service_name=SERVICE_NAME,
            timestamp_ms=timestamp_ms
        )
    
    def Transform(self, request, context):
        """Service B: Apply Tax - calculate total with 15% sales tax"""
        work_ms = request.work_ms if request.work_ms else 0
        time.sleep(work_ms / 1000.0)
        
        # Tax: apply 15% sales tax
        result = int(request.computed_value * 1.15)
        timestamp_ms = int(time.time() * 1000)
        
        return compute_pb2.TransformResponse(
            result=result,
            service_name=SERVICE_NAME,
            timestamp_ms=timestamp_ms
        )
    
    def Aggregate(self, request, context):
        """Service C: Calculate Shipping - base cost plus weight-based rate"""
        work_ms = request.work_ms if request.work_ms else 0
        time.sleep(work_ms / 1000.0)
        
        # Shipping: $50 base + $1 per 10 units
        result = 50 + (request.transformed_value // 10)
        timestamp_ms = int(time.time() * 1000)
        
        return compute_pb2.AggregateResponse(
            result=result,
            service_name=SERVICE_NAME,
            timestamp_ms=timestamp_ms
        )
    
    def Refine(self, request, context):
        """Service D: Processing Fee - add 2.5% transaction fee"""
        work_ms = request.work_ms if request.work_ms else 0
        time.sleep(work_ms / 1000.0)
        
        # Processing fee: add 2.5% transaction fee
        result = int(request.aggregated_value * 1.025)
        timestamp_ms = int(time.time() * 1000)
        
        return compute_pb2.RefineResponse(
            result=result,
            service_name=SERVICE_NAME,
            timestamp_ms=timestamp_ms
        )
    
    def Finalize(self, request, context):
        """Service E: Round to Currency - round final amount to nearest $5"""
        work_ms = request.work_ms if request.work_ms else 0
        time.sleep(work_ms / 1000.0)
        
        # Round to nearest $5 for final invoice
        result = (request.refined_value // 5) * 5
        timestamp_ms = int(time.time() * 1000)
        
        return compute_pb2.FinalizeResponse(
            final_result=result,
            pipeline="A->B->C->D->E",
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