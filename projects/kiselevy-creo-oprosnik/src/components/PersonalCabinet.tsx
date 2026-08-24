import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  User, Clock, Sparkles, Send, Bot, Check, ShieldCheck, 
  ArrowRight, RefreshCw, Calendar, Zap, CreditCard, MessageSquare, 
  Heart, AlertCircle, CheckCircle2, ChevronRight, Lock, Award
} from "lucide-react";

interface PersonalCabinetProps {
  telegramUser?: {
    id: number;
    first_name: string;
    last_name?: string;
    username?: string;
  } | null;
  onOpenQuestionnaire?: () => void;
}

interface ChatMessage {
  id: string;
  sender: "user" | "bot";
  text: string;
  timestamp: string;
}

export default function PersonalCabinet({ telegramUser, onOpenQuestionnaire }: PersonalCabinetProps) {
  // User name calculation
  const userName = telegramUser?.first_name 
    ? `${telegramUser.first_name} ${telegramUser.last_name || ""}`.trim()
    : "Гость";

  const userContact = telegramUser?.username 
    ? `@${telegramUser.username}` 
    : telegramUser?.id 
    ? `ID: ${telegramUser.id}` 
    : "Веб-пользователь";

  // 7-day Trial Timer Logic
  const TRIAL_DAYS = 7;
  const TRIAL_MS = TRIAL_DAYS * 24 * 60 * 60 * 1000;

  const [trialStartDate, setTrialStartDate] = useState<number>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("oprus_trial_start");
      if (saved) return parseInt(saved, 10);
      const now = Date.now();
      localStorage.setItem("oprus_trial_start", now.toString());
      return now;
    }
    return Date.now();
  });

  const [timeLeft, setTimeLeft] = useState<{
    days: number;
    hours: number;
    minutes: number;
    seconds: number;
    totalMs: number;
    isExpired: boolean;
  }>({ days: 7, hours: 0, minutes: 0, seconds: 0, totalMs: TRIAL_MS, isExpired: false });

  useEffect(() => {
    const updateCounter = () => {
      const now = Date.now();
      const expiresAt = trialStartDate + TRIAL_MS;
      const diff = expiresAt - now;

      if (diff <= 0) {
        setTimeLeft({
          days: 0,
          hours: 0,
          minutes: 0,
          seconds: 0,
          totalMs: 0,
          isExpired: true
        });
      } else {
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        setTimeLeft({
          days,
          hours,
          minutes,
          seconds,
          totalMs: diff,
          isExpired: false
        });
      }
    };

    updateCounter();
    const interval = setInterval(updateCounter, 1000);
    return () => clearInterval(interval);
  }, [trialStartDate]);

  // Saved Diagnostics History
  const [lastDiagnostic, setLastDiagnostic] = useState<any>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("oprus_last_diagnostic");
      if (saved) {
        try { return JSON.parse(saved); } catch (e) { return null; }
      }
    }
    return null;
  });

  // Interactive AI Coach Chat
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome-1",
      sender: "bot",
      text: `Здравствуйте, ${userName}! Я Опрус — ваш нейро-коучинг и практический психолог с 50-летним стажем.\n\n🌅 **Время утреннего чек-ина:** С каким настроением вы сегодня проснулись? Что чувствуете в теле и какие 1-2 главные задачи ставите перед собой на день?`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputMsg, setInputMsg] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showSubModal, setShowSubModal] = useState(false);
  const [subSuccess, setSubSuccess] = useState(false);

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputMsg.trim() || isTyping) return;

    const userText = inputMsg.trim();
    setInputMsg("");

    const userMessage: ChatMessage = {
      id: "msg-" + Date.now(),
      sender: "user",
      text: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const res = await fetch("/api/coach/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userMessage: userText,
          userName: userName,
          telegramUserId: telegramUser?.id,
          chatHistory: messages.slice(-6)
        })
      });

      const data = await res.json();
      const botText = data.reply || "Спасибо за мысли! Помни: главное — двигаться в согласии со своими истинными ценностями. Какой один легкий шаг сделаешь прямо сейчас?";

      const botMessage: ChatMessage = {
        id: "bot-" + Date.now(),
        sender: "bot",
        text: botText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error("Error asking AI coach:", err);
      const fallbackMsg: ChatMessage = {
        id: "bot-" + Date.now(),
        sender: "bot",
        text: `Я внимательно изучил ваши слова. За 50 лет практики я вывел важное правило: не пытайтесь решить всё сразу. Возьмите одну главную задачу на сегодня, снимите перфекционизм и сделайте её с легким сердцем.\n\nКак вы отнесетесь к тому, чтобы начать прямо сейчас с самого простого действия?`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, fallbackMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const progressPercent = Math.max(0, Math.min(100, (timeLeft.totalMs / TRIAL_MS) * 100));

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8">
      {/* Profile Header */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-shanti-earth shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-shanti-green/5 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 relative z-10">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-16 h-16 rounded-full bg-shanti-sand border-2 border-shanti-green/40 flex items-center justify-center font-serif text-2xl text-shanti-dark font-bold shadow-inner">
                {userName.charAt(0) || "U"}
              </div>
              <span className="absolute bottom-0 right-0 w-4 h-4 bg-shanti-green rounded-full border-2 border-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-serif text-shanti-dark font-bold">
                  {userName}
                </h1>
                <span className="bg-shanti-green/10 text-shanti-green text-[10px] font-bold px-2.5 py-0.5 rounded-full font-sans uppercase tracking-wider">
                  Личный кабинет
                </span>
              </div>
              <p className="text-xs text-[#8B8C7A] font-mono mt-0.5">
                {userContact} • Доступ открыт 7 дней
              </p>
            </div>
          </div>

          <button
            onClick={() => setShowSubModal(true)}
            className="w-full sm:w-auto px-6 py-3 bg-shanti-green text-white rounded-full font-sans text-xs uppercase tracking-wider font-bold hover:bg-shanti-olive transition-all flex items-center justify-center gap-2 cursor-pointer shadow-sm active:scale-95"
          >
            <Sparkles className="w-4 h-4" />
            <span>Продлить подписку (599 ₽/мес)</span>
          </button>
        </div>

        {/* 3-Systems Unified Access Indicator */}
        <div className="mt-6 pt-5 border-t border-shanti-earth/60 grid grid-cols-1 md:grid-cols-3 gap-3 font-sans text-xs">
          <div className="bg-shanti-sand/60 p-3 rounded-2xl border border-shanti-earth flex items-center gap-3">
            <span className="w-8 h-8 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center font-bold shrink-0">
              📢
            </span>
            <div>
              <span className="font-bold text-shanti-dark block leading-tight">1. Телеграм Канал</span>
              <span className="text-[10px] text-shanti-olive font-medium">Анонсы и авто-воронка @kiselevy_creo</span>
            </div>
          </div>

          <div className="bg-shanti-sand/60 p-3 rounded-2xl border border-shanti-earth flex items-center gap-3">
            <span className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold shrink-0">
              🤖
            </span>
            <div>
              <span className="font-bold text-shanti-dark block leading-tight">2. MAX Бот</span>
              <span className="text-[10px] text-shanti-olive font-medium">Мессенджер MAX & ИИ-коуч</span>
            </div>
          </div>

          <div className="bg-shanti-sand/60 p-3 rounded-2xl border border-shanti-earth flex items-center gap-3">
            <span className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold shrink-0">
              💻
            </span>
            <div>
              <span className="font-bold text-shanti-dark block leading-tight">3. Веб-приложение</span>
              <span className="text-[10px] text-shanti-olive font-medium">TMA + Полный Web-кабинет</span>
            </div>
          </div>
        </div>
      </div>

      {/* 7-Day Free Trial Timer Card */}
      <div className="bg-gradient-to-br from-[#FAF9F5] via-white to-shanti-sand p-6 sm:p-8 rounded-3xl border-2 border-shanti-green/30 shadow-md relative overflow-hidden space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-shanti-earth/60 pb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-shanti-green/10 border border-shanti-green/20 flex items-center justify-center text-shanti-green">
              <Clock className="w-5 h-5 animate-spin-slow" />
            </div>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-widest text-shanti-green block font-sans">
                Статус бесплатных 7 дней
              </span>
              <h2 className="text-lg font-serif font-bold text-shanti-dark">
                {timeLeft.isExpired ? "Бесплатный период завершён" : "Бесплатный период активен"}
              </h2>
            </div>
          </div>

          <div className="bg-white px-4 py-1.5 rounded-full border border-shanti-earth shadow-2xs text-xs font-sans font-semibold text-shanti-dark flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${timeLeft.isExpired ? "bg-rose-500" : "bg-emerald-500 animate-ping"}`} />
            <span>{timeLeft.isExpired ? "Требуется подписка" : "Активен полный доступ"}</span>
          </div>
        </div>

        {/* Live Countdown Grid */}
        <div className="grid grid-cols-4 gap-3 sm:gap-4 text-center">
          <div className="bg-white p-3 sm:p-4 rounded-2xl border border-shanti-earth shadow-2xs">
            <span className="text-2xl sm:text-4xl font-serif font-bold text-shanti-dark block leading-none">
              {String(timeLeft.days).padStart(2, '0')}
            </span>
            <span className="text-[10px] sm:text-xs font-sans text-[#8B8C7A] uppercase tracking-wider mt-1 block">
              Дней
            </span>
          </div>

          <div className="bg-white p-3 sm:p-4 rounded-2xl border border-shanti-earth shadow-2xs">
            <span className="text-2xl sm:text-4xl font-serif font-bold text-shanti-dark block leading-none">
              {String(timeLeft.hours).padStart(2, '0')}
            </span>
            <span className="text-[10px] sm:text-xs font-sans text-[#8B8C7A] uppercase tracking-wider mt-1 block">
              Часов
            </span>
          </div>

          <div className="bg-white p-3 sm:p-4 rounded-2xl border border-shanti-earth shadow-2xs">
            <span className="text-2xl sm:text-4xl font-serif font-bold text-shanti-dark block leading-none">
              {String(timeLeft.minutes).padStart(2, '0')}
            </span>
            <span className="text-[10px] sm:text-xs font-sans text-[#8B8C7A] uppercase tracking-wider mt-1 block">
              Минут
            </span>
          </div>

          <div className="bg-white p-3 sm:p-4 rounded-2xl border border-shanti-earth shadow-2xs">
            <span className="text-2xl sm:text-4xl font-serif font-bold text-shanti-green block leading-none">
              {String(timeLeft.seconds).padStart(2, '0')}
            </span>
            <span className="text-[10px] sm:text-xs font-sans text-shanti-green uppercase tracking-wider mt-1 block font-bold">
              Секунд
            </span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs font-sans text-[#8B8C7A] font-medium">
            <span>Прогресс тестового периода (7 дней)</span>
            <span>Осталось {Math.round(progressPercent)}%</span>
          </div>
          <div className="w-full h-2.5 bg-shanti-earth/50 rounded-full overflow-hidden p-0.5">
            <div 
              className="h-full bg-gradient-to-r from-shanti-green to-emerald-500 rounded-full transition-all duration-1000"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Interactive AI Coach Chat Section */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-shanti-earth shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b border-shanti-earth/60 pb-4">
          <div className="flex items-center gap-3">
            <div className="relative shrink-0 w-12 h-12 rounded-full border-2 border-shanti-green p-0.5 bg-shanti-sand overflow-hidden flex items-center justify-center">
              <img src="/rimma_portrait.jpg" alt="Опрус" className="w-full h-full object-cover rounded-full" />
              <span className="absolute bottom-0 right-0 w-3 h-3 bg-shanti-green rounded-full border-2 border-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase tracking-widest bg-shanti-green text-white px-2 py-0.5 rounded-full font-bold font-sans">
                  50 ЛЕТ СТАЖА
                </span>
                <span className="text-xs text-shanti-green font-bold">Опрус ИИ-Коуч</span>
              </div>
              <h3 className="text-lg font-serif font-bold text-shanti-dark">
                Ежедневный диалог и утренняя настройка
              </h3>
            </div>
          </div>

          <span className="hidden sm:inline-flex items-center gap-1.5 text-xs text-shanti-olive bg-shanti-sand px-3 py-1.5 rounded-full border border-shanti-earth font-medium">
            <Sparkles className="w-3.5 h-3.5 text-shanti-green" />
            <span>Без тупиков</span>
          </span>
        </div>

        {/* Chat Messages List */}
        <div className="bg-[#FAF9F5] p-4 sm:p-6 rounded-2xl border border-shanti-earth/70 min-h-[280px] max-h-[420px] overflow-y-auto space-y-4">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[88%] sm:max-w-[80%] p-4 rounded-2xl text-xs sm:text-sm font-sans leading-relaxed shadow-2xs ${
                  m.sender === "user"
                    ? "bg-shanti-green text-white rounded-br-none"
                    : "bg-white text-shanti-dark border border-shanti-earth rounded-bl-none"
                }`}
              >
                <div className="whitespace-pre-line">{m.text}</div>
                <div
                  className={`text-[9px] mt-2 font-mono text-right ${
                    m.sender === "user" ? "text-white/80" : "text-gray-400"
                  }`}
                >
                  {m.timestamp}
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white p-4 rounded-2xl border border-shanti-earth text-xs text-shanti-olive flex items-center gap-2">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-shanti-green" />
                <span>Опрус анализирует состояние и готовит рекомендацию...</span>
              </div>
            </div>
          )}
        </div>

        {/* Send message form */}
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            value={inputMsg}
            onChange={(e) => setInputMsg(e.target.value)}
            placeholder="Напишите о своем настроении, планах на день или задайте вопрос..."
            className="flex-grow px-4 py-3.5 rounded-2xl border border-shanti-earth bg-white text-xs sm:text-sm font-sans text-shanti-dark focus:outline-none focus:border-shanti-green focus:ring-2 focus:ring-shanti-green/20"
          />
          <button
            type="submit"
            disabled={!inputMsg.trim() || isTyping}
            className="px-6 py-3.5 bg-shanti-green text-white rounded-2xl font-bold hover:bg-shanti-olive transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline text-xs uppercase tracking-wider">Отправить</span>
          </button>
        </form>
      </div>

      {/* Diagnostics History Summary */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-shanti-earth shadow-sm space-y-4">
        <div className="flex justify-between items-center border-b border-shanti-earth/60 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-shanti-green/10 flex items-center justify-center text-shanti-green">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-serif font-bold text-shanti-dark">
                Результаты цифровой диагностики
              </h3>
              <p className="text-xs text-[#8B8C7A]">Данные о вашем психологическом и бизнес-профиле</p>
            </div>
          </div>

          {onOpenQuestionnaire && (
            <button
              onClick={onOpenQuestionnaire}
              className="px-4 py-2 border border-shanti-earth hover:border-shanti-green text-shanti-dark rounded-full text-xs font-sans font-medium transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5 text-shanti-green" />
              <span>Пройти заново</span>
            </button>
          )}
        </div>

        {lastDiagnostic ? (
          <div className="bg-[#FAF9F5] p-5 rounded-2xl border border-shanti-earth space-y-3 text-xs text-shanti-dark">
            <div className="flex justify-between items-center">
              <span className="font-bold text-shanti-green uppercase tracking-wider text-[10px]">
                Сегмент: {lastDiagnostic.segment || "Операционный порядок"}
              </span>
              <span className="text-[#8B8C7A]">Индекс спокойствия: {lastDiagnostic.indexCalm || 12}/20</span>
            </div>
            <p className="italic text-gray-700 leading-relaxed border-l-2 border-shanti-green pl-3">
              "{lastDiagnostic.psychologistAdvice ? lastDiagnostic.psychologistAdvice.slice(0, 180) + "..." : "Персональные рекомендации сформированы."}"
            </p>
          </div>
        ) : (
          <div className="bg-[#FAF9F5] p-5 rounded-2xl border border-shanti-earth text-center space-y-3">
            <p className="text-xs text-gray-600">
              Вы еще не проходили полную диагностику или результат сохранился в Telegram.
            </p>
            {onOpenQuestionnaire && (
              <button
                onClick={onOpenQuestionnaire}
                className="px-5 py-2.5 bg-shanti-green text-white rounded-full text-xs font-bold uppercase tracking-wider hover:bg-shanti-olive transition-all cursor-pointer"
              >
                Запустить опросник Опрус (2 мин)
              </button>
            )}
          </div>
        )}
      </div>

      {/* Subscription Plans Section */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-shanti-earth shadow-sm space-y-6">
        <div className="text-center space-y-2 max-w-xl mx-auto">
          <span className="text-[10px] font-bold uppercase tracking-widest text-shanti-green bg-shanti-green/10 px-3 py-1 rounded-full font-sans">
            ПОДПИСКА И ТАРИФЫ
          </span>
          <h2 className="text-xl sm:text-2xl font-serif text-shanti-dark font-bold">
            Сохраните ИИ-коуча после 7 дней
          </h2>
          <p className="text-xs text-gray-500 leading-relaxed">
            Продолжайте ежедневную работу с мышлением, снятием затыков и автоматизацией задач без ограничений.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Plan 1: Monthly */}
          <div className="bg-[#FAF9F5] p-6 rounded-3xl border-2 border-shanti-earth hover:border-shanti-green transition-all space-y-5 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-serif font-bold text-lg text-shanti-dark">Ежемесячный</h3>
                  <p className="text-xs text-[#8B8C7A]">Гибкий доступ без обязательств</p>
                </div>
                <span className="bg-shanti-sand text-shanti-olive px-3 py-1 rounded-full text-[10px] font-bold font-mono">
                  ПОПУЛЯРНЫЙ
                </span>
              </div>

              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-serif font-bold text-shanti-dark">599 ₽</span>
                <span className="text-xs font-sans text-gray-500">/ месяц</span>
              </div>

              <ul className="space-y-2.5 text-xs text-shanti-dark font-sans">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-shanti-green shrink-0" />
                  <span>Ежедневные утренние чек-ины состояния</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-shanti-green shrink-0" />
                  <span>ИИ-психолог и нейро-коуч 24/7 без тупиков</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-shanti-green shrink-0" />
                  <span>Снятие блоков и разбор задач</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-shanti-green shrink-0" />
                  <span>Отмена подписки в любой момент</span>
                </li>
              </ul>
            </div>

            <button
              onClick={() => setShowSubModal(true)}
              className="w-full py-3.5 bg-shanti-green text-white rounded-2xl font-bold text-xs uppercase tracking-wider hover:bg-shanti-olive transition-all cursor-pointer shadow-xs"
            >
              Оформить за 599 ₽
            </button>
          </div>

          {/* Plan 2: Yearly */}
          <div className="bg-gradient-to-br from-shanti-sand via-white to-[#FAF9F5] p-6 rounded-3xl border-2 border-shanti-green/40 shadow-sm space-y-5 flex flex-col justify-between relative overflow-hidden">
            <div className="absolute top-3 right-3 bg-shanti-green text-white px-3 py-1 rounded-full text-[9px] font-bold font-sans uppercase tracking-wider">
              СКИДКА 30%
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="font-serif font-bold text-lg text-shanti-dark">Годовой VIP</h3>
                <p className="text-xs text-[#8B8C7A]">Максимальная выгода для результатов</p>
              </div>

              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-serif font-bold text-shanti-dark">4 990 ₽</span>
                <span className="text-xs font-sans text-gray-500">/ год (~415 ₽/мес)</span>
              </div>

              <ul className="space-y-2.5 text-xs text-shanti-dark font-sans">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-shanti-green shrink-0" />
                  <span>Всё из ежемесячного тарифа</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-shanti-green shrink-0" />
                  <span>Приоритетные рекомендации от команды</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-shanti-green shrink-0" />
                  <span>Персональный разбор кейса с экспертом</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-shanti-green shrink-0" />
                  <span>Экономия 2 200 ₽ в год</span>
                </li>
              </ul>
            </div>

            <button
              onClick={() => setShowSubModal(true)}
              className="w-full py-3.5 bg-shanti-dark text-white rounded-2xl font-bold text-xs uppercase tracking-wider hover:bg-black transition-all cursor-pointer shadow-md"
            >
              Оформить за 4 990 ₽
            </button>
          </div>
        </div>
      </div>

      {/* Subscription Checkout Modal */}
      <AnimatePresence>
        {showSubModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white p-6 sm:p-8 rounded-3xl max-w-md w-full border border-shanti-earth shadow-2xl space-y-6 relative"
            >
              <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-full bg-shanti-green/10 text-shanti-green flex items-center justify-center mx-auto">
                  <CreditCard className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-serif font-bold text-shanti-dark">
                  Оформление подписки KISELEVY_CREO
                </h3>
                <p className="text-xs text-gray-500">
                  Доступ к нейро-коучу Опрус 24/7 и ежедневным трекерам
                </p>
              </div>

              {subSuccess ? (
                <div className="bg-emerald-50 p-6 rounded-2xl border border-emerald-200 text-center space-y-3">
                  <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto" />
                  <h4 className="font-serif font-bold text-emerald-900 text-base">Заявка успешно создана!</h4>
                  <p className="text-xs text-emerald-700">
                    Перейдите в Telegram-бот или напишите нашему менеджеру для подтверждения оплаты и мгновенной активации.
                  </p>
                  <a
                    href="https://t.me/neuro_kouch_creo_bot?start=subscribe_success"
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-shanti-green text-white rounded-full font-bold text-xs uppercase tracking-wider hover:bg-shanti-olive transition-all"
                  >
                    Открыть Telegram-бота
                  </a>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-[#FAF9F5] p-4 rounded-2xl border border-shanti-earth text-xs space-y-2">
                    <div className="flex justify-between font-bold text-shanti-dark">
                      <span>Нейро-коуч Опрус (1 месяц)</span>
                      <span>599 ₽</span>
                    </div>
                    <p className="text-[10px] text-gray-500">
                      После 7 дней бесплатного тестового периода. Отвязать подписку можно в любой момент.
                    </p>
                  </div>

                  <div className="space-y-2">
                    <button
                      onClick={() => setSubSuccess(true)}
                      className="w-full py-4 bg-shanti-green text-white rounded-2xl font-bold text-xs uppercase tracking-widest hover:bg-shanti-olive transition-all cursor-pointer shadow-sm flex items-center justify-center gap-2"
                    >
                      <ShieldCheck className="w-4 h-4" />
                      <span>Подтвердить и оплатить (599 ₽)</span>
                    </button>

                    <a
                      href="https://t.me/kiselevy_creo"
                      target="_blank"
                      rel="noreferrer"
                      className="w-full py-3 bg-white border border-shanti-earth text-shanti-dark rounded-2xl font-bold text-xs uppercase tracking-wider hover:bg-shanti-sand transition-all cursor-pointer flex items-center justify-center gap-2 text-center"
                    >
                      <span>Написать основателю (@kiselevy_creo)</span>
                    </a>
                  </div>

                  <button
                    onClick={() => setShowSubModal(false)}
                    className="w-full text-center text-xs text-gray-400 hover:text-gray-600 transition-colors pt-2"
                  >
                    Закрыть окно
                  </button>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
