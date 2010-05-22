# Code from http://wiki.python.org/moin/MacPython/CoreAudio
# Copyright Donovan Preston


def debug(txt):
    # print txt
    pass

def FOUR_CHAR_CODE(val):
    from struct import unpack
    return unpack('!I', val)[0]


kAudioHardwarePropertyDefaultOutputDevice = FOUR_CHAR_CODE('dOut')
kAudioDevicePropertyDeviceName = FOUR_CHAR_CODE('name')
kAudioDevicePropertyDeviceIsRunning = FOUR_CHAR_CODE('goin')
kAudioDevicePropertyNominalSampleRate = FOUR_CHAR_CODE('nsrt')
kAudioDevicePropertyBufferFrameSize = FOUR_CHAR_CODE('fsiz')
kAudioDevicePropertyStreamFormat = FOUR_CHAR_CODE('sfmt')

cdef extern from "stdio.h":
    void printf(char *theStr, ...)

cdef extern from "math.h":
    int sin(int theInput)

cdef extern from "Python.h":
    ctypedef enum PyGILState_STATE:
        PyGILState_LOCKED
        PyGILState_UNLOCKED

    PyGILState_STATE PyGILState_Ensure()
    void PyGILState_Release(PyGILState_STATE)


cdef extern from "CoreAudio/AudioHardware.h":
    ctypedef unsigned int UInt32
    ctypedef unsigned int OSStatus

    ctypedef UInt32 AudioHardwarePropertyID
    ctypedef UInt32	AudioDeviceID
    ctypedef UInt32	AudioDevicePropertyID
    ctypedef UInt32	AudioStreamID

    ctypedef double Float64
    ctypedef unsigned long long UInt64
    ctypedef short int SInt16

    ctypedef struct SMPTETime:
        UInt64	mCounter #;			//	total number of messages received
        UInt32	mType #;				//	the SMPTE type (see constants)
        UInt32	mFlags #;				//	flags indicating state (see constants
        SInt16	mHours #;				//	number of hours in the full message
        SInt16	mMinutes #;			//	number of minutes in the full message
        SInt16	mSeconds #;			//	number of seconds in the full message
        SInt16	mFrames #;			//	number of frames in the full message

    ctypedef struct AudioTimeStamp:
        Float64			mSampleTime #;	//	the absolute sample time
        UInt64			mHostTime #;		//	the host's root timebase's time
        Float64			mRateScalar #;	//	the system rate scalar
        UInt64			mWordClockTime #;	//	the word clock time
        SMPTETime		mSMPTETime #;		//	the SMPTE time
        UInt32			mFlags #;			//	the flags indicate which fields are valid
        UInt32			mReserved #;		//	reserved, pads the structure out to force 8 byte alignment

    ctypedef struct AudioStreamBasicDescription:
        Float64	mSampleRate #;		//	the native sample rate of the audio stream
        UInt32	mFormatID #;			//	the specific encoding type of audio stream
        UInt32	mFormatFlags #;		//	flags specific to each format
        UInt32	mBytesPerPacket #;	//	the number of bytes in a packet
        UInt32	mFramesPerPacket #;	//	the number of frames in each packet
        UInt32	mBytesPerFrame #;		//	the number of bytes in a frame
        UInt32	mChannelsPerFrame #;	//	the number of channels in each frame
        UInt32	mBitsPerChannel #;	//	the number of bits in each channel
        UInt32	mReserved #;			//	reserved, pads the structure out to force 8 byte alignment

    OSStatus AudioHardwareGetProperty(
        AudioHardwarePropertyID inPropertyID,
        UInt32 *ioPropertyDataSize,
        void *outPropertyData)

    OSStatus AudioDeviceGetProperty(
        AudioDeviceID inDevice,
        UInt32 inChannel,
        int isInput,
        AudioDevicePropertyID inPropertyID,
        UInt32 *ioPropertyDataSize,
        void *outPropertyData)

    OSStatus AudioDeviceSetProperty(
        AudioDeviceID inDevice,
        AudioTimeStamp *inWhen,
        UInt32 inChannel,
        int isInput,
        AudioDevicePropertyID inPropertyID,
        UInt32 inPropertyDataSize,
        void* inPropertyData)

    ctypedef struct AudioBuffer:
      UInt32	mNumberChannels #;	//	number of interleaved channels in the buffer
      UInt32	mDataByteSize #;		//	the size of the buffer pointed to by mData
      void*	mData #;				//	the pointer to the buffer

    ctypedef struct AudioBufferList:
        UInt32		mNumberBuffers
        AudioBuffer	mBuffers[1]

    ctypedef OSStatus (*AudioDeviceIOProc)(
        AudioDeviceID			inDevice,
        AudioTimeStamp*	inNow,
        AudioBufferList*	inInputData,
        AudioTimeStamp*	inInputTime,
        AudioBufferList*		outOutputData, 
        AudioTimeStamp*	inOutputTime,
        void*					inClientData)

    OSStatus AudioDeviceAddIOProc(
        AudioDeviceID inDevice,
        AudioDeviceIOProc inProc,
        void* inClientData)

    OSStatus AudioDeviceStart(
        AudioDeviceID inDevice,
        AudioDeviceIOProc inProc)

    OSStatus AudioDeviceStop(
        AudioDeviceID inDevice,
        AudioDeviceIOProc inProc)

    OSStatus AudioDeviceRemoveIOProc(
        AudioDeviceID inDevice,
        AudioDeviceIOProc inProc)

