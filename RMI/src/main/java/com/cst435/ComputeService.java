package com.cst435;

import java.rmi.Remote;
import java.rmi.RemoteException;

/**
 * Remote interface for the 5-stage pipeline services.
 * Each service implements one of these methods.
 */
public interface ComputeService extends Remote {
    /**
     * Service A: Multiply input by 2
     */
    int compute(int value, int workMs) throws RemoteException;

    /**
     * Service B: Add 10 to computed value
     */
    int transform(int computedValue, int workMs) throws RemoteException;

    /**
     * Service C: Multiply transformed value by 3
     */
    int aggregate(int transformedValue, int workMs) throws RemoteException;
    
    /**
     * Service D: Subtract 5 from aggregated value
     */
    int refine(int aggregatedValue, int workMs) throws RemoteException;
    
    /**
     * Service E: Divide refined value by 2
     */
    int finalize(int refinedValue, int workMs) throws RemoteException;
}
