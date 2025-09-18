# 🚀 VSS Integration System - Deployment Guide

## Tổng quan

Hướng dẫn triển khai VSS Integration System lên môi trường production với Docker và Kubernetes.

## 📋 Yêu cầu hệ thống

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk**: 20GB SSD
- **Network**: 100Mbps

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Disk**: 50GB SSD
- **Network**: 1Gbps

## 🐳 Triển khai với Docker

### 1. Chuẩn bị môi trường

```bash
# Cài đặt Docker và Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Kiểm tra cài đặt
docker --version
docker-compose --version
```

### 2. Cấu hình môi trường

Tạo file `.env`:

```bash
# Database (Future)
POSTGRES_DB=vss_integration
POSTGRES_USER=vss_user
POSTGRES_PASSWORD=your_secure_password

# Redis (Future)
REDIS_PASSWORD=your_redis_password

# Application
VSS_LOG_LEVEL=INFO
VSS_MAX_WORKERS=4
VSS_ENTERPRISE_API_URL=https://thongtindoanhnghiep.co/api/company
VSS_VSS_API_URL=http://vssapp.teca.vn:8088
```

### 3. Build và chạy

```bash
# Build image
docker build -t vss-integration:latest .

# Chạy với Docker Compose
docker-compose up -d

# Kiểm tra logs
docker-compose logs -f vss-integration
```

### 4. Health Check

```bash
# Kiểm tra container
docker ps

# Test API
curl http://localhost:5000/health

# Test web interface
curl http://localhost:5000/
```

## ☸️ Triển khai với Kubernetes

### 1. Chuẩn bị cluster

```bash
# Tạo namespace
kubectl create namespace vss-integration

# Tạo secrets
kubectl create secret generic vss-secrets \
  --from-literal=postgres-password=your_secure_password \
  --from-literal=redis-password=your_redis_password \
  --namespace vss-integration
```

### 2. Deploy PostgreSQL (Future)

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: vss-integration
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: "vss_integration"
        - name: POSTGRES_USER
          value: "vss_user"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: vss-secrets
              key: postgres-password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
```

### 3. Deploy Redis (Future)

```yaml
# redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: vss-integration
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command: ["redis-server", "--requirepass", "$(REDIS_PASSWORD)"]
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: vss-secrets
              key: redis-password
        ports:
        - containerPort: 6379
```

### 4. Deploy Application

```yaml
# vss-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vss-integration
  namespace: vss-integration
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vss-integration
  template:
    metadata:
      labels:
        app: vss-integration
    spec:
      containers:
      - name: vss-integration
        image: vss-integration:latest
        ports:
        - containerPort: 5000
        env:
        - name: VSS_LOG_LEVEL
          value: "INFO"
        - name: VSS_MAX_WORKERS
          value: "4"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 5. Deploy Service

```yaml
# vss-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: vss-integration-service
  namespace: vss-integration
spec:
  selector:
    app: vss-integration
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

### 6. Deploy Ingress

```yaml
# vss-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vss-integration-ingress
  namespace: vss-integration
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: vss-integration.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vss-integration-service
            port:
              number: 80
```

### 7. Triển khai

```bash
# Apply configurations
kubectl apply -f postgres-deployment.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f vss-deployment.yaml
kubectl apply -f vss-service.yaml
kubectl apply -f vss-ingress.yaml

# Kiểm tra trạng thái
kubectl get pods -n vss-integration
kubectl get services -n vss-integration
kubectl get ingress -n vss-integration
```

## 🔧 Cấu hình nâng cao

### Horizontal Pod Autoscaling

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vss-integration-hpa
  namespace: vss-integration
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vss-integration
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### ConfigMap cho cấu hình

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: vss-config
  namespace: vss-integration
data:
  settings.json: |
    {
      "api": {
        "timeout": 45,
        "max_retries": 5
      },
      "processing": {
        "max_workers": 4,
        "batch_size": 50
      }
    }
```

## 📊 Monitoring và Logging

### Prometheus Metrics

```yaml
# prometheus-service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: vss-integration-monitor
  namespace: vss-integration
spec:
  selector:
    matchLabels:
      app: vss-integration
  endpoints:
  - port: web
    path: /metrics
    interval: 30s
```

### ELK Stack cho Logging

```yaml
# fluent-bit-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: vss-integration
data:
  fluent-bit.conf: |
    [INPUT]
        Name tail
        Path /app/logs/*.log
        Tag vss-integration.*

    [OUTPUT]
        Name elasticsearch
        Host elasticsearch-master
        Port 9200
        Index vss-integration
```

## 🔒 Security Best Practices

### Network Policies

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: vss-integration-netpol
  namespace: vss-integration
spec:
  podSelector:
    matchLabels:
      app: vss-integration
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 5000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

### Security Context

```yaml
# security-context.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vss-integration
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: vss-integration
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
```

## 🚀 CI/CD với GitHub Actions

Workflow đã được cấu hình trong `.github/workflows/ci.yml`:

- **Testing**: Chạy tests trên multiple Python versions
- **Linting**: Code formatting và security checks
- **Building**: Tạo Docker images
- **Deploy**: Tự động deploy lên staging/production

## 📞 Troubleshooting

### Common Issues

1. **Container không start**
   ```bash
   kubectl logs -n vss-integration deployment/vss-integration
   ```

2. **API timeout**
   - Tăng timeout trong config
   - Kiểm tra network connectivity

3. **High memory usage**
   - Giảm max_workers
   - Tăng memory limits

4. **Database connection failed**
   - Kiểm tra database credentials
   - Verify network policies

### Performance Tuning

```bash
# Monitor resource usage
kubectl top pods -n vss-integration

# Check logs
kubectl logs -f deployment/vss-integration -n vss-integration

# Scale deployment
kubectl scale deployment vss-integration --replicas=5 -n vss-integration
```

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Prometheus Monitoring](https://prometheus.io/docs/)

---

*Deployment Guide v2.0.0 - VSS Integration System*