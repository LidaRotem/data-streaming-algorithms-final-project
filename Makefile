.PHONY: smoke test stage3 stage4

smoke:
	python experiments/smoke_test.py --config configs/main.yaml

test:
	pytest tests/ -v

stage3:
	python experiments/characterize_data.py --config configs/main.yaml

stage4:
	python experiments/run_all.py --config configs/main.yaml