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
    Create a tourist chatbot for Russian cities that will:

    1. Build its own database of cities and attractions for given list of cities

    2. Analyze user preferences from their query (climate, budget, interests)

    3. Use RAG to match cities and attractions to user preferences

    4. Explain recommendations

    For llm rag you can use Vikhrmodels/Vikhr-Nemo-12B-Instruct-R-21-09-24 from huggingface
    Here is the instruction on how to use it
    Как работать с RAG
Роль documents представляет из себя список словарей с описанием контента документов, с примнением json.dumps(array, ensure_ascii=False) (см. пример ниже).
Контент документов может быть представлен в 3 различных форматах: Markdown, HTML, Plain Text. Контент каждого документа - может быть чанком текста длиной до 4к символов.

[
  {
    "doc_id": (0..5),
    "title": "(null or str)",
    "content": "(html or markdown or plain text)"
  }
]

Пример правильного использования с OpenAI-like API
Запуск vLLM сервера: vllm serve --dtype half --max-model-len 32000 -tp 1 Vikhrmodels/Vikhr-Nemo-12B-Instruct-R-21-09-24 --api-key token-abc123

GROUNDED_SYSTEM_PROMPT = "Your task is to answer the user's questions using only the information from the provided documents. Give two answers to each question: one with a list of relevant document identifiers and the second with the answer to the question itself, using documents with these identifiers."

documents = [
  {
    "doc_id": 0,
    "title": "Глобальное потепление: ледники",
    "content": "За последние 50 лет объем ледников в мире уменьшился на 30%"
  },
  {
    "doc_id": 1,
    "title": "Глобальное потепление: Уровень моря",
    "content": "Уровень мирового океана повысился на 20 см с 1880 года и продолжает расти на 3,3 мм в год"
  }
]
sample_history = [
    {'role': 'system', 'content': GROUNDED_SYSTEM_PROMPT}, 
    {'role': 'documents', 'content': json.dumps(documents, ensure_ascii=False)},
    {'role': 'user', 'content': 'Глоабльное потепление'}
]
relevant_indexes = llm_client.chat.completions.create(
    model=llm_model,
    messages=sample_history,
    temperature=0.0,
    max_tokens=2048
).choices[0].message.content

print('Using documents: ' + relevant_indexes + '\n----')
final_answer = llm_client.chat.completions.create(
    model=llm_model,
    messages=sample_history + [{'role': 'assistant', 'content': relevant_indexes}],
    temperature=0.3,
    max_tokens=2048
).choices[0].message.content

print(final_answer)

Ответ после выполнения кода будет выглядеть примерно так:

Using documents: {"relevant_doc_ids": [0, 1]}
----

Глобальное потепление – это долгосрочное повышение средней температуры атмосферы и океанов Земли. Это явление имеет множество последствий для нашей планеты, и среди них можно выделить два ключевых аспекта, основанных на доступных мне данных:

1. **Уменьшение объема ледников**: За последние 50 лет наблюдается значительное сокращение объема ледников по всему миру. Согласно данным, объем ледников уменьшился на 30%. Это может быть связано с таянием ледников из-за повышения температур, что является одним из признаков глобального потепления.

2. **Повышение уровня моря**: Уровень мирового океана также увеличивается, что связано с таянием ледников и ледяных покровов, а также с расширением воды при повышении температуры. С 1880 года уровень моря повысился на 20 сантиметров, и этот процесс продолжается, с ежегодным увеличением на 3,3 миллиметра.

Эти изменения имеют серьезные последствия для экосистем, климата и человеческого общества. Таяние ледников приводит к повышению уровня моря, что может привести к затоплению прибрежных территорий и островов, а также к изменению водных ресурсов и климатических паттернов.

Используя первый ответ модели relevant_indexes (JSON), можно понять нашла ли модель информацию в документах или нет, она обучена возврашать пустой массив если ее нет и в таком случае она будет отвечать, что не смогла найти информацию в базе знаний (при генерации второго ответа).

End of example of rag usage.
    The system should improve its recommendations based on evaluation metrics.
    Consider that chatbot will speak in russian, not english.

    """

    test_data = """
    Cities list: ["Москва", "Санкт-Петербург", "Сочи", ...] # full list here

    Test queries:

    1. "Хочу поехать на море летом, бюджет ограничен, люблю исторические места"

    2. "Ищу город для зимнего отдыха, интересует горнолыжный спорт и спа, бюджет не ограничен"

    3. "Планирую культурную поездку весной, интересуют музеи и театры, средний бюджет"

    4. "Хочу посетить места с красивой природой осенью, без большого количества туристов, бюджет средний"

    5. "Ищу город для гастрономического туризма летом, интересует местная кухня и рынки, готов потратиться"
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
