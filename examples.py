#!/usr/bin/env python3
"""
Example script demonstrating VPN Manager API usage
Shows how to integrate VPN management into your own applications
"""

from vpn_manager import VPNManager
import time
import sys


def example_basic_usage():
    """Basic VPN manager usage example"""
    print("=== Basic VPN Manager Usage ===\n")
    
    # Initialize the manager
    manager = VPNManager('config/vpn_config.yaml')
    
    # Check current status
    print("1. Checking VPN status...")
    status = manager.get_vpn_status()
    print(f"   Connected: {status['connected']}")
    print(f"   Healthy: {status['healthy']}")
    print(f"   Connection: {status['connection_name']}\n")
    
    # Get configuration info
    print("2. Configuration details:")
    print(f"   VPN Type: {manager.config['vpn']['connection']['type']}")
    print(f"   Check Interval: {manager.config['vpn']['monitoring']['check_interval']}s")
    print(f"   Auto-reconnect: {manager.config['vpn']['monitoring']['auto_reconnect']}\n")


def example_connection_management():
    """Example of managing VPN connections"""
    print("=== VPN Connection Management ===\n")
    
    manager = VPNManager('config/vpn_config.yaml')
    
    # Connect to VPN
    print("1. Attempting to connect to VPN...")
    if manager.connect_vpn():
        print("   ✓ Successfully connected to VPN\n")
        
        # Wait and check status
        time.sleep(2)
        status = manager.get_vpn_status()
        print(f"   Status after connection: {status['connected']}\n")
        
        # Disconnect
        print("2. Disconnecting from VPN...")
        if manager.disconnect_vpn():
            print("   ✓ Successfully disconnected\n")
    else:
        print("   ✗ Failed to connect (may need root permissions)\n")


def example_monitoring_loop():
    """Example of a custom monitoring loop"""
    print("=== Custom Monitoring Loop ===\n")
    print("Monitoring VPN for 30 seconds...\n")
    
    manager = VPNManager('config/vpn_config.yaml')
    
    # Custom monitoring loop
    iterations = 3
    for i in range(iterations):
        status = manager.get_vpn_status()
        
        print(f"Check {i+1}/{iterations}:")
        print(f"  Time: {status['timestamp']}")
        print(f"  Connected: {status['connected']}")
        print(f"  Healthy: {status['healthy']}")
        
        if not status['connected']:
            print("  ⚠ VPN is disconnected!")
            if manager.config['vpn']['monitoring']['auto_reconnect']:
                print("  → Attempting reconnection...")
                if manager.auto_reconnect():
                    print("  ✓ Reconnected successfully")
                else:
                    print("  ✗ Reconnection failed")
        elif not status['healthy']:
            print("  ⚠ VPN connection is unhealthy!")
        else:
            print("  ✓ VPN is healthy")
        
        print()
        
        if i < iterations - 1:
            time.sleep(10)


def example_health_check():
    """Example of health check functionality"""
    print("=== VPN Health Check ===\n")
    
    manager = VPNManager('config/vpn_config.yaml')
    
    # Get status with health check
    status = manager.get_vpn_status()
    
    print(f"Connection Status: {status['connected']}")
    print(f"Health Status: {status['healthy']}")
    
    if status['connected'] and not status['healthy']:
        print("\n⚠ Warning: VPN is connected but health check failed!")
        print("This may indicate:")
        print("  - DNS resolution issues")
        print("  - Firewall blocking traffic")
        print("  - Routing problems")
        print("  - Test hosts unreachable")
    elif not status['connected']:
        print("\n⚠ VPN is not connected")
    else:
        print("\n✓ VPN is connected and healthy")


def main():
    """Main function to run examples"""
    print("\n" + "="*60)
    print("VPN Manager API Usage Examples")
    print("="*60 + "\n")
    
    examples = {
        '1': ('Basic Usage', example_basic_usage),
        '2': ('Connection Management', example_connection_management),
        '3': ('Monitoring Loop', example_monitoring_loop),
        '4': ('Health Check', example_health_check),
        '5': ('Run All Examples', None),
    }
    
    # If no arguments, show menu
    if len(sys.argv) == 1:
        print("Available examples:")
        for key, (name, _) in examples.items():
            print(f"  {key}. {name}")
        print("\nUsage: python examples.py [example_number]")
        print("Example: python examples.py 1")
        return
    
    choice = sys.argv[1]
    
    try:
        if choice == '5':
            # Run all examples
            for key, (name, func) in examples.items():
                if key != '5':
                    print(f"\nRunning Example {key}: {name}")
                    print("-" * 60)
                    func()
                    print()
        elif choice in examples and examples[choice][1]:
            name, func = examples[choice]
            print(f"\nRunning Example: {name}")
            print("-" * 60)
            func()
        else:
            print(f"Invalid example number: {choice}")
            print("Choose from: 1, 2, 3, 4, or 5")
    except Exception as e:
        print(f"\n✗ Error running example: {e}")
        print("\nNote: Some examples require:")
        print("  - Valid VPN configuration")
        print("  - Root/sudo permissions")
        print("  - VPN software installed (OpenVPN/WireGuard)")


if __name__ == '__main__':
    main()
