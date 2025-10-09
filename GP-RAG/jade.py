#!/usr/bin/env python3
"""
JADE - Unified Security Consultant Launcher
Central entry point for all Jade AI capabilities

Usage:
    ./jade.py [command] [options]

Commands:
    rag         - Launch RAG + LangGraph security consultant (RECOMMENDED)
    ingest      - Ingest training data into vector database
    train       - Fine-tune model (when GPU supports it)
    orchestrator - Launch full orchestrator with scanners
    test        - Test Jade with sample security queries
    info        - Show system information

Examples:
    ./jade.py rag --query "Analyze CVE-2024-33663"
    ./jade.py ingest
    ./jade.py test
"""

import sys
import argparse
from pathlib import Path

# Color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """Print Jade banner"""
    banner = f"""{Colors.CYAN}
    ╔═══════════════════════════════════════════════════╗
    ║           JADE AI Security Consultant            ║
    ║  RAG + LangGraph + Qwen2.5 Offline System       ║
    ╚═══════════════════════════════════════════════════╝
    {Colors.END}"""
    print(banner)


def command_rag(args):
    """Launch RAG + LangGraph consultant"""
    print(f"{Colors.BOLD}🚀 Launching Jade RAG + LangGraph System{Colors.END}\n")

    try:
        # Use new core module location
        sys.path.insert(0, str(Path(__file__).parent / 'core'))
        from jade_engine import JadeRAGAgent

        # Use centralized vector store location
        vector_db = args.vector_db if args.vector_db else str(Path(__file__).parent / 'vector-store' / 'jade-knowledge')
        agent = JadeRAGAgent(vector_db_path=vector_db)

        if args.query:
            # Single query mode
            print(f"\n{Colors.CYAN}Query:{Colors.END} {args.query}\n")
            result = agent.query(args.query)

            print(f"{Colors.GREEN}Response:{Colors.END}\n{result['response']}\n")
            print(f"{Colors.YELLOW}Domain:{Colors.END} {result['domain']}")
            print(f"{Colors.YELLOW}Confidence:{Colors.END} {result['confidence']:.2f}")

        else:
            # Interactive mode
            print(f"{Colors.GREEN}Interactive mode - Type your security questions{Colors.END}")
            print(f"{Colors.YELLOW}Commands: 'quit' or 'exit' to stop{Colors.END}\n")

            while True:
                try:
                    query = input(f"{Colors.CYAN}Jade > {Colors.END}").strip()

                    if query.lower() in ['quit', 'exit', 'q']:
                        print(f"\n{Colors.GREEN}Goodbye!{Colors.END}")
                        break

                    if not query:
                        continue

                    result = agent.query(query)
                    print(f"\n{result['response']}\n")
                    print(f"{Colors.YELLOW}[Confidence: {result['confidence']:.2f} | Domain: {result['domain']}]{Colors.END}\n")

                except KeyboardInterrupt:
                    print(f"\n{Colors.GREEN}Goodbye!{Colors.END}")
                    break
                except Exception as e:
                    print(f"{Colors.RED}Error: {e}{Colors.END}\n")

    except ImportError as e:
        print(f"{Colors.RED}❌ Missing dependencies: {e}{Colors.END}")
        print(f"{Colors.YELLOW}Install: pip install langgraph langchain chromadb sentence-transformers{Colors.END}")
        sys.exit(1)


def command_ingest(args):
    """Ingest training data"""
    print(f"{Colors.BOLD}📚 Ingesting Security Training Data{Colors.END}\n")

    try:
        # Use new unified ingestion tool
        sys.path.insert(0, str(Path(__file__).parent / 'tools'))
        from ingest import JadeKnowledgeIngestion

        ingestion = JadeKnowledgeIngestion()

        # Ingest training data
        training_path = Path(__file__).parent / 'data' / 'raw' / 'training' / 'jade_security_training.jsonl'
        if training_path.exists():
            ingestion.ingest_training_data(str(training_path))

            # Show stats
            stats = ingestion.get_stats()
            print(f"\n{Colors.GREEN}✅ Ingestion complete!{Colors.END}")
            print(f"{Colors.CYAN}Total documents:{Colors.END} {stats['total_documents']}")
            print(f"{Colors.CYAN}Database:{Colors.END} {stats['database_path']}")
        else:
            print(f"{Colors.RED}❌ Training data not found at: {training_path}{Colors.END}")

    except ImportError as e:
        print(f"{Colors.RED}❌ Missing dependencies: {e}{Colors.END}")
        sys.exit(1)


def command_train(args):
    """Fine-tune model"""
    print(f"{Colors.BOLD}🎓 Model Fine-Tuning{Colors.END}\n")

    print(f"{Colors.YELLOW}⚠️  Note: Training currently blocked by RTX 5080 compatibility{Colors.END}")
    print(f"{Colors.CYAN}Reason:{Colors.END} Your GPU (Blackwell sm_120) is too new for current libraries")
    print(f"{Colors.GREEN}Solution:{Colors.END} Use RAG mode (recommended) or wait for PyTorch 2.7")
    print()
    print(f"Training scripts available in: {Colors.BOLD}training/{Colors.END}")
    print(f"  - {Colors.CYAN}training/scripts/train_jade_rtx5080.py{Colors.END} (no quantization)")
    print(f"  - {Colors.CYAN}training/README.md{Colors.END} (full documentation)")


