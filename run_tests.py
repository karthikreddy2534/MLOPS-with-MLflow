#!/usr/bin/env python3
"""
Comprehensive test runner with telemetry integration for MLProject
"""

import sys
import os
import time
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def install_dependencies():
    """Install required dependencies for testing and telemetry"""
    print("📦 Installing dependencies...")
    
    dependencies = [
        "pytest==7.4.3",
        "pytest-cov==4.1.0", 
        "pytest-mock==3.12.0",
        "pytest-html==4.1.1",
        "structlog==23.2.0",
        "prometheus-client==0.19.0",
        "psutil==5.9.6",
        "opentelemetry-api==1.21.0",
        "opentelemetry-sdk==1.21.0",
        "opentelemetry-exporter-prometheus==1.12.0rc1"
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            os.system(f"pip install {dep}")
        except Exception as e:
            print(f"❌ Failed to install {dep}: {e}")
    
    print("✅ Dependencies installation completed!")


def setup_telemetry():
    """Setup telemetry infrastructure"""
    print("🔧 Setting up telemetry...")
    
    try:
        # Try to import and setup telemetry
        from mlProject.telemetry import setup_telemetry, get_logger
        
        # Start metrics server
        setup_telemetry(metrics_port=8000)
        
        # Get logger instance
        logger = get_logger("test_runner")
        logger.info("Telemetry setup completed successfully", 
                   component="test_runner", 
                   action="setup")
        
        print("✅ Telemetry setup completed!")
        return logger
        
    except ImportError as e:
        print(f"⚠️ Telemetry setup failed (dependencies not installed): {e}")
        return None
    except Exception as e:
        print(f"❌ Telemetry setup error: {e}")
        return None


def run_tests(test_type: str = "all", verbose: bool = False, logger: Optional[Any] = None) -> Dict[str, Any]:
    """Run tests with telemetry tracking"""
    
    if logger:
        logger.info(f"Starting test run", 
                   test_type=test_type, 
                   verbose=verbose)
    
    print(f"🧪 Running {test_type} tests...")
    
    # Create test reports directory
    reports_dir = Path("tests/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Base pytest command
    cmd_parts = [
        "python", "-m", "pytest"
    ]
    
    # Add test type specific options
    if test_type == "unit":
        cmd_parts.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd_parts.extend(["-m", "integration"])
    elif test_type == "slow":
        cmd_parts.extend(["-m", "slow"])
    elif test_type == "smoke":
        cmd_parts.extend(["-m", "smoke"])
    
    # Add verbosity
    if verbose:
        cmd_parts.append("-v")
    
    # Add coverage and reporting
    cmd_parts.extend([
        "--cov=src/mlProject",
        "--cov-report=html:tests/reports/coverage",
        "--cov-report=term-missing",
        "--html=tests/reports/report.html",
        "--self-contained-html"
    ])
    
    # Run tests
    start_time = time.time()
    
    try:
        import subprocess
        result = subprocess.run(cmd_parts, capture_output=True, text=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Parse results
        test_results = {
            "success": result.returncode == 0,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
        
        if logger:
            logger.info(f"Test run completed",
                       test_type=test_type,
                       duration=duration,
                       success=test_results["success"],
                       return_code=result.returncode)
        
        if test_results["success"]:
            print(f"✅ {test_type.title()} tests passed in {duration:.2f}s")
        else:
            print(f"❌ {test_type.title()} tests failed in {duration:.2f}s")
            print("Error output:")
            print(result.stderr)
        
        return test_results
        
    except Exception as e:
        error_msg = f"Test execution failed: {e}"
        print(f"❌ {error_msg}")
        
        if logger:
            logger.error(error_msg, test_type=test_type)
        
        return {
            "success": False,
            "duration": time.time() - start_time,
            "error": str(e)
        }


def generate_test_report(results: Dict[str, Any], logger: Optional[Any] = None):
    """Generate a comprehensive test report"""
    
    print("\n📊 Test Report Generation...")
    
    if logger:
        logger.info("Generating test report", results=results)
    
    report_content = f"""
# MLProject Test Report
Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Test Results Summary
"""
    
    for test_type, result in results.items():
        if isinstance(result, dict):
            status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
            duration = result.get("duration", 0)
            report_content += f"\n### {test_type.title()} Tests\n"
            report_content += f"- Status: {status}\n"
            report_content += f"- Duration: {duration:.2f}s\n"
            
            if not result.get("success", False) and "error" in result:
                report_content += f"- Error: {result['error']}\n"
    
    report_content += f"""
## Coverage Report
Coverage reports are available at: `tests/reports/coverage/index.html`

## HTML Report
Detailed HTML report is available at: `tests/reports/report.html`

## Telemetry
Metrics are available at: http://localhost:8000/metrics (if telemetry is enabled)
"""
    
    # Save report
    report_path = Path("tests/reports/test_summary.md")
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    print(f"✅ Test report generated: {report_path}")
    print(f"🌐 View coverage report: tests/reports/coverage/index.html")
    print(f"📋 View HTML report: tests/reports/report.html")


def demonstrate_telemetry():
    """Demonstrate telemetry features"""
    
    print("\n🔍 Demonstrating Telemetry Features...")
    
    try:
        from mlProject.telemetry import get_logger, track_performance, MetricsCollector
        from mlProject.telemetry.metrics import track_ml_metrics
        
        # Get logger
        logger = get_logger("demo")
        
        # Demonstrate structured logging
        logger.info("Demonstrating structured logging",
                   demo_stage="logging",
                   user="demo_user",
                   operation="demo")
        
        # Demonstrate performance tracking
        @track_performance("demo_function")
        def demo_function():
            """Demo function with performance tracking"""
            time.sleep(0.1)  # Simulate work
            return "Demo completed"
        
        result = demo_function()
        logger.info("Demo function completed", result=result)
        
        # Demonstrate ML metrics tracking
        track_ml_metrics("model_training",
                        accuracy=0.95,
                        rmse=0.12,
                        mae=0.08,
                        training_samples=1000)
        
        logger.info("ML metrics tracked",
                   accuracy=0.95,
                   rmse=0.12,
                   mae=0.08)
        
        # Demonstrate error tracking
        try:
            raise ValueError("Demo error for telemetry")
        except Exception as e:
            logger.exception("Demonstrating error tracking", error_type="demo")
        
        print("✅ Telemetry demonstration completed!")
        print("🌐 Check metrics at: http://localhost:8000/metrics")
        
    except ImportError:
        print("⚠️ Telemetry features not available (dependencies not installed)")
    except Exception as e:
        print(f"❌ Telemetry demonstration failed: {e}")


def main():
    """Main function to run tests and demonstrate telemetry"""
    
    parser = argparse.ArgumentParser(description="MLProject Test Runner with Telemetry")
    parser.add_argument("--test-type", choices=["all", "unit", "integration", "slow", "smoke"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies")
    parser.add_argument("--demo-telemetry", action="store_true", help="Demonstrate telemetry features")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    
    args = parser.parse_args()
    
    print("🚀 MLProject Test Runner with Telemetry")
    print("=" * 50)
    
    # Install dependencies if requested
    if args.install_deps:
        install_dependencies()
    
    # Setup telemetry
    logger = setup_telemetry()
    
    # Demonstrate telemetry if requested
    if args.demo_telemetry:
        demonstrate_telemetry()
    
    # Run tests unless skipped
    if not args.skip_tests:
        if args.test_type == "all":
            # Run all test types
            test_types = ["unit", "integration", "slow", "smoke"]
            results = {}
            
            for test_type in test_types:
                print(f"\n{'='*20} {test_type.upper()} TESTS {'='*20}")
                results[test_type] = run_tests(test_type, args.verbose, logger)
                
                # Short break between test types
                time.sleep(1)
            
            print(f"\n{'='*50}")
            print("📊 OVERALL RESULTS")
            print(f"{'='*50}")
            
            for test_type, result in results.items():
                status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
                duration = result.get("duration", 0)
                print(f"{test_type.title()} Tests: {status} ({duration:.2f}s)")
        
        else:
            # Run specific test type
            results = {args.test_type: run_tests(args.test_type, args.verbose, logger)}
        
        # Generate comprehensive report
        generate_test_report(results, logger)
    
    print("\n✅ Test runner completed!")
    print("🌐 Metrics available at: http://localhost:8000/metrics")


if __name__ == "__main__":
    main()