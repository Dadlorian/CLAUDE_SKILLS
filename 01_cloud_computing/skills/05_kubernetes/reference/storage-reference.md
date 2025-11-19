# Kubernetes Storage Reference

## Storage Overview

Kubernetes provides a sophisticated storage abstraction layer that decouples storage from pod lifecycles and enables portable, cloud-native storage management.

## Volume Types

### Ephemeral Volumes

**emptyDir**:
```yaml
volumes:
- name: cache
  emptyDir: {}
```
- Created when pod assigned to node
- Deleted when pod removed from node
- Shared between containers in pod
- Use cases: cache, scratch space, inter-container communication

**emptyDir with memory backing**:
```yaml
volumes:
- name: mem-cache
  emptyDir:
    medium: Memory
    sizeLimit: 1Gi
```

**configMap**:
```yaml
volumes:
- name: config
  configMap:
    name: app-config
    items:
    - key: app.properties
      path: config/app.properties
```

**secret**:
```yaml
volumes:
- name: credentials
  secret:
    secretName: db-credentials
    items:
    - key: username
      path: user
    - key: password
      path: pass
```

**downwardAPI**:
```yaml
volumes:
- name: podinfo
  downwardAPI:
    items:
    - path: "labels"
      fieldRef:
        fieldPath: metadata.labels
    - path: "cpu_limit"
      resourceFieldRef:
        containerName: app
        resource: limits.cpu
```

### Persistent Volumes

**hostPath** (single-node testing only):
```yaml
volumes:
- name: data
  hostPath:
    path: /mnt/data
    type: DirectoryOrCreate
```

**nfs**:
```yaml
volumes:
- name: nfs-volume
  nfs:
    server: nfs-server.example.com
    path: /exported/path
```

**Cloud Provider Volumes**:
- **awsElasticBlockStore**: AWS EBS
- **azureDisk**: Azure Disk
- **azureFile**: Azure Files
- **gcePersistentDisk**: GCE Persistent Disk

**CSI (Container Storage Interface)**:
```yaml
volumes:
- name: csi-volume
  csi:
    driver: ebs.csi.aws.com
    volumeHandle: vol-0123456789abcdef
    fsType: ext4
```

## Persistent Volumes (PV)

### PersistentVolume Example
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-nfs
spec:
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs
  mountOptions:
  - hard
  - nfsvers=4.1
  nfs:
    server: nfs-server.example.com
    path: /exports/data
```

### Access Modes
- **ReadWriteOnce (RWO)**: Single node read-write
- **ReadOnlyMany (ROX)**: Multiple nodes read-only
- **ReadWriteMany (RWX)**: Multiple nodes read-write
- **ReadWriteOncePod (RWOP)**: Single pod read-write (K8s 1.22+)

### Reclaim Policies
- **Retain**: Manual reclamation, preserves data
- **Delete**: Delete volume when PVC released (default for dynamic)
- **Recycle**: Deprecated, basic scrub (rm -rf)

### Volume Modes
- **Filesystem** (default): Mounted as directory
- **Block**: Raw block device

### PV Lifecycle

**Phases**:
1. **Available**: Free, not yet bound
2. **Bound**: Bound to PVC
3. **Released**: PVC deleted, not yet reclaimed
4. **Failed**: Automatic reclamation failed

### Node Affinity
```yaml
nodeAffinity:
  required:
    nodeSelectorTerms:
    - matchExpressions:
      - key: topology.kubernetes.io/zone
        operator: In
        values:
        - us-east-1a
```

## Persistent Volume Claims (PVC)

### PVC Example
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: fast-ssd
  selector:
    matchLabels:
      environment: production
```

### Using PVC in Pod
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mysql
spec:
  containers:
  - name: mysql
    image: mysql:8.0
    volumeMounts:
    - name: data
      mountPath: /var/lib/mysql
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: mysql-pvc
```

### PVC Binding
- Static: Manually created PV, PVC binds to it
- Dynamic: StorageClass provisions PV automatically

### Volume Expansion
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: expandable-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi  # Can be increased later
  storageClassName: expandable
```

**Requirements**:
- StorageClass must have `allowVolumeExpansion: true`
- CSI driver must support expansion
- Some require pod restart, some support online expansion

## Storage Classes

### StorageClass Example
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
  fsType: ext4
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
mountOptions:
- debug
```

### Provisioners

**Built-in (In-Tree, being deprecated)**:
- kubernetes.io/aws-ebs
- kubernetes.io/azure-disk
- kubernetes.io/gce-pd
- kubernetes.io/no-provisioner (local volumes)

**CSI Drivers** (recommended):
- ebs.csi.aws.com (AWS EBS)
- disk.csi.azure.com (Azure Disk)
- pd.csi.storage.gke.io (GCE Persistent Disk)
- csi.ceph.com (Ceph RBD)
- And many more...

### Volume Binding Modes

**Immediate** (default):
- PV provisioned immediately when PVC created
- May bind to PV in wrong zone for pod

**WaitForFirstConsumer** (recommended):
- Delays PV binding until pod using PVC is scheduled
- Ensures PV created in correct zone for pod
- Required for topology-aware provisioning

### Common Storage Classes

**AWS EBS**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

**Azure Disk**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: azure-premium
provisioner: disk.csi.azure.com
parameters:
  storageaccounttype: Premium_LRS
  kind: Managed
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

**GCE Persistent Disk**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gce-ssd
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
  replication-type: regional-pd
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

**Local Storage**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
```

## Volume Snapshots

### VolumeSnapshotClass
```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snapclass
driver: ebs.csi.aws.com
deletionPolicy: Delete
parameters:
  # Driver-specific parameters
```

