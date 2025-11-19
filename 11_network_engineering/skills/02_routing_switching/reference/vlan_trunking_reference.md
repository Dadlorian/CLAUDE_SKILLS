# VLAN and Trunking Quick Reference

## VLAN Fundamentals

- **Standard Range:** 1-1005 (VLAN 1 is default, 1002-1005 reserved for Token Ring/FDDI)
- **Extended Range:** 1006-4094 (requires VTP version 3 or off)
- **Default VLAN:** 1 (cannot be deleted, all ports default to VLAN 1)
- **Management VLAN:** Typically VLAN 99 or higher for administrative access
- **Data VLANs:** 2-1001 standard range for user traffic
- **Voice VLAN:** Separate VLAN for VoIP traffic (typically 110-199 range)

## VLAN Configuration Commands

```
! Create VLAN
vlan 10
  name Sales

! Assign port to VLAN
interface FastEthernet0/1
  switchport mode access
  switchport access vlan 10

! Verify VLAN
show vlan [brief | id 10 | name Sales]
show interfaces vlan 10
```

## Trunking Protocols

### 802.1Q (Recommended)
- **Standard:** IEEE 802.1Q
- **Tag Location:** 4-byte tag after source MAC address
- **Tag Format:** TPID (16-bit) + PCP (3-bit) + CFI (1-bit) + VLAN ID (12-bit)
- **VLAN Range:** All 4094 VLANs (native VLAN untagged)
- **Native VLAN:** Untagged on trunk, default VLAN 1
- **Scope:** Industry standard, multi-vendor support

### ISL (Legacy)
- **Proprietary:** Cisco proprietary
- **Encapsulation:** Complete frame reencapsulation
- **Tag Location:** ISL header prepended (26 bytes)
- **VLAN Range:** 1-4094
- **Overhead:** 30 bytes additional per frame
- **Scope:** Cisco-only, largely obsolete

## Trunk Configuration

```
! Configure trunk (static)
interface GigabitEthernet0/1
  switchport mode trunk
  switchport trunk encapsulation dot1q
  switchport trunk native vlan 99
  switchport trunk allowed vlan 10,20,30,99

! Dynamic Trunking Protocol (DTP) - negotiation
interface GigabitEthernet0/1
  switchport dynamic desirable  ! Initiates negotiation
  switchport dynamic auto       ! Responds to negotiation

! Disable DTP (security best practice)
interface GigabitEthernet0/1
  switchport nonegotiate
```

## Native VLAN

| Setting | Behavior | Risk |
|---------|----------|------|
| Mismatch | Frames loop | Major (STP may not prevent) |
| Tagged | Native VLAN frames tagged | Incompatibility |
| Untagged | Native VLAN frames untagged | Standard behavior |

## Trunk Allowed VLANs

```
! Allow specific VLANs
switchport trunk allowed vlan 10,20,30,99

! Add VLAN to allowed list
switchport trunk allowed vlan add 40

! Remove VLAN from allowed list
switchport trunk allowed vlan remove 25

! Allow all VLANs
switchport trunk allowed vlan all

! Except specific VLANs
switchport trunk allowed vlan except 1,1002-1005
```

## Trunk Port Negotiation

| Local Mode | Remote: Dynamic Desirable | Remote: Dynamic Auto | Remote: Static Trunk | Remote: Static Access |
|-----------|--------------------------|----------------------|----------------------|----------------------|
| Dynamic Desirable | Trunk | Trunk | Trunk | Access |
| Dynamic Auto | Trunk | Access | Trunk | Access |
| Static Trunk | Trunk | Trunk | Trunk | ✗ Mismatch |
| Static Access | Access | Access | ✗ Mismatch | Access |

**Best Practice:** Use `switchport mode trunk` + `switchport nonegotiate`

## Voice VLAN

```
! Configure voice VLAN on access port
interface FastEthernet0/1
  switchport mode access
  switchport access vlan 10                ! Data VLAN
  switchport voice vlan 110                 ! Voice VLAN
  mls qos trust cos                        ! Trust CoS marking from phones

! Verify voice VLAN
show interfaces FastEthernet0/1 switchport
```

## Private VLAN (PVLAN)

- **Purpose:** Layer 2 traffic isolation within VLAN
- **Types:**
  - **Primary VLAN:** Primary VLAN ID (e.g., 100)
  - **Isolated VLAN:** Restricted communication (e.g., 101)
  - **Community VLAN:** Limited communication (e.g., 102)

```
! Configure PVLAN
vlan 100
  private-vlan primary
vlan 101
  private-vlan isolated
vlan 102
  private-vlan community

vlan 100
  private-vlan association 101,102

! Apply to port
interface FastEthernet0/1
  switchport private-vlan host-association 100 101
```

## Dynamic VLAN Assignment (802.1X)

```
aaa new-model
aaa authentication dot1x default group radius
dot1x system-auth-control

interface GigabitEthernet0/1
  authentication port-control auto
  dot1x pae authenticator
  access-session host-mode multi-auth
```

## VLAN Access Control Lists (VACLs)

```
! Create VACL
vlan access-map filter-sales 10
  match ip address 101
  action forward

vlan access-map filter-sales 20
  action forward

vlan filter filter-sales vlan-list 10,20,30
```

## Frame Tagging Process

### Untagged Frame (802.1Q Ingress)

1. Frame arrives on trunk port
2. Switch adds 4-byte 802.1Q tag
3. TPID = 0x8100, PCP = default, VID = port VLAN
4. Frame propagates through trunk
5. Tagged frame delivered to destination ports

### Frame Egress (802.1Q Egress)

1. If destination port = native VLAN: remove tag
2. If destination port = different VLAN: rewrite tag
3. If destination port = access port: remove tag if present

## VLAN Configuration Best Practices

1. Never use VLAN 1 for user traffic (management only)
2. Use contiguous VLAN ranges (easier to manage)
3. Implement voice VLANs separately from data
4. Document VLAN purpose and usage
5. Use meaningful VLAN names (Sales, Engineering, etc.)
6. Configure consistent native VLAN across trunk links
7. Disable DTP on inter-switch trunks (use static)
8. Implement VLAN pruning (allowed VLAN lists)
9. Use VLANs for security segmentation
10. Test trunk configuration with `show interfaces trunk`
