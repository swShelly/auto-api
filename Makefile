# Makefile for AUTO-API

.PHONY: help check lint format test clean install

help:
	@echo "AUTO-API 代码质量检查"
	@echo ""
	@echo "可用命令："
	@echo "  make install   - 安装依赖"
	@echo "  make lint      - 运行代码检查"
	@echo "  make format   - 自动格式化代码"
	@echo "  make check    - 运行所有检查"
	@echo "  make test     - 运行测试"
	@echo "  make clean    - 清理缓存"

install:
	pip install -r requirements.txt

lint:
	python -m ruff check .

format:
	python -m ruff format .

check: lint test
	mypy .

test:
	pytest -v -s

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
