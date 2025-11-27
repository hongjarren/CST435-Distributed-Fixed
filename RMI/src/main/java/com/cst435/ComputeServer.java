package com.cst435;

import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

/**
 * RMI Server for one of the five services (A, B, C, D, or E).
 * Service type is passed as environment variable SERVICE_NAME.
 * Binds the service to the RMI registry on port 1099.
 */
public class ComputeServer {
    public static void main(String[] args) {
        String serviceName = System.getenv("SERVICE_NAME");
        if (serviceName == null || serviceName.isEmpty()) {
            serviceName = "A";
        }
        serviceName = serviceName.toUpperCase();

        if (!serviceName.matches("[ABCDE]")) {
            System.err.println("Invalid SERVICE_NAME: " + serviceName + " (must be A, B, C, D, or E)");
            System.exit(1);
        }

        try {
            String hostIp = System.getenv("HOST_IP");
            if (hostIp == null || hostIp.isBlank()) {
                hostIp = System.getenv("PUBLIC_IP");
            }
            if (hostIp != null && !hostIp.isBlank()) {
                System.setProperty("java.rmi.server.hostname", hostIp.trim());
                System.out.println("Exporting service using hostname " + hostIp);
            } else {
                System.out.println("WARNING: HOST_IP not set; assuming clients run inside same Docker network");
            }

            // Create the service implementation
            ComputeServiceImpl service = new ComputeServiceImpl(serviceName);

            // Try to locate existing registry; if not found, create one
            Registry registry = null;
            try {
                registry = LocateRegistry.getRegistry(1099);
                registry.list(); // Test connection
            } catch (RemoteException e) {
                System.out.println("Creating new RMI registry on port 1099...");
                registry = LocateRegistry.createRegistry(1099);
            }

            // Bind the service to the registry
            String bindName = "ComputeService_" + serviceName;
            registry.rebind(bindName, service);

            System.out.println("Service " + serviceName + " registered as '" + bindName + "' on port 1099");
            System.out.println("Waiting for requests...");

        } catch (RemoteException e) {
            System.err.println("RMI Server error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
