package com.cst435;

import java.io.FileWriter;
import java.io.IOException;
import java.net.Socket;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.RMISocketFactory;
import java.util.*;
import java.util.concurrent.*;

/**
 * Custom socket factory with aggressive timeouts
 */
class FastRMISocketFactory extends RMISocketFactory {
    @Override
    public Socket createSocket(String host, int port) throws IOException {
        Socket socket = new Socket();
        socket.setSoTimeout(2000);  // 2 second read timeout
        socket.setTcpNoDelay(true); // Disable Nagle's algorithm
        socket.connect(new java.net.InetSocketAddress(host, port), 2000); // 2 second connect timeout
        return socket;
    }

    @Override
    public java.net.ServerSocket createServerSocket(int port) throws IOException {
        return new java.net.ServerSocket(port);
    }
}

/**
 * RMI Load Test Client.
 * Sends requests through the 5-stage pipeline (Service A -> B -> C -> D -> E).
 * Outputs results to a CSV file.
 */
public class LoadTestClient {
    static class TestResult {
        int input;
        Integer computed;
        Integer transformed;
        Integer aggregated;
        Integer refined;
        Integer finalResult;
        String serviceA;
        String serviceB;
        String serviceC;
        String serviceD;
        String serviceE;
        long sendTs;
        long recvTs;
        long rttMs;
        String error;

        TestResult(int input, String serviceA, String serviceB, String serviceC, String serviceD, String serviceE) {
            this.input = input;
            this.serviceA = serviceA;
            this.serviceB = serviceB;
            this.serviceC = serviceC;
            this.serviceD = serviceD;
            this.serviceE = serviceE;
            this.sendTs = System.currentTimeMillis();
            this.error = "";
        }

        void toCSV(FileWriter writer) throws IOException {
            writer.write(input + "," +
                    (computed != null ? computed : "") + "," +
                    (transformed != null ? transformed : "") + "," +
                    (aggregated != null ? aggregated : "") + "," +
                    (refined != null ? refined : "") + "," +
                    (finalResult != null ? finalResult : "") + "," +
                    serviceA + "," +
                    serviceB + "," +
                    serviceC + "," +
                    serviceD + "," +
                    serviceE + "," +
                    sendTs + "," +
                    recvTs + "," +
                    (rttMs > 0 ? rttMs : "") + "," +
                    error + "\n");
        }
    }

    static class PipelineWorker implements Callable<List<TestResult>> {
        String hostA, hostB, hostC, hostD, hostE;
        int numRequests;
        int inputValue;
        int workMs;
        
        // Pre-cached service stubs passed from main thread
        ComputeService serviceA, serviceB, serviceC, serviceD, serviceE;

        PipelineWorker(String hostA, String hostB, String hostC, String hostD, String hostE, 
                      int numRequests, int inputValue, int workMs,
                      ComputeService serviceA, ComputeService serviceB, ComputeService serviceC,
                      ComputeService serviceD, ComputeService serviceE) {
            this.hostA = hostA;
            this.hostB = hostB;
            this.hostC = hostC;
            this.hostD = hostD;
            this.hostE = hostE;
            this.numRequests = numRequests;
            this.inputValue = inputValue;
            this.workMs = workMs;
            this.serviceA = serviceA;
            this.serviceB = serviceB;
            this.serviceC = serviceC;
            this.serviceD = serviceD;
            this.serviceE = serviceE;
        }

        @Override
        public List<TestResult> call() {
            List<TestResult> results = new ArrayList<>();
            
            // Service stubs are already cached from main thread
            // Execute requests directly
            for (int i = 0; i < numRequests; i++) {
                TestResult result = runPipeline();
                results.add(result);
            }
            return results;
        }

        private TestResult runPipeline() {
            TestResult result = new TestResult(inputValue, hostA, hostB, hostC, hostD, hostE);
            try {
                // Execute pipeline using cached service stubs
                result.computed = serviceA.compute(inputValue, workMs);
                result.transformed = serviceB.transform(result.computed, workMs);
                result.aggregated = serviceC.aggregate(result.transformed, workMs);
                result.refined = serviceD.refine(result.aggregated, workMs);
                result.finalResult = serviceE.finalize(result.refined, workMs);

                result.recvTs = System.currentTimeMillis();
                result.rttMs = result.recvTs - result.sendTs;

            } catch (RemoteException e) {
                result.recvTs = System.currentTimeMillis();
                result.rttMs = result.recvTs - result.sendTs;
                result.error = e.getMessage();
            }
            return result;
        }
    }

