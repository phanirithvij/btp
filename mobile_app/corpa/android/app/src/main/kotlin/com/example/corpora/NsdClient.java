package com.example.corpora;

import android.content.Context;
import android.net.nsd.NsdManager;
import android.net.nsd.NsdServiceInfo;

import java.util.ArrayList;
import java.util.List;

import io.flutter.Log;

public class NsdClient {
    private Context mContext;

    private String mServiceName;

    private NsdManager mNsdManager;
    private NsdManager.DiscoveryListener mDiscoveryListener;

    //To find all the available networks
//    private static final String SERVICE_TYPE = "_services._dns-sd._udp"
    public static final String SERVICE_TYPE = "_hap._tcp.";
    public static final String TAG = "NsdClient";

    private static ArrayList<NsdServiceInfo> ServicesAvailable = new ArrayList<>();

    public NsdClient(Context context) {
        mContext = context;
        mNsdManager = (NsdManager) context.getSystemService(Context.NSD_SERVICE);
    }

    public void initializeNsd() {
        initializeDiscoveryListener();
    }

    public void initializeDiscoveryListener() {
        mDiscoveryListener = new NsdManager.DiscoveryListener() {

            @Override
            public void onDiscoveryStarted(String regType) {
                Log.d(TAG, "Service discovery started " + regType);
            }

            @Override
            public void onServiceFound(NsdServiceInfo service) {
                Log.d(TAG, "Service discovery success " + service);
                ArrayList<NsdServiceInfo> AVAILABLE_NETWORKS = new ArrayList<>();
                AVAILABLE_NETWORKS.add(service);

                if (!service.getServiceType().equals(SERVICE_TYPE)) {
                    Log.d(TAG, "Unknown Service Type: " + service.getServiceType());
                } else if (service.getServiceName().equals(mServiceName)) {
                    Log.d(TAG, "Same Machine: " + mServiceName);
                } else if (service.getServiceName().contains(mServiceName)) {
                    Log.d(TAG, "Resolving Services: " + service);
                    mNsdManager.resolveService(service, new initializeResolveListener());
                }
            }

            @Override
            public void onServiceLost(NsdServiceInfo service) {
                Log.e(TAG, "service lost" + service);
                if (ServicesAvailable.equals(service)) {
                    ServicesAvailable = null;
                }
            }

            @Override
            public void onDiscoveryStopped(String serviceType) {
                Log.i(TAG, "Discovery stopped: " + serviceType);
            }

            @Override
            public void onStartDiscoveryFailed(String serviceType, int errorCode) {
                Log.e(TAG, "Discovery failed: Error code:" + errorCode);
                mNsdManager.stopServiceDiscovery(this);
            }

            @Override
            public void onStopDiscoveryFailed(String serviceType, int errorCode) {
                Log.e(TAG, "Discovery failed: Error code:" + errorCode);
                mNsdManager.stopServiceDiscovery(this);
            }
        };
    }

    public class initializeResolveListener implements NsdManager.ResolveListener {

        @Override
        public void onResolveFailed(NsdServiceInfo serviceInfo, int errorCode) {
            Log.e(TAG, "Resolve failed " + errorCode);
            switch (errorCode) {
                case NsdManager.FAILURE_ALREADY_ACTIVE:
                    Log.e(TAG, "FAILURE ALREADY ACTIVE");
                    mNsdManager.resolveService(serviceInfo, new initializeResolveListener());
                    break;
                case NsdManager.FAILURE_INTERNAL_ERROR:
                    Log.e(TAG, "FAILURE_INTERNAL_ERROR");
                    break;
                case NsdManager.FAILURE_MAX_LIMIT:
                    Log.e(TAG, "FAILURE_MAX_LIMIT");
                    break;
            }
        }

        @Override
        public void onServiceResolved(NsdServiceInfo serviceInfo) {
            Log.e(TAG, "Resolve Succeeded. " + serviceInfo);


            if (serviceInfo.getServiceName().equals(mServiceName)) {
                Log.d(TAG, "Same IP.");
            }

        }
    }

    public void stopDiscovery() {
        mNsdManager.stopServiceDiscovery(mDiscoveryListener);
    }

    public List<NsdServiceInfo> getChosenServiceInfo() {
        return ServicesAvailable;
    }

    public void discoverServices() {
        mNsdManager.discoverServices(
                SERVICE_TYPE, NsdManager.PROTOCOL_DNS_SD, mDiscoveryListener);
    }
}