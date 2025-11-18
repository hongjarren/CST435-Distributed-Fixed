package com.cst435;

import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;

/**
 * Implementation of the ComputeService remote interface.
 * Handles Compute, Transform, and Aggregate operations with simulated work.
 */
public class ComputeServiceImpl extends UnicastRemoteObject implements ComputeService {
    private static final long serialVersionUID = 1L;
    private String serviceName;

    public ComputeServiceImpl(String serviceName) throws RemoteException {
        super();
        this.serviceName = serviceName;
    }

    @Override
    public int compute(int value, int workMs) throws RemoteException {
        if (!serviceName.equals("A")) {
            throw new RemoteException("This service does not implement compute()");
        }
        simulateWork(workMs);
        // Inventory Check: add incoming stock to base inventory (100)
        int result = value + 100;
        System.out.println("[Service A] compute(" + value + ") = " + result);
        return result;
    }

    @Override
    public int transform(int computedValue, int workMs) throws RemoteException {
        if (!serviceName.equals("B")) {
            throw new RemoteException("This service does not implement transform()");
        }
        simulateWork(workMs);
        // Apply Tax: calculate total with 15% sales tax
        int result = (int)(computedValue * 1.15);
        System.out.println("[Service B] transform(" + computedValue + ") = " + result);
        return result;
    }

    @Override
    public int aggregate(int transformedValue, int workMs) throws RemoteException {
        if (!serviceName.equals("C")) {
            throw new RemoteException("This service does not implement aggregate()");
        }
        simulateWork(workMs);
        // Calculate Shipping: $50 base cost + $1 per 10 units
        int result = 50 + (transformedValue / 10);
        System.out.println("[Service C] aggregate(" + transformedValue + ") = " + result);
        return result;
    }
    
    @Override
    public int refine(int aggregatedValue, int workMs) throws RemoteException {
        if (!serviceName.equals("D")) {
            throw new RemoteException("This service does not implement refine()");
        }
        simulateWork(workMs);
        // Processing Fee: add 2.5% transaction fee
        int result = (int)(aggregatedValue * 1.025);
        System.out.println("[Service D] refine(" + aggregatedValue + ") = " + result);
        return result;
    }
    
    @Override
    public int finalize(int refinedValue, int workMs) throws RemoteException {
        if (!serviceName.equals("E")) {
            throw new RemoteException("This service does not implement finalize()");
        }
        simulateWork(workMs);
        // Round to Currency: round final amount to nearest $5
        int result = (refinedValue / 5) * 5;
        System.out.println("[Service E] finalize(" + refinedValue + ") = " + result);
        return result;
    }

    private void simulateWork(int workMs) {
        if (workMs > 0) {
            try {
                Thread.sleep(workMs);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
}
