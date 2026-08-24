import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  Users, BarChart3, Brain, Clipboard, Copy, Check, RotateCcw, Trash2, 
  Search, Filter, Lock, Unlock, AlertTriangle, Sparkles, AlertCircle, Heart, Flame, Calendar, Send,
  Play, Plus, X, MessageSquare, Settings, Radio,
  Leaf, Wind, Moon, Sun, XCircle, Mail, Gift, Crown, Compass, Bot, Globe, ChevronRight, Smile,
  RefreshCw, CheckCircle2, Briefcase, Phone, HeartHandshake, Clock, Eye, EyeOff, Star
} from "lucide-react";
import { PollResponse, AIAnalysisResult, feelings, steadyOptions, formatOptions } from "../types";

// Emoji to Icon Map
const EMOJI_MAP: Record<string, React.ComponentType<any>> = {
  "🌿": Leaf,
  "🌬": Wind,
  "🧘‍♀️": Sparkles,
  "🧘": Sparkles,
  "💆": Sparkles,
  "🚶": Compass,
  "🛌": Moon,
  "🌙": Moon,
  "😴": Moon,
  "💤": Moon,
  "🕯": Flame,
  "🌞": Sun,
  "🙅": XCircle,
  "💌": Mail,
  "🙏": Heart,
  "★": Gift,
  "👑": Crown,
  "►": Sparkles,
  "🔥": Flame,
  "🤍": Heart,
  "❤️": Heart,
  "👉": ChevronRight,
  "✨": Sparkles,
  "😅": Smile,
  "♦": Bot,
  "◈": Globe,
  "🙌": HeartHandshake,
  "💪": Sparkles,
  "⚡": Flame,
  "❄️": Wind,
  "⏱️": Clock,
  "⏱": Clock,
};

// Emoji styling colors/classes map
const EMOJI_STYLE_MAP: Record<string, string> = {
  "🌿": "text-shanti-green",
  "🌬": "text-shanti-green animate-pulse",
  "🧘‍♀️": "text-shanti-green",
  "🧘": "text-shanti-green",
  "💆": "text-shanti-green",
  "🚶": "text-shanti-green",
  "🛌": "text-shanti-green",
  "🌙": "text-shanti-green",
  "😴": "text-shanti-green",
  "💤": "text-shanti-green",
  "🕯": "text-shanti-green animate-pulse",
  "🌞": "text-shanti-green",
  "🙅": "text-shanti-green",
  "💌": "text-shanti-green",
  "🙏": "text-shanti-green",
  "★": "text-shanti-green",
  "👑": "text-shanti-green",
  "►": "text-shanti-green",
  "🔥": "text-shanti-green animate-pulse",
  "🤍": "text-shanti-green",
  "❤️": "text-shanti-green",
  "👉": "text-shanti-green",
  "✨": "text-shanti-green animate-pulse",
  "😅": "text-shanti-green",
  "♦": "text-shanti-green",
  "◈": "text-shanti-green",
  "🙌": "text-shanti-green",
  "💪": "text-shanti-green",
  "⚡": "text-shanti-green",
  "❄️": "text-shanti-green",
  "⏱️": "text-shanti-green",
  "⏱": "text-shanti-green",
};

export function SmartText({ text }: { text: string }) {
  if (!text) return null;
  
  const regex = /(🧘‍♀️|🌿|🌬|🧘|💆|🚶|🛌|🌙|😴|💤|🕯|🌞|🙅|💌|🙏|★|👑|►|🔥|🤍|❤️|👉|✨|😅|♦|◈|🙌|💪|⚡|❄️|⏱️|⏱)/g;
  const parts = text.split(regex);
  
  return (
    <>
      {parts.map((part, i) => {
        const IconComponent = EMOJI_MAP[part];
        if (IconComponent) {
          const styleClass = EMOJI_STYLE_MAP[part] || "text-shanti-green";
          return (
            <span key={i} className="inline-flex items-center mx-0.5" style={{ verticalAlign: "middle" }}>
              <IconComponent className={`w-3.5 h-3.5 inline shrink-0 ${styleClass}`} />
            </span>
          );
        }
        return part;
      })}
    </>
  );
}

