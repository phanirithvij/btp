package com.example.corpora

import android.content.Context
import io.flutter.Log
import io.flutter.util.PathUtils.getFilesDir
import java.io.File
import java.io.FileNotFoundException
import java.io.FileOutputStream
import java.io.IOException
import kotlin.experimental.and

class Wave(sampleRate: Int, nChannels: Short, data: ShortArray, start: Int, end: Int, val applicationContext: Context) {
    private val LONGINT = 4
    private val SMALLINT = 2
    private val INTEGER = 4
    private val ID_STRING_SIZE = 4
    private val WAV_RIFF_SIZE = LONGINT + ID_STRING_SIZE
    private val WAV_FMT_SIZE = 4 * SMALLINT + INTEGER * 2 + LONGINT + ID_STRING_SIZE
    private val WAV_DATA_SIZE = ID_STRING_SIZE + LONGINT
    private val WAV_HDR_SIZE = WAV_RIFF_SIZE + ID_STRING_SIZE + WAV_FMT_SIZE + WAV_DATA_SIZE
    private val PCM: Short = 1
    private val SAMPLE_SIZE = 2
    var cursor: Int
    var nSamples: Int
    var output: ByteArray

    // ------------------------------------------------------------
    private fun buildHeader(sampleRate: Int, nChannels: Short) {
        write("RIFF")
        write(output.size)
        write("WAVE")
        writeFormat(sampleRate, nChannels)
    }

    // ------------------------------------------------------------
    fun writeFormat(sampleRate: Int, nChannels: Short) {
        write("fmt ")
        write(WAV_FMT_SIZE - WAV_DATA_SIZE)
        write(PCM)
        write(nChannels)
        write(sampleRate)
        write(nChannels * sampleRate * SAMPLE_SIZE)
        write((nChannels * SAMPLE_SIZE).toShort())
        write(16.toShort())
    }

    // ------------------------------------------------------------
    fun writeData(data: ShortArray, start: Int, end: Int) {
        write("data")
        write(nSamples * SMALLINT)
        var i = start
        while (i <= end) {
            write(data[i++])
        }
    }

    // ------------------------------------------------------------
    private fun write(b: Byte) {
        output[cursor++] = b
    }

    // ------------------------------------------------------------
    private fun write(id: String) {
        if (id.length != ID_STRING_SIZE) Log.e("Ell", "String $id must have four characters.") else {
            for (i in 0 until ID_STRING_SIZE) write(id[i].toByte())
        }
    }

    // ------------------------------------------------------------
    private fun write(i: Int) {
        var i = i
        write((i and 0xFF).toByte())
        i = i shr 8
        write((i and 0xFF).toByte())
        i = i shr 8
        write((i and 0xFF).toByte())
        i = i shr 8
        write((i and 0xFF).toByte())
    }

    // ------------------------------------------------------------
    private fun write(i: Short) {
        var i = i
        write((i and 0xFF).toByte())
        i = (i.toInt() shr 8).toShort()
        write((i and 0xFF).toByte())
    }

    // ------------------------------------------------------------
    fun writeToFile(filename: String): Boolean {
        var ok = false
        try {
            val path = File(getFilesDir(applicationContext), filename)
            val outFile = FileOutputStream(path)
            outFile.write(output)
            outFile.close()
            ok = true
        } catch (e: FileNotFoundException) {
            e.printStackTrace()
        } catch (e: IOException) {
            e.printStackTrace()
        }
        return ok
    }

    init {
        nSamples = end - start + 1
        cursor = 0
        output = ByteArray(nSamples * SMALLINT + WAV_HDR_SIZE)
        buildHeader(sampleRate, nChannels)
        writeData(data, start, end)
    }
}