cdef UInt32 bufSize = 1024

cdef OSStatus audioDeviceIOCallback(
        AudioDeviceID			inDevice,
        AudioTimeStamp*	inNow,
        AudioBufferList*	inInputData,
        AudioTimeStamp*	inInputTime,
        AudioBufferList*		outOutputData, 
        AudioTimeStamp*	inOutputTime,
        void*					inClientData):

    cdef PyGILState_STATE st
    cdef float * buffer
    cdef int offset
    cdef float v
    cdef object data
    cdef object rv

    st = PyGILState_Ensure()

    # Stolen from http://www.omnigroup.com/mailman/archive/macosx-dev/2000-May/001922.html

    data = <object> inClientData

    rv = data.callback()

    buffer = <float *>outOutputData.mBuffers[0].mData
    for frame from 0 <= frame < bufSize:
        v = rv[frame]
        buffer[2* frame + 0] = v
        buffer[2 * frame + 1] = v
    PyGILState_Release(st)

    return 0


def initAudio():
    """Code stolen from:
    http://www.omnigroup.com/mailman/archive/macosx-dev/2000-October/005756.html
    """
    cdef AudioDeviceID outputDeviceID
    cdef UInt32 propertySize
    cdef OSStatus status

    propertySize = sizeof(outputDeviceID)

    # Get the default sound output device
    status = AudioHardwareGetProperty(kAudioHardwarePropertyDefaultOutputDevice, &propertySize, &outputDeviceID)
    if status:
        raise RuntimeError, "Unable to get default output device ID"
    if outputDeviceID == 0:
        raise RuntimeError, "Default audio device was unknown."

    # Get name of the device
    cdef char deviceName[256]

    propertySize = 256
    status = AudioDeviceGetProperty(outputDeviceID, 0, False, kAudioDevicePropertyDeviceName, &propertySize, deviceName)

    debug("Device name: %s" % deviceName)

    if status:
        raise RuntimeError, "Unable to get the audio device name."

    # Check device status
    cdef UInt32 running

    propertySize = sizeof(running)
    status = AudioDeviceGetProperty(outputDeviceID, 0, False, kAudioDevicePropertyDeviceIsRunning, &propertySize, &running)

    debug("Running: %d" % running)

    # Set the sample rate of the device
    cdef double deviceSampleRate
    propertySize = sizeof(deviceSampleRate)
    deviceSampleRate = 8.0

    status = AudioDeviceGetProperty(outputDeviceID, 0, False, kAudioDevicePropertyNominalSampleRate, &propertySize, &deviceSampleRate)
    if status:
        raise RuntimeError, "Unable to get nominal sample rate."
    debug("Sample rate: %d" % deviceSampleRate)

    # Get the buffer size
    propertySize = sizeof(bufSize)

    status = AudioDeviceGetProperty(outputDeviceID, 0, False, kAudioDevicePropertyBufferFrameSize, &propertySize, &bufSize)
    if status:
        raise RuntimeError, "Unable to get the buffer frame size."

    debug("Buffer frame size: %d" % bufSize)

    cdef AudioStreamBasicDescription outputStreamBasicDescription
    propertySize = sizeof(outputStreamBasicDescription)
    status = AudioDeviceGetProperty(outputDeviceID, 0, False, kAudioDevicePropertyStreamFormat, &propertySize, &outputStreamBasicDescription)
    if status:
        raise RuntimeError, "Unable to get the output stream basic description"

    debug("Output stream description:")
    debug("\tSample rate: %d" % outputStreamBasicDescription.mSampleRate)
    debug("\tFormat ID: %d" % outputStreamBasicDescription.mFormatID)
    debug("\tFormat flags: %x" % outputStreamBasicDescription.mFormatFlags)
    debug("\tBytes per packet: %d" % outputStreamBasicDescription.mBytesPerPacket)
    debug("\tBytes per frame: %d" % outputStreamBasicDescription.mBytesPerFrame)
    debug("\tChannels per frame: %d" % outputStreamBasicDescription.mChannelsPerFrame)
    debug("\tBits per channel: %d" % outputStreamBasicDescription.mBitsPerChannel)

    return (outputDeviceID, deviceSampleRate, bufSize)


def installAudioCallback(AudioDeviceID outputDeviceID, cb):
    cdef OSStatus status
    cb.deviceId = outputDeviceID

    status = AudioDeviceAddIOProc(outputDeviceID, <AudioDeviceIOProc>&audioDeviceIOCallback, <void *>cb)
    if status:
        raise RuntimeError, "Failed to add the IO Proc."

    status = AudioDeviceStart(outputDeviceID, <AudioDeviceIOProc>&audioDeviceIOCallback)
    if status:
        raise RuntimeError, "Couldn't start the device."
    debug("done.")


def stopAudio(obj):
    debug("stopping")
    AudioDeviceStop(obj.deviceId, <AudioDeviceIOProc>&audioDeviceIOCallback)
    debug("removing")
    AudioDeviceRemoveIOProc(obj.deviceId, <AudioDeviceIOProc>&audioDeviceIOCallback)
    debug("done")

