#!/usr/bin/env python

import carla

import time
import argparse

def main():

    argparser = argparse.ArgumentParser()
        
    argparser.add_argument(
        '--host',
        metavar='H',
        default='localhost',
        help='IP of the host server (default: localhost)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '--fixed-delta-seconds',
        metavar='T',
        default=0.05,
        type=float,
        help='Fixed delta seconds (default: 0.05s)')
    argparser.add_argument(
        '--timeout',
        metavar='T',
        default=10.0,
        type=float,
        help='Connection timeout duration (default: 10.0s)')
    argparser.add_argument(
        '--sleep',
        metavar='T',
        default=0.05,
        type=float,
        help='Sleep (default: 0.05s)')

    args = argparser.parse_args()
        
    client = carla.Client(args.host, args.port)
    client.set_timeout(args.timeout)

    world = client.get_world()
    
    new_settings = world.get_settings()
    new_settings.synchronous_mode = True
    new_settings.fixed_delta_seconds = args.fixed_delta_seconds
    
    world.apply_settings(new_settings) 
    
    while True:
        if(args.sleep > 0.0):
            time.sleep(args.sleep)

        world.tick()


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
