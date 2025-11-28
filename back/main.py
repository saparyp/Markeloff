from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import logging
import uuid

from models import EmailProcessingRequest, ProcessingResponse
from agents.classifier_agent import ClassifierAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Corporate Email AI Processor", version="1.0.0")

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # Адреса фронта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# инициализация
classifier_agent = ClassifierAgent()


@app.get("/")
async def root():
    return {"message": "Corporate Email AI Processor API", "status": "active"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "email_processor"}


@app.post("/process-email", response_model=ProcessingResponse)
async def process_email(request: EmailProcessingRequest):
    """
    Основной эндпоинт для обработки email
    Получает текст письма и возвращает классификацию
    """

    try:
        logger.info(f"Processing email request, text length: {len(request.email_text)}")

        # агент-классификатор
        classification_result = await classifier_agent.classify_email(
            request.email_text
        )

        response = ProcessingResponse(
            status="completed",
            classification=classification_result,
            message="Email successfully processed and classified",
        )

        logger.info(f"Classification completed: {classification_result.type}")
        return response

    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/process-email-async", response_model=ProcessingResponse)
async def process_email_async(
    request: EmailProcessingRequest, background_tasks: BackgroundTasks
):
    """
    Асинхронная обработка (для длительных операций)
    Возвращает task_id сразу, результат можно получить позже
    """

    task_id = str(uuid.uuid4())

    # background_tasks.add_task(process_email_background, task_id, request.dict())

    return ProcessingResponse(
        task_id=task_id,
        status="processing",
        message="Email accepted for background processing",
    )


# Эндпоинт
@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    return {
        "task_id": task_id,
        "status": "completed",  # будет проверять статус в Celery
        "result_available": True,
    }
