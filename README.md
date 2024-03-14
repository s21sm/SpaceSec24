# SpaceSec24

[SpaceSec24] - COSPAS Search and Rescue Satellite Uplink: A MAC-Based  Security Enhancement

## Table of Contents

- [About](#about)
- [Prerequisites](#prerequisites)
- [Encoding](#encoding)
- [Signal Transmission](#signal-transmission)
- [Signal Receiption](#signal-receiption)
- [Verification](#verification)

## About

This project contains source of code of the article titled "COSPAS Search and Rescue Satellite Uplink: A MAC-Based  Security Enhancement" presented in SpaceSec'24 workshop 

## Prerequisites
### Hardware
- HackRF (for TX)
- RTL-SDR (for RX)

### Software
- Python 3
- SDR sharp
- EPIRB plotter
- GNU Radio Companion
- Virtual Audio Cable

## Encoding
Using encoder.py, there are two ways to encode the data for transmission: one for BPSK format and one for WAV format. Either of them is acceptable. If any data is changed, the program will calculate the BCH code accordingly. For more information, kindly have a look at the [Specification for COSPAS-SARSAT 406 MHz Distress Beacons](https://sar.mot.go.th/document/THMCC/T001-MAR-26-2021%20SPECIFICATION%20FOR%20COSPAS-SARSAT%20406%20MHz%20DISTRESS%20BEACONS.pdf)

## Signal Transmission
To transmit the signal, you will need a HackRF (it is tested with HackRF, however, with some adjustment other SDRs e.g., Pluto, USRP, BladeRF may also work). If you're using the BPSK format, use the "BPSK_mode.grc" file; if you're using the WAV format, use the "NFM_mode.grc" file. It's very straightforward: simply select the desired file. Optionally, you can adjust the transmission gain, frequency, etc.

## Signal Receiption
Tune the transmission frequency. Choose the NFM mode in SDR Sharp software to ensure accurate audio. Route the audio to the EPIRB plotter using a virtual audio cable. Alternatively, you can record the audio for later processing. If you receive a signal from a satellite, you may need to use the Doppler correction library in SDR Sharp to correct the Doppler shift.

## Verification
The EPIRB plotter will display the decoded data. Alternatively, we have provided the verification.py script to verify the MAC. Please note that we used a 48K sampling rate in audio recording. If you recorded the audio using a different sampling rate, you may need to either resample it to 48K or change the source code for the proper sample rate to match Manchester encoding.