    public static void main(String[] args) {
        // Disable reverse DNS lookups to prevent RMI blocking
        System.setProperty("sun.net.spi.nameservice.provider.1", "dns,sun");
        System.setProperty("sun.net.inetaddr.ttl", "0");
        System.setProperty("java.security.krb5.disableReferrals", "true");
        
        // TCP optimization to eliminate handshake delays and reduce timeouts
        System.setProperty("sun.rmi.transport.tcp.responseTimeout", "2000");
        System.setProperty("sun.rmi.transport.connectionTimeout", "2000");
        System.setProperty("java.rmi.server.disableHttp", "true");
        
        String hostA = "localhost";
        String hostB = "localhost";
        String hostC = "localhost";
        String hostD = "localhost";
        String hostE = "localhost";
        int numRequests = 300;
        int concurrency = 10;
        int inputValue = 5;
        int workMs = 10;
        String outputFile = "./results/results.csv";

        // Parse command line arguments
        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "--targets":
                    String[] targets = args[++i].split(",");
                    if (targets.length >= 1) hostA = targets[0].trim();
                    if (targets.length >= 2) hostB = targets[1].trim();
                    if (targets.length >= 3) hostC = targets[2].trim();
                    if (targets.length >= 4) hostD = targets[3].trim();
                    if (targets.length >= 5) hostE = targets[4].trim();
                    break;
                case "--requests":
                    numRequests = Integer.parseInt(args[++i]);
                    break;
                case "--concurrency":
                    concurrency = Integer.parseInt(args[++i]);
                    break;
                case "--input":
                    inputValue = Integer.parseInt(args[++i]);
                    break;
                case "--work_ms":
                    workMs = Integer.parseInt(args[++i]);
                    break;
                case "--out":
                    outputFile = args[++i];
                    break;
            }
        }

        System.out.println("RMI Load Test Client");
        System.out.println("Targets: " + hostA + ", " + hostB + ", " + hostC + ", " + hostD + ", " + hostE);
        System.out.println("Requests: " + numRequests + ", Concurrency: " + concurrency);
        System.out.println("Input: " + inputValue + ", Work: " + workMs + "ms");

        // Pre-cache service stubs in main thread (once for all workers)
        System.out.println("\nLooking up services...");
        ComputeService serviceA, serviceB, serviceC, serviceD, serviceE;
        try {
            long lookupStart = System.currentTimeMillis();
            
            long t1 = System.currentTimeMillis();
            Registry regA = LocateRegistry.getRegistry(hostA, 1099);
            serviceA = (ComputeService) regA.lookup("ComputeService_A");
            System.out.println("  ✓ Service A found (" + (System.currentTimeMillis() - t1) + "ms)");

            long t2 = System.currentTimeMillis();
            Registry regB = LocateRegistry.getRegistry(hostB, 1099);
            serviceB = (ComputeService) regB.lookup("ComputeService_B");
            System.out.println("  ✓ Service B found (" + (System.currentTimeMillis() - t2) + "ms)");

            long t3 = System.currentTimeMillis();
            Registry regC = LocateRegistry.getRegistry(hostC, 1099);
            serviceC = (ComputeService) regC.lookup("ComputeService_C");
            System.out.println("  ✓ Service C found (" + (System.currentTimeMillis() - t3) + "ms)");
            
            long t4 = System.currentTimeMillis();
            Registry regD = LocateRegistry.getRegistry(hostD, 1099);
            serviceD = (ComputeService) regD.lookup("ComputeService_D");
            System.out.println("  ✓ Service D found (" + (System.currentTimeMillis() - t4) + "ms)");
            
            long t5 = System.currentTimeMillis();
            Registry regE = LocateRegistry.getRegistry(hostE, 1099);
            serviceE = (ComputeService) regE.lookup("ComputeService_E");
            System.out.println("  ✓ Service E found (" + (System.currentTimeMillis() - t5) + "ms)");
            
            long lookupTime = System.currentTimeMillis() - lookupStart;
            System.out.println("All services found in " + lookupTime + "ms\n");
            
        } catch (RemoteException | NotBoundException e) {
            System.err.println("FATAL: Service lookup failed: " + e.getMessage());
            e.printStackTrace();
            return;
        }

        List<TestResult> allResults = new ArrayList<>();
        ExecutorService executor = Executors.newFixedThreadPool(concurrency);
        List<Future<List<TestResult>>> futures = new ArrayList<>();

        long experimentStart = System.currentTimeMillis();
        System.out.println("Starting experiment...");

        // Submit tasks with pre-cached stubs
        int perThread = Math.max(1, numRequests / concurrency);
        for (int i = 0; i < concurrency; i++) {
            futures.add(executor.submit(new PipelineWorker(
                hostA, hostB, hostC, hostD, hostE, 
                perThread, inputValue, workMs,
                serviceA, serviceB, serviceC, serviceD, serviceE
            )));
        }

        // Collect results
        try {
            for (Future<List<TestResult>> future : futures) {
                allResults.addAll(future.get());
            }
        } catch (InterruptedException | ExecutionException e) {
            System.err.println("Error collecting results: " + e.getMessage());
            e.printStackTrace();
        }
        executor.shutdown();

        long experimentEnd = System.currentTimeMillis();
        long totalTime = experimentEnd - experimentStart;

        // Write CSV
        try {
            new java.io.File(outputFile).getParentFile().mkdirs();
            try (FileWriter writer = new FileWriter(outputFile)) {
                writer.write("input,computed,transformed,aggregated,refined,final_result,service_a,service_b,service_c,service_d,service_e,send_ts,recv_ts,rtt_ms,error\n");
                for (TestResult r : allResults) {
                    r.toCSV(writer);
                }
            }

            // Print summary
            long firstSend = allResults.stream().mapToLong(r -> r.sendTs).min().orElse(0);
            long lastRecv = allResults.stream().mapToLong(r -> r.recvTs).max().orElse(0);
            long pipelineTime = lastRecv - firstSend;
            double avgRtt = allResults.stream().mapToLong(r -> r.rttMs).filter(r -> r > 0).average().orElse(0);
            long minRtt = allResults.stream().mapToLong(r -> r.rttMs).filter(r -> r > 0).min().orElse(0);
            long maxRtt = allResults.stream().mapToLong(r -> r.rttMs).filter(r -> r > 0).max().orElse(0);

            System.out.println("\n=== Experiment Summary ===");
            System.out.println("Total requests: " + allResults.size());
            System.out.println("Total time: " + pipelineTime + "ms (" + (pipelineTime / 1000.0) + "s)");
            System.out.println("Average RTT per request: " + String.format("%.2f", avgRtt) + "ms");
            System.out.println("Min RTT: " + minRtt + "ms");
            System.out.println("Max RTT: " + maxRtt + "ms");
            System.out.println("Wrote " + allResults.size() + " rows to " + outputFile);

        } catch (IOException e) {
            System.err.println("Error writing CSV: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
