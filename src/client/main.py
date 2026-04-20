from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import requests

app = FastAPI(
    title="Определение Усталости Пилотов",
    description="Система мониторинга усталости для авиации",
    version="1.0.0",
)

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Определение Усталости Пилотов</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                background: linear-gradient(135deg, #1a365d 0%, #2c5282 50%, #1a365d 100%);
                min-height: 100vh; padding: 20px;
                color: #333;
            }
            .container { max-width: 1000px; margin: 0 auto; }
            .header {
                text-align: center; margin-bottom: 30px; color: white;
            }
            .header h1 { font-size: 2.2em; margin-bottom: 10px; }
            .header p { font-size: 1.1em; opacity: 0.9; }
            .logo {
                font-size: 3em; margin-bottom: 15px;
            }
            .card {
                background: white; border-radius: 20px; padding: 30px;
                margin-bottom: 25px; box-shadow: 0 15px 50px rgba(0,0,0,0.3);
            }
            .card h2 { 
                color: #1a365d; margin-bottom: 20px; 
                padding-bottom: 15px; border-bottom: 3px solid #4299e1;
                font-size: 1.5em;
            }
            .card h3 {
                color: #2d3748; margin: 20px 0 10px;
                font-size: 1.2em;
            }
            .form-group { margin-bottom: 18px; }
            label { 
                display: block; margin-bottom: 6px; color: #4a5568; 
                font-weight: 600; font-size: 0.95em;
            }
            .hint {
                font-size: 0.85em; color: #718096; margin-top: 3px;
            }
            input[type="number"], input[type="file"] {
                width: 100%; padding: 14px; border: 2px solid #e2e8f0;
                border-radius: 10px; font-size: 16px; transition: all 0.3s;
                background: #f7fafc;
            }
            input:focus { 
                outline: none; border-color: #4299e1; 
                background: white; box-shadow: 0 0 0 3px rgba(66,153,225,0.2);
            }
            .btn {
                background: linear-gradient(135deg, #2b6cb0 0%, #4299e1 100%);
                color: white; border: none; padding: 16px 30px;
                border-radius: 10px; font-size: 18px; cursor: pointer;
                width: 100%; transition: all 0.3s;
                font-weight: 600;
            }
            .btn:hover { 
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(66,153,225,0.4);
            }
            .btn:disabled { opacity: 0.6; cursor: not-allowed; }
            .result {
                margin-top: 25px; padding: 25px; border-radius: 15px;
                display: none; animation: fadeIn 0.5s;
            }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } }
            .result.success { background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%); border: 2px solid #48bb78; }
            .result.warning { background: linear-gradient(135deg, #fffaf0 0%, #feebc8 100%); border: 2px solid #ed8936; }
            .result.danger { background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%); border: 2px solid #f56565; }
            .result.error { background: #fff5f5; border: 2px solid #f56565; }
            .result h3 { margin-bottom: 15px; color: #2d3748; font-size: 1.3em; }
            .result p { margin: 8px 0; color: #4a5568; }
            .fatigue-badge {
                display: inline-block; padding: 12px 25px; border-radius: 25px;
                font-weight: bold; font-size: 1.4em; margin: 10px 0;
            }
            .fatigue-high { background: linear-gradient(135deg, #c53030 0%, #e53e3e 100%); color: white; }
            .fatigue-moderate { background: linear-gradient(135deg, #c05621 0%, #ed8936 100%); color: white; }
            .fatigue-low { background: linear-gradient(135deg, #276749 0%, #48bb78 100%); color: white; }
            .confidence { font-size: 0.95em; color: #718096; }
            .preview-image { max-width: 100%; max-height: 250px; margin: 15px auto; display: block; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
            .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
            .spinner {
                border: 4px solid #e2e8f0; border-top: 4px solid #4299e1;
                border-radius: 50%; width: 40px; height: 40px;
                animation: spin 1s linear infinite; margin: 20px auto;
            }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .recommendation {
                background: white; border-radius: 12px; padding: 20px;
                margin: 15px 0; border-left: 5px solid #4299e1;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            }
            .recommendation h4 {
                color: #2d3748; margin-bottom: 10px; font-size: 1.1em;
                display: flex; align-items: center; gap: 8px;
            }
            .recommendation p { color: #4a5568; line-height: 1.6; }
            .rest-time {
                background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
                border-radius: 10px; padding: 15px; margin: 15px 0;
                text-align: center;
            }
            .rest-time .time {
                font-size: 2.5em; font-weight: bold; color: #2b6cb0;
            }
            .rest-time .label {
                color: #4a5568; font-size: 0.95em;
            }
            .status-bar {
                background: rgba(0,0,0,0.8); color: white; padding: 12px 20px;
                text-align: center; position: fixed; bottom: 0; left: 0; right: 0;
                backdrop-filter: blur(10px);
            }
            .status-indicator { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }
            .status-connected { background: #48bb78; }
            .status-disconnected { background: #f56565; }
            .prob-bar {
                background: #e2e8f0; border-radius: 5px; height: 20px;
                margin: 5px 0; overflow: hidden;
            }
            .prob-fill {
                height: 100%; border-radius: 5px; transition: width 0.5s;
            }
            .prob-high { background: linear-gradient(90deg, #fc8181, #f56565); }
            .prob-moderate { background: linear-gradient(90deg, #fbd38d, #ed8936); }
            .prob-low { background: linear-gradient(90deg, #9ae6b4, #48bb78); }
            .info-box {
                background: #ebf8ff; border-radius: 10px; padding: 15px;
                margin: 15px 0; border-left: 4px solid #4299e1;
            }
            .info-box p { color: #2b6cb0; font-size: 0.9em; }
            .flight-info {
                display: flex; gap: 20px; margin-bottom: 20px;
            }
            .flight-stat {
                flex: 1; background: #f7fafc; padding: 15px;
                border-radius: 10px; text-align: center;
            }
            .flight-stat .value { font-size: 1.8em; font-weight: bold; color: #2b6cb0; }
            .flight-stat .label { font-size: 0.85em; color: #718096; }
            @media (max-width: 768px) {
                .grid-2, .grid-3 { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">&#x2708;&#xFE0F;</div>
                <h1>Определение Усталости Пилотов</h1>
                <p>Система мониторинга усталости для обеспечения безопасности полётов</p>
            </div>
            
            <div class="card">
                <h2>&#x1F4CB; Анализ изображений (Усталость по лицу)</h2>
                <div class="info-box">
                    <p>Загрузите фотографию лица для анализа признаков усталости: положение глаз, мимика, цвет кожи.</p>
                </div>
                <div id="image-preview-container" style="display: none; text-align: center;">
                    <img id="image-preview" class="preview-image" />
                </div>
                <input type="file" id="image-input" accept="image/*" onchange="previewImage(this)">
                <button class="btn" onclick="uploadImage()" style="margin-top: 15px;">
                    &#x1F50D; Анализировать изображение
                </button>
                <div id="image-spinner" class="spinner" style="display: none;"></div>
                <div id="image-result" class="result"></div>
            </div>

            <div class="card">
                <h2>&#x1F4CA; Ввод данных (Усталость принятия решений)</h2>
                <div class="info-box">
                    <p>Введите параметры для оценки когнитивной усталости пилота.</p>
                </div>
                
                <div class="flight-info">
                    <div class="flight-stat">
                        <div class="value" id="flight-hours">0</div>
                        <div class="label">Часов полёта</div>
                    </div>
                    <div class="flight-stat">
                        <div class="value" id="sleep-deficit">0</div>
                        <div class="label">Дефицит сна (часы)</div>
                    </div>
                </div>

                <div class="grid-2">
                    <div class="form-group">
                        <label>Часов бодрствования</label>
                        <input type="number" id="hours_awake" min="0" max="48" step="0.5" value="8" onchange="updateStats()">
                        <div class="hint">Время с последнего сна</div>
                    </div>
                    <div class="form-group">
                        <label>Часов сна прошлой ночью</label>
                        <input type="number" id="sleep_hours" min="0" max="24" step="0.5" value="7" onchange="updateStats()">
                        <div class="hint">Рекомендуется 7-9 часов</div>
                    </div>
                    <div class="form-group">
                        <label>Принято решений</label>
                        <input type="number" id="decisions_made" min="0" value="20" onchange="updateStats()">
                        <div class="hint">Количество решений за смену</div>
                    </div>
                    <div class="form-group">
                        <label>Переключений задач</label>
                        <input type="number" id="task_switches" min="0" value="5" onchange="updateStats()">
                        <div class="hint">Смена между задачами</div>
                    </div>
                    <div class="form-group">
                        <label>Среднее время решения (сек)</label>
                        <input type="number" id="avg_decision_time" min="0" step="0.1" value="2.5" onchange="updateStats()">
                        <div class="hint">Время на принятие решения</div>
                    </div>
                    <div class="form-group">
                        <label>Потребление кофеина (чашки)</label>
                        <input type="number" id="caffeine_cups" min="0" value="2" onchange="updateStats()">
                        <div class="hint">Кофе, чай, энергетики</div>
                    </div>
                </div>

                <div class="grid-3">
                    <div class="form-group">
                        <label>Уровень стресса (1-10)</label>
                        <input type="number" id="stress_level" min="1" max="10" value="5" onchange="updateStats()">
                    </div>
                    <div class="form-group">
                        <label>Частота ошибок (0-1)</label>
                        <input type="number" id="error_rate" min="0" max="1" step="0.01" value="0.05" onchange="updateStats()">
                    </div>
                    <div class="form-group">
                        <label>Когнитивная нагрузка (0-1)</label>
                        <input type="number" id="cognitive_load" min="0" max="1" step="0.01" value="0.5" onchange="updateStats()">
                    </div>
                </div>

                <button class="btn" onclick="submitTabular()">
                    &#x1F50D; Провести анализ усталости
                </button>
                
                <div id="tabular-spinner" class="spinner" style="display: none;"></div>
                <div id="tabular-result" class="result"></div>
            </div>

            <div class="card" style="background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%); color: white;">
                <h2 style="color: white; border-bottom-color: #63b3ed;">&#x2139;&#xFE0F; О системе</h2>
                <p style="margin: 15px 0; line-height: 1.8;">
                    Система определения усталости пилотов разработана для обеспечения безопасности авиаперевозок.
                    Мониторинг усталости - критически важный элемент управления безопасностью полётов (SMS).
                </p>
                <p style="opacity: 0.8; font-size: 0.9em;">
                    Система не является заменой медицинского осмотра. При сомнениях обратитесь к руководству и медицинскому персоналу.
                </p>
            </div>
        </div>

        <div class="status-bar">
            <span id="status-indicator" class="status-indicator status-disconnected"></span>
            <span id="status-text">Проверка подключения к серверу...</span>
        </div>

        <script>
            const SERVER_URL = '""" + SERVER_URL + """';
            
            const RECOMMENDATIONS = {
                'High': {
                    icon: '&#x26A0;&#xFE0F;',
                    title: 'КРИТИЧЕСКИЙ УРОВЕНЬ УСТАЛОСТИ',
                    color: 'danger',
                    restTime: '12-14 часов',
                    actions: [
                        '&#x274C; НЕМЕДЛЕННО прекратите выполнение полётных обязанностей',
                        '&#x1F6AB; Не допускайте к выполнению рейса',
                        '&#x1F4DE; Сообщите руководству о невозможности выполнения полёта',
                        '&#x1F4F1; Обратитесь за медицинской помощью при необходимости',
                        '&#x1F6CF; Обеспечьте полноценный отдых перед следующей сменой'
                    ],
                    description: 'Пилот находится в состоянии сильной усталости. Риск ошибок критически высок.'
                },
                'Moderate': {
                    icon: '&#x26A0;&#xFE0F;',
                    title: 'ПОВЫШЕННЫЙ УРОВЕНЬ УСТАЛОСТИ',
                    color: 'warning',
                    restTime: '8-10 часов',
                    actions: [
                        '&#x26A0; Рекомендуется отмена или перенос некритичных рейсов',
                        '&#x1F4AC; Проведите дополнительный брифинг с вторым пилотом',
                        '&#x23F0; Увеличьте частоту перерывов',
                        '&#x1F4A4; Избегайте сложных метеоусловий',
                        '&#x1F4A1; Используйте дополнительное освещение в кабине'
                    ],
                    description: 'Усталость влияет на принятие решений. Требуется повышенное внимание.'
                },
                'Low': {
                    icon: '&#x2705;',
                    title: 'УРОВЕНЬ УСТАЛОСТИ В НОРМЕ',
                    color: 'success',
                    restTime: 'Обычный отдых',
                    actions: [
                        '&#x2705; Можно выполнять полётные обязанности',
                        '&#x1F4CB; Следуйте стандартным процедурам',
                        '&#x23F0; Поддерживайте регулярные перерывы',
                        '&#x1F4DD; Ведите записи о своём состоянии'
                    ],
                    description: 'Усталость в допустимых пределах. Продолжайте стандартный мониторинг.'
                }
            };
            
            const FLIGHT_HOURS_LIMIT = 900;
            const DAILY_LIMIT = 8;
            const WEEKLY_LIMIT = 60;

            function updateStats() {
                const hoursAwake = parseFloat(document.getElementById('hours_awake').value) || 0;
                const sleepHours = parseFloat(document.getElementById('sleep_hours').value) || 0;
                const decisions = parseFloat(document.getElementById('decisions_made').value) || 0;
                
                document.getElementById('flight-hours').textContent = hoursAwake;
                document.getElementById('sleep-deficit').textContent = Math.max(0, (8 - sleepHours)).toFixed(1);
            }
            
            async function checkConnection() {
                try {
                    const response = await fetch(SERVER_URL + '/health');
                    if (response.ok) {
                        document.getElementById('status-indicator').className = 'status-indicator status-connected';
                        document.getElementById('status-text').textContent = 'Подключено к серверу';
                    } else {
                        throw new Error('Server error');
                    }
                } catch (e) {
                    document.getElementById('status-indicator').className = 'status-indicator status-disconnected';
                    document.getElementById('status-text').textContent = 'Отключено - сервер недоступен';
                }
            }
            
            function previewImage(input) {
                const container = document.getElementById('image-preview-container');
                const preview = document.getElementById('image-preview');
                if (input.files && input.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        container.style.display = 'block';
                    };
                    reader.readAsDataURL(input.files[0]);
                }
            }
            
            async function uploadImage() {
                const input = document.getElementById('image-input');
                const spinner = document.getElementById('image-spinner');
                const result = document.getElementById('image-result');
                
                if (!input.files[0]) {
                    alert('Пожалуйста, выберите изображение');
                    return;
                }
                
                spinner.style.display = 'block';
                result.style.display = 'none';
                
                const formData = new FormData();
                formData.append('file', input.files[0]);
                
                try {
                    const response = await fetch(SERVER_URL + '/predict/image', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    const isFatigue = data.prediction === 'Fatigue';
                    const rec = RECOMMENDATIONS[isFatigue ? 'High' : 'Low'];
                    
                    result.className = `result ${rec.color}`;
                    result.style.display = 'block';
                    result.innerHTML = `
                        <h3>${rec.icon} ${data.prediction === 'Fatigue' ? 'Признаки усталости обнаружены' : 'Усталость не обнаружена'}</h3>
                        <p><span class="fatigue-badge ${isFatigue ? 'fatigue-high' : 'fatigue-low'}">${data.prediction === 'Fatigue' ? 'Усталость' : 'Бодрость'}</span></p>
                        <p class="confidence">Уверенность: ${(data.confidence * 100).toFixed(1)}%</p>
                        <div class="recommendation">
                            <h4>${rec.icon} ${rec.title}</h4>
                            <p>${rec.description}</p>
                            <div class="rest-time">
                                <div class="label">Рекомендуемый отдых:</div>
                                <div class="time">${rec.restTime}</div>
                            </div>
                            <h4 style="margin-top: 15px;">Рекомендации:</h4>
                            ${rec.actions.map(a => `<p style="margin: 5px 0;">${a}</p>`).join('')}
                        </div>
                    `;
                } catch (e) {
                    result.className = 'result error';
                    result.style.display = 'block';
                    result.innerHTML = `<h3>&#x274C; Ошибка</h3><p>Не удалось проанализировать изображение: ${e.message}</p>`;
                } finally {
                    spinner.style.display = 'none';
                }
            }
            
            function submitTabular() {
                const data = {
                    Hours_Awake: parseFloat(document.getElementById('hours_awake').value) || 0,
                    Decisions_Made: parseFloat(document.getElementById('decisions_made').value) || 0,
                    Task_Switches: parseFloat(document.getElementById('task_switches').value) || 0,
                    Avg_Decision_Time_sec: parseFloat(document.getElementById('avg_decision_time').value) || 0,
                    Sleep_Hours_Last_Night: parseFloat(document.getElementById('sleep_hours').value) || 0,
                    Caffeine_Intake_Cups: parseFloat(document.getElementById('caffeine_cups').value) || 0,
                    Stress_Level_1_10: parseFloat(document.getElementById('stress_level').value) || 5,
                    Error_Rate: parseFloat(document.getElementById('error_rate').value) || 0,
                    Cognitive_Load_Score: parseFloat(document.getElementById('cognitive_load').value) || 0
                };
                
                analyzeTabularData(data);
            }
            
            async function analyzeTabularData(data) {
                const spinner = document.getElementById('tabular-spinner');
                const result = document.getElementById('tabular-result');
                
                spinner.style.display = 'block';
                result.style.display = 'none';
                
                try {
                    const response = await fetch(SERVER_URL + '/predict/tabular', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    
                    const resultData = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(resultData.detail || 'Ошибка сервера');
                    }
                    
                    const prediction = resultData.prediction;
                    const rec = RECOMMENDATIONS[prediction];
                    
                    result.className = `result ${rec.color}`;
                    result.style.display = 'block';
                    
                    let probHtml = '';
                    const probs = resultData.probabilities || {};
                    ['High', 'Moderate', 'Low'].forEach(level => {
                        const val = (probs[level] || 0) * 100;
                        const colorClass = level === 'High' ? 'prob-high' : level === 'Moderate' ? 'prob-moderate' : 'prob-low';
                        probHtml += `
                            <div style="margin: 8px 0;">
                                <span>${level === 'High' ? 'Высокая' : level === 'Moderate' ? 'Умеренная' : 'Низкая'}: ${val.toFixed(1)}%</span>
                                <div class="prob-bar"><div class="prob-fill ${colorClass}" style="width: ${val}%;"></div></div>
                            </div>
                        `;
                    });
                    
                    result.innerHTML = `
                        <h3>${rec.icon} ${rec.title}</h3>
                        <p><span class="fatigue-badge fatigue-${prediction.toLowerCase()}">${prediction === 'High' ? 'ВЫСОКАЯ' : prediction === 'Moderate' ? 'УМЕРЕННАЯ' : 'НИЗКАЯ'} УСТАЛОСТЬ</span></p>
                        <p class="confidence">Уверенность: ${((resultData.confidence || 0) * 100).toFixed(1)}%</p>
                        
                        <h3 style="margin-top: 20px;">Распределение вероятностей:</h3>
                        ${probHtml}
                        
                        <div class="rest-time">
                            <div class="label">Рекомендуемое время отдыха:</div>
                            <div class="time">${rec.restTime}</div>
                        </div>
                        
                        <div class="recommendation">
                            <h4>${rec.icon} ${rec.description}</h4>
                            <h4 style="margin-top: 15px;">&#x1F4CB; Рекомендации для пилота:</h4>
                            ${rec.actions.map(a => `<p style="margin: 8px 0;">${a}</p>`).join('')}
                        </div>
                        
                        <div class="info-box" style="margin-top: 20px;">
                            <p><strong>&#x2139;&#xFE0F; Примечание:</strong> Данная система является вспомогательным инструментом. 
                            Окончательное решение о допуске к полёту принимается в соответствии с медицинскими нормами и SOP авиакомпании.</p>
                        </div>
                    `;
                } catch (e) {
                    result.className = 'result error';
                    result.innerHTML = `<h3>&#x274C; Ошибка</h3><p>Не удалось проанализировать данные: ${e.message}</p>`;
                    result.style.display = 'block';
                } finally {
                    spinner.style.display = 'none';
                }
            }
            
            updateStats();
            checkConnection();
            setInterval(checkConnection, 30000);
        </script>
    </body>
    </html>
    """


@app.get("/client")
async def client():
    return await home()


@app.get("/api/status")
async def get_status():
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        return {"connected": True, "server_status": response.json()}
    except Exception as e:
        return {"connected": False, "error": str(e)}


@app.post("/api/upload/image")
async def upload_image(file: UploadFile = File(...)):
    try:
        files = {"file": (file.filename, await file.read(), file.content_type)}
        response = requests.post(f"{SERVER_URL}/predict/image", files=files, timeout=60)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload/tabular")
async def upload_tabular(data: dict):
    try:
        response = requests.post(
            f"{SERVER_URL}/predict/tabular",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload/batch/tabular")
async def upload_batch_tabular(data: list):
    try:
        response = requests.post(
            f"{SERVER_URL}/predict/batch/tabular",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
