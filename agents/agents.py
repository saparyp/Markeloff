from langchain_ollama import OllamaLLM
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
import prompts

llm = OllamaLLM(model="qwen2.5:7b", temperature=0)


# Создаем инструменты с помощью декоратора @tool
@tool
def classify_correspondence(text: str) -> str:
    """Классифицирует входящие письма по типу, срочности, формальности и определяет отделы для согласования"""
    prompt = f"{prompts.classification_prompt}\n\nВходящее письмо: {text}"
    return llm.invoke(prompt)


@tool
def extract_entities(text: str) -> str:
    """Извлекает сущности из письма: реквизиты, требования, нормативные ссылки"""
    prompt = f"{prompts.structuring_prompt}\n\nТекст письма для анализа: {text}"
    return llm.invoke(prompt)


@tool
def analyze_legal_risks(context: str) -> str:
    """Анализирует юридические риски и соответствие политикам"""
    prompt = f"{prompts.lawyer_prompt}\n\nКонтекст для анализа: {context}"
    return llm.invoke(prompt)


@tool
def generate_draft(context: str) -> str:
    """Генерирует черновик ответного письма в нужном стиле"""
    prompt = f"{prompts.draftwriter_prompt}\n\nКонтекст: {context}"
    return llm.invoke(prompt)


@tool
def harmonize_draft(requirements_and_draft: str) -> str:
    """Проверяет и улучшает стиль письма, адаптирует тон"""
    prompt = f"{prompts.harmonizer_prompt}\n\n{requirements_and_draft}"
    return llm.invoke(prompt)


@tool
def define_approval_workflow(analysis_data: str) -> str:
    """Определяет маршрут согласования и формирует рекомендации для согласующих"""
    prompt = f"{prompts.reviewer_prompt}\n\nДанные для анализа: {analysis_data}"
    return llm.invoke(prompt)


@tool
def quality_check(source_and_draft: str) -> str:
    """Проводит финальную проверку качества и формирует итоговую версию"""
    prompt = f"{prompts.qa_prompt}\n\n{source_and_draft}"
    return llm.invoke(prompt)


def create_main_agent():
    llm = OllamaLLM(model="qwen2.5:7b", temperature=0)

    # Создаем список инструментов
    tools = [
        classify_correspondence,
        extract_entities,
        analyze_legal_risks,
        generate_draft,
        harmonize_draft,
        define_approval_workflow,
        quality_check,
    ]

    # Создаем системный промпт для агента
    system_prompt = """Ты — главный оркестратор системы обработки деловой переписки банка. 
Ты координируешь работу 7 специализированных агентов для полной обработки входящих писем.

Доступные инструменты:
- classify_correspondence - классифицирует письмо по типу, срочности, формальности
- extract_entities - извлекает сущности, реквизиты, требования
- analyze_legal_risks - анализирует юридические риски
- generate_draft - генерирует черновик ответа
- harmonize_draft - проверяет и улучшает стиль
- define_approval_workflow - определяет маршрут согласования
- quality_check - проводит финальную проверку качества

Используй инструменты в логической последовательности для обработки входящего письма.

Порядок работы:
1. Сначала классифицируй письмо
2. Затем извлеки сущности и требования
3. Проанализируй юридические риски
4. Сгенерируй черновик ответа
5. Проверь и улучши стиль
6. Определи маршрут согласования
7. Проведи финальную проверку качества"""

    # Создаем главного агента-оркестратора
    main_agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt)

    return main_agent


def create_sequential_workflow():
    """Последовательная обработка как запасной вариант"""
    llm = OllamaLLM(model="qwen2.5:7b", temperature=0)

    def sequential_processor(input_text: str) -> dict:
        """Обрабатывает письмо последовательно через все этапы"""
        result = {}

        # Извлекаем текст письма из запроса
        if "письмо:" in input_text:
            letter_text = input_text.split("письмо:")[1].strip().strip("'\"")
        else:
            letter_text = input_text

        print("🔍 Шаг 1: Классификация...")
        result["classification"] = classify_correspondence.invoke(letter_text)

        print("📊 Шаг 2: Извлечение сущностей...")
        result["entities"] = extract_entities.invoke(letter_text)

        print("⚖️ Шаг 3: Юридический анализ...")
        context = (
            f"Классификация: {result['classification']}\nСущности: {result['entities']}"
        )
        result["legal_analysis"] = analyze_legal_risks.invoke(context)

        print("📝 Шаг 4: Генерация черновика...")
        draft_context = f"{context}\nЮридический анализ: {result['legal_analysis']}"
        result["draft"] = generate_draft.invoke(draft_context)

        print("🎨 Шаг 5: Гармонизация стиля...")
        harmonize_data = (
            f"Требования: {result['classification']}\nЧерновик: {result['draft']}"
        )
        result["harmonized"] = harmonize_draft.invoke(harmonize_data)

        print("🔄 Шаг 6: Определение согласования...")
        approval_data = f"Классификация: {result['classification']}\nЮридический анализ: {result['legal_analysis']}"
        result["approval"] = define_approval_workflow.invoke(approval_data)

        print("✅ Шаг 7: Финальная проверка...")
        qa_data = f"Исходные данные: {result['classification']}\n{result['entities']}\nФинальный текст: {result['harmonized']}"
        result["final"] = quality_check.invoke(qa_data)

        return result

    return sequential_processor


