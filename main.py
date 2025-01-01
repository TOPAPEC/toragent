import os
import json
from datetime import datetime
from dotenv import load_dotenv
from claude_interface import ClaudeInterface
from solution_generator import SolutionGenerator
from environment_manager import EnvironmentManager
from analysis_module import AnalysisModule
from debug_module import DebugModule

def create_run_directory():
    runs_dir = "runs"
    os.makedirs(runs_dir, exist_ok=True)
    current_run = os.path.join(runs_dir, f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(current_run)
    return current_run

def save_step_result(run_dir, step_name, data):
    step_file = os.path.join(run_dir, f"{step_name}.json")
    with open(step_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nSaved {step_name} results to: {step_file}")
    print("Content preview:")
    print("=" * 50)
    print(json.dumps(data, indent=2)[:500] + "..." if len(json.dumps(data)) > 500 else json.dumps(data, indent=2))
    print("=" * 50)

def check_dependencies():
    try:
        import anthropic
        import dotenv
        print("All dependencies are installed correctly.")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False

def main():
    # Create run directory
    run_dir = create_run_directory()
    print(f"\nCreated run directory: {run_dir}")

    # Load environment variables
    load_dotenv()

    # Check if ANTHROPIC_API_KEY is set
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        return

    # Initialize all modules
    claude = ClaudeInterface(api_key)
    solution_gen = SolutionGenerator(claude)
    env_manager = EnvironmentManager()
    analyzer = AnalysisModule(claude)
    debugger = DebugModule(claude)

    # Test task and data
    test_task = """
    Create a simple NLP system that can identify basic emotions in text.
    The system should classify text into: happy, sad, angry, or neutral.
    """

    test_data = """
    Sample texts:

    1. "I love this beautiful day!"

    2. "I'm feeling really down today."

    3. "This is absolutely frustrating!"

    4. "The sky is blue."
    """

    # Save initial configuration
    save_step_result(run_dir, "00_initial_config", {
        "test_task": test_task,
        "test_data": test_data,
        "timestamp": datetime.now().isoformat()
    })

    try:
        # Generate solution
        print("\nGenerating solution...")
        solution = solution_gen.generate_solution(test_task, test_data)
        save_step_result(run_dir, "01_generated_solution", solution)

        # Create new iteration environment
        print("\nCreating iteration environment...")
        iteration_dir = env_manager.create_iteration(
            solution['code'],
            solution['requirements']
        )
        save_step_result(run_dir, "02_iteration_setup", {
            "iteration_dir": iteration_dir,
            "code_file": os.path.join(iteration_dir, "main.py"),
            "requirements_file": os.path.join(iteration_dir, "requirements.txt")
        })

        # Run the iteration
        print("\nRunning iteration...")
        output_file = env_manager.run_iteration(iteration_dir)

        # Read output
        with open(output_file, 'r') as f:
            output = f.read()

        save_step_result(run_dir, "03_iteration_output", {
            "output_file": output_file,
            "output_content": output
        })

        debug_results = None
        # Check if there are errors in output
        if "Error" in output:
            print("\nErrors detected, starting debug process...")
            fixed_code, requirement_changes = debugger.debug_code(
                solution['code'],
                output,
                solution['requirements']
            )

            debug_results = {
                "original_error": output,
                "fixed_code": fixed_code,
                "requirement_changes": requirement_changes
            }
            save_step_result(run_dir, "04_debug_results", debug_results)

            if requirement_changes:
                print("\nUpdating requirements and creating new iteration...")
                iteration_dir = env_manager.create_iteration(
                    fixed_code,
                    solution['requirements'] + "\n" + "\n".join(requirement_changes)
                )
                output_file = env_manager.run_iteration(iteration_dir)

                with open(output_file, 'r') as f:
                    output = f.read()

                save_step_result(run_dir, "05_fixed_iteration_output", {
                    "new_iteration_dir": iteration_dir,
                    "output_file": output_file,
                    "output_content": output
                })

        # Analyze results
        print("\nAnalyzing results...")
        analysis = analyzer.analyze_iteration(
            solution['code'],
            output,
            analyzer.history
        )

        save_step_result(run_dir, "06_analysis_results", analysis)

        # Create summary
        summary = {
            "run_directory": run_dir,
            "timestamp": datetime.now().isoformat(),
            "solution_generated": bool(solution),
            "debug_needed": bool(debug_results),
            "final_output_file": output_file,
            "token_usage": claude.get_token_usage()
        }
        save_step_result(run_dir, "07_run_summary", summary)

        # Display final status
        print("\nRun completed!")
        print(f"All results saved in: {run_dir}")
        print("\nToken Usage:")
        print(json.dumps(claude.get_token_usage(), indent=2))

        # Wait for user input before next iteration
        input("\nPress Enter to continue...")

    except Exception as e:
        error_info = {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "last_successful_step": os.listdir(run_dir)[-1] if os.listdir(run_dir) else None
        }
        save_step_result(run_dir, "error_log", error_info)
        print(f"Error in execution: {str(e)}")

if __name__ == "__main__":
    if check_dependencies():
        main()
