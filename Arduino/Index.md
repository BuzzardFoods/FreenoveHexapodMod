# FreenoveHexapodMod Arduino Index
## These sketches are based off of the FreenoveHexapodv2, a Mega2560 built on freenove's custom board. It probably won't work out of the box on other setups, but is pretty easy to customize. 

This folder contains the Arduino sketches used by the Python programs in BuzzardFoods/FreenoveHexapodMod/Python/.

I'm in the process of merging everything into a single, unified sketch that keeps all the functionality. In the meantime, I’ve published them separately so the Python programs can remain operational.

<sup>(The filename index is made obsolete/redundant by adding tags after each filename for their counterpart.
**EXAMPLE_123.ino** with **EXAMPLEFOO_123.py** _and_ **EXAMPLEBAR_123.py** are....examples.)</sup>

Below is the list of sketches and their respective Python counterparts, as well as short summaries of functionality. This list will be updated with every addition to the repos.


# .Ino + .Py

- **BasicSerialServoCtrl_BSSC.INO** - **ServoCam_AudioTracking_BSSC.py** Motion/audio/manual servo control - Inputs from a webcam and tracks the motion with servos, can assign axis(← ↑ → ↓) to any servo. Can adjust angle range and sensitivity. The camera input also has filters, purely aesthetic. Audio mode where each servo is assigned to a frequency band, basically a mechanical visualizer/eq output. Also contains the same function of the BasicSerialServoControl program, controlling each servo manually. (Using multiple servos at once causes latency problems, the movement will be jittery and it will miss some of the serial commands. I intend on fixing this when it's more entertaining I.E. I get a laser pointer and use it to track my cat and keep him from yelling at me all the time.) 

- TBA (ran out of time for now, more to come.)
