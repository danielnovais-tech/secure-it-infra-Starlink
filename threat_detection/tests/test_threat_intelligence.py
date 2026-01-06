"""
Tests for Threat Intelligence Updater
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from threat_intelligence import ThreatIntelligenceUpdater


def test_ip_validation():
    """Test IP address validation"""
    config = {'feeds': {}}
    updater = ThreatIntelligenceUpdater(config)
    
    # Valid IPs
    assert updater._is_valid_ip('192.168.1.1') == True
    assert updater._is_valid_ip('10.0.0.1') == True
    assert updater._is_valid_ip('255.255.255.255') == True
    assert updater._is_valid_ip('0.0.0.0') == True
    
    # Invalid IPs
    assert updater._is_valid_ip('256.1.1.1') == False
    assert updater._is_valid_ip('192.168.1') == False
    assert updater._is_valid_ip('192.168.1.1.1') == False
    assert updater._is_valid_ip('abc.def.ghi.jkl') == False
    assert updater._is_valid_ip('') == False
    
    print("✓ IP validation test passed")


def test_parse_plain_ip_list():
    """Test parsing plain IP list format"""
    config = {'feeds': {}}
    updater = ThreatIntelligenceUpdater(config)
    
    content = """# Comment line
192.168.1.1
10.0.0.5
# Another comment
172.16.0.1
invalid-ip
203.0.113.10
"""
    
    ips = updater._parse_plain_ip_list(content)
    
    assert len(ips) == 4
    assert '192.168.1.1' in ips
    assert '10.0.0.5' in ips
    assert '172.16.0.1' in ips
    assert '203.0.113.10' in ips
    assert 'invalid-ip' not in ips
    
    print("✓ Plain IP list parsing test passed")


def test_parse_dshield_feed():
    """Test parsing DShield format feed"""
    config = {'feeds': {}}
    updater = ThreatIntelligenceUpdater(config)
    
    content = """# DShield format
# IP	NETMASK	ATTACKS
192.168.1.100	24	1500
10.0.0.50	16	2000
# Comment
172.16.0.1	8	500
"""
    
    ips = updater._parse_dshield_feed(content)
    
    assert len(ips) == 3
    assert '192.168.1.100' in ips
    assert '10.0.0.50' in ips
    assert '172.16.0.1' in ips
    
    print("✓ DShield feed parsing test passed")


def test_threat_ip_checking():
    """Test checking if IP is in threat list"""
    config = {'feeds': {}}
    updater = ThreatIntelligenceUpdater(config)
    
    # Add some threat IPs manually
    updater.threat_ips = {'192.168.1.100', '10.0.0.50', '172.16.0.1'}
    
    # Check threat IPs
    assert updater.is_threat_ip('192.168.1.100') == True
    assert updater.is_threat_ip('10.0.0.50') == True
    
    # Check non-threat IP
    assert updater.is_threat_ip('8.8.8.8') == False
    
    print("✓ Threat IP checking test passed")


def test_get_threat_ips():
    """Test getting list of threat IPs"""
    config = {'feeds': {}}
    updater = ThreatIntelligenceUpdater(config)
    
    # Add threat IPs
    test_ips = {'192.168.1.1', '10.0.0.1', '172.16.0.1'}
    updater.threat_ips = test_ips
    
    threat_list = updater.get_threat_ips()
    
    assert len(threat_list) == 3
    assert set(threat_list) == test_ips
    
    print("✓ Get threat IPs test passed")


def test_save_and_load_threat_ips():
    """Test saving and loading threat IPs"""
    import tempfile
    
    config = {'feeds': {}}
    updater = ThreatIntelligenceUpdater(config)
    
    # Add threat IPs
    test_ips = {'192.168.1.1', '10.0.0.1', '172.16.0.1'}
    updater.threat_ips = test_ips
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        temp_file = f.name
    
    try:
        updater.save_threat_ips(temp_file)
        
        # Create new updater and load
        updater2 = ThreatIntelligenceUpdater(config)
        updater2.load_threat_ips(temp_file)
        
        assert updater2.threat_ips == test_ips
        
        print("✓ Save and load threat IPs test passed")
    finally:
        os.unlink(temp_file)


if __name__ == '__main__':
    test_ip_validation()
    test_parse_plain_ip_list()
    test_parse_dshield_feed()
    test_threat_ip_checking()
    test_get_threat_ips()
    test_save_and_load_threat_ips()
    print("\n✓ All threat intelligence tests passed!")
