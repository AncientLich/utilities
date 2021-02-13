# utilities
A bunch of various utilities. All MIT-licensed.
Currently available:
   
   * [playsnd](#playsnd)
   * [remok](#remok)
   * [slp](#slp)

## playsnd
a small application in order to play a sound (it will be played until the end)
Useful to allow you to use a sound to notify a finish work while working on scripts
It is a cpp application and requires to be built.

   Requirements for building:
   
   * g++ compiler
   * pkg-config
   * SDL2 libraries (-dev)
   * SDL2_mixer libraries (-dev)

How to use it
   
   > ./playsnd FILE_TO_PLAY.ogg
   
Supported formats:

   * WAV
   * OGG
   * MP3

   
## remok
A tool for removing old kernel under Ubuntu (and probably debian)
remok itself doesn't remove anything, but it generates a bash script "kernel_remove"
launching the generated "kernel_remove" (requires sudo) will actually remove old kernels

How to use it
  
   > ./remok                  -> generates kernel_remove
   > sudo ./kernel_remove     -> step 2) remove old kernels

   
## slp
A simple cont-down timer. It will run until time elapsed showing you how much time is missing.

How to use it

   > ./slp 10      -> 10 minutes 
   > ./slp 3:35    -> 3 hours and 35 minutes
