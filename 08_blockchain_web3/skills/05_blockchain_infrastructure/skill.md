# Blockchain Infrastructure

## Overview
Deploy and maintain blockchain nodes, validators, indexers, and infrastructure services. Master node operations, monitoring, DevOps practices, and infrastructure as code for blockchain systems.

## Node Operations

### 1. Ethereum Nodes
- **Execution Clients**: Geth, Nethermind, Besu, Erigon
- **Consensus Clients**: Prysm, Lighthouse, Teku, Nimbus
- **Archive Nodes**: Full historical state
- **Light Clients**: Minimal resource requirements
- **RPC Nodes**: JSON-RPC endpoint provision

### 2. Node Setup
```bash
# Geth installation
sudo apt-get install geth

# Run Geth node
geth --http --http.api eth,net,web3 --syncmode snap

# Lighthouse beacon node
lighthouse bn --network mainnet --http

# Lighthouse validator
lighthouse vc --network mainnet
```

### 3. Node Configuration
```toml
# Geth config.toml
[Eth]
SyncMode = "snap"
NetworkId = 1

[Node]
HTTPHost = "0.0.0.0"
HTTPPort = 8545
HTTPVirtualHosts = ["*"]

[Node.HTTPModules]
Modules = ["eth", "net", "web3"]
```

## Validator Operations

### 1. Validator Setup
- **Hardware Requirements**: CPU, RAM, SSD, network
- **Key Management**: Secure key generation and storage
- **Deposit Process**: 32 ETH stake for Ethereum
- **Client Diversity**: Run minority clients
- **Slashing Protection**: Prevent double signing

### 2. Staking Operations
```bash
# Generate validator keys
./deposit new-mnemonic --num_validators 1 --chain mainnet

# Import keys to validator
lighthouse account validator import --directory keys

# Start validator
lighthouse validator --network mainnet --beacon-nodes http://localhost:5052
```

### 3. Monitoring
- **Uptime Tracking**: Monitor validator online status
- **Attestation Performance**: Track inclusion distance
- **Reward Tracking**: Monitor staking rewards
- **Slashing Prevention**: Alert on misconfigurations
- **Sync Status**: Ensure node is synced

## Indexing Services

### 1. The Graph Protocol
```graphql
# GraphQL schema
type Transfer @entity {
  id: ID!
  from: Bytes!
  to: Bytes!
  value: BigInt!
  timestamp: BigInt!
}

# Subgraph mapping
export function handleTransfer(event: Transfer): void {
  let transfer = new TransferEntity(
    event.transaction.hash.toHex() + "-" + event.logIndex.toString()
  );

  transfer.from = event.params.from;
  transfer.to = event.params.to;
  transfer.value = event.params.value;
  transfer.timestamp = event.block.timestamp;

  transfer.save();
}
```

### 2. Custom Indexers
- **Event Listening**: Subscribe to contract events
- **Data Processing**: Parse and transform events
- **Database Storage**: Store indexed data
- **API Layer**: Expose data via GraphQL/REST
- **Real-time Updates**: WebSocket support

### 3. Indexer Stack
```javascript
// Event listener with ethers.js
const contract = new ethers.Contract(address, abi, provider);

contract.on('Transfer', async (from, to, amount, event) => {
    await db.transfers.create({
        transactionHash: event.transactionHash,
        blockNumber: event.blockNumber,
        from,
        to,
        amount: amount.toString()
    });
});
```

## Infrastructure as Code

### 1. Terraform
```hcl
# AWS EC2 for Ethereum node
resource "aws_instance" "eth_node" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "m5.2xlarge"

  root_block_device {
    volume_size = 2000
    volume_type = "gp3"
  }

  user_data = file("scripts/install_geth.sh")

  tags = {
    Name = "ethereum-node"
  }
}
```

### 2. Docker Deployment
```dockerfile
# Dockerfile for Geth
FROM ethereum/client-go:latest

COPY genesis.json /root/genesis.json

RUN geth init /root/genesis.json

EXPOSE 8545 8546 30303

CMD ["geth", "--http", "--http.addr", "0.0.0.0"]
```

### 3. Kubernetes
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: geth
spec:
  serviceName: geth
  replicas: 3
  selector:
    matchLabels:
      app: geth
  template:
    metadata:
      labels:
        app: geth
    spec:
      containers:
      - name: geth
        image: ethereum/client-go:latest
        ports:
        - containerPort: 8545
        volumeMounts:
        - name: data
          mountPath: /root/.ethereum
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 2Ti
```

## Monitoring & Alerting

### 1. Prometheus Metrics
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'geth'
    static_configs:
      - targets: ['localhost:6060']

  - job_name: 'lighthouse'
    static_configs:
      - targets: ['localhost:5054']
```

