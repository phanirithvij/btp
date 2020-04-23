package com.example.corpora

import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder


@Suppress("SameParameterValue")
class RawToWav internal constructor(private val mSampleRate: Int, private val mNumChannels: Int) {
    fun convert(raw: ShortArray): ByteArray {
        val baos = ByteArrayOutputStream()
        try {
            // write WAV header
            // reference for wav header: recorder.js by matt diamond, https://github.com/mattdiamond/Recorderjs
            // and http://stackoverflow.com/a/5810662/5272567 by
            //   user663321, Evan Merz and Dan Vargo
            baos.write(byteArrayOf('R'.toByte(), 'I'.toByte(), 'F'.toByte(), 'F'.toByte()), 0, 4)
            baos.write(intToBytes(36 + raw.size * 2, "LITTLE_ENDIAN"), 0, 4)
            baos.write(byteArrayOf('W'.toByte(), 'A'.toByte(), 'V'.toByte(), 'E'.toByte()), 0, 4)
            baos.write(byteArrayOf('f'.toByte(), 'm'.toByte(), 't'.toByte(), ' '.toByte()), 0, 4)
            baos.write(intToBytes(16, "LITTLE_ENDIAN"), 0, 4)
            baos.write(shortToBytes(1.toShort(), "LITTLE_ENDIAN"), 0, 2)
            baos.write(shortToBytes(mNumChannels.toShort(), "LITTLE_ENDIAN"), 0, 2)
            baos.write(intToBytes(mSampleRate, "LITTLE_ENDIAN"), 0, 4)
            baos.write(intToBytes(mSampleRate * mNumChannels * 2, "LITTLE_ENDIAN"), 0, 4)
            baos.write(shortToBytes((mNumChannels * 2).toShort(), "LITTLE_ENDIAN"), 0, 2)
            baos.write(shortToBytes(16.toShort(), "LITTLE_ENDIAN"), 0, 2)
            baos.write(byteArrayOf('d'.toByte(), 'a'.toByte(), 't'.toByte(), 'a'.toByte()), 0, 4)
            baos.write(intToBytes(raw.size * 2, "LITTLE_ENDIAN"), 0, 4)
            // write WAV data
            // turn short array to byte array, compliments of Peter Lawrey, http://stackoverflow.com/a/5626003/5272567
            val byteData = ByteArray(raw.size * 2)
            ByteBuffer.wrap(byteData).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer().put(raw)
            baos.write(byteData, 0, byteData.size)
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return baos.toByteArray()
    }

    private fun intToBytes(a: Int, endian: String): ByteArray {
        val b = ByteBuffer.allocate(4)
        if (endian == "LITTLE_ENDIAN") {
            b.order(ByteOrder.LITTLE_ENDIAN)
        } else {
            b.order(ByteOrder.BIG_ENDIAN)
        }
        b.putInt(a)
        return b.array()
    }

    private fun shortToBytes(a: Short, endian: String): ByteArray {
        val b = ByteBuffer.allocate(4)
        if (endian == "LITTLE_ENDIAN") {
            b.order(ByteOrder.LITTLE_ENDIAN)
        } else {
            b.order(ByteOrder.BIG_ENDIAN)
        }
        b.putShort(a)
        return b.array()
    }

}