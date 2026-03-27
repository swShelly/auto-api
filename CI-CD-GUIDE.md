# 持续交付流水线配置指南

## 🚀 概述

这个 CI/CD 流水线完整覆盖以下阶段：

```
代码质量检查 → 安全扫描 → 测试 & 覆盖率 → 构建 → 发布 → 部署 → 监控 & 通知
```

## 🔑 必需的 GitHub Secrets

在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 中添加以下 Secrets：

### PyPI 发布凭证（必需）
- **PYPI_API_TOKEN**: PyPI 生产环境 token
  - 获取方式：https://pypi.org/manage/account/token/
- **TESTPYPI_API_TOKEN**: TestPyPI token（可选，用于测试）
  - 获取方式：https://test.pypi.org/manage/account/token/

### Docker Registry 凭证（可选，用于私有镜像仓库）
- **DOCKER_USERNAME**: Docker Hub 用户名
- **DOCKER_PASSWORD**: Docker Hub token 或密码
- 或使用 GitHub Container Registry（GHCR），自动使用 GITHUB_TOKEN

### 部署凭证（可选）
- **DEPLOY_STAGING_HOST**: Staging 服务器地址
- **DEPLOY_STAGING_USER**: Staging 部署用户
- **DEPLOY_STAGING_SSH_KEY**: Staging SSH 私钥

- **DEPLOY_PROD_HOST**: Production 服务器地址
- **DEPLOY_PROD_USER**: Production 部署用户
- **DEPLOY_PROD_SSH_KEY**: Production SSH 私钥

### 通知凭证（可选）
- **SLACK_WEBHOOK_URL**: Slack webhook 链接（用于通知）
- **DINGTALK_WEBHOOK_URL**: 钉钉 webhook 链接（用于通知）

---

## 📋 工作流触发条件

| 事件 | 触发条件 | 执行阶段 |
|------|--------|--------|
| Push | `main/master/develop` 分支 | 所有阶段 |
| Tag | `v*` 标签 | 所有阶段 + 发布到 PyPI + 部署到 Prod |
| Pull Request | `main/master` 分支 | 检查 + 测试（不部署） |
| Manual | 手动触发（workflow_dispatch） | 所有阶段 + 选择环境 |

---

## 🔄 流水线各阶段说明

### 1️⃣ 代码质量检查（Lint & Type Check）
- **Lint**: 使用 Ruff 检查代码风格和潜在问题
- **Type Check**: 使用 mypy 进行静态类型检查

### 2️⃣ 安全扫描（Security）
- **Safety**: 检查依赖中的已知安全漏洞
- **Bandit**: 扫描 Python 代码中的安全问题
- **pip-audit**: 审计已安装包的安全漏洞

### 3️⃣ 测试 & 覆盖率（Test）
- **多版本测试**: Python 3.10, 3.11, 3.12 并行运行
- **覆盖率收集**: 生成 HTML、XML、terminal 三种格式报告
- **上传到 Codecov**: 自动上传覆盖率数据
- **Allure 报告**: 生成高级测试报告

### 4️⃣ 构建（Build）
- **构建 Wheel/Tar.gz**: 生成 Python 包
- **验证**: 使用 twine 验证包完整性
- **Docker 镜像**: 多阶段构建最小化镜像体积
- **推送到 Registry**: GHCR / Docker Hub

### 5️⃣ 发布（Publish）
- **条件**: 仅在标签或 main 分支触发
- **TestPyPI**: main 分支发布到测试环境
- **PyPI**: 标签发布到生产环境

### 6️⃣ 部署（Deploy）
- **条件**: 发布成功后
- **Staging 环境**: 总是部署（用于测试）
- **Prod 环境**: 仅标签发布部署
- **健康检查**: 部署后自动验证服务状态

### 7️⃣ 监控 & 通知（Notify）
- **执行摘要**: 生成 GitHub Action 摘要页面
- **成功/失败通知**: 明确显示流水线状态
- **状态表格**: 展示各阶段执行结果

---

## 🛠️ 本地开发使用

### 快速入门
```bash
# 安装依赖
make install

# 运行所有检查
make check

# 运行测试
make test

# 生成覆盖率报告
make coverage

# 运行安全扫描
make security-scan

# 构建 Docker 镜像
make build-docker

# 部署到 Staging
make deploy-staging

# 查看帮助
make help
```

### 本地部署
```bash
# 启动 Staging + Production + 监控栈
docker-compose up -d

# 查看 Staging 日志
make logs-staging

# 查看 Production 日志  
make logs-prod

# 执行健康检查
make health-check

# 查看监控面板
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000
```

---

## 🔐 安全最佳实践

### 1. Secret 管理
- ✅ 使用 GitHub Secrets 存储敏感信息
- ✅ 定期轮换 API tokens
- ❌ 不要在代码中硬编码凭证
- ❌ 不要在日志中输出 secrets

### 2. 权限管理
```yaml
permissions:
  contents: read          # 读取代码
  id-token: write         # 仅发布时需要
  security-events: write  # 仅安全扫描时需要
```

### 3. 部署保护
- 生产部署需要额外确认（如果执行的是脚本，需要 manual approval）
- 使用环保护规则（branch protection rules）
- 部署前自动运行所有检查

---

## 📊 监控与告警

### Prometheus 指标
在你的应用中暴露 Prometheus metrics，例如：
```python
from prometheus_client import Counter, Histogram
import time

request_count = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.get("/api/endpoint")
def my_endpoint():
    request_count.labels(method='GET', endpoint='/api/endpoint').inc()
    with request_duration.time():
        # 你的业务逻辑
        pass
```

### Grafana 仪表板
- 自动连接 Prometheus 数据源
- 创建自定义仪表板监控关键指标
- 配置告警规则

---

## 🚨 故障排查

### 常见问题

#### Q: PyPI 发布失败
```
ERROR: Invalid distribution on upload.
```
**解决**: 运行本地验证 `twine check dist/*`，确保构建产物有效

#### Q: Docker 构建超时
**解决**: 检查网络连接，或使用本地镜像源加速

#### Q: 部署健康检查失败
**解决**: 
- 检查应用是否正确实现了 `/health` 端点
- 查看容器日志：`docker logs auto-api-staging`
- 确认端口映射正确

#### Q: 覆盖率低
**解决**:
- 编写更多单元测试
- 使用 `pytest --cov-report=html` 查看覆盖率详情
- 关注 CI 输出的覆盖率趋势

---

## ✨ 进阶配置

### 1. 添加 Slack 通知
```yaml
- name: Slack notification
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 2. 添加自动化生成 Release Notes
```bash
npx release-it --ci
```

### 3. 添加合规检查（SBOM）
```bash
pip install cyclonedx-python
cyclonedx-python > sbom.xml
```

### 4. 添加性能基准测试
```bash
pip install pytest-benchmark
pytest tests/benchmark/ --benchmark-compare
```

---

## 📚 相关资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [PyPI 发布指南](https://packaging.python.org/guides/publishing-package-distribution-releases-to-pypi/)
- [Docker 多阶段构建](https://docs.docker.com/build/building/multi-stage/)
- [Codecov 配置](https://docs.codecov.io/)

---

## 💡 总结

这个流水线提供了：
- ✅ 完整的代码质量检查
- ✅ 多版本兼容性测试
- ✅ 安全漏洞扫描
- ✅ 自动化发布到 PyPI
- ✅ Docker 容器化与部署
- ✅ 监控与告警
- ✅ 详细的执行摘要与通知

现在你拥有了一个企业级的 CI/CD 流水线！🎉
