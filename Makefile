# Makefile for AUTO-API - 持续交付流水线支持

.PHONY: help check lint format test clean install build-docker publish deploy monitor security-scan coverage

help:
	@echo "AUTO-API 持续交付流水线"
	@echo ""
	@echo "📋 代码质量命令："
	@echo "  make install         - 安装依赖"
	@echo "  make lint            - 运行代码检查"
	@echo "  make format          - 自动格式化代码"
	@echo "  make check           - 运行所有检查"
	@echo "  make test            - 运行单元测试"
	@echo "  make coverage        - 运行测试并生成覆盖率报告"
	@echo "  make security-scan   - 运行安全扫描（safety, bandit, pip-audit）"
	@echo ""
	@echo "🔨 构建命令："
	@echo "  make build-docker    - 构建 Docker 镜像"
	@echo "  make build-wheel     - 构建 Python wheel 包"
	@echo ""
	@echo "📦 发布命令："
	@echo "  make publish-test    - 发布到 TestPyPI"
	@echo "  make publish-prod    - 发布到 PyPI (需谨慎)"
	@echo ""
	@echo "🚀 部署命令："
	@echo "  make deploy-staging  - 部署到 Staging 环境"
	@echo "  make deploy-prod     - 部署到 Production 环境"
	@echo "  make health-check    - 执行健康检查"
	@echo ""
	@echo "🔍 监控命令："
	@echo "  make logs-staging    - 查看 Staging 日志"
	@echo "  make logs-prod       - 查看 Production 日志"
	@echo "  make monitor         - 启动本地监控栈 (Prometheus + Grafana)"
	@echo ""
	@echo "🧹 清理命令："
	@echo "  make clean           - 清理缓存和临时文件"

# ==================== 初始化 ====================
install:
	pip install -r requirements.txt

# ==================== 代码质量 ====================
lint:
	python -m ruff check .

format:
	python -m ruff format .

check: lint
	mypy .

test:
	pytest -v --tb=short

coverage:
	pytest -v \
		--cov=core \
		--cov-report=html \
		--cov-report=term \
		--cov-report=xml
	@echo "✅ 覆盖率报告已生成: htmlcov/index.html"

security-scan:
	@echo "🔒 运行安全扫描..."
	@echo "\n--- Checking dependencies with safety ---"
	pip install safety
	safety check --json > safety-report.json || true
	@echo "\n--- Checking code with bandit ---"
	pip install bandit
	bandit -r . -f json -o bandit-report.json || true
	@echo "\n--- Checking dependencies with pip-audit ---"
	pip install pip-audit
	pip-audit --desc > pip-audit-report.txt || true
	@echo "✅ 安全扫描完成，报告已保存"

# ==================== 构建 ====================
build-docker:
	docker build -t auto-api:latest .
	@echo "✅ Docker 镜像构建完成：auto-api:latest"

build-wheel:
	pip install build twine
	python -m build
	twine check dist/*
	@echo "✅ Python wheel 构建完成：dist/"

# ==================== 发布 ====================
publish-test:
	pip install twine
	twine upload --repository testpypi dist/* --skip-existing
	@echo "✅ 已发布到 TestPyPI"

publish-prod:
	@echo "⚠️  即将发布到 PyPI 生产环境..."
	@echo "确认操作? [y/N]"
	@read -r response; \
	if [ "$$response" = "y" ]; then \
		pip install twine; \
		twine upload dist/* --skip-existing; \
		echo "✅ 已发布到 PyPI"; \
	else \
		echo "❌ 取消发布"; \
	fi

# ==================== 部署 ====================
deploy-staging:
	docker-compose up -d app-staging
	@echo "✅ Staging 环境已部署"
	sleep 5
	@make health-check-staging

deploy-prod:
	@echo "⚠️  即将部署到 Production 环境..."
	@echo "确认操作? [y/N]"
	@read -r response; \
	if [ "$$response" = "y" ]; then \
		docker-compose up -d app-production; \
		echo "✅ Production 环境已部署"; \
		sleep 5; \
		make health-check-prod; \
	else \
		echo "❌ 取消部署"; \
	fi

health-check-staging:
	@echo "🏥 检查 Staging 健康状态..."
	curl -f http://localhost:8001/health || echo "❌ Staging 健康检查失败"

health-check-prod:
	@echo "🏥 检查 Production 健康状态..."
	curl -f http://localhost:8002/health || echo "❌ Production 健康检查失败"

health-check: health-check-staging health-check-prod

# ==================== 监控 ====================
logs-staging:
	docker-compose logs -f app-staging

logs-prod:
	docker-compose logs -f app-production

monitor:
	docker-compose up -d prometheus grafana
	@echo "✅ 监控栈已启动"
	@echo "📊 Prometheus: http://localhost:9090"
	@echo "📊 Grafana:    http://localhost:3000 (admin/admin)"

# ==================== 清理 ====================
clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov coverage.xml
	rm -rf *.log
	@echo "✅ 清理完成"

# ==================== CI/CD 完整流程 ====================
ci: clean check security-scan coverage build-docker
	@echo "✅ CI 流程完成"

cd: build-docker deploy-staging
	@echo "✅ CD 流程完成"

pipeline: ci cd
	@echo "✅ 完整的 CI/CD 流水线执行完成"
