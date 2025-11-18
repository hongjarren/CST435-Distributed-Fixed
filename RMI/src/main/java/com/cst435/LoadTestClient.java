package com.cst435;

import java.io.FileWriter;
import java.io.IOException;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.*;
import java.util.concurrent.*;

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

        PipelineWorker(String hostA, String hostB, String hostC, String hostD, String hostE, int numRequests, int inputValue, int workMs) {
            this.hostA = hostA;
            this.hostB = hostB;
            this.hostC = hostC;
            this.hostD = hostD;
            this.hostE = hostE;
            this.numRequests = numRequests;
            this.inputValue = inputValue;
            this.workMs = workMs;
        }

        @Override
        public List<TestResult> call() {
            List<TestResult> results = new ArrayList<>();
            for (int i = 0; i < numRequests; i++) {
                TestResult result = runPipeline();
                results.add(result);
            }
            return results;
        }

        private TestResult runPipeline() {
            TestResult result = new TestResult(inputValue, hostA, hostB, hostC, hostD, hostE);
            try {
                // Look up services in RMI registry
                Registry regA = LocateRegistry.getRegistry(hostA, 1099);
                ComputeService serviceA = (ComputeService) regA.lookup("ComputeService_A");

                Registry regB = LocateRegistry.getRegistry(hostB, 1099);
                ComputeService serviceB = (ComputeService) regB.lookup("ComputeService_B");

                Registry regC = LocateRegistry.getRegistry(hostC, 1099);
                ComputeService serviceC = (ComputeService) regC.lookup("ComputeService_C");
                
                Registry regD = LocateRegistry.getRegistry(hostD, 1099);
                ComputeService serviceD = (ComputeService) regD.lookup("ComputeService_D");
                
                Registry regE = LocateRegistry.getRegistry(hostE, 1099);
                ComputeService serviceE = (ComputeService) regE.lookup("ComputeService_E");

                // Execute pipeline
                result.computed = serviceA.compute(inputValue, workMs);
                result.transformed = serviceB.transform(result.computed, workMs);
                result.aggregated = serviceC.aggregate(result.transformed, workMs);
                result.refined = serviceD.refine(result.aggregated, workMs);
                result.finalResult = serviceE.finalize(result.refined, workMs);

                result.recvTs = System.currentTimeMillis();
                result.rttMs = result.recvTs - result.sendTs;

            } catch (RemoteException | NotBoundException e) {
                result.recvTs = System.currentTimeMillis();
                result.rttMs = result.recvTs - result.sendTs;
                result.error = e.getMessage();
            }
            return result;
        }
    }

    public static void main(String[] args) {
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

        List<TestResult> allResults = new ArrayList<>();
        ExecutorService executor = Executors.newFixedThreadPool(concurrency);
        List<Future<List<TestResult>>> futures = new ArrayList<>();

        long experimentStart = System.currentTimeMillis();

        // Submit tasks
        int perThread = Math.max(1, numRequests / concurrency);
        for (int i = 0; i < concurrency; i++) {
            futures.add(executor.submit(new PipelineWorker(hostA, hostB, hostC, hostD, hostE, perThread, inputValue, workMs)));
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
