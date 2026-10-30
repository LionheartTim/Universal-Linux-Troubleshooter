"""Regression gate for the retired-AI, Manual-only application."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / 'universal_linux_troubleshooter'


def test_live_gui_contains_exactly_manual_and_info_tabs():
    main = (PKG / 'ui/main_window.py').read_text()
    tree = ast.parse(main)
    assert 'self.tabs.addTab(self.manual, "Manual Diagnostics")' in main
    assert 'self.tabs.addTab(self.info, "Info")' in main
    assert main.count('self.tabs.addTab(') == 2
    assert 'AiAssistantPage' not in main
    assert 'self.ai' not in main
    assert 'ai_components_ready' not in main
    assert '_maybe_show_ai_notice' not in main
    modules = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert not any((module or '').endswith('pages.ai') or (module or '').endswith('model_bundle') for module in modules)


def test_info_is_manual_only_and_model_independent():
    info = (PKG / 'pages/info.py').read_text()
    assert 'AI Assistant' not in info and 'AI Diagnostics' not in info
    assert 'model_bundle' not in info
    assert 'Manual Diagnostics' in info
    assert 'Universal-Linux-Software-Manager' in info
    assert 'Universal-Linux-Terminal' in info


def test_no_model_distribution_or_ai_runtime_dependency():
    project = (ROOT / 'pyproject.toml').read_text()
    assert 'dependencies = ["PySide6-Essentials>=6.6,<7"]' in project
    assert 'llama-cpp-python' not in project
    assert 'models/*.gguf' not in project
    assert not any(ROOT.rglob('*.gguf'))


def test_manual_catalog_and_offline_bridge_preserved():
    data = json.loads((ROOT/'knowledge_sources/diagnosis_trees.json').read_text())
    assert data['counts']['total'] == 250
    assert data['counts']['cross_domain_undirected_links'] == 42
    assert (PKG/'pages/manual.py').exists()
    assert (PKG/'diagnostics/bridge.py').exists()
    assert (PKG/'diagnostics/worker.py').exists()
    assert (PKG/'system_profile119.py').exists()
    assert (PKG/'profile_worker119.py').exists()
    manual = (PKG/'pages/manual.py').read_text()
    assert 'DiagnosticWorker' in manual
    assert 'ManualDiagnosticsPage' in manual
    assert 'Qwen' not in manual
