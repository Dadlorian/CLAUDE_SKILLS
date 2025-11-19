# Autoscaling Examples

This directory contains Kubernetes autoscaling configuration examples.

## Files

### HPA (Horizontal Pod Autoscaler)

1. **hpa-cpu-basic.yaml** - Basic CPU-based HPA
   - Scales from 3 to 10 replicas
   - Target: 70% CPU utilization

2. **hpa-multi-metric.yaml** - Advanced multi-metric HPA
   - Scales from 5 to 50 replicas
   - Metrics: CPU, Memory, Custom (RPS)
   - Advanced scaling behavior

### VPA (Vertical Pod Autoscaler)

3. **vpa-recommendations.yaml** - VPA in recommendations mode
   - Provides resource recommendations
   - Does not automatically apply changes
   - Safe to use alongside HPA

4. **vpa-auto.yaml** - VPA in auto mode
   - Automatically applies resource recommendations
   - Will restart pods to apply changes
   - Use carefully in production

### Complete Example

5. **complete-autoscaling-example.yaml** - Full stack example
   - Deployment with resource requests/limits
   - Service
   - HPA for horizontal scaling
   - VPA for resource optimization (recommendations)
   - PodDisruptionBudget for availability

## Usage

### Deploy HPA
```bash
kubectl apply -f hpa-cpu-basic.yaml
```

### View HPA status
```bash
kubectl get hpa -n production
kubectl describe hpa web-app-hpa -n production
```

### Deploy VPA
```bash
kubectl apply -f vpa-recommendations.yaml
```

### View VPA recommendations
```bash
kubectl describe vpa web-app-vpa -n production
```

### Deploy complete example
```bash
kubectl apply -f complete-autoscaling-example.yaml
```

### Monitor autoscaling
```bash
# Watch HPA
kubectl get hpa -n production --watch

# Watch pods
kubectl get pods -n production --watch

# Watch VPA recommendations
watch kubectl describe vpa web-app-vpa -n production
```

## Testing Autoscaling

### Generate load to trigger HPA
```bash
# Create load generator
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh

# Inside the pod
while true; do wget -q -O- http://web-app.production.svc.cluster.local; done
```

### Monitor scaling events
```bash
kubectl get events -n production --sort-by='.lastTimestamp'
```

## Best Practices

1. **Always set resource requests** - Required for HPA to work
2. **Use PodDisruptionBudgets** - Ensure availability during scaling
3. **Avoid VPA + HPA on same metric** - Use VPA in "Off" mode or scale different resources
4. **Monitor scaling behavior** - Watch for flapping or slow response
5. **Test thoroughly** - Validate autoscaling with load tests

## Troubleshooting

### HPA not scaling
```bash
# Check metrics availability
kubectl top pods -n production

# Check HPA status
kubectl describe hpa web-app-hpa -n production

# Verify resource requests are set
kubectl get deployment web-app -n production -o yaml | grep -A 5 resources
```

### VPA not providing recommendations
```bash
# Check VPA components
kubectl get pods -n kube-system | grep vpa

# Check VPA status
kubectl describe vpa web-app-vpa -n production
```
