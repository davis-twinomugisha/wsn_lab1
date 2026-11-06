"""Capture a new serial log with host receipt timestamps. Requires pyserial.
Usage: python python/capture_serial.py --port COM6 --rows 600
The device counter is retained as a counter, not interpreted as elapsed seconds.
"""
import argparse,csv,time
from pathlib import Path
import serial

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--port',required=True)
 p.add_argument('--baud',type=int,default=115200)
 p.add_argument('--rows',type=int,default=600)
 p.add_argument('--timeout',type=float,default=1800)
 p.add_argument('--output',default='data/raw/hardware_timestamped.csv')
 a=p.parse_args()
 if a.rows<1:raise ValueError('rows must be positive')
 output=Path(a.output);output.parent.mkdir(parents=True,exist_ok=True)
 mapping={'temp':'temperature','light':'light_pct','timestamp':'device_counter'}
 count=0;header=None;writer=None;first=None;deadline=time.monotonic()+a.timeout
 with serial.Serial(a.port,a.baud,timeout=2) as ser, output.open('w',newline='') as f:
  print('Close the Arduino Serial Monitor. Reset the board to emit its CSV header.')
  while count<a.rows and time.monotonic()<deadline:
   parts=ser.readline().decode(errors='replace').strip().split(',')
   if len(parts)<2:continue
   if parts[0] in ('timestamp','temperature','sample'):
    incoming=[mapping.get(x,x) for x in parts]
    if header is not None and incoming!=header:raise ValueError('CSV schema changed during capture')
    header=incoming
    if writer is None:
     writer=csv.DictWriter(f,fieldnames=['host_elapsed_s']+header);writer.writeheader()
    continue
   if header is None or len(parts)!=len(header):continue
   now=time.monotonic()
   if first is None:first=now
   writer.writerow({'host_elapsed_s':f'{now-first:.6f}',**dict(zip(header,parts))})
   count+=1
  f.flush()
 print(f'Saved {count} rows to {output}')
 if count<a.rows:raise SystemExit('Capture ended before the requested number of rows.')

if __name__=='__main__':main()