### 2. Grafana Dashboards
- Node sync status
- Block production rate
- Peer connections
- Memory/CPU usage
- Disk I/O
- Network bandwidth

### 3. Alerting Rules
```yaml
groups:
  - name: node_alerts
    rules:
      - alert: NodeNotSyncing
        expr: eth_sync_status == 0
        for: 5m
        annotations:
          summary: "Node is not syncing"

      - alert: LowPeerCount
        expr: eth_peers < 5
        for: 10m
        annotations:
          summary: "Low peer count"
```

## RPC Services

### 1. Load Balancing
```nginx
upstream eth_rpc {
    least_conn;
    server node1:8545;
    server node2:8545;
    server node3:8545;
}

server {
    listen 443 ssl;
    server_name rpc.example.com;

    location / {
        proxy_pass http://eth_rpc;
        proxy_set_header Host $host;
    }
}
```

### 2. Rate Limiting
```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
    windowMs: 1000, // 1 second
    max: 10, // 10 requests per second
    message: 'Too many requests'
});

app.use('/v1/', limiter);
```

### 3. Caching
```javascript
const redis = require('redis');
const client = redis.createClient();

async function cachedRPC(method, params) {
    const key = `rpc:${method}:${JSON.stringify(params)}`;
    const cached = await client.get(key);

    if (cached) return JSON.parse(cached);

    const result = await provider.send(method, params);
    await client.set(key, JSON.stringify(result), 'EX', 60);

    return result;
}
```

## Security

### 1. Firewall Rules
```bash
# UFW firewall
sudo ufw allow 30303/tcp  # P2P
sudo ufw allow 30303/udp
sudo ufw deny 8545/tcp    # RPC - only local
sudo ufw enable
```

### 2. SSL/TLS
```bash
# Certbot for Let's Encrypt
sudo certbot --nginx -d rpc.example.com
```

### 3. Key Management
- Hardware wallets for validator keys
- Encrypted key storage
- Key backup procedures
- HSM integration for production

## Backup & Recovery

### 1. Database Backups
```bash
# Backup chaindata
tar -czf chaindata-backup.tar.gz ~/.ethereum/geth/chaindata

# Upload to S3
aws s3 cp chaindata-backup.tar.gz s3://backups/
```

### 2. Disaster Recovery
- Automated backup schedules
- Off-site backup storage
- Recovery time objectives (RTO)
- Recovery point objectives (RPO)
- Regular restore testing

## Cost Optimization

### 1. Resource Optimization
- Right-size instances
- Use spot instances
- Optimize storage (gp3 vs io2)
- Network egress optimization
- Reserved instances for stable workloads

### 2. Monitoring Costs
```python
# AWS cost tracking
import boto3

ce = boto3.client('ce')

response = ce.get_cost_and_usage(
    TimePeriod={
        'Start': '2024-01-01',
        'End': '2024-01-31'
    },
    Granularity='DAILY',
    Metrics=['UnblendedCost']
)
```

## Performance Tuning

### 1. Geth Optimization
```bash
geth \
    --cache 8192 \
    --maxpeers 50 \
    --txlookuplimit 0 \
    --syncmode snap \
    --state.scheme path
```

### 2. System Tuning
```bash
# Increase file descriptors
ulimit -n 65536

# Optimize disk I/O
sudo echo deadline > /sys/block/nvme0n1/queue/scheduler
```

## Multi-Chain Infrastructure

### 1. Chain-Specific Nodes
- Ethereum (Geth, Nethermind)
- Polygon (Bor, Heimdall)
- Arbitrum (Nitro)
- Optimism (op-geth, op-node)
- BSC (Geth fork)

### 2. Cross-Chain Indexing
```javascript
const chains = {
    ethereum: { rpc: 'https://eth.llamarpc.com', chainId: 1 },
    polygon: { rpc: 'https://polygon-rpc.com', chainId: 137 },
    arbitrum: { rpc: 'https://arb1.arbitrum.io/rpc', chainId: 42161 }
};

for (const [name, config] of Object.entries(chains)) {
    const provider = new ethers.JsonRpcProvider(config.rpc);
    // Index each chain
}
```

## Resources

### Documentation
- Ethereum Node Documentation
- Lighthouse Book
- Geth Documentation
- The Graph Documentation
- Kubernetes Documentation

### Tools
- Prometheus
- Grafana
- Terraform
- Docker
- Ansible

## Conclusion

Blockchain infrastructure requires expertise in DevOps, distributed systems, and blockchain-specific knowledge. Focus on reliability, security, and cost optimization for successful infrastructure operations.
