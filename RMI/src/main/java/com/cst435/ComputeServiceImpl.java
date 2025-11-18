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
        int result = value * 2;
        System.out.println("[Service A] compute(" + value + ") = " + result);
        return result;
    }

    @Override
    public int transform(int computedValue, int workMs) throws RemoteException {
        if (!serviceName.equals("B")) {
            throw new RemoteException("This service does not implement transform()");
        }
        simulateWork(workMs);
        int result = computedValue + 10;
        System.out.println("[Service B] transform(" + computedValue + ") = " + result);
        return result;
    }

    @Override
    public int aggregate(int transformedValue, int workMs) throws RemoteException {
        if (!serviceName.equals("C")) {
            throw new RemoteException("This service does not implement aggregate()");
        }
        simulateWork(workMs);
        int result = transformedValue * 3;
        System.out.println("[Service C] aggregate(" + transformedValue + ") = " + result);
        return result;
    }
    
    @Override
    public int refine(int aggregatedValue, int workMs) throws RemoteException {
        if (!serviceName.equals("D")) {
            throw new RemoteException("This service does not implement refine()");
        }
        simulateWork(workMs);
        int result = aggregatedValue - 5;
        System.out.println("[Service D] refine(" + aggregatedValue + ") = " + result);
        return result;
    }
    
    @Override
    public int finalize(int refinedValue, int workMs) throws RemoteException {
        if (!serviceName.equals("E")) {
            throw new RemoteException("This service does not implement finalize()");
        }
        simulateWork(workMs);
        int result = refinedValue / 2;
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
