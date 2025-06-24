# FreenoveHexapodMod Arduino Index
## These sketches are based off of the FreenoveHexapodv2, a Mega2560 built on freenove's custom board. It probably won't work out of the box on other setups, but is pretty easy to customize. 

This folder contains the Arduino sketches used by the Python programs in BuzzardFoods/FreenoveHexapodMod/Python/.

I'm in the process of merging everything into a single, unified sketch that keeps all the functionality. In the meantime, I’ve published them separately so the Python programs can remain operational.

<sup>(The filename index is made obsolete/redundant by adding tags after each filename for their counterpart.
**EXAMPLE_123.ino** with **EXAMPLEFOO_123.py** _and_ **EXAMPLEBAR_123.py** are....examples.)</sup>

Below is the list of sketches and their respective Python counterparts, as well as short summaries of functionality. This list will be updated with every addition to the repos.


# .Ino + .Py

- **BasicSerialServoCtrl_BSSC.INO** - (**ServoCam_AudioTracking_BSSC.py**) This sketch allows manual control of up to 18 servos on the Freenove Hexapod V2 via serial commands. Send `S:{index}:{angle}` to move individual servos, and use +V or -V to toggle verbose output. Useful for testing servo positions or integrating with external control programs like Python scripts. I rely on this sketch a ton.
  
- TBA (ran out of time for now, more to come.)