def create_simple_workflow():
    """Самая простая реализация без агентов"""
    llm = OllamaLLM(model="qwen2.5:7b", temperature=0)

    def simple_processor(input_text: str) -> str:
        """Простая обработка с ручным вызовом инструментов"""
        if "письмо:" in input_text:
            letter_text = input_text.split("письмо:")[1].strip().strip("'\"")
        else:
            letter_text = input_text

        output = "🚀 РЕЗУЛЬТАТ ОБРАБОТКИ ПИСЬМА\n\n"

        # Последовательно вызываем все инструменты
        output += "1. 🔍 КЛАССИФИКАЦИЯ:\n"
        classification = classify_correspondence.invoke(letter_text)
        output += f"{classification}\n\n"

        output += "2. 📊 ИЗВЛЕЧЕНИЕ СУЩНОСТЕЙ:\n"
        entities = extract_entities.invoke(letter_text)
        output += f"{entities}\n\n"

        output += "3. ⚖️ ЮРИДИЧЕСКИЙ АНАЛИЗ:\n"
        legal = analyze_legal_risks.invoke(f"{classification}\n{entities}")
        output += f"{legal}\n\n"

        output += "4. 📝 ЧЕРНОВИК ОТВЕТА:\n"
        draft = generate_draft.invoke(f"{classification}\n{entities}\n{legal}")
        output += f"{draft}\n\n"

        output += "5. 🎨 ГАРМОНИЗИРОВАННЫЙ ТЕКСТ:\n"
        harmonized = harmonize_draft.invoke(f"{classification}\n{draft}")
        output += f"{harmonized}\n\n"

        output += "6. 🔄 МАРШРУТ СОГЛАСОВАНИЯ:\n"
        approval = define_approval_workflow.invoke(f"{classification}\n{legal}")
        output += f"{approval}\n\n"

        output += "7. ✅ ФИНАЛЬНАЯ ПРОВЕРКА:\n"
        final = quality_check.invoke(f"{classification}\n{entities}\n{harmonized}")
        output += f"{final}\n\n"

        return output

    return simple_processor


if __name__ == "__main__":
    try:
        print("🚀 Создание главного агента...")
        agent = create_main_agent()
        print("✅ Агент создан успешно")

        test_letter = "Обработай входящее письмо: 'Просим предоставить выписки по счету 40702810500000012345 за последние 3 месяца для подачи в налоговую инспекцию'"

        print("\n🎯 Запуск обработки письма...")

        # Пробуем разные способы вызова агента
        try:
            # Способ 1: через run
            result = agent.run(test_letter)
        except:
            try:
                # Способ 2: через invoke с input
                result = agent.invoke({"input": test_letter})
            except:
                try:
                    # Способ 3: через invoke с messages
                    result = agent.invoke(
                        {"messages": [{"role": "user", "content": test_letter}]}
                    )
                except Exception as e:
                    print(f"❌ Все способы вызова агента не сработали: {e}")
                    raise

        print("\n" + "=" * 60)
        print("ФИНАЛЬНЫЙ РЕЗУЛЬТАТ ОБРАБОТКИ:")
        print("=" * 60)
        print(result)

    except Exception as e:
        print(f"❌ Ошибка при работе агента: {e}")
        print("🔄 Использую простую обработку...")

        simple_processor = create_simple_workflow()
        result = simple_processor(
            "Обработай входящее письмо: 'Просим предоставить выписки по счету 40702810500000012345 за последние 3 месяца для подачи в налоговую инспекцию'"
        )
        print("\n" + "=" * 60)
        print("ФИНАЛЬНЫЙ РЕЗУЛЬТАТ ОБРАБОТКИ:")
        print("=" * 60)
        print(result)
