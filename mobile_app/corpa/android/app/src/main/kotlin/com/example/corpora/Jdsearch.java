package com.example.corpora;

import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;

import javax.jmdns.JmDNS;
import javax.jmdns.ServiceEvent;
import javax.jmdns.ServiceListener;

import io.flutter.Log;

public class Jdsearch {

    private static class SampleListener implements ServiceListener {
        @Override
        public void serviceAdded(ServiceEvent event) {
            Log.d("fucker", "Service added: " + event.getInfo());
        }

        @Override
        public void serviceRemoved(ServiceEvent event) {
            Log.d("fucker", "Service removed: " + event.getInfo());
        }

        @Override
        public void serviceResolved(ServiceEvent event) {
            Log.d("fucker", "Service resolved: " + event.getInfo());
        }
    }


    public void start() {
        try {
            // Create a JmDNS instance
            JmDNS jmdns = JmDNS.create(InetAddress.getLocalHost());

            // Add a service listener
            jmdns.addServiceListener("_coolapp._tcp.local.", new SampleListener());

            // Wait a bit
            Thread.sleep(30000);
        } catch (UnknownHostException e) {
            Log.e("fucker", e.getMessage());
        } catch (IOException e) {
            Log.e("fucker", e.getMessage());
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws InterruptedException {
        try {
            // Create a JmDNS instance
            JmDNS jmdns = JmDNS.create(InetAddress.getLocalHost());

            // Add a service listener
            jmdns.addServiceListener("_coolapp._tcp.local.", new SampleListener());

            // Wait a bit
            Thread.sleep(30000);
        } catch (UnknownHostException e) {
            System.out.println(e.getMessage());
        } catch (IOException e) {
            System.out.println(e.getMessage());
        }
    }
}
