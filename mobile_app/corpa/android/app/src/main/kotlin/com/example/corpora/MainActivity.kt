package com.example.corpora

//import android.os.Bundle
//import android.os.PersistableBundle
//import android.util.Log

import android.content.Context
import android.net.wifi.WifiManager
import androidx.annotation.NonNull
import io.flutter.Log
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugins.GeneratedPluginRegistrant
import java.io.IOException
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.SocketTimeoutException


@Suppress("PrivatePropertyName")
class MainActivity : FlutterActivity() {

    override fun configureFlutterEngine(@NonNull flutterEngine: FlutterEngine) {
        GeneratedPluginRegistrant.registerWith(flutterEngine)

        Log.d("fucker", "ASJHJSHJHJ")
        print("MC Candy San")
        Log.d("fucker", getBroadcastAddress().toString())

        RegSTart().start()
        Search().start()

        val c = Client()
        c.start()
    }


    @Throws(IOException::class)
    fun getBroadcastAddress(): InetAddress? {
        val wifi: WifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
        val dhcp = wifi.dhcpInfo
        // handle null somehow
        val broadcast = dhcp.ipAddress and dhcp.netmask or dhcp.netmask.inv()
        val quads = ByteArray(4)
        for (k in 0..3) quads[k] = (broadcast shr k * 8 and 0xFF).toByte()
        return InetAddress.getByAddress(quads)
    }

    inner class Search : Thread() {
        override fun run() {
            val s = Jdsearch()
            s.start()
            super.run()
        }

    }

    inner class RegSTart: Thread(){
        override fun run() {
            val r = JDregister()
            r.start()
            super.run()
        }
    }

    inner class Client : Thread() {
        override fun run() {


            Log.d("fucker", "DIIDIID")
            val socket = DatagramSocket(9000)
            socket.broadcast = true
            socket.soTimeout = 500

            Log.d("fucker", socket.isConnected.toString())

            val data = "fuck ya"
            val piker = DatagramPacket(data.toByteArray(), data.length, getBroadcastAddress(), 9000)
            socket.send(piker)

            try {
                while (true) {
                    val buf = ByteArray(1024)
                    val packet = DatagramPacket(buf, buf.size)
                    socket.receive(packet)

                    val x = String(packet.data, 0, packet.length)

//                Log.d("fucker", socket.remoteSocketAddress.toString())

//                val x = buf.contentToString()
                    Log.d("fucker", x)
                }

            } catch (e: SocketTimeoutException){
                Log.e("fucker", e.message!!)
            }
        }
    }

}