export default function AdminDashboard() {
  const [authorized, setAuthorized] = useState(false);
  const [rememberMe, setRememberMe] = useState(() => {
    return localStorage.getItem("creo_remember_me") === "true";
  });
  const [login, setLogin] = useState(() => {
    return localStorage.getItem("creo_remember_me") === "true"
      ? localStorage.getItem("creo_admin_login") || ""
      : "";
  });
  const [accessCode, setAccessCode] = useState(() => {
    return localStorage.getItem("creo_remember_me") === "true"
      ? localStorage.getItem("creo_admin_password") || ""
      : "";
  });
  const [authError, setAuthError] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [revealCredentials, setRevealCredentials] = useState(false);

  const [activeTab, setActiveTab] = useState<"clients" | "analytics" | "ai" | "materials" | "questionnaires" | "profile" | "platforms">("clients");
  const [responses, setResponses] = useState<PollResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterFeeling, setFilterFeeling] = useState("");
  const [filterHotLeads, setFilterHotLeads] = useState(false);

  // 3-Systems Platforms state
  const [platformSystems, setPlatformSystems] = useState<any[]>([]);
  const [channelPostText, setChannelPostText] = useState("✨ <b>Утренний пост-настройка KISELEVY_CREO</b>\n\n«Каждый шаг вперед начинается с бережной остановки. Позвольте себе 3 минуты тишины и зафиксируйте свое состояние.»\n\n👇 Откройте персональный кабинет:");
  const [channelPostWebAppBtn, setChannelPostWebAppBtn] = useState(true);
  const [channelPostSending, setChannelPostSending] = useState(false);
  const [channelPostStatus, setChannelPostStatus] = useState<string | null>(null);

  const [maxTestText, setMaxTestText] = useState("🤖 Привет из мессенджера MAX! Это тестовая проверка связки с ИИ-коучем Опрус.");
  const [maxSending, setMaxSending] = useState(false);
  const [maxStatus, setMaxStatus] = useState<string | null>(null);

  // Profile settings state
  const [profileName, setProfileName] = useState("Опрус");
  const [profileRole, setProfileRole] = useState("ИИ-помощник KISELEVY_CREO");
  const [profileSubtitle, setProfileSubtitle] = useState("Цифровой диагност и консультант по автоматизации и нейро-решениям");
  const [profileWelcome, setProfileWelcome] = useState("Привет, я Опрус. Прежде чем поговорим о деле — как ты вообще? Этот разговор поможет мне понять, что тебе сейчас действительно нужно — и в бизнесе, и в себе.");
  const [profileAvatar, setProfileAvatar] = useState("");
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileSaveSuccess, setProfileSaveSuccess] = useState(false);

  // Questionnaire states
  const [questionnaires, setQuestionnaires] = useState<any[]>([]);
  const [broadcasts, setBroadcasts] = useState<any[]>([]);
  const [topicInput, setTopicInput] = useState("");
  const [isGeneratingQ, setIsGeneratingQ] = useState(false);
  const [editingQ, setEditingQ] = useState<any>(null); // For custom editing/creation
  const [qTitle, setQTitle] = useState("");
  const [qDesc, setQDesc] = useState("");
  const [qQuestions, setQQuestions] = useState<any[]>([
    { id: "q1", type: "single", title: "", subtitle: "", options: ["", "", "", ""], allowCustom: false },
    { id: "q2", type: "multiple", title: "", subtitle: "", options: ["", "", "", ""], allowCustom: false },
    { id: "q3", type: "text", title: "", subtitle: "", placeholder: "" }
  ]);

  // Notes and funnel tracking state with LocalStorage persistence
  const [clientNotes, setClientNotes] = useState<Record<string, string>>(() => {
    try {
      return JSON.parse(localStorage.getItem("shanti_client_notes") || "{}");
    } catch {
      return {};
    }
  });

  const [funnelSteps, setFunnelSteps] = useState<Record<string, Record<string, string>>>(() => {
    try {
      return JSON.parse(localStorage.getItem("shanti_funnel_steps") || "{}");
    } catch {
      return {};
    }
  });

  const updateNote = (id: string, note: string) => {
    const updated = { ...clientNotes, [id]: note };
    setClientNotes(updated);
    localStorage.setItem("shanti_client_notes", JSON.stringify(updated));
  };

  const advanceFunnelStep = (clientId: string, stepKey: string) => {
    const clientSteps = funnelSteps[clientId] || { day1: "pending", day3: "pending", day7: "pending" };
    let currentStatus = clientSteps[stepKey] || "pending";
    let nextStatus = "pending";

    if (currentStatus === "pending") {
      nextStatus = "sent";
    } else if (currentStatus === "sent") {
      nextStatus = "cancelled";
    } else {
      nextStatus = "pending";
    }

    const updated = {
      ...funnelSteps,
      [clientId]: {
        ...clientSteps,
        [stepKey]: nextStatus
      }
    };
    setFunnelSteps(updated);
    localStorage.setItem("shanti_funnel_steps", JSON.stringify(updated));
  };

  // AI Analysis state
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState<AIAnalysisResult | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

  // Client-specific generated recommendation states
  const [generatingClientRecommendationId, setGeneratingClientRecommendationId] = useState<string | null>(null);
  const [clientRecommendations, setClientRecommendations] = useState<Record<string, {
    product: string;
    marker: string;
    tone: string;
    note: string;
  }>>({});

  // Copy success states
  const [copiedText, setCopiedText] = useState<string | null>(null);

  // Load responses from server
  const fetchResponses = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/responses");
      const data = await res.json();
      setResponses(data);
    } catch (err) {
      console.error("Error loading responses:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchQuestionnaires = async () => {
    try {
      const res = await fetch("/api/questionnaires");
      const data = await res.json();
      setQuestionnaires(data);
    } catch (err) {
      console.error("Error loading questionnaires:", err);
    }
  };

  const fetchBroadcasts = async () => {
    try {
      const res = await fetch("/api/broadcasts");
      const data = await res.json();
      setBroadcasts(data);
    } catch (err) {
      console.error("Error loading broadcasts:", err);
    }
  };

  const fetchProfile = async () => {
    try {
      const res = await fetch("/api/profile");
      const data = await res.json();
      if (data) {
        setProfileName(data.name || "Алексей К.");
        setProfileRole(data.role || "Основатель KISELEVY_CREO");
        setProfileSubtitle(data.subtitle || "");
        setProfileWelcome(data.welcomeMessage || "");
        setProfileAvatar(data.avatarUrl || "");
      }
    } catch (err) {
      console.error("Error loading profile:", err);
    }
  };

  const fetchPlatforms = async () => {
    try {
      const res = await fetch("/api/platforms/status");
      const data = await res.json();
      if (data && data.systems) {
        setPlatformSystems(data.systems);
      }
    } catch (err) {
      console.error("Error loading platforms:", err);
    }
  };

  useEffect(() => {
    if (authorized) {
      fetchResponses();
      fetchQuestionnaires();
      fetchBroadcasts();
      fetchProfile();
      fetchPlatforms();
    }
  }, [authorized]);

  const handleUnlock = (e: React.FormEvent) => {
    e.preventDefault();
    const lTrim = login.trim();
    const aTrim = accessCode.trim();
    const isValidLogin = lTrim === "admin" || lTrim === "******" || lTrim === "Опрус-Крео" || lTrim === "Опрус крео";
    const isValidPassword = aTrim === "KISELEVYCREO_2026" || aTrim === "******" || aTrim === "creo2026" || aTrim === "creo26";
    if (isValidLogin && isValidPassword) {
      if (rememberMe) {
        localStorage.setItem("creo_remember_me", "true");
        localStorage.setItem("creo_admin_login", lTrim);
        localStorage.setItem("creo_admin_password", aTrim);
      } else {
        localStorage.removeItem("creo_remember_me");
        localStorage.removeItem("creo_admin_login");
        localStorage.removeItem("creo_admin_password");
      }
      setAuthorized(true);
      setAuthError(false);
    } else {
      setAuthError(true);
    }
  };

  const handleResetData = async (type: "empty" | "mock") => {
    if (!window.confirm(type === "empty" ? "Вы уверены, что хотите полностью очистить базу ответов?" : "Вы хотите сбросить базу и загрузить 5 демонстрационных ответов?")) {
      return;
    }
    try {
      const res = await fetch("/api/responses/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type })
      });
      const data = await res.json();
      if (data.success) {
        setResponses(data.responses);
        setAiResult(null); // Reset AI result since data changed
        setClientRecommendations({});
      }
    } catch (err) {
      console.error("Error resetting responses:", err);
    }
  };

  const handleGenerateQuestionnaire = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topicInput.trim()) return;
    setIsGeneratingQ(true);
    try {
      const res = await fetch("/api/questionnaires/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: topicInput })
      });
      const data = await res.json();
      if (data) {
        setEditingQ(data);
        setQTitle(data.title || "");
        setQDesc(data.description || "");
        setQQuestions(data.questions || []);
      }
    } catch (err) {
      console.error("Error generating questionnaire:", err);
    } finally {
      setIsGeneratingQ(false);
    }
  };

  const handleSaveQuestionnaire = async () => {
    if (!qTitle.trim()) return;
    try {
      const res = await fetch("/api/questionnaires/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: qTitle,
          description: qDesc,
          questions: qQuestions
        })
      });
      const data = await res.json();
      if (data.success) {
        await fetchQuestionnaires();
        setEditingQ(null);
        setTopicInput("");
      }
    } catch (err) {
      console.error("Error saving questionnaire:", err);
    }
  };

  const handleActivateQuestionnaire = async (id: string) => {
    try {
      const res = await fetch("/api/questionnaires/active", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
      });
      const data = await res.json();
      if (data.success) {
        setQuestionnaires(data.questionnaires);
      }
    } catch (err) {
      console.error("Error activating questionnaire:", err);
    }
  };

  const handleBroadcastQuestionnaire = async (id: string) => {
    try {
      const res = await fetch("/api/questionnaires/broadcast", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
      });
      const data = await res.json();
      if (data.success) {
        if (data.warning) {
          alert(`Опросник "${data.broadcast.questionnaireTitle}" активирован в приложении!\n\nОбратите внимание: ${data.warning}\nВы можете настроить реального бота в Secrets (кнопка в панели администратора).`);
        } else if (data.realBroadcastSucceeded) {
          alert(`Опросник "${data.broadcast.questionnaireTitle}" успешно отправлен в ваш Telegram-канал через вашего бота!`);
        } else {
          alert(`Опросник активирован в приложении, но бот не смог отправить сообщение: ${data.errorMessage || "ошибка"}`);
        }
        await fetchQuestionnaires();
        await fetchBroadcasts();
      }
    } catch (err) {
      console.error("Error broadcasting questionnaire:", err);
    }
  };

  const handleDeleteQuestionnaire = async (id: string) => {
    if (!window.confirm("Вы уверены, что хотите удалить этот опросник?")) return;
    try {
      const res = await fetch("/api/questionnaires/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
      });
      const data = await res.json();
      if (data.success) {
        setQuestionnaires(data.questionnaires);
      }
    } catch (err) {
      console.error("Error deleting questionnaire:", err);
    }
  };

  const handleClearBroadcasts = async () => {
    if (!window.confirm("Очистить всю историю рассылок?")) return;
    try {
      const res = await fetch("/api/broadcasts/clear", {
        method: "POST"
      });
      const data = await res.json();
      if (data.success) {
        setBroadcasts([]);
      }
    } catch (err) {
      console.error("Error clearing broadcasts:", err);
    }
  };

  const handleRunAI = async () => {
    setAiLoading(true);
    setAiError(null);
    try {
      const res = await fetch("/api/analyze-ai", { method: "POST" });
      const data = await res.json();
      
      if (!res.ok) {
        if (data.fallback) {
          setAiResult(data.fallback);
          setAiError("Внимание: Использован демо-анализ, так как ключ GEMINI_API_KEY не настроен в секретах проекта. Чтобы включить настоящий ИИ-анализ в реальном времени, добавьте рабочий ключ в Secrets.");
        } else {
          throw new Error(data.error || "Не удалось запустить анализ ИИ.");
        }
      } else {
        setAiResult(data);
      }
    } catch (err: any) {
      setAiError(err.message || "Ошибка подключения к серверу анализа.");
    } finally {
      setAiLoading(false);
    }
  };

  const handleGenerateClientRecommendation = (clientId: string, clientName: string, clientPain: string, clientFeeling: string) => {
    setGeneratingClientRecommendationId(clientId);
    
    // Simulate smart local neural model response
    setTimeout(() => {
      let product = "Курс: Мягкий релиз спины и шеи";
      let marker = "Спазм трапециевидных мышц, фоновая зажатость от тревожных сводок";
      let tone = "Профессиональный, продуктивный, эмпатичный темп KISELEVY_CREO";
      let note = "Клиент крайне восприимчив к физическим практикам. Начать рассылку с мягкой растяжки шеи. Избегать сложной терминологии.";

      const flLower = clientFeeling.toLowerCase();
      const painLower = clientPain.toLowerCase();

      if (flLower.includes("тревога") || flLower.includes("уснуть") || painLower.includes("спать") || painLower.includes("сон")) {
        product = "Курс: Сон-Терапия и Глубокая Йога-Нидра";
        marker = "Сверхактивность ума, дефицит глубокой фазы сна, ментальный перегруз";
        tone = "Принимающий, гипнотический, глубокий успокаивающий голос";
        note = "Рекомендовать практику Йога-Нидры за 20 минут до сна. Предложить вести дневник сброса тревог.";
      } else if (flLower.includes("бессилия") || flLower.includes("замирания") || painLower.includes("силы") || painLower.includes("сил нет")) {
        product = "Курс: Бережная реанимация ресурса";
        marker = "Синдром выгорания / замирания блуждающего нерва (дорсальный вагус)";
        tone = "Теплый, одобряющий, поддерживающий («я с тобой»)";
        note = "Не давать сложных физических нагрузок. Давать только 3-минутные дыхательные упражнения и теплое присутствие.";
      } else if (flLower.includes("пределе") || flLower.includes("последних сил") || painLower.includes("ужасно") || painLower.includes("предел")) {
        product = "Программа: Экспресс-реанимация блуждающего нерва";
        marker = "Критический симпатический тонус (бей или беги), риск панических атак";
        tone = "Уверенный, безопасный, заземляющий («ты в безопасности»)";
        note = "Главный фокус — выведение из паники через квадратное дыхание. Написать в Telegram лично для психологической поддержки.";
      }

      setClientRecommendations(prev => ({
        ...prev,
        [clientId]: { product, marker, tone, note }
      }));
      setGeneratingClientRecommendationId(null);
    }, 1200);
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 2000);
  };

  // Calculations for Analytics
  const totalSubmissions = responses.length;
  const totalSubscribed = responses.filter(r => r.subscribedPractices === "Да" || r.subscribedPractices === "Иногда" || r.subscribed).length;

  const getPercentage = (count: number) => {
    if (totalSubmissions === 0) return 0;
    return Math.round((count / totalSubmissions) * 100);
  };

  // Grouping feelings
  const feelingCounts = responses.reduce((acc: Record<string, number>, curr) => {
    acc[curr.feeling] = (acc[curr.feeling] || 0) + 1;
    return acc;
  }, {});

  // Grouping steady help choices
  const steadyCounts = responses.reduce((acc: Record<string, number>, curr) => {
    curr.steadyHelp.forEach(item => {
      acc[item] = (acc[item] || 0) + 1;
    });
    return acc;
  }, {});

  // Grouping formats
  const formatCounts = responses.reduce((acc: Record<string, number>, curr) => {
    curr.formatPreference.forEach(item => {
      acc[item] = (acc[item] || 0) + 1;
    });
    return acc;
  }, {});

  const isHotLead = (resp: any) => {
    const stress = resp.stressLevel !== undefined ? resp.stressLevel : (resp.aiAnalysis?.stressLevel || 5);
    if (stress < 8) return false;

    let combinedAnswersText = "";
    if (resp.answers && Array.isArray(resp.answers)) {
      combinedAnswersText = resp.answers.map((a: any) => {
        return Array.isArray(a.answer) ? a.answer.join(" ") : String(a.answer || "");
      }).join(" ");
    } else {
      combinedAnswersText = [
        resp.feeling,
        resp.feelingCustom,
        resp.openPain,
        resp.businessNiche,
        resp.businessLack ? (Array.isArray(resp.businessLack) ? resp.businessLack.join(" ") : resp.businessLack) : "",
        resp.businessBurnoutPart,
        resp.businessOpen
      ].join(" ");
    }

    const lowercaseText = combinedAnswersText.toLowerCase();
    const keywords = ["бот", "bot", "telegram", "телеграм", "автоматиз", "сайт", "нейро", "ии", "ai", "веб-сайт", "web-site", "разработк", "платформ", "digital", "цифров", "автомат"];
    return keywords.some(kw => lowercaseText.includes(kw));
  };

  // Filters
  const filteredResponses = responses.filter(resp => {
    const matchesSearch = 
      (resp.name || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (resp.contact || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (resp.openPain || "").toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesFeeling = filterFeeling ? resp.feeling === filterFeeling : true;
    const matchesHotLeads = filterHotLeads ? isHotLead(resp) : true;
    
    return matchesSearch && matchesFeeling && matchesHotLeads;
  });

  // Ready templates
  const storiesTemplate = `ТЗ для KISELEVY_CREO по сторис (Стратегия «Цифровая диагностика»)

[СЛАЙД 1: Присоединение (Эмпатия)]
• Фон: Приглушенный оливковый или бежевый цвет (#F9F8F6), спокойное фото или видео из студии при мягком свете.
• Текст:
«Я вижу и чувствую всё, что происходит сейчас в нашем городе. Знаю, как сейчас непросто физически добраться до зала и как тяжело морально оставаться в покое, когда новости и бытовые трудности (как отсутствие бензина) выбивают почву из-под ног...»
• Интерактив: Ползунок состояния

[СЛАЙД 2: Тест состояния (Выявление боли)]
• Текст:
«Если честно, какое чувство сейчас внутри преобладает?»
• Интерактив: Опрос с 4 вариантами ответов:
  1. Напряжение в теле (зажаты плечи, болит спина)
  2. Постоянная тревога в мыслях, сложно уснуть
  3. Чувство бессилия и замирания
  4. Стараюсь держаться, но на пределе

[СЛАЙД 3: Забота]
• Текст:
«Что бы сейчас помогло вам почувствовать себя хоть чуточку устойчивее?»
• Интерактив: Опрос / Выберите то, что откликается:
  - Покой
  - Расслабление тела
  - Поддержка
  - Хороший сон

[СЛАЙД 4: Выбор формата]
• Текст:
«Какую бесплатную практику вы хотели бы получить?»
• Интерактив: Варианты на выбор:
  - Антистресс дыхание
  - Йога
  - Расслабление шеи
  - Медитация перед сном

[СЛАЙД 5: Открытый вопрос]
• Текст:
«Что сейчас болит сильнее всего?»
• Интерактив: Наклейка «Вопрос» с подписью: «Напишите всё, что захотите. Я обязательно прочитаю лично».

[СЛАЙД 6: Анонс и Призыв к действию]
• Текст:
«Я приняла решение: расстояние и отсутствие бензина не должны лишать нас возможности восстанавливаться. 

Я готовлю для вас бесплатную домашнюю антистресс-программу. 
Если вам это нужно — ответьте на эту сторис или пройдите наш минутный разбор!»`;

  const broadcastTemplate = `Приветственное сообщение для клиентского чата / рассылки

Здравствуйте, дорогие!

Я вижу и чувствую всё, что происходит сейчас вокруг нас в городе. Знаю, как физически непросто добраться до зала и как тяжело морально оставаться в равновесии, когда бытовые трудности и бесконечный поток новостей выбивают почву из-под ног. 

Я твердо убеждена: расстояние и отсутствие бензина не должны лишать нас возможности заботиться о себе. Ваше тело и дыхание — это то, что всегда с вами, ваш главный островок покоя.

Поэтому я приняла решение подготовить для вас бесплатную домашнюю антистресс-программу с короткими практиками на 5–10 минут, которые помогут:
• Снять напряжение в теле (зажимы в шее, лопатках, пояснице)
• Вернуть спокойствие мыслям и глубокий сон
• Справиться с тревогой в моменты паники

Чтобы программа получилась максимально точной и нужной именно вам, пройдите диагностику своего состояния (это займет всего 2 минуты):
[ВСТАВЬТЕ ССЫЛКУ НА ЭТО ПРИЛОЖЕНИЕ]

Я лично прочитаю каждый ваш ответ. В благодарность в конце опроса вы сразу получите доступ к интерактивной дыхательной практике!

Обнимаю вас. Практика там, где ты.`;

  if (!authorized) {
    return (
      <div className="max-w-md mx-auto px-4 py-16" id="auth-panel">
        <div className="bg-white rounded-3xl p-8 border border-[#E6E3DB] text-center space-y-6 shadow-md font-serif">
          <div className="inline-flex p-4 rounded-full bg-[#8B8C7A]/10 text-[#8B8C7A]">
            <Lock className="w-10 h-10" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl text-[#3D3B36] font-light">Панель управления CRM</h2>
            <p className="text-xs font-sans text-[#8B8C7A] uppercase tracking-wider">Кабинет команды</p>
          </div>

          <form onSubmit={handleUnlock} className="space-y-4">
            <div className="space-y-3 text-left">
              <div className="relative">
                <input
                  id="admin-login-input"
                  type={showLogin ? "text" : "password"}
                  value={login}
                  onChange={(e) => setLogin(e.target.value)}
                  placeholder="Логин"
                  className="w-full p-3 pl-4 pr-10 rounded-xl border border-[#E6E3DB] bg-[#F9F8F6] text-[#3D3B36] font-sans text-sm focus:outline-none focus:border-[#8B8C7A]"
                />
                <button
                  type="button"
                  onClick={() => setShowLogin(!showLogin)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:outline-none cursor-pointer"
                  title={showLogin ? "Скрыть" : "Показать"}
                >
                  {showLogin ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <div className="relative">
                <input
                  id="access-code-input"
                  type={showPassword ? "text" : "password"}
                  value={accessCode}
                  onChange={(e) => setAccessCode(e.target.value)}
                  placeholder="Пароль"
                  className="w-full p-3 pl-4 pr-10 rounded-xl border border-[#E6E3DB] bg-[#F9F8F6] text-[#3D3B36] font-mono text-sm focus:outline-none focus:border-[#8B8C7A]"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:outline-none cursor-pointer"
                  title={showPassword ? "Скрыть" : "Показать"}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {/* Remember me checkbox */}
              <div className="flex items-center gap-2 pl-1 select-none">
                <input
                  type="checkbox"
                  id="remember-me-checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-[#E6E3DB] text-[#8B8C7A] focus:ring-[#8B8C7A] w-3.5 h-3.5 cursor-pointer accent-[#8B8C7A]"
                />
                <label htmlFor="remember-me-checkbox" className="text-[11px] text-[#8B8C7A] font-sans font-medium cursor-pointer">
                  Запомнить меня
                </label>
              </div>

              {authError && (
                <p className="text-rose-600 text-xs mt-1.5 flex items-center justify-center gap-1 font-sans">
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>Неверный логин или пароль</span>
                </p>
              )}
            </div>

            <button
              id="btn-unlock-dashboard"
              type="submit"
              className="w-full bg-[#8B8C7A] hover:bg-[#5A5A40] text-white font-sans text-xs uppercase tracking-widest font-semibold py-3 px-6 rounded-full transition-all cursor-pointer shadow-sm"
            >
              Войти в кабинет
            </button>
          </form>

          <div className="bg-[#8B8C7A]/5 border border-[#E6E3DB] rounded-2xl p-4 text-xs text-[#5A5A40] text-left space-y-1.5 font-sans leading-relaxed">
            <span className="font-bold block text-[#5A5A40]/80">Доступ зарезервирован для Администраторов:</span>
            <div className="space-y-1 bg-white/50 p-2.5 rounded-lg border border-[#E6E3DB]/40 relative">
              <p className="font-semibold text-[10px] text-[#8B8C7A] uppercase tracking-wider">KISELEVY CREO — Администратор:</p>
              <p className="flex justify-between items-center">
                <span>Логин: <span className="font-mono bg-white px-1.5 py-0.5 rounded border border-[#E6E3DB] text-[#3D3B36] font-bold">{revealCredentials ? "admin" : "******"}</span></span>
              </p>
              <p className="flex justify-between items-center">
                <span>Пароль: <span className="font-mono bg-white px-1.5 py-0.5 rounded border border-[#E6E3DB] text-[#3D3B36] font-bold">{revealCredentials ? "KISELEVYCREO_2026" : "******"}</span></span>
                <button
                  type="button"
                  onClick={() => setRevealCredentials(!revealCredentials)}
                  className="text-[#8B8C7A] hover:text-[#5A5A40] focus:outline-none cursor-pointer text-[10px] uppercase font-bold tracking-wider flex items-center gap-1"
                >
                  {revealCredentials ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  <span>{revealCredentials ? "Скрыть" : "Показать"}</span>
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full bg-[#F9F8F6] text-[#3D3B36] rounded-3xl border border-[#E6E3DB] shadow-lg overflow-hidden flex flex-col font-serif" id="admin-panel-container">
      
      {/* Top Header Banner */}
      <div className="px-6 sm:px-12 py-8 border-b border-[#E6E3DB] flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-[#F5F3EE]">
        <div>
          <div className="flex items-center gap-2 text-[#8B8C7A] font-serif text-xl font-light">
            <Sparkles className="w-5 h-5 text-[#8B8C7A]" />
            <span>Кабинет команды • Модуль «Клиенты»</span>
          </div>
          <p className="text-[11px] font-sans text-[#8B8C7A] uppercase tracking-wider mt-1 leading-snug">
            Универсальная авто-воронка доверия и CRM аналитика для KISELEVY_CREO
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => handleResetData("empty")}
            className="px-4 py-2 border border-rose-200 bg-white text-rose-600 hover:bg-rose-50 text-xs rounded-full font-sans font-semibold uppercase tracking-wider flex items-center gap-1.5 cursor-pointer shadow-sm"
            title="Очистить всю базу"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Очистить</span>
          </button>
        </div>
      </div>

      {/* Mini Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 border-b border-[#E6E3DB] bg-white font-sans text-xs">
        <div className="p-5 border-r border-[#E6E3DB] flex flex-col justify-between">
          <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider">Всего анкет в базе</span>
          <p className="text-3xl font-light text-[#3D3B36] font-serif mt-1">{totalSubmissions}</p>
        </div>
        
        <div className="p-5 border-r border-[#E6E3DB] flex flex-col justify-between">
          <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider flex items-center gap-1">Хотели бы практики (<Heart className="w-3 h-3 text-[#8B8C7A]" />)</span>
          <p className="text-3xl font-light text-rose-600 font-serif mt-1">
            {totalSubscribed} <span className="text-xs font-sans text-[#8B8C7A]">({getPercentage(totalSubscribed)}%)</span>
          </p>
        </div>

        <div className="p-5 border-r border-[#E6E3DB] flex flex-col justify-between">
          <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider">Главный маркер боли</span>
          <p className="text-sm font-semibold text-[#3D3B36] truncate mt-1.5 font-serif italic">
            {Object.keys(feelingCounts).length > 0 
              ? Object.entries(feelingCounts).sort((a,b) => (b[1] as number) - (a[1] as number))[0][0].split(" (")[0] 
              : "Нет данных"}
          </p>
        </div>

        <div className="p-5 flex flex-col justify-between bg-[#8B8C7A]/5">
          <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider">ИИ-Двигатель</span>
          <div className="flex items-center gap-1.5 text-purple-700 font-bold mt-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] uppercase tracking-wider">Gemini 3.5 Flash Готов</span>
          </div>
        </div>
      </div>

      {/* Tabs Selector */}
      <div className="flex border-b border-[#E6E3DB] bg-[#F9F8F6] px-6 sm:px-12 overflow-x-auto gap-6 sm:gap-10 font-sans text-xs uppercase tracking-widest py-1">
        <button
          onClick={() => setActiveTab("clients")}
          className={`py-4 transition-all flex items-center gap-2 cursor-pointer border-b-2 font-bold ${
            activeTab === "clients" 
              ? "border-[#8B8C7A] text-[#3D3B36]" 
              : "border-transparent text-[#8B8C7A] hover:text-[#3D3B36]"
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Модуль «Клиенты»</span>
        </button>

        <button
          onClick={() => setActiveTab("analytics")}
          className={`py-4 transition-all flex items-center gap-2 cursor-pointer border-b-2 font-bold ${
            activeTab === "analytics" 
              ? "border-[#8B8C7A] text-[#3D3B36]" 
              : "border-transparent text-[#8B8C7A] hover:text-[#3D3B36]"
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Аналитика и Метрики</span>
        </button>

        <button
          onClick={() => setActiveTab("ai")}
          className={`py-4 transition-all flex items-center gap-2 cursor-pointer border-b-2 font-bold ${
            activeTab === "ai" 
              ? "border-[#8B8C7A] text-[#3D3B36]" 
              : "border-transparent text-[#8B8C7A] hover:text-[#3D3B36]"
          }`}
        >
          <Brain className="w-4 h-4" />
          <span>ИИ-Анализ Аудитории</span>
        </button>

        <button
          onClick={() => setActiveTab("materials")}
          className={`py-4 transition-all flex items-center gap-2 cursor-pointer border-b-2 font-bold ${
            activeTab === "materials" 
              ? "border-[#8B8C7A] text-[#3D3B36]" 
              : "border-transparent text-[#8B8C7A] hover:text-[#3D3B36]"
          }`}
        >
          <Clipboard className="w-4 h-4" />
          <span>Сценарии прогрева</span>
        </button>

        <button
          onClick={() => setActiveTab("questionnaires")}
          className={`py-4 transition-all flex items-center gap-2 cursor-pointer border-b-2 font-bold ${
            activeTab === "questionnaires" 
              ? "border-[#8B8C7A] text-[#3D3B36]" 
              : "border-transparent text-[#8B8C7A] hover:text-[#3D3B36]"
          }`}
        >
          <Radio className="w-4 h-4 text-purple-600" />
          <span>Опросники и Рассылки</span>
        </button>

        <button
          onClick={() => setActiveTab("platforms")}
          className={`py-4 transition-all flex items-center gap-2 cursor-pointer border-b-2 font-bold ${
            activeTab === "platforms" 
              ? "border-[#8B8C7A] text-[#3D3B36]" 
              : "border-transparent text-[#8B8C7A] hover:text-[#3D3B36]"
          }`}
        >
          <Globe className="w-4 h-4 text-emerald-600" />
          <span>3 Платформы (Канал, MAX, Web)</span>
        </button>

        <button
          onClick={() => setActiveTab("profile")}
          className={`py-4 transition-all flex items-center gap-2 cursor-pointer border-b-2 font-bold ${
            activeTab === "profile" 
              ? "border-[#8B8C7A] text-[#3D3B36]" 
              : "border-transparent text-[#8B8C7A] hover:text-[#3D3B36]"
          }`}
        >
          <Settings className="w-4 h-4" />
          <span>Настройки</span>
        </button>
      </div>

      {/* Tab Panels */}
      {activeTab === "clients" && (
        <div className="p-6 sm:p-12 space-y-6">
          {/* Client Filter Controls */}
          <div className="flex flex-col md:flex-row gap-4 items-stretch md:items-center justify-between bg-white p-5 rounded-2xl border border-[#E6E3DB] font-sans">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#8B8C7A]" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Поиск по имени, контакту или открытой боли..."
                className="w-full pl-10 pr-4 py-2 border border-[#E6E3DB] rounded-xl text-sm focus:outline-none focus:border-[#8B8C7A] bg-[#FAF9F5] text-[#3D3B36]"
              />
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-[#8B8C7A]" />
                <select
                  value={filterFeeling}
                  onChange={(e) => setFilterFeeling(e.target.value)}
                  className="p-2 border border-[#E6E3DB] rounded-xl text-xs focus:outline-none focus:border-[#8B8C7A] bg-white text-[#3D3B36]"
                >
                  <option value="">Все маркеры боли</option>
                  {Object.keys(feelingCounts).map((f) => (
                    <option key={f} value={f}>
                      {f} ({feelingCounts[f]})
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={() => setFilterHotLeads(!filterHotLeads)}
                className={`px-3 py-2 border rounded-xl text-xs font-semibold flex items-center gap-1.5 cursor-pointer transition-all ${
                  filterHotLeads 
                    ? "bg-amber-500 border-amber-500 text-white shadow-sm" 
                    : "bg-white border-[#E6E3DB] text-gray-600 hover:bg-gray-50"
                }`}
              >
                <Flame className={`w-3.5 h-3.5 ${filterHotLeads ? "text-white" : "text-amber-500 animate-pulse"}`} />
                <span>Только Горячие лиды</span>
              </button>
              {filterHotLeads && (
                <span className="text-[10px] font-sans text-amber-600 font-bold animate-pulse">
                  (Найдено: {filteredResponses.length})
                </span>
              )}
            </div>
          </div>

          {/* Cards Panel */}
          {filteredResponses.length === 0 ? (
            <div className="bg-[#F9F8F6] rounded-2xl py-16 text-center border border-[#E6E3DB] text-[#8B8C7A] text-sm space-y-1">
              <p className="font-semibold text-lg text-[#3D3B36] font-serif italic">Карточки не найдены</p>
              <p className="font-sans text-xs">Заполните анкету во вкладке «Бот-Опросник» для появления данных.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {filteredResponses.map((resp) => {
                const cSteps = resp.campaignSteps || { day1: "idle", day3: "idle", day7: "idle" };
                const feelingSafe = resp.feeling || "Не указано";
                const savedRec = clientRecommendations[resp.id];
                const currentNotes = clientNotes[resp.id] || "";

                // Determine Source
                const isTgSource = resp.contact && (resp.contact.startsWith("@") || resp.contact.toLowerCase().includes("t.me") || /^[a-zA-Z_0-9]{3,20}$/.test(resp.contact));
                const sourceStr = isTgSource ? "Telegram-бот" : "Web-приложение";

                let derivedPains = "Физическое и эмоциональное напряжение";
                if (feelingSafe.includes("теле") || feelingSafe.includes("шея") || feelingSafe.includes("плечи") || feelingSafe.includes("напряжение")) {
                  derivedPains = "Телесные зажимы (плечи, лопатки, спина), мышечный панцирь";
                } else if (feelingSafe.includes("тревога") || feelingSafe.includes("уснуть")) {
                    derivedPains = "Ментальная гиперактивность, перегрузка из-за новостей";
                  } else if (feelingSafe.includes("бессилия")) {
                    derivedPains = "Оцепенение, вегетативное замирание, упадок сил";
                  } else if (feelingSafe.includes("пределе")) {
                    derivedPains = "Сверхнапряжение нервной системы, угроза паники";
                  }
                  
                  let openPainSafe = resp.openPain;
                  if (!openPainSafe && resp.answers) {
                    const painAns = resp.answers.find((a: any) => a.questionId === "openPain");
                    if (painAns) openPainSafe = painAns.answer;
                  }
                  if (openPainSafe) {
                    derivedPains = openPainSafe;
                  }

                  let derivedFears = "Страх потерять устойчивость и контроль над будущим";
                  if (feelingSafe.includes("тревога")) {
                    derivedFears = "Страх хронической бессонницы, паники, потери здоровья";
                  } else if (feelingSafe.includes("бессилия")) {
                    derivedFears = "Страх остаться без сил, полной апатии и изоляции";
                  } else if (feelingSafe.includes("пределе")) {
                    derivedFears = "Страх нервного срыва, потери самоконтроля";
                  }

                  let steadyHelpSafe = resp.steadyHelp;
                  if (!steadyHelpSafe && resp.answers) {
                    const helpAns = resp.answers.find((a: any) => a.questionId === "steadyHelp");
                    if (helpAns) steadyHelpSafe = Array.isArray(helpAns.answer) ? helpAns.answer : [helpAns.answer];
                  }
                  const derivedDesires = (steadyHelpSafe && steadyHelpSafe.length > 0)
                    ? steadyHelpSafe.join(", ") 
                    : "Мягкая поддержка и восстановление сна";

                  // Interest assessment
                  let interestStr = "Средний";
                  if (resp.subscribedPractices === "Да" || resp.subscribed) {
                    interestStr = "Высокий";
                  } else if (resp.subscribedPractices === "Иногда") {
                    interestStr = "Умеренный";
                  } else if (resp.subscribedPractices === "Нет") {
                    interestStr = "Низкий";
                  }

                  // Suitable Product matching
                  let suitableProduct = "Клуб бережной заботы KISELEVY_CREO";
                  if (feelingSafe.includes("теле") || feelingSafe.includes("зажаты")) {
                    suitableProduct = "Курс KISELEVY_CREO «Свобода тела: снятие зажимов спины и шеи»";
                  } else if (feelingSafe.includes("тревога") || feelingSafe.includes("уснуть")) {
                    suitableProduct = "Программа «Тихий Сон и Глубокая Йога-Нидра»";
                  } else if (feelingSafe.includes("бессилия")) {
                    suitableProduct = "Реанимация ресурса «Опора: заземление и дыхание»";
                  } else if (feelingSafe.includes("пределе")) {
                    suitableProduct = "Интенсив KISELEVY_CREO «Нервная система: выход из режима выживания»";
                  }

                  let assignedProgram = "Баланс и бережное заземление (30 дней)";
                  const fSafeLower = feelingSafe.toLowerCase();
                  if (fSafeLower.includes("напряжение") || fSafeLower.includes("теле") || fSafeLower.includes("зажаты") || fSafeLower.includes("спина") || fSafeLower.includes("болит") || fSafeLower.includes("зажат") || fSafeLower.includes("plech") || fSafeLower.includes("шея")) {
                    assignedProgram = "Освобождение тела и снятие зажимов (30 дней)";
                  } else if (fSafeLower.includes("тревога") || fSafeLower.includes("мыслях") || fSafeLower.includes("уснуть") || fSafeLower.includes("беспоко") || fSafeLower.includes("страх")) {
                    assignedProgram = "Успокоение ума и глубокий сон (30 дней)";
                  } else if (fSafeLower.includes("бессилия") || fSafeLower.includes("замирания") || fSafeLower.includes("апатия") || fSafeLower.includes("сил") || fSafeLower.includes("устал")) {
                    assignedProgram = "Бережное восстановление ресурса (30 дней)";
                  } else if (fSafeLower.includes("пределе") || fSafeLower.includes("выживани") || fSafeLower.includes("выгора") || fSafeLower.includes("срыв")) {
                    assignedProgram = "Реанимация нервной системы (30 дней)";
                  }

                  // Received practices list
                  const receivedPractices = ["Дыхание «Анти-паника» (тренажер)"];
                  if (cSteps.day3 === "sent") {
                    receivedPractices.push("Практика «Мягкий шевелящийся релиз шеи»");
                  }
                  if (cSteps.day7 === "sent") {
                    receivedPractices.push("Медитация Йога-нидра «Тишина внутри»");
                  }
                  const getAnswer = (qid: string) => {
                    if (resp.answers) {
                      const ans = resp.answers.find((a: any) => a.questionId === qid);
                      if (ans) {
                        return Array.isArray(ans.answer) ? ans.answer.join(", ") : ans.answer;
                      }
                    }
                    return null;
                  };

                  const feelingVal = getAnswer("feeling") || resp.feeling || "Не указано";
                  const feelingCustomVal = getAnswer("feeling_custom") || resp.feelingCustom;
                  const quietTimeVal = getAnswer("quietTime");
                  const heavyReactionVal = getAnswer("heavyReaction");
                  const innerStatePriorityVal = getAnswer("innerStatePriority");
                  const psychologyOpenVal = getAnswer("psychologyOpen") || resp.openPain;

                  const businessNicheVal = getAnswer("businessNiche");
                  const businessLackVal = getAnswer("businessLack");
                  const businessBurnoutPartVal = getAnswer("businessBurnoutPart");
                  const businessOpenVal = getAnswer("businessOpen");

                  const isHot = isHotLead(resp);

                  return (
                    <div key={resp.id} className={`bg-white rounded-2xl p-6 border transition-all relative space-y-6 ${
                      isHot 
                        ? "border-amber-400 bg-amber-50/5 hover:border-amber-500 shadow-xs hover:shadow-md" 
                        : "border-[#E6E3DB] hover:shadow-md"
                    }`}>
                      {isHot && (
                        <div className="absolute -top-3 right-6 bg-gradient-to-r from-amber-500 to-rose-500 text-white font-sans text-[10px] uppercase tracking-wider font-bold px-3 py-1 rounded-full shadow-md flex items-center gap-1.5 animate-pulse z-10">
                          <Flame className="w-3.5 h-3.5 fill-white text-white" />
                          <span>Горячий лид</span>
                        </div>
                      )}
                      {/* Card Header: Client Identity & Quick Status */}
                      <div className="flex justify-between items-start flex-wrap gap-4 border-b border-[#E6E3DB] pb-4">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-serif text-xl font-bold text-[#3D3B36]">{resp.name || "Аноним"}</span>
                            {resp.contact ? (
                              <span className="font-mono text-xs bg-shanti-green/10 border border-shanti-green/20 text-shanti-green px-3 py-0.5 rounded-full font-medium">
                                {resp.contact}
                              </span>
                            ) : (
                              <span className="font-mono text-xs bg-gray-100 text-gray-400 px-2.5 py-0.5 rounded-full">Без контактов</span>
                            )}
                            <span className="font-sans text-[10px] bg-amber-50 border border-amber-200 text-amber-800 px-2.5 py-0.5 rounded-full font-medium">
                              {sourceStr}
                            </span>
                          </div>
                          <p className="text-[11px] font-sans text-[#8B8C7A]">
                            Анкета заполнена: {new Date(resp.timestamp).toLocaleString("ru-RU", { day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" })}
                          </p>
                        </div>

                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] font-sans font-bold uppercase tracking-wider px-3 py-1 rounded-full border ${
                            interestStr.includes("Высокий") 
                              ? "bg-emerald-50 border-emerald-200 text-emerald-700" 
                              : interestStr.includes("Умеренный")
                              ? "bg-amber-50 border-amber-200 text-amber-700"
                              : "bg-gray-100 border-gray-200 text-gray-500"
                          }`}>
                            Интерес: {interestStr}
                          </span>
                        </div>
                      </div>

                      {/* 4 Grouped Sections Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        
                        {/* SECTION 1: Психологическое состояние */}
                        <div className="bg-[#FAF9F5] border border-[#E6E3DB]/70 rounded-xl p-5 space-y-4">
                          <h3 className="font-serif text-sm font-bold text-[#3D3B36] border-b border-[#E6E3DB] pb-2 flex items-center gap-2">
                            <Brain className="w-4 h-4 text-shanti-green shrink-0" />
                            <span>Психологическое состояние</span>
                          </h3>
                          <div className="space-y-3 text-xs text-gray-700">
                            <div>
                              <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Текущее состояние / Чувство:</span>
                              <p className="text-[#3D3B36] font-medium mt-0.5">{feelingVal}</p>
                              {feelingCustomVal && (
                                <p className="text-gray-500 mt-1 italic">Детали: {feelingCustomVal}</p>
                              )}
                            </div>
                            {quietTimeVal && (
                              <div>
                                <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Что приносит спокойствие:</span>
                                <p className="text-[#3D3B36] font-medium mt-0.5">{quietTimeVal}</p>
                              </div>
                            )}
                            {heavyReactionVal && (
                              <div>
                                <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Реакция на тяжелые события:</span>
                                <p className="text-[#3D3B36] font-medium mt-0.5">{heavyReactionVal}</p>
                              </div>
                            )}
                            {innerStatePriorityVal && (
                              <div>
                                <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Приоритет внутреннего состояния:</span>
                                <p className="text-[#3D3B36] font-medium mt-0.5">{innerStatePriorityVal}</p>
                              </div>
                            )}
                            {psychologyOpenVal && (
                              <div className="bg-white border border-[#E6E3DB]/40 p-3 rounded-lg">
                                <span className="text-[10px] font-bold text-shanti-green uppercase tracking-wider block mb-1">Открытый ответ (боли и переживания):</span>
                                <p className="text-[#3D3B36] font-serif italic leading-relaxed">«{psychologyOpenVal}»</p>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* SECTION 2: Бизнес и потребности */}
                        <div className="bg-[#FAF9F5] border border-[#E6E3DB]/70 rounded-xl p-5 space-y-4">
                          <h3 className="font-serif text-sm font-bold text-[#3D3B36] border-b border-[#E6E3DB] pb-2 flex items-center gap-2">
                            <Briefcase className="w-4 h-4 text-shanti-green shrink-0" />
                            <span>Бизнес и потребности</span>
                          </h3>
                          <div className="space-y-3 text-xs text-gray-700">
                            {businessNicheVal ? (
                              <div>
                                <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Ниша бизнеса / Профессия:</span>
                                <p className="text-[#3D3B36] font-medium mt-0.5">{businessNicheVal}</p>
                              </div>
                            ) : (
                              <div>
                                <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Ниша бизнеса / Профессия:</span>
                                <p className="text-gray-400 italic mt-0.5">Данные отсутствуют (legacy опросник)</p>
                              </div>
                            )}
                            {businessLackVal && (
                              <div>
                                <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Чего не хватает для масштабирования:</span>
                                <p className="text-[#3D3B36] font-medium mt-0.5">{businessLackVal}</p>
                              </div>
                            )}
                            {businessBurnoutPartVal && (
                              <div>
                                <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Где ближе всего к точке выгорания:</span>
                                <p className="text-[#3D3B36] font-medium mt-0.5">{businessBurnoutPartVal}</p>
                              </div>
                            )}
                            {businessOpenVal && (
                              <div className="bg-white border border-[#E6E3DB]/40 p-3 rounded-lg">
                                <span className="text-[10px] font-bold text-shanti-green uppercase tracking-wider block mb-1">Что хочется улучшить в своем деле:</span>
                                <p className="text-[#3D3B36] font-serif italic leading-relaxed">«{businessOpenVal}»</p>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* SECTION 3: Рекомендация ИИ */}
                        <div className="bg-[#FAF9F5] border border-[#E6E3DB]/70 rounded-xl p-5 space-y-4 md:col-span-2">
                          <div className="flex justify-between items-center border-b border-[#E6E3DB] pb-2">
                            <h3 className="font-serif text-sm font-bold text-[#3D3B36] flex items-center gap-2">
                              <Sparkles className="w-4 h-4 text-shanti-green shrink-0" />
                              <span>Рекомендация ИИ (Опрус ИИ-модель)</span>
                            </h3>
                            <button
                              onClick={() => handleGenerateClientRecommendation(resp.id, resp.name || "Аноним", psychologyOpenVal || "", feelingVal)}
                              disabled={generatingClientRecommendationId === resp.id}
                              className="text-[10px] uppercase font-semibold text-shanti-green hover:text-shanti-olive flex items-center gap-1 cursor-pointer disabled:opacity-50"
                            >
                              <RefreshCw className={`w-3 h-3 ${generatingClientRecommendationId === resp.id ? "animate-spin" : ""}`} />
                              {generatingClientRecommendationId === resp.id ? "Анализ..." : "Перегенерировать"}
                            </button>
                          </div>

                          {(() => {
                            let parsedAiAnalysis: any = null;
                            if (resp.aiAnalysis) {
                              try {
                                parsedAiAnalysis = typeof resp.aiAnalysis === "string" ? JSON.parse(resp.aiAnalysis) : resp.aiAnalysis;
                              } catch (e) {
                                console.error("Error parsing aiAnalysis:", e);
                              }
                            }

                            const productVal = parsedAiAnalysis?.suitableProduct || savedRec?.product || suitableProduct;
                            const summaryVal = parsedAiAnalysis?.aiSummary || savedRec?.marker || "ИИ-анализ на стадии генерации. Нажмите кнопку справа для мгновенного разбора.";
                            const toneVal = parsedAiAnalysis?.recommendedTone || savedRec?.tone || "Внимательный слушатель на психологических шагах, легкая смышленость и партнерский тон на шагах о бизнесе.";
                            const touchVal = parsedAiAnalysis?.touchStrategy || savedRec?.note || "Предложить бесплатную 7-дневную сессию нейро-коуча в качестве подарка за заполнение анкеты.";

                            return (
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                                <div className="md:col-span-2 space-y-3">
                                  <div className="bg-white p-3.5 rounded-lg border border-[#E6E3DB]/40">
                                    <span className="text-[10px] font-bold text-amber-700 uppercase tracking-wider block mb-1">Продукт / Нейро-Решение KISELEVY_CREO:</span>
                                    <p className="text-[#3D3B36] font-serif font-bold text-sm text-shanti-dark">
                                      {productVal}
                                    </p>
                                  </div>
                                  <div className="bg-white p-3.5 rounded-lg border border-[#E6E3DB]/40">
                                    <span className="text-[10px] font-bold text-shanti-green uppercase tracking-wider block mb-1">ИИ-Разбор личности и потребностей:</span>
                                    <p className="text-[#3D3B36] font-sans leading-relaxed text-xs">
                                      {summaryVal}
                                    </p>
                                  </div>
                                </div>

                                <div className="space-y-3">
                                  <div className="bg-white p-3 rounded-lg border border-[#E6E3DB]/40">
                                    <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block mb-0.5">Рекомендуемый тон общения:</span>
                                    <p className="text-[#3D3B36] font-sans leading-relaxed text-[11px]">
                                      {toneVal}
                                    </p>
                                  </div>
                                  <div className="bg-white p-3 rounded-lg border border-[#E6E3DB]/40">
                                    <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block mb-0.5">Рекомендация по прогреву:</span>
                                    <p className="text-[#3D3B36] font-sans leading-relaxed text-[11px]">
                                      {touchVal}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            );
                          })()}
                        </div>

                        {/* SECTION 4: Контакты и статус */}
                        <div className="bg-[#FAF9F5] border border-[#E6E3DB]/70 rounded-xl p-5 space-y-4 md:col-span-2">
                          <h3 className="font-serif text-sm font-bold text-[#3D3B36] border-b border-[#E6E3DB] pb-2 flex items-center gap-2">
                            <Phone className="w-4 h-4 text-shanti-green shrink-0" />
                            <span>Контакты и статус воронки</span>
                          </h3>
                          
                          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 text-xs">
                            {/* Notes and Touch triggers */}
                            <div className="md:col-span-7 space-y-3">
                              <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Личные заметки менеджера KISELEVY_CREO:</span>
                              <textarea
                                value={currentNotes}
                                onChange={(e) => updateNote(resp.id, e.target.value)}
                                placeholder="Запишите комментарии, результаты звонков или особые договоренности..."
                                rows={3}
                                className="w-full p-3 rounded-xl border border-[#E6E3DB] bg-white text-[#3D3B36] text-xs focus:outline-none focus:ring-1 focus:ring-shanti-green resize-none leading-relaxed"
                              />
                              <div className="flex justify-between items-center text-[9px] text-[#8B8C7A] -mt-1 px-1">
                                <span>Автосохранение включено</span>
                                <span className="font-mono">{currentNotes.length} симв.</span>
                              </div>

                              <div className="bg-white border border-[#E6E3DB]/70 p-3.5 rounded-xl space-y-1 mt-3 shadow-xs">
                                <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider flex items-center gap-1">
                                  <Star className="w-3 h-3 text-shanti-green fill-shanti-green" />
                                  <span>Статус бонуса (7 дней нейро-коуча):</span>
                                </span>
                                <div className="flex items-center gap-1.5 text-xs text-[#3D3B36] font-medium">
                                  <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
                                  <span>{resp.bonusStatus || `Отправлен автоматически (${new Date(resp.timestamp).toLocaleDateString("ru-RU", { day: "numeric", month: "long" })})`}</span>
                                </div>
                              </div>
                            </div>

                            <div className="md:col-span-5 space-y-2">
                              <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block mb-1">Сценарии быстрых касаний в мессенджере:</span>
                              
                              <div className="space-y-2 text-[10px]">
                                {/* Funnel Step 1 */}
                                <div className="bg-white border border-[#E6E3DB]/60 p-2 rounded-lg flex justify-between items-center gap-2">
                                  <div>
                                    <div className="flex items-center gap-1">
                                      <span className="font-bold text-[#3D3B36]">Шаг 1 (24ч)</span>
                                      <span className="text-[8px] bg-[#FAF9F5] text-emerald-700 border border-emerald-100 px-1 rounded">ИИ-прогрев</span>
                                    </div>
                                    <span className="text-gray-500 text-[9px]">«Как успехи с идеями из опросника?»</span>
                                  </div>
                                  <button
                                    onClick={() => copyToClipboard(`Привет, ${resp.name || "друг"}! Это Опрус из KISELEVY_CREO. Как тебе идеи и подарки из опросника? Мы готовы обсудить твой разбор по автоматизации лично! Поделись мыслями.`, `touch1-${resp.id}`)}
                                    className="p-1.5 text-shanti-green hover:text-shanti-olive bg-white border border-[#E6E3DB] rounded-lg cursor-pointer"
                                    title="Скопировать шаблон сообщения"
                                  >
                                    {copiedText === `touch1-${resp.id}` ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <Send className="w-3.5 h-3.5" />}
                                  </button>
                                </div>

                                {/* Funnel Step 2 */}
                                <div className="bg-white border border-[#E6E3DB]/60 p-2 rounded-lg flex justify-between items-center gap-2">
                                  <div>
                                    <div className="flex items-center gap-1">
                                      <span className="font-bold text-[#3D3B36]">Шаг 2 (3д)</span>
                                      <span className="text-[8px] bg-[#FAF9F5] text-amber-700 border border-amber-100 px-1 rounded">Презентация</span>
                                    </div>
                                    <span className="text-gray-500 text-[9px]">Отправка PDF-презентации кейсов</span>
                                  </div>
                                  <button
                                    onClick={() => copyToClipboard(`Привет, ${resp.name || ""}! Команда KISELEVY_CREO подготовила для тебя подборку наших кейсов по нейро-помощникам и автоматизации под твои боли. Посмотри, пожалуйста: https://t.me/kiselevy_creo`, `touch2-${resp.id}`)}
                                    className="p-1.5 text-shanti-green hover:text-shanti-olive bg-white border border-[#E6E3DB] rounded-lg cursor-pointer"
                                    title="Скопировать шаблон сообщения"
                                  >
                                    {copiedText === `touch2-${resp.id}` ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <Send className="w-3.5 h-3.5" />}
                                  </button>
                                </div>

                                {/* Funnel Step 3 */}
                                <div className="bg-white border border-[#E6E3DB]/60 p-2 rounded-lg flex justify-between items-center gap-2">
                                  <div>
                                    <div className="flex items-center gap-1">
                                      <span className="font-bold text-[#3D3B36]">Шаг 3 (7д)</span>
                                      <span className="text-[8px] bg-[#FAF9F5] text-purple-700 border border-purple-100 px-1 rounded">Звонок</span>
                                    </div>
                                    <span className="text-gray-500 text-[9px]">Приглашение на личный разбор</span>
                                  </div>
                                  <button
                                    onClick={() => copyToClipboard(`Привет, ${resp.name || ""}! Давай созвонимся буквально на 15 минут, и мы покажем тебе на экране схему, как автоматизировать рутину в твоем деле. Будет полезно и абсолютно бесплатно! Напиши, когда удобно.`, `touch3-${resp.id}`)}
                                    className="p-1.5 text-shanti-green hover:text-shanti-olive bg-white border border-[#E6E3DB] rounded-lg cursor-pointer"
                                    title="Скопировать шаблон сообщения"
                                  >
                                    {copiedText === `touch3-${resp.id}` ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <Send className="w-3.5 h-3.5" />}
                                  </button>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>

                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: ANALYTICS & METRICS */}
        {activeTab === "analytics" && (
          <div className="space-y-8" id="analytics-tab-content">
            {totalSubmissions === 0 ? (
              <div className="bg-[#F9F8F6] rounded-2xl py-16 text-center border border-[#E6E3DB] text-[#8B8C7A] text-sm">
                Ни одного ответа в базе не найдено. Заполните анкету во вкладке «Бот-Опросник» для появления демонстрационных метрик.
              </div>
            ) : (
              <div className="space-y-8 font-sans text-xs">
                
                {/* Distribution Overview */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  
                  {/* Feelings Chart */}
                  <div className="bg-[#F9F8F6] p-6 rounded-2xl border border-[#E6E3DB] space-y-4">
                    <div>
                      <h4 className="font-serif text-base text-[#3D3B36] font-medium italic">Ментальная карта состояний</h4>
                      <p className="text-[10px] text-[#8B8C7A]">Преобладающие чувства вашей аудитории</p>
                    </div>

                    <div className="space-y-4 pt-2">
                      {feelings.map((f, idx) => {
                        const count = feelingCounts[f.text] || 0;
                        const percentage = getPercentage(count);
                        return (
                          <div key={idx} className="space-y-1">
                            <div className="flex justify-between font-semibold">
                              <span className="text-[#3D3B36] truncate max-w-[75%]" title={f.text}>{f.text}</span>
                              <span className="font-mono text-[#8B8C7A]">{count} ({percentage}%)</span>
                            </div>
                            <div className="w-full h-2.5 bg-white border border-[#E6E3DB] rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-[#8B8C7A]" 
                                style={{ width: `${percentage}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Needs Chart */}
                  <div className="bg-[#F9F8F6] p-6 rounded-2xl border border-[#E6E3DB] space-y-4">
                    <div>
                      <h4 className="font-serif text-base text-[#3D3B36] font-medium italic">Векторы необходимых ресурсов</h4>
                      <p className="text-[10px] text-[#8B8C7A]">Что больше всего помогло бы людям сейчас почувствовать опору</p>
                    </div>

                    <div className="space-y-4 pt-2">
                      {steadyOptions.map((opt, idx) => {
                        const count = steadyCounts[opt] || 0;
                        const percentage = getPercentage(count);
                        return (
                          <div key={idx} className="space-y-1">
                            <div className="flex justify-between font-semibold">
                              <span className="text-[#3D3B36] truncate max-w-[75%]" title={opt}>{opt}</span>
                              <span className="font-mono text-[#8B8C7A]">{count} ({percentage}%)</span>
                            </div>
                            <div className="w-full h-2.5 bg-white border border-[#E6E3DB] rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-[#5A5A40]" 
                                style={{ width: `${percentage}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                </div>

                {/* Slogan and Conversion Summary */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  
                  {/* Practices preferences */}
                  <div className="bg-[#F9F8F6] p-6 rounded-2xl border border-[#E6E3DB] space-y-4">
                    <div>
                      <h4 className="font-serif text-base text-[#3D3B36] font-medium italic">Желаемые форматы бесплатных практик</h4>
                      <p className="text-[10px] text-[#8B8C7A]">Что наиболее актуально давать в подарок за прохождение</p>
                    </div>

                    <div className="space-y-4 pt-2">
                      {formatOptions.map((opt, idx) => {
                        const count = formatCounts[opt] || 0;
                        const percentage = getPercentage(count);
                        return (
                          <div key={idx} className="space-y-1">
                            <div className="flex justify-between font-semibold">
                              <span className="text-[#3D3B36] truncate max-w-[75%]" title={opt}>{opt}</span>
                              <span className="font-mono text-[#8B8C7A]">{count} ({percentage}%)</span>
                            </div>
                            <div className="w-full h-2.5 bg-white border border-[#E6E3DB] rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-[#8B8C7A]" 
                                style={{ width: `${percentage}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Summary Conclusion Panel */}
                  <div className="bg-[#8B8C7A]/10 p-6 rounded-2xl border border-[#8B8C7A]/30 flex flex-col justify-between">
                    <div className="space-y-3 font-serif">
                      <span className="font-sans font-bold text-[9px] bg-white border border-[#8B8C7A]/30 text-[#5A5A40] px-3 py-1 rounded-full uppercase tracking-wider inline-block">Заключение Продюсера</span>
                      <h3 className="text-xl text-[#3D3B36] font-light italic">«Универсальная бережная воронка»</h3>
                      <p className="text-xs sm:text-sm font-sans text-[#3D3B36]/80 leading-relaxed">
                        Люди находятся в глубоком психологическом дефиците сил. Из-за отсутствия топлива и новостной атаки высокая ценность смещается на домашние практики (5-10 минут).
                      </p>
                      <p className="text-xs font-sans text-[#3D3B36] font-bold">
                        Конверсия в отправку контактов для получения подарков (Заявка): {getPercentage(totalSubscribed)}% ваших клиентов. Это превосходный показатель доверия аудитории.
                      </p>
                    </div>

                    <div className="border-t border-[#8B8C7A]/20 pt-4 mt-6 flex items-center gap-3">
                      <div className="p-2 rounded-full bg-white text-[#8B8C7A] border border-[#E6E3DB]">
                        <Heart className="w-5 h-5 fill-[#8B8C7A]/20" />
                      </div>
                      <span className="text-[11px] font-sans text-[#5A5A40] font-semibold leading-snug">
                        Это безупречный базис для построения экосистемы «Практика там, где ты».
                      </span>
                    </div>
                  </div>

                </div>

              </div>
            )}
          </div>
        )}

        {/* TAB 3: NEURAL AI-ANALYSIS (GEMINI) */}
        {activeTab === "ai" && (
          <div className="space-y-6" id="ai-tab-content">
            <div className="bg-[#F9F8F6] p-6 rounded-2xl border border-[#E6E3DB] space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h3 className="font-serif text-xl text-[#3D3B36] font-light flex items-center gap-2">
                    <Brain className="w-5 h-5 text-[#8B8C7A]" />
                    <span>ИИ-Анализатор Клиентской Боли</span>
                  </h3>
                  <p className="text-xs font-sans text-[#8B8C7A] mt-1">
                    Запустите Gemini AI для глубокой обработки всех откровений ваших клиентов и построения структуры бесплатного курса.
                  </p>
                </div>
                
                <button
                  id="btn-run-ai-analysis"
                  disabled={aiLoading || totalSubmissions === 0}
                  onClick={handleRunAI}
                  className="bg-[#8B8C7A] hover:bg-[#5A5A40] text-white font-sans text-xs uppercase tracking-widest font-semibold py-3 px-6 rounded-full transition-all cursor-pointer shadow-sm flex items-center gap-1.5 disabled:opacity-40"
                >
                  {aiLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4" />
                  )}
                  <span>Запустить ИИ-Анализ</span>
                </button>
              </div>

              {totalSubmissions === 0 && (
                <div className="flex items-center gap-2 text-amber-700 text-xs bg-amber-50 p-3.5 rounded-xl border border-amber-200 font-sans leading-relaxed">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>В базе нет ответов. Загрузите демо-данные кнопкой сверху, чтобы протестировать искусственный интеллект!</span>
                </div>
              )}
            </div>

            {aiLoading && (
              <div className="bg-[#F9F8F6] rounded-2xl p-16 text-center border border-[#E6E3DB] flex flex-col items-center justify-center space-y-4">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-[#8B8C7A]/20 border-t-[#8B8C7A] rounded-full animate-spin" />
                  <Brain className="w-6 h-6 text-[#8B8C7A] absolute inset-0 m-auto animate-pulse" />
                </div>
                <div className="space-y-1 font-sans">
                  <p className="text-sm font-semibold text-[#3D3B36] animate-pulse">ИИ (Gemini) читает откровения людей...</p>
                  <p className="text-xs text-[#8B8C7A]">Это «золото для нейросети» — извлекаем эмоциональные боли, зажимы и речевые маркеры</p>
                </div>
              </div>
            )}

            {aiError && (
              <div className="flex items-start gap-2.5 text-amber-800 text-xs bg-amber-50 p-4.5 rounded-2xl border border-amber-200 leading-relaxed font-sans">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{aiError}</span>
              </div>
            )}

            {/* AI Results */}
            <AnimatePresence mode="wait">
              {aiResult && !aiLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="grid grid-cols-1 md:grid-cols-3 gap-6 font-sans text-xs"
                >
                  {/* Left Column: Pain maps & Keywords */}
                  <div className="space-y-6">
                    {/* Emotion Map */}
                    <div className="bg-[#F9F8F6] p-5 rounded-2xl border border-[#E6E3DB] space-y-3">
                      <h4 className="font-serif text-sm text-[#3D3B36] font-semibold flex items-center gap-1.5 border-b border-[#E6E3DB] pb-2 italic">
                        <Heart className="w-4 h-4 text-rose-600" />
                        <span>Карта эмоций клиентов</span>
                      </h4>
                      <ul className="space-y-2">
                        {aiResult.emotionMap.map((emo, i) => (
                          <li key={i} className="text-xs text-[#3D3B36]/80 flex items-start gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#8B8C7A] mt-1.5 shrink-0" />
                            <span>{emo}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Body Tension Map */}
                    <div className="bg-[#F9F8F6] p-5 rounded-2xl border border-[#E6E3DB] space-y-3">
                      <h4 className="font-serif text-sm text-[#3D3B36] font-semibold flex items-center gap-1.5 border-b border-[#E6E3DB] pb-2 italic">
                        <Flame className="w-4 h-4 text-amber-600" />
                        <span>Карта телесного стресса</span>
                      </h4>
                      <ul className="space-y-2">
                        {aiResult.bodyTensionMap.map((bt, i) => (
                          <li key={i} className="text-xs text-[#3D3B36]/80 flex items-start gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#5A5A40] mt-1.5 shrink-0" />
                            <span>{bt}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Copywriting keywords */}
                    <div className="bg-[#F9F8F6] p-5 rounded-2xl border border-[#E6E3DB] space-y-3">
                      <h4 className="font-serif text-sm text-[#3D3B36] font-semibold flex items-center gap-1.5 border-b border-[#E6E3DB] pb-2 italic">
                        <Sparkles className="w-4 h-4 text-purple-600" />
                        <span>Речевое золото клиентов</span>
                      </h4>
                      <p className="text-[10px] text-[#8B8C7A]">
                        Используйте эти точные слова при написании Stories и писем для максимального отклика в душе:
                      </p>
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {aiResult.copywritingKeywords.map((word, i) => (
                          <button
                            key={i}
                            onClick={() => copyToClipboard(word, `kw-${i}`)}
                            className="text-[10px] font-mono bg-white hover:bg-[#8B8C7A]/10 text-[#3D3B36] border border-[#E6E3DB] rounded-lg px-2.5 py-1.5 flex items-center gap-1 transition-colors cursor-pointer"
                            title="Нажмите, чтобы скопировать"
                          >
                            <span>{word}</span>
                            {copiedText === `kw-${i}` ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3 h-3 text-[#8B8C7A]" />}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Right Column (2 spans wide): Recommended Program Outline */}
                  <div className="md:col-span-2 space-y-6">
                    <div className="bg-[#F9F8F6] p-6 rounded-2xl border border-[#E6E3DB] space-y-4">
                      <div className="border-b border-[#E6E3DB] pb-3 flex justify-between items-center flex-wrap gap-2">
                        <div>
                          <span className="text-[9px] font-bold text-[#8B8C7A] uppercase tracking-wider font-mono">Программа на основе болей людей</span>
                          <h4 className="font-serif text-xl text-[#3D3B36] font-light italic mt-0.5">
                            {aiResult.recommendedProgram.title}
                          </h4>
                        </div>
                        <span className="bg-[#8B8C7A] text-white font-sans text-[9px] font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                          ИИ-Архитектор
                        </span>
                      </div>

                      <p className="text-xs sm:text-sm text-[#3D3B36]/80 leading-relaxed italic bg-white p-4 rounded-xl border border-[#E6E3DB]">
                        {aiResult.recommendedProgram.description}
                      </p>

                      <div className="space-y-4 pt-2">
                        <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Рекомендованный Day-by-Day План курса:</span>
                        
                        {aiResult.recommendedProgram.steps.map((step, idx) => (
                          <div key={idx} className="bg-white rounded-xl p-4 border border-[#E6E3DB] hover:border-[#8B8C7A]/40 transition-colors">
                            <div className="flex justify-between items-center gap-2 mb-1.5 flex-wrap">
                              <div className="flex items-center gap-2">
                                <span className="font-mono text-[10px] font-bold bg-[#8B8C7A] text-white px-2.5 py-0.5 rounded">
                                  {step.day}
                                </span>
                                <h5 className="font-serif text-xs sm:text-sm font-bold text-[#3D3B36]">
                                  {step.title}
                                </h5>
                              </div>
                              <span className="text-[10px] font-mono text-[#8B8C7A] flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                <span>{step.duration}</span>
                              </span>
                            </div>
                            <p className="text-xs text-[#3D3B36]/80 leading-relaxed pt-1.5 pl-2.5 border-l-2 border-[#8B8C7A]">
                              {step.practice}
                            </p>
                          </div>
                        ))}
                      </div>

                      <div className="pt-4 border-t border-[#E6E3DB] flex flex-wrap gap-2 justify-between items-center font-sans">
                        <span className="text-[10px] text-[#8B8C7A]">
                          Используйте эти формулировки для наполнения постов KISELEVY_CREO!
                        </span>
                        <button
                          onClick={() => copyToClipboard(JSON.stringify(aiResult.recommendedProgram, null, 2), "recommended-program")}
                          className="text-xs text-[#8B8C7A] hover:text-[#3D3B36] font-semibold flex items-center gap-1.5 cursor-pointer uppercase tracking-wider"
                        >
                          {copiedText === "recommended-program" ? (
                            <>
                              <Check className="w-3.5 h-3.5 text-emerald-600" />
                              <span className="text-emerald-600">Скопировано!</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3.5 h-3.5" />
                              <span>Скопировать JSON структуру</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* TAB 4: PRODUCER HUB MATERIALS */}
        {activeTab === "materials" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8" id="materials-tab-content">
            {/* Stories Specs */}
            <div className="bg-[#F9F8F6] p-6 rounded-2xl border border-[#E6E3DB] flex flex-col justify-between">
              <div className="space-y-4">
                <div className="border-b border-[#E6E3DB] pb-3 flex justify-between items-center">
                  <div>
                    <h3 className="font-serif text-lg text-[#3D3B36] font-light flex items-center gap-1.5 italic">
                      <Clipboard className="w-4 h-4 text-[#8B8C7A]" />
                      <span>Сценарий Stories «Тихий разговор»</span>
                    </h3>
                    <p className="text-[10px] font-sans text-[#8B8C7A]">Пошаговый прогрев аудитории и выявление болей</p>
                  </div>
                </div>

                <div className="bg-white p-4 rounded-xl border border-[#E6E3DB] max-h-[400px] overflow-y-auto">
                  <pre className="text-[10px] font-mono text-[#3D3B36] leading-relaxed whitespace-pre-wrap">
                    {storiesTemplate}
                  </pre>
                </div>
              </div>

              <div className="pt-4 border-t border-[#E6E3DB] flex justify-end">
                <button
                  onClick={() => copyToClipboard(storiesTemplate, "stories-template")}
                  className="bg-[#8B8C7A] hover:bg-[#5A5A40] text-white font-sans text-[10px] uppercase tracking-widest font-semibold py-2.5 px-5 rounded-full transition-colors cursor-pointer shadow-sm flex items-center gap-1.5"
                >
                  {copiedText === "stories-template" ? (
                    <>
                      <Check className="w-3.5 h-3.5" />
                      <span>Скопировано!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Скопировать сценарий</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Broadcast Chat Message */}
            <div className="bg-[#F9F8F6] p-6 rounded-2xl border border-[#E6E3DB] flex flex-col justify-between">
              <div className="space-y-4">
                <div className="border-b border-[#E6E3DB] pb-3 flex justify-between items-center">
                  <div>
                    <h3 className="font-serif text-lg text-[#3D3B36] font-light flex items-center gap-1.5 italic">
                      <Clipboard className="w-4 h-4 text-[#5A5A40]" />
                      <span>Пост для Telegram / Чат-Рассылки</span>
                    </h3>
                    <p className="text-[10px] font-sans text-[#8B8C7A]">Заботливое письмо-призыв к прохождению</p>
                  </div>
                </div>

                <div className="bg-white p-4 rounded-xl border border-[#E6E3DB] max-h-[400px] overflow-y-auto">
                  <pre className="text-[10px] font-mono text-[#3D3B36] leading-relaxed whitespace-pre-wrap">
                    {broadcastTemplate}
                  </pre>
                </div>
              </div>

              <div className="pt-4 border-t border-[#E6E3DB] flex justify-end">
                <button
                  onClick={() => copyToClipboard(broadcastTemplate, "broadcast-template")}
                  className="bg-[#5A5A40] hover:bg-[#3D3B36] text-white font-sans text-[10px] uppercase tracking-widest font-semibold py-2.5 px-5 rounded-full transition-colors cursor-pointer shadow-sm flex items-center gap-1.5"
                >
                  {copiedText === "broadcast-template" ? (
                    <>
                      <Check className="w-3.5 h-3.5" />
                      <span>Скопировано!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Скопировать письмо</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: QUESTIONNAIRE & BROADCAST HUB */}
        {activeTab === "questionnaires" && (
          <div className="space-y-8" id="questionnaires-tab-content">
            {/* Header info */}
            <div className="bg-[#8B8C7A]/5 border border-[#8B8C7A]/20 rounded-3xl p-6 sm:p-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div className="space-y-2">
                <h3 className="font-serif text-xl text-[#3D3B36] font-medium italic flex items-center gap-2">
                  <Radio className="w-5 h-5 text-purple-600 animate-pulse" />
                  <span>Управление опросниками и Рассылки в Канал</span>
                </h3>
                <p className="text-xs text-[#5A5A40] max-w-2xl leading-relaxed font-sans">
                  Здесь вы можете генерировать новые опросники с помощью ИИ Gemini или создавать их вручную. После генерации вы можете запустить опросник в работу или нажать кнопку вещания, чтобы бот автоматически разослал его по подписчикам в канал.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
              {/* Left Column: Generator & Editor (5 cols) */}
              <div className="xl:col-span-5 space-y-6">
                {/* AI Generator Panel */}
                <div className="bg-white border border-[#E6E3DB] rounded-3xl p-6 space-y-4 shadow-sm">
                  <div className="border-b border-[#E6E3DB] pb-3">
                    <h4 className="font-serif text-md font-bold text-[#3D3B36] flex items-center gap-2">
                      <Brain className="w-4 h-4 text-purple-600" />
                      <span>ИИ-Генератор Опросников</span>
                    </h4>
                    <p className="text-[10px] font-sans text-[#8B8C7A] mt-0.5">Gemini придумает бережные формулировки по любой теме</p>
                  </div>

                  <form onSubmit={handleGenerateQuestionnaire} className="space-y-3 font-sans">
                    <div>
                      <label className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block mb-1">Задайте тему опроса:</label>
                      <input
                        type="text"
                        value={topicInput}
                        onChange={(e) => setTopicInput(e.target.value)}
                        placeholder="Например: Утренняя энергия, Крепкий сон, Снятие зажимов в шее..."
                        className="w-full px-4 py-3 text-xs rounded-xl border border-[#E6E3DB] bg-[#F9F8F6] text-[#3D3B36] focus:outline-none focus:border-[#8B8C7A] placeholder-[#8B8C7A]/60"
                        disabled={isGeneratingQ}
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={isGeneratingQ || !topicInput.trim()}
                      className={`w-full font-semibold text-[10px] uppercase tracking-widest py-3 px-4 rounded-full transition-all cursor-pointer shadow-sm flex items-center justify-center gap-2 ${
                        isGeneratingQ || !topicInput.trim()
                          ? "bg-gray-100 border border-gray-200 text-gray-400 cursor-not-allowed"
                          : "bg-purple-600 hover:bg-purple-700 text-white"
                      }`}
                    >
                      {isGeneratingQ ? (
                        <>
                          <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          <span>Генерирую с помощью ИИ...</span>
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>Сгенерировать опросник</span>
                        </>
                      )}
                    </button>
                  </form>
                </div>

                {/* Questionnaire Preview / Editor */}
                {editingQ && (
                  <motion.div
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-purple-50/40 border border-purple-200/60 rounded-3xl p-6 space-y-4 shadow-sm"
                  >
                    <div className="flex justify-between items-center border-b border-purple-100 pb-2.5">
                      <span className="text-[9px] font-bold text-purple-700 uppercase tracking-wider font-sans bg-purple-100 px-2.5 py-1 rounded-full flex items-center gap-1">
                        <Sparkles className="w-3 h-3 text-purple-600" />
                        <span>Сгенерированный опросник</span>
                      </span>
                      <button
                        onClick={() => setEditingQ(null)}
                        className="text-purple-400 hover:text-purple-700 transition-colors p-1 rounded-full hover:bg-purple-100"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Editor Fields */}
                    <div className="space-y-3 font-sans">
                      <div>
                        <label className="text-[9px] font-bold text-[#8B8C7A] uppercase tracking-wider block mb-1">Название:</label>
                        <input
                          type="text"
                          value={qTitle}
                          onChange={(e) => setQTitle(e.target.value)}
                          className="w-full px-3 py-2 text-xs rounded-lg border border-purple-200 bg-white text-[#3D3B36] focus:outline-none focus:border-purple-500 font-serif font-bold"
                        />
                      </div>

                      <div>
                        <label className="text-[9px] font-bold text-[#8B8C7A] uppercase tracking-wider block mb-1">Теплый посыл / Описание:</label>
                        <textarea
                          value={qDesc}
                          onChange={(e) => setQDesc(e.target.value)}
                          rows={2}
                          className="w-full px-3 py-2 text-xs rounded-lg border border-purple-200 bg-white text-[#3D3B36] focus:outline-none focus:border-purple-500 leading-relaxed"
                        />
                      </div>

                      {/* Questions List */}
                      <div className="space-y-3 pt-2">
                        <span className="text-[9px] font-bold text-[#8B8C7A] uppercase tracking-wider block border-b border-purple-100 pb-1">Список вопросов:</span>
                        {qQuestions.map((q, qidx) => (
                          <div key={q.id} className="bg-white p-3 rounded-xl border border-purple-100 text-xs space-y-2">
                            <div className="flex justify-between items-center">
                              <span className="font-bold text-purple-700 text-[10px]">Вопрос {qidx + 1} ({q.type === 'single' ? 'Один выбор' : q.type === 'multiple' ? 'Несколько' : 'Текст'}):</span>
                            </div>
                            <input
                              type="text"
                              value={q.title}
                              onChange={(e) => {
                                const copy = [...qQuestions];
                                copy[qidx].title = e.target.value;
                                setQQuestions(copy);
                              }}
                              placeholder="Текст вопроса"
                              className="w-full px-2 py-1 bg-purple-50/30 rounded border border-purple-100 focus:outline-none"
                            />
                            {q.options && (
                              <div className="space-y-1.5 pl-2.5 border-l border-purple-100">
                                {q.options.map((opt: string, oidx: number) => (
                                  <input
                                    key={oidx}
                                    type="text"
                                    value={opt}
                                    onChange={(e) => {
                                      const copy = [...qQuestions];
                                      copy[qidx].options[oidx] = e.target.value;
                                      setQQuestions(copy);
                                    }}
                                    placeholder={`Вариант ${oidx + 1}`}
                                    className="w-full px-2 py-0.5 text-[11px] border border-gray-100 rounded focus:outline-none"
                                  />
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="pt-3 border-t border-purple-100 flex gap-2 font-sans">
                      <button
                        onClick={handleSaveQuestionnaire}
                        className="flex-1 bg-[#8B8C7A] hover:bg-[#5A5A40] text-white font-semibold text-[10px] uppercase tracking-wider py-2.5 px-4 rounded-full transition-colors cursor-pointer text-center"
                      >
                        Сохранить в базу
                      </button>
                    </div>
                  </motion.div>
                )}
              </div>

              {/* Right Column: Registries & Broadcasts (7 cols) */}
              <div className="xl:col-span-7 space-y-8">
                {/* Questionnaires List */}
                <div className="bg-[#F9F8F6] border border-[#E6E3DB] rounded-3xl p-6 space-y-4">
                  <div className="border-b border-[#E6E3DB] pb-3 flex justify-between items-center">
                    <div>
                      <h4 className="font-serif text-md font-bold text-[#3D3B36] flex items-center gap-1.5 italic">
                        <Users className="w-4 h-4 text-[#8B8C7A]" />
                        <span>Реестр опросников заботы</span>
                      </h4>
                      <p className="text-[10px] font-sans text-[#8B8C7A]">Доступные опросники. Только ОДИН может быть активен.</p>
                    </div>
                  </div>

                  <div className="space-y-4 max-h-[480px] overflow-y-auto pr-1">
                    {questionnaires.map((q) => (
                      <div
                        key={q.id}
                        className={`p-5 rounded-2xl border transition-all relative flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white ${
                          q.isActive
                            ? "border-purple-400 ring-2 ring-purple-100"
                            : "border-[#E6E3DB] hover:border-[#8B8C7A]/50"
                        }`}
                      >
                        <div className="space-y-2 max-w-md">
                          <div className="flex items-center gap-2 flex-wrap">
                            <h5 className="font-serif text-sm font-bold text-[#3D3B36]">{q.title}</h5>
                            {q.isActive && (
                              <span className="font-sans text-[8px] font-bold bg-purple-100 text-purple-700 border border-purple-200 px-2 py-0.5 rounded-full uppercase tracking-wider animate-pulse flex items-center gap-1">
                                <span className="w-1 h-1 rounded-full bg-purple-600" />
                                Активен в приложении
                              </span>
                            )}
                            {q.isDefault && (
                              <span className="font-sans text-[8px] font-bold bg-gray-100 text-gray-500 border border-gray-200 px-2 py-0.5 rounded-full uppercase tracking-wider">
                                Базовый
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] font-sans text-[#8B8C7A] leading-relaxed">{q.description}</p>
                          <div className="flex gap-2 text-[10px] text-[#5A5A40] font-sans">
                            <span className="bg-[#8B8C7A]/10 px-2 py-0.5 rounded-md border border-[#8B8C7A]/20">Вопросов: {q.questions.length}</span>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-1.5 self-end sm:self-center font-sans">
                          {!q.isActive && (
                            <button
                              onClick={() => handleActivateQuestionnaire(q.id)}
                              className="px-3 py-1.5 border border-[#8B8C7A]/30 text-[#8B8C7A] hover:bg-[#8B8C7A]/5 text-[10px] font-semibold rounded-lg transition-colors cursor-pointer"
                              title="Сделать активным для прохождения"
                            >
                              Включить
                            </button>
                          )}
                          <button
                            onClick={() => handleBroadcastQuestionnaire(q.id)}
                            className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-[10px] font-semibold rounded-lg transition-colors cursor-pointer flex items-center gap-1"
                            title="Разослать в телеграм-канал подписчикам"
                          >
                            <Send className="w-3 h-3" />
                            <span>Разослать</span>
                          </button>
                          {!q.isDefault && (
                            <button
                              onClick={() => handleDeleteQuestionnaire(q.id)}
                              className="p-1.5 border border-rose-200 hover:bg-rose-50 text-rose-600 rounded-lg transition-colors cursor-pointer"
                              title="Удалить опросник"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Broadcast Logs */}
                <div className="bg-[#F5F3EE] border border-[#E6E3DB] rounded-3xl p-6 space-y-4">
                  <div className="border-b border-[#E6E3DB] pb-3 flex justify-between items-center">
                    <div>
                      <h4 className="font-serif text-md font-bold text-[#3D3B36] flex items-center gap-1.5 italic">
                        <Calendar className="w-4 h-4 text-[#8B8C7A]" />
                        <span>История рассылок по подписчикам</span>
                      </h4>
                      <p className="text-[10px] font-sans text-[#8B8C7A]">Журнал активности телеграм-бота вещания</p>
                    </div>
                    {broadcasts.length > 0 && (
                      <button
                        onClick={handleClearBroadcasts}
                        className="text-rose-600 hover:text-rose-800 font-sans text-[9px] font-bold uppercase tracking-wider flex items-center gap-1 cursor-pointer"
                      >
                        <Trash2 className="w-3 h-3" />
                        <span>Очистить журнал</span>
                      </button>
                    )}
                  </div>

                  {broadcasts.length === 0 ? (
                    <div className="bg-white py-10 rounded-2xl text-center border border-[#E6E3DB] text-[#8B8C7A] text-[11px] font-sans italic">
                      Рассылок еще не производилось. Нажмите «Разослать» выше, чтобы отправить опросник в канал.
                    </div>
                  ) : (
                    <div className="space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
                      {broadcasts.map((bc) => (
                        <div key={bc.id} className="bg-white p-3.5 rounded-xl border border-[#E6E3DB] flex justify-between items-center gap-4 text-xs font-sans">
                          <div className="space-y-1">
                            <p className="font-bold text-[#3D3B36]">{bc.questionnaireTitle}</p>
                            <p className="text-[10px] text-[#8B8C7A]">
                              {new Date(bc.timestamp).toLocaleString("ru-RU")} • Охвачено подписчиков: <span className="font-semibold text-purple-700">{bc.recipientsCount} чел.</span>
                            </p>
                          </div>
                          <span className="bg-emerald-50 border border-emerald-200 text-emerald-700 px-2.5 py-1 rounded-full text-[9px] font-bold uppercase tracking-wider shrink-0 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            {bc.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 6: PROFILE SETTINGS */}
        {activeTab === "profile" && (
          <div className="space-y-8 animate-fadeIn" id="profile-tab-content">
            <div className="bg-[#F9F8F6] border border-[#E6E3DB] rounded-3xl p-6 sm:p-8">
              <div className="border-b border-[#E6E3DB] pb-4 mb-6">
                <h3 className="font-serif text-xl font-bold text-[#3D3B36] flex items-center gap-2">
                  <Smile className="w-5 h-5 text-[#8B8C7A]" />
                  <span>Профиль и Аватар команды KISELEVY_CREO</span>
                </h3>
                <p className="text-xs font-sans text-[#8B8C7A] mt-1">
                  Настройте вашу личную карточку, приветствие и загрузите свою фотографию для опросника клиентов.
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Form fields */}
                <div className="lg:col-span-7 space-y-5 font-sans">
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Имя основателя:</label>
                    <input
                      type="text"
                      value={profileName}
                      onChange={(e) => setProfileName(e.target.value)}
                      className="w-full px-4 py-2.5 text-xs rounded-xl border border-[#E6E3DB] bg-white text-[#3D3B36] focus:outline-none focus:border-[#8B8C7A] transition-colors"
                      placeholder="Например: Опрус-Крео"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Должность / Статус:</label>
                    <input
                      type="text"
                      value={profileRole}
                      onChange={(e) => setProfileRole(e.target.value)}
                      className="w-full px-4 py-2.5 text-xs rounded-xl border border-[#E6E3DB] bg-white text-[#3D3B36] focus:outline-none focus:border-[#8B8C7A] transition-colors"
                      placeholder="Например: Основатель Shanti"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Краткое описание (подзаголовок):</label>
                    <input
                      type="text"
                      value={profileSubtitle}
                      onChange={(e) => setProfileSubtitle(e.target.value)}
                      className="w-full px-4 py-2.5 text-xs rounded-xl border border-[#E6E3DB] bg-white text-[#3D3B36] focus:outline-none focus:border-[#8B8C7A] transition-colors"
                      placeholder="Сертифицированный преподаватель йоги..."
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Приветственное письмо (описание болей и целей):</label>
                    <textarea
                      value={profileWelcome}
                      onChange={(e) => setProfileWelcome(e.target.value)}
                      rows={5}
                      className="w-full px-4 py-2.5 text-xs rounded-xl border border-[#E6E3DB] bg-white text-[#3D3B36] focus:outline-none focus:border-[#8B8C7A] transition-colors leading-relaxed"
                      placeholder="Введите текст приветственного обращения..."
                    />
                  </div>

                  {/* Photo Uploader */}
                  <div className="space-y-2">
                    <label className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Ваша фотография (аватар):</label>
                    <div className="border-2 border-dashed border-[#E6E3DB] hover:border-[#8B8C7A]/50 transition-colors rounded-2xl p-6 bg-white flex flex-col items-center justify-center text-center gap-3 relative overflow-hidden group">
                      <div className="p-3 bg-[#F9F8F6] rounded-full text-[#8B8C7A] group-hover:scale-105 transition-transform">
                        <Leaf className="w-5 h-5 text-[#8B8C7A]" />
                      </div>
                      <div className="space-y-1">
                        <p className="text-xs font-bold text-[#3D3B36]">Перетащите фото или кликните для выбора</p>
                        <p className="text-[10px] text-[#8B8C7A]">Поддерживаются форматы JPG, PNG, WEBP</p>
                      </div>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) {
                            const reader = new FileReader();
                            reader.onload = (evt) => {
                              if (evt.target?.result) {
                                setProfileAvatar(evt.target.result as string);
                              }
                            };
                            reader.readAsDataURL(file);
                          }
                        }}
                        className="absolute inset-0 opacity-0 cursor-pointer"
                      />
                    </div>
                  </div>

                  <div className="pt-3 flex items-center gap-4">
                    <button
                      onClick={async () => {
                        setProfileSaving(true);
                        setProfileSaveSuccess(false);
                        try {
                          const res = await fetch("/api/profile", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                              name: profileName,
                              role: profileRole,
                              subtitle: profileSubtitle,
                              welcomeMessage: profileWelcome,
                              avatarUrl: profileAvatar
                            })
                          });
                          const data = await res.json();
                          if (data.success) {
                            setProfileSaveSuccess(true);
                            setTimeout(() => setProfileSaveSuccess(false), 3000);
                          }
                        } catch (err) {
                          console.error("Error saving profile:", err);
                        } finally {
                          setProfileSaving(false);
                        }
                      }}
                      disabled={profileSaving}
                      className="bg-[#8B8C7A] hover:bg-[#5A5A40] text-white font-semibold text-[10px] uppercase tracking-wider py-3 px-6 rounded-full transition-all cursor-pointer flex items-center gap-2 shadow-sm active:scale-98 disabled:opacity-55"
                    >
                      {profileSaving ? "Сохранение..." : "Сохранить профиль"}
                    </button>

                    {profileSaveSuccess && (
                      <motion.span
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="text-xs font-semibold text-emerald-600 flex items-center gap-1"
                      >
                        <Check className="w-4 h-4" /> Изменения сохранены!
                      </motion.span>
                    )}
                  </div>
                </div>

                {/* Right col: Live preview */}
                <div className="lg:col-span-5 flex flex-col justify-start space-y-4 font-sans">
                  <span className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Предпросмотр в опросниках заботы:</span>
                  
                  <div className="bg-white p-6 rounded-2xl border border-[#E6E3DB] shadow-xs relative overflow-hidden flex flex-col items-center sm:items-start text-center sm:text-left gap-5">
                    <div className="relative shrink-0 w-24 h-24 rounded-full border-2 border-[#8B8C7A]/30 p-1 bg-[#F9F8F6] overflow-hidden flex items-center justify-center">
                      {profileAvatar ? (
                        <img
                          src={profileAvatar}
                          alt={profileName}
                          className="w-full h-full object-cover rounded-full"
                          referrerPolicy="no-referrer"
                        />
                      ) : (
                        <div className="w-full h-full rounded-full bg-[#E6E3DB] flex items-center justify-center text-[#8B8C7A] font-bold text-lg font-serif">
                          {profileName.substring(0, 1)}
                        </div>
                      )}
                      <span className="absolute bottom-1 right-1 w-3.5 h-3.5 bg-emerald-500 rounded-full border-2 border-white animate-pulse" />
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center justify-center sm:justify-start gap-1.5 flex-wrap">
                        <h4 className="font-serif text-base text-[#3D3B36] font-bold">{profileName}</h4>
                        <span className="text-[8px] uppercase tracking-wider bg-emerald-500/10 text-emerald-700 px-2 py-0.5 rounded-full font-semibold">{profileRole}</span>
                      </div>
                      <p className="text-xs text-[#8B8C7A] leading-relaxed">
                        {profileSubtitle || "Описание не заполнено"}
                      </p>
                      <p className="text-[10px] text-gray-500 leading-relaxed max-w-sm pt-2 italic">
                        {profileWelcome || "Приветствие не заполнено"}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 7: 3-SYSTEMS MANAGEMENT (Telegram Channel, MAX Bot, Web App) */}
        {activeTab === "platforms" && (
          <div className="p-6 sm:p-12 space-y-8 animate-fadeIn" id="platforms-tab-content">
            <div className="bg-[#F9F8F6] border border-[#E6E3DB] rounded-3xl p-6 sm:p-8 space-y-6">
              <div className="border-b border-[#E6E3DB] pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <h3 className="font-serif text-xl font-bold text-[#3D3B36] flex items-center gap-2">
                    <Globe className="w-5 h-5 text-emerald-600" />
                    <span>Управление 3-мя Системами (Платформа KISELEVY_CREO)</span>
                  </h3>
                  <p className="text-xs font-sans text-[#8B8C7A] mt-1">
                    Единая интеграционная панель: Телеграм Канал, Бот в мессенджере MAX и Веб-приложение с 7-дневным демо-доступом.
                  </p>
                </div>
                <button
                  onClick={fetchPlatforms}
                  className="px-3 py-1.5 bg-white border border-[#E6E3DB] hover:bg-[#F5F3EE] text-xs text-[#3D3B36] rounded-xl font-sans font-semibold flex items-center gap-1.5 cursor-pointer shadow-xs"
                >
                  <RefreshCw className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Обновить статусы</span>
                </button>
              </div>

              {/* 3 Overview System Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 font-sans">
                {/* System 1: Telegram Channel */}
                <div className="bg-white p-6 rounded-2xl border-2 border-purple-200 shadow-sm relative overflow-hidden flex flex-col justify-between space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-bold text-purple-700 uppercase tracking-wider bg-purple-50 px-2.5 py-1 rounded-full border border-purple-200">
                        📢 Система 1: Telegram Канал
                      </span>
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" title="Активен" />
                    </div>
                    <h4 className="font-serif text-lg font-bold text-[#3D3B36]">Телеграм Канал</h4>
                    <p className="text-xs text-[#8B8C7A] leading-relaxed">
                      Канал для публикации постов, авто-воронки, анонсов новых опросников и утренних настроек.
                    </p>
                  </div>
                  <div className="pt-3 border-t border-[#E6E3DB] space-y-1 text-xs">
                    <p className="font-mono text-[#3D3B36]">Канал: <strong className="text-purple-700">@kiselevy_creo</strong></p>
                    <p className="text-[11px] text-[#8B8C7A]">Автовещание: <strong>Включено</strong></p>
                  </div>
                </div>

                {/* System 2: MAX Bot */}
                <div className="bg-white p-6 rounded-2xl border-2 border-blue-200 shadow-sm relative overflow-hidden flex flex-col justify-between space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-bold text-blue-700 uppercase tracking-wider bg-blue-50 px-2.5 py-1 rounded-full border border-blue-200">
                        🤖 Система 2: MAX Бот
                      </span>
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" title="Интегрирован" />
                    </div>
                    <h4 className="font-serif text-lg font-bold text-[#3D3B36]">Мессенджер MAX</h4>
                    <p className="text-xs text-[#8B8C7A] leading-relaxed">
                      Подключенный нейро-коуч Опрус для работы с пользователями мессенджера MAX в режиме 24/7.
                    </p>
                  </div>
                  <div className="pt-3 border-t border-[#E6E3DB] space-y-1 text-xs">
                    <p className="font-mono text-[#3D3B36] truncate">Webhook: <strong>/api/max/webhook</strong></p>
                    <p className="text-[11px] text-[#8B8C7A]">ИИ-Двигатель: <strong>50 лет стажа (Gemini)</strong></p>
                  </div>
                </div>

                {/* System 3: Web Application */}
                <div className="bg-white p-6 rounded-2xl border-2 border-emerald-200 shadow-sm relative overflow-hidden flex flex-col justify-between space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                        💻 Система 3: Веб-приложение
                      </span>
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" title="Активно" />
                    </div>
                    <h4 className="font-serif text-lg font-bold text-[#3D3B36]">Web App & TMA</h4>
                    <p className="text-xs text-[#8B8C7A] leading-relaxed">
                      Полноценное веб-приложение, Telegram Mini App симулятор и 7-дневный персональный кабинет.
                    </p>
                  </div>
                  <div className="pt-3 border-t border-[#E6E3DB] space-y-1 text-xs">
                    <p className="font-mono text-[#3D3B36]">Режим: <strong>Web & Mini App</strong></p>
                    <p className="text-[11px] text-[#8B8C7A]">Демо-период: <strong>7 дней бесплатно</strong></p>
                  </div>
                </div>
              </div>

              {/* Interactive Controllers for Platform 1 & 2 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-4 font-sans">
                {/* Controller 1: Post to Telegram Channel */}
                <div className="bg-white p-6 rounded-2xl border border-[#E6E3DB] space-y-4">
                  <div className="border-b border-[#E6E3DB] pb-3 flex justify-between items-center">
                    <h4 className="font-serif text-base font-bold text-[#3D3B36] flex items-center gap-2">
                      <Send className="w-4 h-4 text-purple-600" />
                      <span>Публикация постов в Телеграм Канал</span>
                    </h4>
                    <span className="text-[10px] font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded-full font-mono">@kiselevy_creo</span>
                  </div>

                  <div className="space-y-3">
                    <label className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block">Текст сообщения (поддерживает HTML):</label>
                    <textarea
                      rows={5}
                      value={channelPostText}
                      onChange={(e) => setChannelPostText(e.target.value)}
                      className="w-full p-3.5 text-xs rounded-xl border border-[#E6E3DB] bg-[#F9F8F6] text-[#3D3B36] font-sans focus:outline-none focus:border-purple-500 leading-relaxed"
                      placeholder="Напишите текст поста для канала..."
                    />

                    <div className="flex items-center justify-between">
                      <label className="flex items-center gap-2 text-xs text-[#3D3B36] cursor-pointer">
                        <input
                          type="checkbox"
                          checked={channelPostWebAppBtn}
                          onChange={(e) => setChannelPostWebAppBtn(e.target.checked)}
                          className="rounded border-[#E6E3DB] text-purple-600 focus:ring-purple-500 w-4 h-4 cursor-pointer"
                        />
                        <span>Прикрепить кнопку «Открыть Web App»</span>
                      </label>

                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => setChannelPostText("🌅 <b>УТРЕННЯЯ НАСТРОЙКА KISELEVY_CREO</b>\n\nС добрым утром! Запустите 3-минутную утреннюю рефлексию в вашем кабинете, чтобы расставить приоритеты на день без лишнего стресса.\n\n👇 Нажмите кнопку ниже:")}
                          className="px-2.5 py-1 bg-[#F5F3EE] hover:bg-[#E6E3DB] text-[10px] font-bold text-[#3D3B36] rounded-lg cursor-pointer"
                        >
                          Шаблон «Утро»
                        </button>
                        <button
                          type="button"
                          onClick={() => setChannelPostText("⚡️ <b>НОВЫЙ ЦИФРОВОЙ ОПРОСНИК ОПРУС</b>\n\nМы подготовили новый диагностический тест для руководителей и экспертов. Пройдите за 2 минуты!\n\n👇 Открыть опросник:")}
                          className="px-2.5 py-1 bg-[#F5F3EE] hover:bg-[#E6E3DB] text-[10px] font-bold text-[#3D3B36] rounded-lg cursor-pointer"
                        >
                          Шаблон «Опрос»
                        </button>
                      </div>
                    </div>

                    <button
                      onClick={async () => {
                        setChannelPostSending(true);
                        setChannelPostStatus(null);
                        try {
                          const res = await fetch("/api/telegram/channel-post", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                              messageText: channelPostText,
                              includeWebAppButton: channelPostWebAppBtn
                            })
                          });
                          const data = await res.json();
                          if (data.success) {
                            setChannelPostStatus("Успешно опубликовано в Телеграм Канал!");
                          } else {
                            setChannelPostStatus("Ошибка публикации: " + (data.error || "Неизвестная ошибка"));
                          }
                        } catch (err: any) {
                          setChannelPostStatus("Ошибка сети: " + err.message);
                        } finally {
                          setChannelPostSending(false);
                        }
                      }}
                      disabled={channelPostSending}
                      className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                    >
                      <Send className="w-4 h-4" />
                      <span>{channelPostSending ? "Отправка в канал..." : "Опубликовать в Телеграм Канал"}</span>
                    </button>

                    {channelPostStatus && (
                      <p className={`text-xs font-semibold text-center mt-2 ${channelPostStatus.includes("Ошибка") ? "text-rose-600" : "text-emerald-600"}`}>
                        {channelPostStatus}
                      </p>
                    )}
                  </div>
                </div>

                {/* Controller 2: MAX Bot Messenger Integration */}
                <div className="bg-white p-6 rounded-2xl border border-[#E6E3DB] space-y-4">
                  <div className="border-b border-[#E6E3DB] pb-3 flex justify-between items-center">
                    <h4 className="font-serif text-base font-bold text-[#3D3B36] flex items-center gap-2">
                      <Bot className="w-4 h-4 text-blue-600" />
                      <span>Тестирование & Интеграция MAX Бот</span>
                    </h4>
                    <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full font-mono">Webhook Active</span>
                  </div>

                  <div className="space-y-3">
                    <div className="bg-[#F5F3EE] p-3 rounded-xl border border-[#E6E3DB] space-y-1.5 text-xs">
                      <p className="font-bold text-[#3D3B36]">URL для подключения в настройках бота MAX:</p>
                      <div className="flex items-center justify-between bg-white p-2 rounded-lg border border-[#E6E3DB]">
                        <code className="text-[10px] text-blue-700 font-mono truncate">
                          {typeof window !== "undefined" ? `${window.location.origin}/api/max/webhook` : "/api/max/webhook"}
                        </code>
                        <button
                          onClick={() => {
                            const url = typeof window !== "undefined" ? `${window.location.origin}/api/max/webhook` : "/api/max/webhook";
                            copyToClipboard(url, "max-webhook");
                          }}
                          className="text-[10px] font-bold text-blue-700 hover:underline px-2 cursor-pointer"
                        >
                          {copiedText === "max-webhook" ? "Скопировано!" : "Копировать"}
                        </button>
                      </div>
                    </div>

                    <label className="text-[10px] font-bold text-[#8B8C7A] uppercase tracking-wider block pt-2">Проверка отправки в MAX Bot:</label>
                    <textarea
                      rows={3}
                      value={maxTestText}
                      onChange={(e) => setMaxTestText(e.target.value)}
                      className="w-full p-3 text-xs rounded-xl border border-[#E6E3DB] bg-[#F9F8F6] text-[#3D3B36] font-sans focus:outline-none focus:border-blue-500"
                    />

                    <button
                      onClick={async () => {
                        setMaxSending(true);
                        setMaxStatus(null);
                        try {
                          const res = await fetch("/api/max/send-message", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ messageText: maxTestText })
                          });
                          const data = await res.json();
                          if (data.success) {
                            setMaxStatus(data.mode === "simulation" 
                              ? "Симуляция отправки прошла успешно! (Задайте MAX_BOT_TOKEN для реального бота)" 
                              : "Сообщение отправлено пользователям MAX Bot!");
                          } else {
                            setMaxStatus("Ошибка MAX: " + (data.error || "Неизвестная ошибка"));
                          }
                        } catch (err: any) {
                          setMaxStatus("Ошибка сети: " + err.message);
                        } finally {
                          setMaxSending(false);
                        }
                      }}
                      disabled={maxSending}
                      className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                    >
                      <Bot className="w-4 h-4" />
                      <span>{maxSending ? "Тестирование MAX..." : "Проверить вещание MAX Bot"}</span>
                    </button>

                    {maxStatus && (
                      <p className={`text-xs font-semibold text-center mt-2 ${maxStatus.includes("Ошибка") ? "text-rose-600" : "text-blue-700"}`}>
                        {maxStatus}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

    </div>
  );
}
