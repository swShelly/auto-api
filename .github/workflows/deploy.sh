#!/bin/bash
# CI/CD 部署脚本辅助文件
# 此脚本展示如何在实际 CI/CD 中执行部署

set -e  # 出错时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ==================== 检查环境 ====================
check_environment() {
    log_info "检查部署环境..."
    
    if [ -z "$ENVIRONMENT" ]; then
        log_error "缺少 ENVIRONMENT 环境变量 (staging/production)"
        exit 1
    fi
    
    if [ -z "$IMAGE_NAME" ]; then
        log_error "缺少 IMAGE_NAME 环境变量"
        exit 1
    fi
    
    if [ -z "$DOCKER_REGISTRY" ]; then
        log_warning "未设置 DOCKER_REGISTRY，使用默认值：ghcr.io"
        DOCKER_REGISTRY="ghcr.io"
    fi
    
    log_success "环境检查完成"
}

# ==================== Staging 部署 ====================
deploy_staging() {
    log_info "部署到 Staging 环境..."
    
    # 创建部署目录
    mkdir -p deployment
    
    # 创建部署清单
    cat > deployment/staging-deployment.yaml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auto-api-staging
  namespace: staging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: auto-api
      env: staging
  template:
    metadata:
      labels:
        app: auto-api
        env: staging
    spec:
      containers:
      - name: auto-api
        image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION}
        ports:
        - containerPort: 8000
        env:
        - name: ENV
          value: staging
        - name: LOG_LEVEL
          value: INFO
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      restartPolicy: Always
---
apiVersion: v1
kind: Service
metadata:
  name: auto-api-staging
  namespace: staging
spec:
  selector:
    app: auto-api
    env: staging
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
EOF
    
    log_success "Staging 部署清单已生成"
    
    # 实际部署命令（示例）
    # kubectl apply -f deployment/staging-deployment.yaml
    
    # 或使用 Docker Compose
    log_info "使用 Docker Compose 部署..."
    docker-compose -f docker-compose.yml up -d app-staging
    
    sleep 10
    
    # 健康检查
    if curl -f http://localhost:8001/health; then
        log_success "Staging 部署成功"
    else
        log_error "Staging 健康检查失败"
        return 1
    fi
}

# ==================== Production 部署 ====================
deploy_production() {
    log_warning "准备部署到 Production 环境..."
    log_info "当前版本: $VERSION"
    
    # 确认部署
    read -p "确实要部署到 Production 吗? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_error "部署已取消"
        return 1
    fi
    
    # 创建部署清单
    cat > deployment/production-deployment.yaml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auto-api-production
  namespace: production
spec:
  replicas: 3  # Production 需要更多副本
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: auto-api
      env: production
  template:
    metadata:
      labels:
        app: auto-api
        env: production
        version: ${VERSION}
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - auto-api
              topologyKey: kubernetes.io/hostname
      containers:
      - name: auto-api
        image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION}
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: ENV
          value: production
        - name: LOG_LEVEL
          value: WARNING
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 2
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        securityContext:
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
      restartPolicy: Always
---
apiVersion: v1
kind: Service
metadata:
  name: auto-api-production
  namespace: production
spec:
  selector:
    app: auto-api
    env: production
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: auto-api-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: auto-api-production
  minReplicas: 3
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
EOF
    
    log_success "Production 部署清单已生成"
    
    # 实际部署命令（示例）
    # kubectl apply -f deployment/production-deployment.yaml
    
    # 或使用 Docker Compose
    log_info "使用 Docker Compose 部署..."
    docker-compose -f docker-compose.yml up -d app-production
    
    sleep 15
    
    # 健康检查
    if curl -f http://localhost:8002/health; then
        log_success "Production 部署成功"
        
        # 部署后通知
        log_info "发送部署通知..."
        # 可集成 Slack、钉钉等通知
    else
        log_error "Production 健康检查失败，请检查日志"
        docker-compose logs app-production
        return 1
    fi
}

# ==================== 烟雾测试 ====================
smoke_tests() {
    log_info "运行烟雾测试..."
    
    local api_url=""
    if [ "$ENVIRONMENT" == "staging" ]; then
        api_url="http://localhost:8001"
    else
        api_url="http://localhost:8002"
    fi
    
    # 测试健康检查端点
    if curl -f "$api_url/health"; then
        log_success "✓ 健康检查通过"
    else
        log_error "✗ 健康检查失败"
        return 1
    fi
    
    # 测试状态端点
    if curl -f "$api_url/api/v1/status"; then
        log_success "✓ 状态端点通过"
    else
        log_error "✗ 状态端点失败"
        return 1
    fi
    
    # 测试 API 创建端点
    response=$(curl -s -X POST "$api_url/api/v1/test" \
        -H "Content-Type: application/json" \
        -d '{"name":"Test","description":"Smoke Test"}')
    
    if echo "$response" | grep -q '"status":"created"'; then
        log_success "✓ 创建测试通过"
    else
        log_error "✗ 创建测试失败"
        return 1
    fi
    
    log_success "烟雾测试完成"
}

# ==================== 主流程 ====================
main() {
    log_info "========== 部署流程开始 =========="
    
    check_environment
    
    VERSION=${VERSION:-"latest"}
    export VERSION
    
    case "$ENVIRONMENT" in
        staging)
            deploy_staging
            smoke_tests
            ;;
        production)
            deploy_production
            smoke_tests
            ;;
        *)
            log_error "未知环境: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    log_success "========== 部署流程完成 =========="
}

# 执行主流程
main "$@"
