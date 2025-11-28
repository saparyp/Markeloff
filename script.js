document.addEventListener("DOMContentLoaded", function () {
  const API_BASE = "http://localhost:8000";

  let currentThreadId = null;
  let currentResponseOptions = null;
  const fileButton = document.getElementById("fileButton");
  const generateButton = document.getElementById("generateButton");
  const copyButton = document.getElementById("copyButton");
  const deleteButton = document.getElementById("deleteButton");
  const inputText = document.getElementById("inputText");
  const responseText = document.getElementById("responseText");
  const fileNameDisplay = document.getElementById("fileName");

  let currentFile = null; // Храним информацию о текущем файле

  // Обработка загрузки файла
  fileButton.addEventListener("click", function () {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".txt,.text,.doc,.docx,.pdf,.rtf,.odt";
    fileInput.style.display = "none";
    document.body.appendChild(fileInput);

    fileInput.addEventListener("change", function () {
      if (this.files.length > 0) {
        const file = this.files[0];
        const fileName = file.name;
        const fileExtension = fileName.split(".").pop().toLowerCase();

        // Разрешенные расширения файлов
        const allowedExtensions = [
          "txt",
          "text",
          "doc",
          "docx",
          "pdf",
          "rtf",
          "odt",
        ];
        const allowedTypes = [
          "text/plain",
          "application/msword",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          "application/pdf",
          "application/rtf",
          "application/vnd.oasis.opendocument.text",
        ];

        // Проверка расширения и типа файла
        if (
          !allowedExtensions.includes(fileExtension) ||
          !allowedTypes.includes(file.type)
        ) {
          alert(
            "Пожалуйста, выберите текстовый файл (.txt, .doc, .docx, .pdf, .rtf, .odt)"
          );
          resetFile();
          document.body.removeChild(fileInput);
          return;
        }

        // Проверка размера файла (максимум 5MB)
        const maxSize = 5 * 1024 * 1024;
        if (file.size > maxSize) {
          alert("Файл слишком большой. Максимальный размер: 5MB");
          resetFile();
          document.body.removeChild(fileInput);
          return;
        }

        // Сохраняем информацию о файле
        currentFile = {
          name: fileName,
          size: file.size,
          type: file.type,
          extension: fileExtension,
        };

        updateFileDisplay();

        // Чтение содержимого файла
        const reader = new FileReader();

        reader.onload = function (e) {
          if (file.type.includes("text") || fileExtension === "txt") {
            inputText.value = e.target.result;
          } else {
            inputText.value = `[Файл "${fileName}" загружен успешно]\n\nДля файлов формата .${fileExtension} содержимое автоматически не извлекается. Пожалуйста, скопируйте текст вручную.`;
          }
        };

        reader.onerror = function () {
          alert("Ошибка при чтении файла");
          resetFile();
        };

        reader.readAsText(file);
      }
      document.body.removeChild(fileInput);
    });

    fileInput.click();
  });

  // Обработка удаления файла
  deleteButton.addEventListener("click", function () {
    resetFile();
  });

  // Функция сброса файла
  function resetFile() {
    currentFile = null;
    fileNameDisplay.textContent = "Файл не выбран";
    deleteButton.style.display = "none";
    inputText.value = "";
  }

  // Функция обновления отображения информации о файле
  function updateFileDisplay() {
    if (currentFile) {
      // Форматируем размер файла
      const fileSize =
        currentFile.size > 1024 * 1024
          ? (currentFile.size / (1024 * 1024)).toFixed(2) + " MB"
          : (currentFile.size / 1024).toFixed(2) + " KB";

      fileNameDisplay.textContent = `${currentFile.name} (${fileSize})`;
      deleteButton.style.display = "flex";
    } else {
      fileNameDisplay.textContent = "Файл не выбран";
      deleteButton.style.display = "none";
    }
  }

  // Обработка генерации ответа
  generateButton.addEventListener("click", function () {
    const text = inputText.value.trim();

    if (!text) {
      alert("Пожалуйста, введите текст обращения или загрузите файл");
      return;
    }

    // Добавляем анимацию загрузки
    this.classList.add("loading");
    this.textContent = "ГЕНЕРАЦИЯ...";
    this.disabled = true;

    // Имитация процесса генерации ответа
    setTimeout(() => {
      const generatedResponse = generateMockResponse(text);
      responseText.value = generatedResponse;

      // Возвращаем исходное состояние кнопки
      this.classList.remove("loading");
      this.textContent = "СГЕНЕРИРОВАТЬ";
      this.disabled = false;
    }, 1500);
  });

  // Обработка копирования текста
  copyButton.addEventListener("click", function () {
    if (!responseText.value.trim()) {
      alert("Нет текста для копирования");
      return;
    }

    responseText.select();
    responseText.setSelectionRange(0, 99999);

    try {
      navigator.clipboard
        .writeText(responseText.value)
        .then(() => {
          const originalText = this.textContent;
          this.textContent = "СКОПИРОВАНО!";
          this.style.background = "#666";
          this.style.color = "white";

          setTimeout(() => {
            this.textContent = originalText;
            this.style.background = "transparent";
            this.style.color = "#666";
          }, 2000);
        })
        .catch((err) => {
          console.error("Ошибка копирования: ", err);
          const successful = document.execCommand("copy");
          if (successful) {
            const originalText = this.textContent;
            this.textContent = "СКОПИРОВАНО!";
            setTimeout(() => {
              this.textContent = originalText;
            }, 2000);
          } else {
            alert("Не удалось скопировать текст");
          }
        });
    } catch (err) {
      console.error("Не удалось скопировать текст: ", err);
      alert("Не удалось скопировать текст");
    }
  });

  // Функция для генерации mock-ответа
  function generateMockResponse(inputText) {
    const cleanText = inputText.replace(
      /\[Файл ".*" загружен успешно\]\n\n/,
      ""
    );

    const responses = [
      `Уважаемый пользователь,\n\nБлагодарим Вас за обращение. Рассмотрев Ваш запрос, мы подготовили следующий ответ:\n\n${cleanText.substring(
        0,
        100
      )}...\n\nС уважением,\nСлужба поддержки`,

      `На основании Вашего обращения сообщаем следующее:\n\nВаш запрос был тщательно изучен. Принято решение о необходимости дополнительной проверки указанной информации. Срок рассмотрения - 5 рабочих дней.\n\nБлагодарим за понимание.`,

      `Здравствуйте!\n\nПолучили Ваше обращение. В настоящее время специалисты работают над решением данного вопроса. О результатах уведомим дополнительно.\n\nС наилучшими пожеланиями.`,
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  }
});
