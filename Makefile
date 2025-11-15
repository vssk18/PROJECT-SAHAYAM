CXX   := g++
PY    := python3
JAVAC := javac
JAVA  := java

all: quick-demo

# --------------------------------------------------
# Quick demo: C++, Java, Python checklist
# --------------------------------------------------
quick-demo: build-sms-filter build-passphrase-demo build-checklist-demo
	@echo "=== SAHAYAM quick demo ==="
	@echo "[1] Running C++ SMS scam filter on sample_sms.txt"
	@cd apps/cpp_sms_filter && \
		echo "Your KYC will be blocked, click bit.ly/scam" > sample_sms.txt && \
		echo "Dinner at 8?" >> sample_sms.txt && \
		./sms_filter sample_sms.txt --stats
	@echo
	@echo "[2] Running Java passphrase trainer (demo input)"
	@cd apps/java_passphrase_trainer && \
		printf "mango train temple\n" | $(JAVA) PassphraseTrainer
	@echo
	@echo "[3] Generating example checklist (EN)"
	@cd apps/py_checklist_generator && \
		$(PY) generate_checklist.py --name "Demo User" --phone "XXXX1234" --lang en --out demo_checklist.md && \
		echo "Generated apps/py_checklist_generator/demo_checklist.md"

# --------------------------------------------------
# Build steps
# --------------------------------------------------
build-sms-filter:
	@cd apps/cpp_sms_filter && \
		$(CXX) -O2 sms_filter.cpp -o sms_filter

build-passphrase-demo:
	@cd apps/java_passphrase_trainer && \
		$(JAVAC) PassphraseTrainer.java

build-checklist-demo:
	@cd apps/py_checklist_generator || exit 1

# --------------------------------------------------
# Tools for you while running clinics
# --------------------------------------------------
metrics-demo:
	@cd apps/py_metrics_logger && $(PY) summarize_metrics.py

clinic-demo:
	@cd apps/py_clinic_assistant && $(PY) clinic_assistant.py

synthetic-data:
	@cd apps/py_clinic_assistant && $(PY) generate_synthetic_metrics.py

# --------------------------------------------------
# Cleanup
# --------------------------------------------------
clean:
	@rm -f apps/cpp_sms_filter/sms_filter
	@rm -f apps/java_passphrase_trainer/PassphraseTrainer.class
	@rm -f apps/py_checklist_generator/demo_checklist.md

dashboard:
	@cd apps/py_dashboard && $(PY) dashboard.py

