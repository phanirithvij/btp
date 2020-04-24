package com.example.corpora


import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import androidx.annotation.NonNull
import androidx.core.app.ActivityCompat
import io.flutter.Log
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import io.flutter.plugins.GeneratedPluginRegistrant

private const val REQUEST_RECORD_AUDIO_PERMISSION = 200

class MainActivity : FlutterActivity() {

    private val CHANNEL = "com.example.corpora/open"
    private var permissionToRecordAccepted = false
    private var permissions: Array<String> = arrayOf(Manifest.permission.RECORD_AUDIO)
    private val recorder = Recorder()
    private var recording = false
    private var playing = false
    //    private var recorder: MediaRecorder? = null

    override fun onRequestPermissionsResult(
            requestCode: Int,
            permissions: Array<String>,
            grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        permissionToRecordAccepted = if (requestCode == REQUEST_RECORD_AUDIO_PERMISSION) {
            grantResults[0] == PackageManager.PERMISSION_GRANTED
        } else {
            false
        }
        if (!permissionToRecordAccepted) finish()
    }

    override fun configureFlutterEngine(@NonNull flutterEngine: FlutterEngine) {
        GeneratedPluginRegistrant.registerWith(flutterEngine)

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "startRec" -> {
                    Log.d("HELP", call.arguments.toString())
                    ActivityCompat.requestPermissions(this, permissions, REQUEST_RECORD_AUDIO_PERMISSION)
                    recorder.run {
                        fileName = call.argument<String>("name")!!
                        onRecord(!recording)
                    }
                    recording = true
                    result.success(null)
                }
                "stopRec" -> {
                    recorder.onRecord(!recording)
                    recording = false
                    result.success(null)
                }
                "startPlay" -> {
                    recorder.onPlay(true)
                    result.success(null)
                }
                "stopPlay" -> {
                    recorder.onPlay(false)
                    result.success(null)
                }
                "openFolder" -> {
                    // https://stackoverflow.com/a/26651827/8608146
                    val selectedUri: Uri = Uri.parse(call.argument("path")!!)
                    val intent = Intent(Intent.ACTION_VIEW)
                    intent.setDataAndType(selectedUri, "resource/folder")

                    if (intent.resolveActivityInfo(packageManager, 0) != null) {
                        startActivity(intent)
                        result.success(null)
                    } else {
                        // if you reach this place, it means there is no any file
                        // explorer app installed on your device
                        result.error("noF", "No file manager found", null)
                    }
                }
                else -> {
                    result.notImplemented()
                }
            }
        }

    }
}