### VolumeSnapshot
```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: mysql-snapshot
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: mysql-pvc
```

### Restore from Snapshot
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-restored
spec:
  dataSource:
    name: mysql-snapshot
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: fast-ssd
```

### Volume Cloning
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cloned-pvc
spec:
  dataSource:
    name: source-pvc
    kind: PersistentVolumeClaim
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: fast-ssd
```

## StatefulSet Storage

### Volume Claim Templates
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 10Gi
```

**Behavior**:
- Creates PVC for each pod: `data-mysql-0`, `data-mysql-1`, `data-mysql-2`
- PVCs persist when StatefulSet deleted (unless manually deleted)
- PVCs reattached when StatefulSet recreated

## CSI (Container Storage Interface)

### CSI Driver Architecture

**Components**:
1. **CSI Controller** (Deployment)
   - Provisioning/deletion
   - Attaching/detaching
   - Snapshotting
   - Resizing

2. **CSI Node** (DaemonSet)
   - Mounting/unmounting
   - Volume statistics

### Popular CSI Drivers

**Cloud Providers**:
- AWS EBS CSI Driver
- AWS EFS CSI Driver
- Azure Disk CSI Driver
- Azure File CSI Driver
- GCE PD CSI Driver
- GCS Fuse CSI Driver

**Storage Systems**:
- Ceph CSI (RBD and CephFS)
- NetApp Trident
- Dell EMC PowerStore
- Pure Storage
- Portworx
- OpenEBS

**Special Purpose**:
- NFS CSI Driver
- SMB CSI Driver
- Local Path Provisioner
- HostPath CSI Driver (testing)

### CSI Features

**Supported Operations**:
- Dynamic provisioning
- Pre-provisioned volumes
- Volume snapshots
- Volume cloning
- Volume expansion
- Volume metrics
- Topology awareness
- Raw block volumes
- Ephemeral volumes
- ReadWriteOncePod access mode

### CSI Volume Example
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: csi-pv
spec:
  capacity:
    storage: 5Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Delete
  csi:
    driver: ebs.csi.aws.com
    volumeHandle: vol-0123456789abcdef
    fsType: ext4
    volumeAttributes:
      storage: "5Gi"
```

## Local Persistent Volumes

### Local PV Example
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Delete
  storageClassName: local-storage
  local:
    path: /mnt/disks/ssd1
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - node-1
```

### Local Volume Static Provisioner
- Discovers local disks
- Creates PVs automatically
- Used for high-performance workloads

### Use Cases
- Distributed databases (Cassandra, ScyllaDB)
- Distributed file systems (GlusterFS, Ceph)
- High-performance computing
- Edge computing

**Limitations**:
- No volume replication
- Node failure = data loss (unless application replicates)
- Manual disk management
- No dynamic provisioning

## Storage Best Practices

### Performance

**Fast Storage**:
- Use SSD-backed volumes for databases
- Use provisioned IOPS for predictable performance
- Consider local volumes for maximum performance
- Use volume type appropriate for workload (gp3, io2, etc.)

**Large Files**:
- Use block storage for databases
- Use object storage (S3, GCS, Azure Blob) for large objects
- Use file storage (EFS, Azure Files) for shared access

### Reliability

**Backups**:
- Use VolumeSnapshots for point-in-time backups
- Regular snapshot schedules
- Test restore procedures
- Consider cross-region snapshots for DR

**High Availability**:
- Use regional persistent disks where available
- Application-level replication for stateful apps
- Pod disruption budgets
- Multi-zone StatefulSets

### Security

**Encryption**:
- Enable encryption at rest
- Use encrypted storage classes
- Manage encryption keys properly (KMS)

**Access Control**:
- Use RBAC for PV/PVC access
- Namespace isolation
- Read-only mounts where possible
- Security contexts (fsGroup, runAsUser)

### Cost Optimization

**Right-Sizing**:
- Monitor actual usage
- Use volume expansion instead of oversizing
- Delete unused PVCs (set reclaim policy appropriately)
- Use cheaper storage tiers for non-critical data

**Lifecycle Management**:
- Implement PVC cleanup policies
- Use TTL for temporary storage
- Archive old snapshots
- Use object storage for archival

### Capacity Planning

**Monitoring**:
- Track PVC usage
- Alert on high usage
- Monitor disk IOPS and throughput
- Capacity forecasting

**Quotas**:
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: storage-quota
spec:
  hard:
    requests.storage: 100Gi
    persistentvolumeclaims: "10"
```

## Troubleshooting

### Common Issues

**PVC Pending**:
- No available PV matches
- No StorageClass found
- Insufficient permissions
- Volume zone mismatch

**Pod ContainerCreating**:
- Volume mount failure
- Volume not attached
- Permission issues
- Filesystem corruption

**Volume Expansion Failed**:
- StorageClass doesn't allow expansion
- CSI driver doesn't support expansion
- Filesystem resize failed
- Online expansion not supported

### Debugging Commands

```bash
# Check PVC status
kubectl get pvc

# Check PV status
kubectl get pv

# Check storage classes
kubectl get sc

# Describe PVC
kubectl describe pvc <pvc-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check CSI driver logs
kubectl logs -n kube-system -l app=csi-driver

# Check volume attachments
kubectl get volumeattachment
```

## References

- [Kubernetes Storage](https://kubernetes.io/docs/concepts/storage/)
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Volume Snapshots](https://kubernetes.io/docs/concepts/storage/volume-snapshots/)
- [CSI Specification](https://github.com/container-storage-interface/spec)
