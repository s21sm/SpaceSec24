# -*- coding: utf-8 -*-
"""Verification.ipynb

"""

#!pip install pydub

import wave
import hashlib
import hmac
import os
import time
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

with wave.open('example/audio.wav', 'rb') as wav_file:
    # Get the audio file's properties
    channels = wav_file.getnchannels()
    sample_width = wav_file.getsampwidth()
    frame_rate = wav_file.getframerate()
    num_frames = wav_file.getnframes()
    print(channels,sample_width,frame_rate,num_frames)
    frames = wav_file.readframes(num_frames)

# Convert the binary data to a numpy array
data = np.frombuffer(frames, dtype=np.uint8)
# Normalize the data to the range [-1, 1]
data = (data.astype(np.float32) - 128) / 128.0

preambel_members = []
binary_value =[]
skip_iterations = 0

samples_per_bit = frame_rate/400
samples_per_half_bit = int(samples_per_bit/2)

for i in range(len(data)):
    if skip_iterations > 0:
        skip_iterations -= 1
        continue

    if i < len(data)-samples_per_bit :

      first_part = data [i:i+samples_per_half_bit]
      second_part = data [i+samples_per_half_bit:i+samples_per_half_bit+samples_per_half_bit]


      first_part_avg = sum(first_part)/len(first_part)
      second_part_avg = sum(second_part)/len(second_part)

      first_part_max = max(first_part)
      second_part_max = max(second_part)
      first_part_min = min(first_part)
      second_part_min = min(second_part)

      first_part_max_index = i+ np.argmax(first_part)
      second_part_max_index = i+samples_per_half_bit+ np.argmax(second_part)
      first_part_min_index = i+ np.argmin(first_part)
      second_part_min_index = i+samples_per_half_bit+ np.argmin(second_part)



      if first_part_avg > second_part_avg and i == first_part_min_index and first_part_max != first_part_min and second_part_max != second_part_min:
        skip_iterations = samples_per_half_bit

        if preambel_members== []:
          preambel_members.append(i)
        elif len(preambel_members)>=1:
          if samples_per_bit-10 <= (i - preambel_members[-1]) <= samples_per_bit+10:
            preambel_members.append(i)
          else:
            preambel_members.clear()

        if len(preambel_members)>= 10:   ## standard preamble length is 15, however it is better to start with bit smaller number because of noisy RF
          print("preamble detected")
          print(preambel_members)
          break


# Check if the event never occurred in consecutive 10 iterations
if len(preambel_members) < 10:
    print("preamble was not detected")


preambel_members_values = list(map(lambda index: data[index], preambel_members))
x = np.arange(0, len(data))
fig = plt.figure(figsize=(24, 3))
plt.plot(x, data)
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('Transmitted signal')
plt.scatter(preambel_members, preambel_members_values, s=240, color='red')
plt.grid(True)
plt.show()

starting_point = preambel_members[1] # Good and safe to start after few preamble, due to inital brust low values
binary_values = []
for i in range(starting_point, starting_point +53520, 120):  
    if i + 120 > len(data):
        break
    first_part  = data[i+5:i+55]
    second_part = data [i+65:i+115]
    first_part_avg = sum(first_part)/50
    second_part_avg = sum(second_part)/50

    if first_part_avg > second_part_avg:
      binary_values.append(1)
    elif second_part_avg > first_part_avg:
      binary_values.append(0)
    else:
      binary_values.append(2) # adding error


if len(binary_values)>=431: 
  if 2 not in binary_values: # check there in no error inside data
    first_zero_index = binary_values.index(0)
    binary_values = [1]*15 + binary_values[first_zero_index:] # adding 15 1's as preamble
    msg_and_time = binary_values[0:175]
    mac = binary_values[175:431]
    clock = binary_values[144:175]

    # Convert binary list to a string
    msg_string = ''.join(str(bit) for bit in msg_and_time)
    mac_string = ''.join(str(bit) for bit in mac)
    clock_string = ''.join(str(bit) for bit in clock)
    # Convert binary string to hexadecimal string
    hex_msg = hex(int(msg_string, 2))
    mac_msg = hex(int(mac_string, 2))
    clock_msg = hex(int(clock_string, 2))
    print("Retrieved Message and Timestamp: ", hex_msg)
    print("Retrieved MAC:", mac_msg)
    print("Retrieved Timestampe", clock_msg)
  else:
    print('Incorrect data')

else:
  print('Not sufficient data')

# This is our Shared Secret
shared_key = b'\r\xa1\x14&\x1d>\xbaIw\x82\x94\x11\xaa\x1a\xa5\x88\xa7\xef\xaf\x1ab\x17\xd6\xbbm\xc6KZ/\xe7vh'
# There should be a threshold between transmission and verification time after receiption
# We have put a larger number because users of this proram will use if after a long time.
# This period need to be adjust
threshold_period = 10000000


current_timestamp = int(time.time())


# Received message
received_message = bytes([int(msg_string[i:i+8], 2) for i in range(0, len(msg_string), 8)]) # in byte format
# Received MAC
received_mac = bytes.fromhex(mac_msg[2:])
# Received time
received_time = bytes.fromhex(clock_msg[2:])
#Received time in iteger
received_timestamp = int.from_bytes(received_time[-8:], 'big')


if current_timestamp - received_timestamp < threshold_period:
  calculated_mac = hmac.new(shared_key, received_message, hashlib.sha256).digest()
  # Compare the calculated MAC with the received MAC
  if hmac.compare_digest(calculated_mac, received_mac):
      print("MAC validation successful. The message is authentic and unaltered.")
  else:
      print("Message authentication failed: MAC failure")

else:
  print("Message authentication failed: Timestamp expired")
