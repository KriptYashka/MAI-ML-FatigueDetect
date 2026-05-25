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
                min-height: 100vh; padding: 20px; color: #333;
            }
            .container { max-width: 1000px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; color: white; }
            .header h1 { font-size: 2.2em; margin-bottom: 10px; }
            .header p { font-size: 1.1em; opacity: 0.9; }
            .logo { font-size: 3em; margin-bottom: 15px; }
            .card {
                background: white; border-radius: 20px; padding: 30px;
                margin-bottom: 25px; box-shadow: 0 15px 50px rgba(0,0,0,0.3);
            }
            .card h2 { 
                color: #1a365d; margin-bottom: 20px; 
                padding-bottom: 15px; border-bottom: 3px solid #4299e1;
                font-size: 1.5em;
            }
            .card h3 { color: #2d3748; margin: 20px 0 10px; font-size: 1.2em; }
            .form-group { margin-bottom: 18px; }
            label { display: block; margin-bottom: 6px; color: #4a5568; font-weight: 600; font-size: 0.95em; }
            .hint { font-size: 0.85em; color: #718096; margin-top: 3px; }
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
                width: 100%; transition: all 0.3s; font-weight: 600;
            }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(66,153,225,0.4); }
            .btn:disabled { opacity: 0.6; cursor: not-allowed; }
            .btn-success { background: linear-gradient(135deg, #276749 0%, #48bb78 100%); }
            .btn-danger { background: linear-gradient(135deg, #c53030 0%, #e53e3e 100%); }
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
            .recommendation h4 { color: #2d3748; margin-bottom: 10px; font-size: 1.1em; display: flex; align-items: center; gap: 8px; }
            .recommendation p { color: #4a5568; line-height: 1.6; }
            .rest-time {
                background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
                border-radius: 10px; padding: 15px; margin: 15px 0;
                text-align: center;
            }
            .rest-time .time { font-size: 2.5em; font-weight: bold; color: #2b6cb0; }
            .rest-time .label { color: #4a5568; font-size: 0.95em; }
            .status-bar {
                background: rgba(0,0,0,0.8); color: white; padding: 12px 20px;
                text-align: center; position: fixed; bottom: 0; left: 0; right: 0;
                backdrop-filter: blur(10px);
            }
            .status-indicator { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }
            .status-connected { background: #48bb78; }
            .status-disconnected { background: #f56565; }
            .prob-bar { background: #e2e8f0; border-radius: 5px; height: 20px; margin: 5px 0; overflow: hidden; }
            .prob-fill { height: 100%; border-radius: 5px; transition: width 0.5s; }
            .prob-high { background: linear-gradient(90deg, #fc8181, #f56565); }
            .prob-moderate { background: linear-gradient(90deg, #fbd38d, #ed8936); }
            .prob-low { background: linear-gradient(90deg, #9ae6b4, #48bb78); }
            .info-box { background: #ebf8ff; border-radius: 10px; padding: 15px; margin: 15px 0; border-left: 4px solid #4299e1; }
            .info-box p { color: #2b6cb0; font-size: 0.9em; }
            .step-indicator { display: flex; margin-bottom: 20px; gap: 10px; }
            .step {
                flex: 1; padding: 12px; border-radius: 10px; text-align: center;
                font-weight: 600; transition: all 0.3s;
            }
            .step-active { background: #4299e1; color: white; }
            .step-done { background: #48bb78; color: white; }
            .step-pending { background: #e2e8f0; color: #a0aec0; }
            .game-area {
                background: #1a202c; border-radius: 15px; padding: 30px;
                text-align: center; min-height: 250px; position: relative;
                overflow: hidden;
            }
            .game-target {
                width: 80px; height: 80px; border-radius: 50%;
                display: inline-flex; align-items: center; justify-content: center;
                cursor: pointer; font-size: 24px; font-weight: bold;
                transition: all 0.1s; position: absolute;
                user-select: none; box-shadow: 0 0 20px rgba(255,255,255,0.3);
            }
            .game-target:active { transform: scale(0.9); }
            .game-target.green { background: radial-gradient(circle at 30% 30%, #48bb78, #276749); }
            .game-target.red { background: radial-gradient(circle at 30% 30%, #fc8181, #c53030); }
            .game-target.yellow { background: radial-gradient(circle at 30% 30%, #fbd38d, #b7791f); }
            .game-target.blue { background: radial-gradient(circle at 30% 30%, #63b3ed, #2b6cb0); }
            .game-timer-bar {
                height: 8px; background: #e2e8f0; border-radius: 4px;
                margin-bottom: 15px; overflow: hidden;
            }
            .game-timer-fill {
                height: 100%; background: linear-gradient(90deg, #48bb78, #f6ad55, #fc8181);
                border-radius: 4px; transition: width 0.1s linear;
            }
            .game-scoreboard {
                display: flex; gap: 15px; margin-bottom: 20px;
                justify-content: center; flex-wrap: wrap;
            }
            .game-stat {
                background: #2d3748; color: white; padding: 10px 20px;
                border-radius: 10px; text-align: center; min-width: 100px;
            }
            .game-stat .value { font-size: 1.5em; font-weight: bold; }
            .game-stat .label { font-size: 0.75em; opacity: 0.8; }
            .game-instruction {
                background: #2d3748; color: #e2e8f0; padding: 15px;
                border-radius: 10px; margin-bottom: 20px; font-size: 1em;
                line-height: 1.6;
            }
            .phase-separator { text-align: center; margin: 30px 0; position: relative; }
            .phase-separator::before {
                content: ''; position: absolute; left: 0; right: 0; top: 50%;
                height: 2px; background: #e2e8f0;
            }
            .phase-label {
                background: white; padding: 10px 20px;
                border-radius: 20px; position: relative; z-index: 1;
                color: #718096; font-size: 0.9em;
            }
            .manual-section { display: none; }
            .manual-section.active { display: block; animation: fadeIn 0.5s; }
            @media (max-width: 768px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">&#x2708;&#xFE0F;</div>
                <h1>Определение Усталости Пилотов</h1>
                <p>Двухэтапная диагностика: игра на внимательность + опрос</p>
            </div>
            
            <div class="card">
                <h2>&#x1F4F7; Анализ изображений</h2>
                <div class="info-box"><p>Загрузите фотографию лица для визуальной диагностики усталости.</p></div>
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
                <h2>&#x1F3AE; Диагностика когнитивной усталости</h2>
                
                <div class="step-indicator">
                    <div id="step1" class="step step-active">&#x1F3AE; Этап 1: Игра 30 сек</div>
                    <div id="step2" class="step step-pending">&#x1F4CB; Этап 2: Дополнительные данные</div>
                    <div id="step3" class="step step-pending">&#x1F9E0; Результат</div>
                </div>

                <div id="game-section">
                    <div class="game-instruction">
                        <strong>&#x1F6A8; Тест на внимательность (авиационный симулятор):</strong><br>
                        На экране будет появляться &#x1F534; красный индикатор — нажимайте <strong>ПРОБЕЛ</strong> как можно быстрее.<br>
                        &#x1F7E2; Зелёный — <strong>НЕ НАЖИМАЙТЕ</strong> (сдерживание реакции).<br>
                        &#x23F1;&#xFE0F; Тест длится 30 секунд. Чем быстрее и точнее — тем ниже усталость.
                    </div>

                    <div class="game-timer-bar">
                        <div id="game-timer-fill" class="game-timer-fill" style="width: 100%;"></div>
                    </div>

                    <div class="game-scoreboard">
                        <div class="game-stat">
                            <div class="value" id="game-time">30</div>
                            <div class="label">&#x23F1;&#xFE0F; Секунд</div>
                        </div>
                        <div class="game-stat">
                            <div class="value" id="game-reactions">0</div>
                            <div class="label">&#x1F4A8; Реакций</div>
                        </div>
                        <div class="game-stat">
                            <div class="value" id="game-correct">0</div>
                            <div class="label">&#x2705; Верных</div>
                        </div>
                        <div class="game-stat">
                            <div class="value" id="game-wrong">0</div>
                            <div class="label">&#x274C; Ошибок</div>
                        </div>
                        <div class="game-stat">
                            <div class="value" id="game-avg-ms">0</div>
                            <div class="label">&#x23F0; Среднее (мс)</div>
                        </div>
                    </div>

                    <div class="game-area" id="game-area">
                        <div id="game-message" style="color: #a0aec0; font-size: 1.2em;">
                            Нажмите <strong>"Начать тест"</strong> для запуска
                        </div>
                        <div id="game-target" class="game-target" style="display: none;"></div>
                    </div>

                    <button id="game-start-btn" class="btn btn-success" onclick="startGame()" style="margin-top: 15px;">
                        &#x25B6;&#xFE0F; Начать тест на внимательность
                    </button>
                    <button id="game-next-btn" class="btn" onclick="goToManual()" style="margin-top: 15px; display: none;">
                        &#x1F4CB; Перейти к вводу дополнительных данных
                    </button>
                </div>

                <div id="manual-section" class="manual-section">
                    <div class="info-box" style="margin-bottom: 20px;">
                        <p>&#x2705; Игра завершена. Заполните оставшиеся параметры для полного анализа.</p>
                    </div>
                    
                    <div class="grid-2">
                        <div class="form-group">
                            <label>&#x23F0; Часов бодрствования</label>
                            <input type="number" id="hours_awake" min="0" max="48" step="0.5" value="8">
                            <div class="hint">Сколько часов вы уже не спите</div>
                        </div>
                        <div class="form-group">
                            <label>&#x1F634; Часов сна прошлой ночью</label>
                            <input type="number" id="sleep_hours" min="0" max="24" step="0.5" value="7">
                            <div class="hint">Сколько часов вы спали</div>
                        </div>
                        <div class="form-group">
                            <label>&#x2615; Потребление кофеина (чашки)</label>
                            <input type="number" id="caffeine_cups" min="0" value="2">
                            <div class="hint">Кофе, чай, энергетики за сегодня</div>
                        </div>
                        <div class="form-group">
                            <label>&#x1F4A8; Уровень стресса (1-10)</label>
                            <input type="number" id="stress_level" min="1" max="10" value="5">
                            <div class="hint">Субъективная оценка стресса</div>
                        </div>
                    </div>

                    <button class="btn" onclick="submitCombined()">
                        &#x1F9E0; Провести полный анализ
                    </button>
                </div>

                <div id="tabular-spinner" class="spinner" style="display: none;"></div>
                <div id="tabular-result" class="result"></div>
            </div>

            <div class="card" style="background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%); color: white;">
                <h2 style="color: white; border-bottom-color: #63b3ed;">&#x2139;&#xFE0F; О системе</h2>
                <p style="margin: 15px 0; line-height: 1.8;">
                    Система определения усталости пилотов разработана для обеспечения безопасности авиаперевозок.
                    Двухэтапная диагностика включает объективный тест на внимательность и сбор дополнительных данных.
                </p>
                <p style="opacity: 0.8; font-size: 0.9em;">
                    Система не является заменой медицинского осмотра. При сомнениях обратитесь к руководству.
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
                    icon: '&#x26A0;&#xFE0F;', title: 'КРИТИЧЕСКИЙ УРОВЕНЬ УСТАЛОСТИ',
                    color: 'danger', restTime: '12-14 часов',
                    actions: [
                        '&#x274C; НЕМЕДЛЕННО прекратите выполнение полётных обязанностей',
                        '&#x1F6AB; Не допускайте к выполнению рейса',
                        '&#x1F4DE; Сообщите руководству',
                        '&#x1F6CF; Обеспечьте 12+ часов отдыха'
                    ],
                    description: 'Пилот в состоянии сильной усталости. Риск ошибок критически высок.'
                },
                'Moderate': {
                    icon: '&#x26A0;&#xFE0F;', title: 'ПОВЫШЕННЫЙ УРОВЕНЬ УСТАЛОСТИ',
                    color: 'warning', restTime: '8-10 часов',
                    actions: [
                        '&#x26A0; Рекомендуется перенос некритичных рейсов',
                        '&#x1F4AC; Усиленный брифинг с экипажем',
                        '&#x23F0; Увеличьте частоту перерывов',
                        '&#x1F4A4; Избегайте сложных метеоусловий'
                    ],
                    description: 'Усталость влияет на внимание. Требуется повышенный контроль.'
                },
                'Low': {
                    icon: '&#x2705;', title: 'УРОВЕНЬ УСТАЛОСТИ В НОРМЕ',
                    color: 'success', restTime: 'Обычный отдых',
                    actions: [
                        '&#x2705; Можно выполнять полётные обязанности',
                        '&#x1F4CB; Следуйте стандартным процедурам',
                        '&#x23F0; Поддерживайте регулярные перерывы'
                    ],
                    description: 'Усталость в допустимых пределах.'
                }
            };

            let gameData = {
                running: false,
                reactions: 0,
                correct: 0,
                wrong: 0,
                totalTime: 0,
                startTime: 0,
                timeLeft: 30,
                currentStimulus: null,
                stimulusTime: 0,
                reactionTimes: [],
                stimulusSequence: [],
                keyPressed: false,
                stimulusTimeout: null,
                trialTimeout: null,
            };

            function startGame() {
                const btn = document.getElementById('game-start-btn');
                btn.disabled = true;
                btn.textContent = '⏳ Идёт тест...';

                gameData.running = true;
                gameData.reactions = 0;
                gameData.correct = 0;
                gameData.wrong = 0;
                gameData.timeLeft = 30;
                gameData.reactionTimes = [];
                gameData.stimulusSequence = [];
                gameData.startTime = Date.now();
                gameData.keyPressed = false;

                document.getElementById('game-next-btn').style.display = 'none';
                document.getElementById('game-message').style.display = 'none';
                document.getElementById('tabular-result').style.display = 'none';
                updateScoreboard();

                document.addEventListener('keydown', handleKeyPress);
                gameLoop();
            }

            function gameLoop() {
                if (!gameData.running) return;
                
                const elapsed = (Date.now() - gameData.startTime) / 1000;
                gameData.timeLeft = Math.max(0, 30 - elapsed);
                
                updateTimer();
                updateScoreboard();

                if (gameData.timeLeft <= 0) {
                    endGame();
                    return;
                }

                if (!gameData.currentStimulus && !gameData.keyPressed) {
                    showRandomStimulus();
                }

                requestAnimationFrame(gameLoop);
            }

            function showRandomStimulus() {
                gameData.keyPressed = false;
                
                const target = document.getElementById('game-target');
                const area = document.getElementById('game-area');
                const areaRect = area.getBoundingClientRect();
                
                const isRed = Math.random() < 0.7;
                const color = isRed ? 'red' : 'green';
                const label = isRed ? '!' : 'O';

                target.className = `game-target ${color}`;
                target.textContent = label;
                target.style.display = 'flex';
                
                const padding = 100;
                const maxX = area.offsetWidth - 100;
                const maxY = area.offsetHeight - 100;
                target.style.left = (padding + Math.random() * (maxX - 2 * padding)) + 'px';
                target.style.top = (padding + Math.random() * (maxY - 2 * padding)) + 'px';

                gameData.currentStimulus = { isRed, time: Date.now(), responded: false };
                gameData.stimulusSequence.push({ isRed, time: Date.now(), missed: true });

                const timeout = 3000 + Math.random() * 2000;
                gameData.stimulusTimeout = setTimeout(() => {
                    if (gameData.currentStimulus && !gameData.currentStimulus.responded) {
                        if (gameData.currentStimulus.isRed) {
                            gameData.wrong++;
                            gameData.reactions++;
                        }
                        target.style.display = 'none';
                        gameData.currentStimulus = null;
                        updateScoreboard();
                    }
                }, 3000);
            }

            function handleKeyPress(e) {
                if (e.code === 'Space') {
                    e.preventDefault();
                    if (!gameData.running || !gameData.currentStimulus || gameData.currentStimulus.responded) return;

                    gameData.currentStimulus.responded = true;
                    clearTimeout(gameData.stimulusTimeout);
                    
                    const reactionTime = Date.now() - gameData.currentStimulus.time;
                    
                    if (gameData.currentStimulus.isRed) {
                        gameData.correct++;
                        gameData.reactionTimes.push(reactionTime);
                    } else {
                        gameData.wrong++;
                    }
                    
                    gameData.reactions++;
                    
                    const last = gameData.stimulusSequence[gameData.stimulusSequence.length - 1];
                    if (last) last.missed = false;
                    
                    document.getElementById('game-target').style.display = 'none';
                    gameData.currentStimulus = null;
                    updateScoreboard();
                }
            }

            function updateScoreboard() {
                document.getElementById('game-reactions').textContent = gameData.reactions;
                document.getElementById('game-correct').textContent = gameData.correct;
                document.getElementById('game-wrong').textContent = gameData.wrong;
                
                if (gameData.reactionTimes.length > 0) {
                    const avg = gameData.reactionTimes.reduce((a, b) => a + b, 0) / gameData.reactionTimes.length;
                    document.getElementById('game-avg-ms').textContent = Math.round(avg);
                }
            }

            function updateTimer() {
                const pct = (gameData.timeLeft / 30) * 100;
                document.getElementById('game-timer-fill').style.width = pct + '%';
                document.getElementById('game-time').textContent = Math.ceil(gameData.timeLeft);
            }

            function endGame() {
                gameData.running = false;
                document.removeEventListener('keydown', handleKeyPress);
                document.getElementById('game-target').style.display = 'none';
                document.getElementById('game-message').textContent = '⏰ Тест завершён!';
                document.getElementById('game-message').style.display = 'block';
                
                const totalTrials = gameData.stimulusSequence.length;
                const missedCount = gameData.stimulusSequence.filter(s => s.missed && s.isRed).length;
                
                const decisions_made = gameData.reactions;
                const error_rate = gameData.reactions > 0 ? (gameData.wrong / gameData.reactions) : 0;
                const task_switches = Math.floor(gameData.stimulusSequence.length / 3);
                const avg_time = gameData.reactionTimes.length > 0
                    ? (gameData.reactionTimes.reduce((a, b) => a + b, 0) / gameData.reactionTimes.length) / 1000
                    : 5.0;
                
                gameData.measured = {
                    decisions_made: Math.max(decisions_made, 10),
                    task_switches: Math.max(task_switches, 3),
                    avg_decision_time_sec: Math.max(avg_time, 0.5),
                    error_rate: Math.min(error_rate, 0.5),
                    cognitive_load_score: Math.min(error_rate * 1.5 + (1 - gameData.correct / Math.max(gameData.reactions, 1)) * 0.5 + 0.2, 1.0)
                };

                const btn = document.getElementById('game-start-btn');
                btn.disabled = false;
                btn.textContent = '🔄 Пройти заново';

                document.getElementById('game-next-btn').style.display = 'block';
                document.getElementById('step1').className = 'step step-done';
                document.getElementById('step2').className = 'step step-active';

                document.getElementById('game-message').innerHTML = `
                    &#x2705; Тест пройден!<br>
                    <span style="font-size: 0.8em;">
                        Реакций: ${gameData.reactions} | 
                        Верных: ${gameData.correct} | 
                        Ошибок: ${gameData.wrong} | 
                    </span>
                `;
            }

            function goToManual() {
                document.getElementById('game-section').style.display = 'none';
                document.getElementById('manual-section').classList.add('active');
            }

            function submitCombined() {
                const measured = gameData.measured || {
                    decisions_made: 20,
                    task_switches: 5,
                    avg_decision_time_sec: 2.5,
                    error_rate: 0.05,
                    cognitive_load_score: 0.3
                };

                const data = {
                    Hours_Awake: parseFloat(document.getElementById('hours_awake').value) || 8,
                    Decisions_Made: Math.round(measured.decisions_made),
                    Task_Switches: Math.round(measured.task_switches),
                    Avg_Decision_Time_sec: parseFloat(measured.avg_decision_time_sec.toFixed(2)),
                    Sleep_Hours_Last_Night: parseFloat(document.getElementById('sleep_hours').value) || 7,
                    Caffeine_Intake_Cups: parseFloat(document.getElementById('caffeine_cups').value) || 0,
                    Stress_Level_1_10: parseFloat(document.getElementById('stress_level').value) || 5,
                    Error_Rate: parseFloat(measured.error_rate.toFixed(4)),
                    Cognitive_Load_Score: parseFloat(measured.cognitive_load_score.toFixed(4))
                };

                document.getElementById('step2').className = 'step step-done';

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
                    
                    if (!response.ok) throw new Error(resultData.detail || 'Ошибка сервера');
                    
                    document.getElementById('step3').className = 'step step-done';
                    
                    const prediction = resultData.prediction;
                    const rec = RECOMMENDATIONS[prediction];
                    
                    result.className = `result ${rec.color}`;
                    result.style.display = 'block';
                    
                    let probHtml = '';
                    const probs = resultData.probabilities || {};
                    ['High', 'Moderate', 'Low'].forEach(level => {
                        const val = (probs[level] || 0) * 100;
                        const cc = level === 'High' ? 'prob-high' : level === 'Moderate' ? 'prob-moderate' : 'prob-low';
                        probHtml += `
                            <div style="margin: 8px 0;">
                                <span>${level === 'High' ? 'Высокая' : level === 'Moderate' ? 'Умеренная' : 'Низкая'}: ${val.toFixed(1)}%</span>
                                <div class="prob-bar"><div class="prob-fill ${cc}" style="width: ${val}%;"></div></div>
                            </div>
                        `;
                    });

                    result.innerHTML = `
                        <h3>${rec.icon} ${rec.title}</h3>
                        <p><span class="fatigue-badge fatigue-${prediction.toLowerCase()}">${prediction === 'High' ? 'ВЫСОКАЯ' : prediction === 'Moderate' ? 'УМЕРЕННАЯ' : 'НИЗКАЯ'}</span></p>
                        <p class="confidence">Уверенность: ${((resultData.confidence || 0) * 100).toFixed(1)}%</p>

                        <h3 style="margin-top: 20px;">&#x1F3AE; Результаты теста:</h3>
                        <div class="grid-2" style="margin: 15px 0;">
                            <div><strong>Реакций:</strong> ${gameData.reactions}</div>
                            <div><strong>Верных:</strong> ${gameData.correct}</div>
                            <div><strong>Ошибок:</strong> ${gameData.wrong}</div>
                            <div><strong>Среднее время:</strong> ${gameData.reactionTimes.length > 0 ? Math.round(gameData.reactionTimes.reduce((a,b) => a+b, 0) / gameData.reactionTimes.length) + ' мс' : '---'}</div>
                        </div>

                        <h3>Распределение вероятностей усталости:</h3>
                        ${probHtml}
                        
                        <div class="rest-time">
                            <div class="label">&#x23F0; Рекомендуемое время отдыха:</div>
                            <div class="time">${rec.restTime}</div>
                        </div>
                        
                        <div class="recommendation">
                            <h4>${rec.icon} ${rec.description}</h4>
                            <h4 style="margin-top: 15px;">&#x1F4CB; Рекомендации:</h4>
                            ${rec.actions.map(a => `<p style="margin: 8px 0;">${a}</p>`).join('')}
                        </div>
                        
                        <div class="info-box" style="margin-top: 20px;">
                            <p><strong>&#x2139;&#xFE0F;</strong> Окончательное решение о допуске принимается по медицинским нормам и SOP авиакомпании.</p>
                        </div>
                    `;
                } catch (e) {
                    result.className = 'result error';
                    result.innerHTML = `<h3>&#x274C; Ошибка</h3><p>${e.message}</p>`;
                    result.style.display = 'block';
                } finally {
                    spinner.style.display = 'none';
                }
            }

            async function checkConnection() {
                try {
                    const response = await fetch(SERVER_URL + '/health');
                    if (response.ok) {
                        document.getElementById('status-indicator').className = 'status-indicator status-connected';
                        document.getElementById('status-text').textContent = 'Подключено к серверу';
                    } else throw new Error('err');
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
                    reader.onload = function(e) { preview.src = e.target.result; container.style.display = 'block'; };
                    reader.readAsDataURL(input.files[0]);
                }
            }

            async function uploadImage() {
                const input = document.getElementById('image-input');
                const spinner = document.getElementById('image-spinner');
                const result = document.getElementById('image-result');
                if (!input.files[0]) { alert('Выберите изображение'); return; }
                
                spinner.style.display = 'block'; result.style.display = 'none';
                const formData = new FormData();
                formData.append('file', input.files[0]);
                
                try {
                    const response = await fetch(SERVER_URL + '/predict/image', { method: 'POST', body: formData });
                    const data = await response.json();
                    const isFatigue = data.prediction === 'Fatigue';
                    const rec = RECOMMENDATIONS[isFatigue ? 'High' : 'Low'];
                    
                    result.className = `result ${rec.color}`; result.style.display = 'block';
                    result.innerHTML = `
                        <h3>${rec.icon} ${data.prediction === 'Fatigue' ? 'Признаки усталости' : 'Усталость не обнаружена'}</h3>
                        <p><span class="fatigue-badge ${isFatigue ? 'fatigue-high' : 'fatigue-low'}">${data.prediction === 'Fatigue' ? 'Усталость' : 'Бодрость'}</span></p>
                        <p class="confidence">Уверенность: ${(data.confidence * 100).toFixed(1)}%</p>
                        <div class="recommendation">
                            <h4>${rec.icon} ${rec.title}</h4>
                            <p>${rec.description}</p>
                            <div class="rest-time"><div class="label">Отдых:</div><div class="time">${rec.restTime}</div></div>
                            ${rec.actions.map(a => `<p style="margin: 5px 0;">${a}</p>`).join('')}
                        </div>
                    `;
                } catch (e) {
                    result.className = 'result error'; result.style.display = 'block';
                    result.innerHTML = `<h3>&#x274C; Ошибка</h3><p>${e.message}</p>`;
                } finally { spinner.style.display = 'none'; }
            }

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
