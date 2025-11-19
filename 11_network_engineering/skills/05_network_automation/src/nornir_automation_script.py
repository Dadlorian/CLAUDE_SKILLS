#!/usr/bin/env python3
"""Nornir-based network automation tasks"""

from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_get
from nornir.plugins.functions.text import print_result

def get_device_facts(task: Task) -> Result:
    """Get device facts using NAPALM"""
    result = task.run(
        task=napalm_get,
        getters=["facts", "interfaces", "arp_table"]
    )
    
    facts = result[0].result
    
    return Result(
        host=task.host,
        result={
            'hostname': facts['facts']['hostname'],
            'vendor': facts['facts']['vendor'],
            'interfaces': len(facts['interfaces']),
            'arp_entries': len(facts['arp_table'])
        }
    )

def main():
    """Execute Nornir tasks"""
    nr = InitNornir(config_file="nornir/config.yaml")
    
    print("Running device fact collection...")
    results = nr.run(task=get_device_facts)
    
    print_result(results)
    
    # Summary
    success = sum(1 for r in results.values() if not r.failed)
    failed = sum(1 for r in results.values() if r.failed)
    
    print(f"\nSummary: {success} succeeded, {failed} failed")

if __name__ == '__main__':
    main()
