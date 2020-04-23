package com.example.corpora

import android.Manifest
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaPlayer
import android.media.MediaRecorder
import android.util.Log
import java.io.BufferedOutputStream
import java.io.FileOutputStream
import java.io.IOException

private const val LOG_TAG = "AudioRecordTest"

class Recorder {

    private var mAudioRecord: AudioRecord? = null

    private val AUDIOSOURCE = MediaRecorder.AudioSource.VOICE_RECOGNITION
    private val SAMPLERATE = 44100
    private val CHANNELCONFIG = AudioFormat.CHANNEL_IN_STEREO
    private val AUDIOFORMAT = AudioFormat.ENCODING_PCM_16BIT

    // might have to change this buffer size if we get problems recording
    private val BUFFERSIZE = AudioRecord.getMinBufferSize(SAMPLERATE, CHANNELCONFIG, AUDIOFORMAT) * 2

    private val audioBuffer = ShortArray(BUFFERSIZE)
    private var audioData = ArrayList<Short>()

    var fileName: String = ""

    private var player: MediaPlayer? = null

    // Requesting permission to RECORD_AUDIO


    fun onRecord(start: Boolean) = if (start) {
        startRecording()
    } else {
        stopRecording()
    }

    fun onPlay(start: Boolean) = if (start) {
        startPlaying()
    } else {
        stopPlaying()
    }

    private fun startPlaying() {
        player = MediaPlayer().apply {
            try {
                setDataSource(fileName)
                prepare()
                start()
            } catch (e: IOException) {
                Log.e(LOG_TAG, "prepare() failed")
            }
        }
    }

    private fun stopPlaying() {
        player?.release()
        player = null
    }

    private fun startRecording() {
        mAudioRecord = AudioRecord(AUDIOSOURCE, SAMPLERATE, CHANNELCONFIG, AUDIOFORMAT, BUFFERSIZE * 2).apply {
            startRecording()
        }

        Thread(Runnable {
            while (mAudioRecord!!.recordingState ==
                    AudioRecord.RECORDSTATE_RECORDING) {
                mAudioRecord!!.read(audioBuffer, 0, BUFFERSIZE)
                for (element in audioBuffer) {
                    audioData.add(element)
                }
            }
        }, "AudioRecorder Thread").start()

    }


    private fun stopRecording() {
        mAudioRecord?.stop()
        val numChannels = if (CHANNELCONFIG == AudioFormat.CHANNEL_IN_MONO) 1 else 2
        val rtw = RawToWav(SAMPLERATE, numChannels)
        // grab data from our audioData, convert it to short[]
        // for our rtw.convert() function
        var tempData = arrayOfNulls<Short>(audioData.size)
        tempData = audioData.toArray(tempData) as Array<Short?>
        val data = ShortArray(tempData.size)
        for (i in data.indices) {
            data[i] = tempData[i]!!.toShort()
        }
        val wav = rtw.convert(data)

        val outStream = BufferedOutputStream(FileOutputStream(fileName))
        outStream.write(wav)
        outStream.flush()
        outStream.close()

        readyForNextRecording()
    }

    private fun readyForNextRecording() {
        audioData = ArrayList()
    }
}