def command_orchestrator(args):
    """Launch full orchestrator"""
    print(f"{Colors.BOLD}🎯 Launching Jade Orchestrator{Colors.END}\n")

    try:
        from jade_orchestrator import main as orchestrator_main
        orchestrator_main()
    except ImportError as e:
        print(f"{Colors.RED}❌ Missing dependencies: {e}{Colors.END}")
        sys.exit(1)


def command_test(args):
    """Run tests"""
    print(f"{Colors.BOLD}🧪 Testing Jade Capabilities{Colors.END}\n")

    test_queries = [
        "Analyze CVE-2024-33663 affecting python-jose",
        "How do I secure a Kubernetes pod against privilege escalation?",
        "What are common Bandit findings in Python code?",
        "Explain OPA Gatekeeper policies for container security"
    ]

    try:
        from jade_rag_langgraph import JadeRAGAgent

        agent = JadeRAGAgent()

        for i, query in enumerate(test_queries, 1):
            print(f"\n{Colors.CYAN}{'='*80}{Colors.END}")
            print(f"{Colors.BOLD}Test {i}/{len(test_queries)}:{Colors.END} {query}")
            print(f"{Colors.CYAN}{'='*80}{Colors.END}")

            result = agent.query(query)
            print(f"\n{result['response'][:500]}...")
            print(f"\n{Colors.YELLOW}[Full response truncated | Confidence: {result['confidence']:.2f}]{Colors.END}")

        print(f"\n{Colors.GREEN}✅ All tests completed!{Colors.END}")

    except Exception as e:
        print(f"{Colors.RED}❌ Test error: {e}{Colors.END}")


def command_info(args):
    """Show system information"""
    print(f"{Colors.BOLD}ℹ️  Jade System Information{Colors.END}\n")

    # Check GPU
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"{Colors.GREEN}✅ GPU:{Colors.END} {gpu_name} ({gpu_memory:.1f}GB)")
        else:
            print(f"{Colors.YELLOW}⚠️  No GPU detected{Colors.END}")
    except:
        print(f"{Colors.YELLOW}⚠️  PyTorch not installed{Colors.END}")

    # Check models
    model_path = Path.home() / ".cache/huggingface/hub"
    if (model_path / "models--Qwen--Qwen2.5-7B-Instruct").exists():
        print(f"{Colors.GREEN}✅ Model:{Colors.END} Qwen2.5-7B-Instruct (cached)")
    else:
        print(f"{Colors.YELLOW}⚠️  Model:{Colors.END} Qwen2.5-7B-Instruct (will download on first use)")

    # Check vector database
    vector_db = Path(__file__).parent / "vector-store" / "jade-knowledge"
    if vector_db.exists():
        print(f"{Colors.GREEN}✅ Vector DB:{Colors.END} vector-store/jade-knowledge (ready)")
    else:
        print(f"{Colors.YELLOW}⚠️  Vector DB:{Colors.END} Not initialized (run: ./jade.py ingest)")

    # Check dependencies
    deps = ['langgraph', 'langchain', 'chromadb', 'transformers']
    missing = []
    for dep in deps:
        try:
            __import__(dep)
            print(f"{Colors.GREEN}✅ {dep}{Colors.END}")
        except ImportError:
            print(f"{Colors.RED}❌ {dep}{Colors.END}")
            missing.append(dep)

    if missing:
        print(f"\n{Colors.YELLOW}Install missing: pip install {' '.join(missing)}{Colors.END}")

    # Show file structure
    print(f"\n{Colors.BOLD}Available Scripts:{Colors.END}")
    scripts = [
        ("jade_rag_langgraph.py", "RAG + LangGraph consultant (recommended)"),
        ("jade_orchestrator.py", "Full orchestrator with scanner integration"),
        ("ingest_training_data.py", "Ingest data into vector database"),
        ("training/", "Fine-tuning scripts and data")
    ]

    for script, desc in scripts:
        print(f"  {Colors.CYAN}{script:30s}{Colors.END} - {desc}")


def main():
    parser = argparse.ArgumentParser(
        description="Jade AI Security Consultant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # RAG command
    rag_parser = subparsers.add_parser('rag', help='Launch RAG + LangGraph consultant')
    rag_parser.add_argument('--query', '-q', type=str, help='Single query mode')
    rag_parser.add_argument('--vector-db', type=str, help='Vector database path (default: vector-store/jade-knowledge)')

    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest training data')

    # Train command
    train_parser = subparsers.add_parser('train', help='Fine-tune model')

    # Orchestrator command
    orch_parser = subparsers.add_parser('orchestrator', help='Launch full orchestrator')

    # Test command
    test_parser = subparsers.add_parser('test', help='Run test queries')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show system information')

    args = parser.parse_args()

    # Show banner
    print_banner()

    # Route to command
    if args.command == 'rag':
        command_rag(args)
    elif args.command == 'ingest':
        command_ingest(args)
    elif args.command == 'train':
        command_train(args)
    elif args.command == 'orchestrator':
        command_orchestrator(args)
    elif args.command == 'test':
        command_test(args)
    elif args.command == 'info':
        command_info(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()