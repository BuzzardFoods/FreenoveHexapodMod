## Freenove Hexapod Mods[^1]
<sup>I am **not** affiliated with Freenove and do not receive any compensation. The only contact I have had with them was sending them an email to praise their open-source projects.</sup>

This repository contains various Python programs and Arduino sketches for use with the **Freenove Hexapod Kit** Version 2 as a base. (ArduinoMega + Arduino Uno)
These should be pretty easily modified to use with the base components, an Ardunio Mega and/or an Arduino Uno.[^2] If you have any suggestions or comments feel free to message BuzzardFoods on github. 


**The scripts in the **[BuzzardFoods/FreenoveHexapodMod](https://github.com/BuzzardFoods/FreenoveHexapodMod/)** repository utilize the board(s) included with the Freenove Hexapod Robot kit V2 (w/ controller.)**

The Freenove official github is located [here](https://github.com/freenove). 

[Repo for the Hexapod Robot Kit V2](https://github.com/Freenove/Freenove_Hexapod_Robot_Kit)

[Repo for the Freenove Controller](https://github.com/Freenove/Freenove_Remote_Control_Kit)[^3] 

<sup>_Big thanks to Freenove for their Hexapod kit. It’s a fun and easy way to get started with robotics. I often think about how different things might have been if I had received this as a kid. If you’re considering getting one of their kits, I highly recommend it—they’re excellent.Their support is reportedly excellent, but any questions I had were answered in their detailed documentation.</sup>

[^1]:Please note that I am not responsible for any damage or issues resulting from improper wiring or power setup. I am also not responsible for any damage or issues resulting from my scripting, I am not an expert. These worked great on my setup, but always C.Y.A. <ins>Never run any code you do not understand.</ins> 
[^2]:you will need to modify the code by removing any servo power control pins, as the Arduino cannot safely power servos directly. Servos must be powered by an external power source capable of supplying enough current. Connecting servos’ power lines directly to the Arduino pins can cause permanent damage to your board. Again: Please note that I am not responsible for any damage or issues resulting from improper wiring or power setup. Always ensure you have a common ground between your Arduino and the external power supply.
[^3]:I have the blue board controller, I haven't checked into _how_ they're different, but the blue and black boards have different documentation. 
