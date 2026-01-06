#!/usr/bin/env python3
"""
VPN Manager CLI
Command-line interface for managing VPN connections with YAML configuration
"""

import sys
import argparse
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from vpn_manager import VPNManager


def main():
    """Main entry point for VPN Manager CLI."""
    parser = argparse.ArgumentParser(
        description='VPN Manager - YAML-based VPN management for Starlink infrastructure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor VPN with default config
  python main.py monitor
  
  # Check VPN status
  python main.py status
  
  # Connect to VPN
  python main.py connect
  
  # Disconnect from VPN
  python main.py disconnect
  
  # Use custom config file
  python main.py --config /path/to/config.yaml monitor
        """
    )
    
    parser.add_argument(
        '--config',
        '-c',
        type=str,
        default='config/vpn_config.yaml',
        help='Path to VPN configuration YAML file (default: config/vpn_config.yaml)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Monitor command
    subparsers.add_parser(
        'monitor',
        help='Start monitoring VPN connection with auto-reconnection'
    )
    
    # Status command
    subparsers.add_parser(
        'status',
        help='Check current VPN connection status'
    )
    
    # Connect command
    subparsers.add_parser(
        'connect',
        help='Connect to VPN'
    )
    
    # Disconnect command
    subparsers.add_parser(
        'disconnect',
        help='Disconnect from VPN'
    )
    
    args = parser.parse_args()
    
    # Show help if no command specified
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Get absolute path to config file
    config_path = os.path.abspath(args.config)
    
    # Check if config file exists
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
    
    try:
        # Initialize VPN Manager
        vpn_manager = VPNManager(config_path)
        
        # Execute command
        if args.command == 'monitor':
            print("Starting VPN monitoring... (Press Ctrl+C to stop)")
            vpn_manager.monitor()
            
        elif args.command == 'status':
            status = vpn_manager.get_vpn_status()
            print("\n" + "="*50)
            print("VPN Status Report")
            print("="*50)
            print(f"Connection Name: {status['connection_name']}")
            print(f"Connected: {'Yes' if status['connected'] else 'No'}")
            print(f"Healthy: {'Yes' if status['healthy'] else 'No'}")
            print(f"Timestamp: {status['timestamp']}")
            print("="*50 + "\n")
            
            # Exit with appropriate code
            sys.exit(0 if status['connected'] and status['healthy'] else 1)
            
        elif args.command == 'connect':
            print("Attempting to connect to VPN...")
            if vpn_manager.connect_vpn():
                print("Successfully connected to VPN")
                sys.exit(0)
            else:
                print("Failed to connect to VPN")
                sys.exit(1)
                
        elif args.command == 'disconnect':
            print("Attempting to disconnect from VPN...")
            if vpn_manager.disconnect_vpn():
                print("Successfully disconnected from VPN")
                sys.exit(0)
            else:
                print("Failed to disconnect from VPN")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
