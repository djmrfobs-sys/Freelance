import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  Heart, 
  ChevronRight, 
  ChevronLeft, 
  Send, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  Smile, 
  Play, 
  Pause, 
  RefreshCw,
  Leaf,
  Wind,
  Moon,
  Sun,
  Flame,
  XCircle,
  Mail,
  Gift,
  Crown,
  Compass,
  Briefcase,
  Phone,
  HeartHandshake,
  Clock,
  Bot,
  Globe,
  User,
  ShieldCheck,
  FileText,
  ArrowRight
} from "lucide-react";
import { PollResponse, feelings, steadyOptions, formatOptions } from "../types";
import ConsentModal from "./ConsentModal";
import LegalDocumentsModal, { DocumentType } from "./LegalDocumentsModal";

export function formatRussianName(rawName: string): string {
  if (!rawName || !rawName.trim()) return "Друг";
  const words = rawName.trim().split(/\s+/);
  return words
    .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

export function detectGenderByName(rawName: string): "female" | "male" {
  if (!rawName || !rawName.trim()) return "male";
  
  const clean = rawName.trim().toLowerCase();
  const parts = clean.split(/\s+/);
  
  const maleExceptions = new Set([
    "никита", "илья", "данила", "данил", "фома", "кузьма", "савва", "лука",
    "лёва", "лева", "паша", "саша", "женя", "ваня", "дима", "миша", "гриша",
    "коля", "толя", "юра", "стёпа", "степа", "яша", "федя", "рома", "гена",
    "сева", "костя", "боря", "вася", "витя", "гоша", "влад", "тимур", "артем",
    "артём", "максим", "антон", "олег", "игорь", "павел", "глеб", "лев", "марк",
    "егор", "иван", "сергей", "андрей", "дмитрий", "александр", "михаил", "роман",
    "денис", "вадим", "владимир", "виктор", "владислав", "степан", "константин",
    "руслан", "артур", "вячеслав", "георгий", "евгений", "марат", "рустам", "захар",
    "семен", "семён", "родион", "богдан", "филипп", "всеволод", "валерий", "анатолий",
    "василий", "юрий", "григорий", "геннадий", "виталий", "аркадий", "арсений"
  ]);

  const femaleExceptions = new Set([
    "любовь", "нинель", "юдифь", "кармен", "адель", "мишель", "николь", "жюли",
    "айгуль", "гульназ", "асель", "софи", "меган", "элен", "элин"
  ]);

  for (const part of parts) {
    if (maleExceptions.has(part)) return "male";
    if (femaleExceptions.has(part)) return "female";
  }

  let firstName = parts[0];
  if (parts.length > 1) {
    if (parts[0].endsWith("ов") || parts[0].endsWith("ев") || parts[0].endsWith("ин") || parts[0].endsWith("ский")) {
      firstName = parts[1];
    }
  }

  if (firstName.endsWith("вна") || firstName.endsWith("чна")) return "female";
  if (firstName.endsWith("вич") || firstName.endsWith("лич")) return "male";

  const lastChar = firstName.slice(-1);
  const lastTwo = firstName.slice(-2);

  if (lastTwo === "ия" || lastTwo === "ея" || lastTwo === "ья" || lastTwo === "ая") {
    return "female";
  }

  if (lastChar === "а" || lastChar === "я") {
    return "female";
  }

  return "male";
}

export function toGenitiveCase(rawName: string): string {
  if (!rawName || !rawName.trim()) return "вас";
  const formatted = formatRussianName(rawName);
  const parts = formatted.split(/\s+/);

  return parts.map(part => {
    const lower = part.toLowerCase();
    if (lower === "друг") return "друга";
    if (part.endsWith("й")) return part.slice(0, -1) + "я";
    if (part.endsWith("ь")) return part.slice(0, -1) + "я";
    if (part.endsWith("ий")) return part.slice(0, -2) + "ия";
    if (part.endsWith("я")) return part.slice(0, -1) + "и";
    if (part.endsWith("а")) {
      const stem = part.slice(0, -1);
      const lastStemChar = stem.slice(-1).toLowerCase();
      if ("гкхжчшщ".includes(lastStemChar)) return stem + "и";
      return stem + "ы";
    }
    if ("бвгдзклмнпрстфхцчшщ".includes(part.slice(-1).toLowerCase())) {
      if (lower === "павел") return "Павла";
      if (lower === "лев") return "Льва";
      return part + "а";
    }
    return part;
  }).join(" ");
}

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
  "🙌": "text-shanti-green",
  "💪": "text-shanti-green",
  "⚡": "text-shanti-green",
  "❄️": "text-shanti-green",
  "⏱️": "text-shanti-green",
  "⏱": "text-shanti-green",
};

export function SmartText({ text }: { text: string }) {
  if (!text) return null;
  const cleanStr = String(text)
    .replace(/\*\*/g, "")
    .replace(/—/g, "-")
    .replace(/--/g, "-");
  
  const regex = /(🧘‍♀️|🌿|🌬|🧘|💆|🚶|🛌|🌙|😴|💤|🕯|🌞|🙅|💌|🙏|★|👑|►|🔥|🤍|❤️|👉|✨|😅|🙌|💪|⚡|❄️|⏱️|⏱)/g;
  const parts = cleanStr.split(regex);
  
  return (
    <>
      {parts.map((part, i) => {
        const IconComponent = EMOJI_MAP[part];
        if (IconComponent) {
          const styleClass = EMOJI_STYLE_MAP[part] || "text-shanti-green";
          return (
            <span key={i} className="inline-flex items-center mx-0.5" style={{ verticalAlign: "middle" }}>
              <IconComponent className={`w-4 h-4 inline shrink-0 ${styleClass}`} />
            </span>
          );
        }
        return <React.Fragment key={i}>{part}</React.Fragment>;
      })}
    </>
  );
}

interface QuestionnaireProps {
  onSuccess: () => void;
  telegramUser?: { id: number; first_name: string; last_name?: string; username?: string; } | null;
}

export default function Questionnaire({ onSuccess, telegramUser }: QuestionnaireProps) {
  const [step, setStep] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Active Dynamic Questionnaire State
  const [activeQ, setActiveQ] = useState<any>(null);
  const [qLoading, setQLoading] = useState<boolean>(true);
  const [dynamicAnswers, setDynamicAnswers] = useState<Record<string, any>>({});
  const [profile, setProfile] = useState<{
    name: string;
    role: string;
    subtitle: string;
    welcomeMessage: string;
    avatarUrl: string;
  }>({
    name: "Опрус",
    role: "ИИ-помощник KISELEVY_CREO",
    subtitle: "Цифровой диагност и консультант по автоматизации и нейро-решениям",
    welcomeMessage: "Привет, я Опрус. Прежде чем поговорим о деле — как ты вообще? Этот разговор поможет мне понять, что тебе сейчас действительно нужно — и в бизнесе, и в себе.",
    avatarUrl: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&h=400&q=80"
  });

  const questionsList = activeQ?.questions || [];
  const isCustom = questionsList.length > 0;

  // Form State
  const [feeling, setFeeling] = useState<string>("");
  const [feelingCustom, setFeelingCustom] = useState<string>("");
  const [steadyHelp, setSteadyHelp] = useState<string[]>([]);
  const [steadyHelpCustom, setSteadyHelpCustom] = useState<string>("");
  const [formatPreference, setFormatPreference] = useState<string[]>([]);
  const [openPain, setOpenPain] = useState<string>("");
  const [subscribedPractices, setSubscribedPractices] = useState<string>("Да");
  const [name, setName] = useState<string>("");
  const [contact, setContact] = useState<string>("");
  const [acceptedConsent, setAcceptedConsent] = useState<boolean>(true);
  const [isConsentOpen, setIsConsentOpen] = useState<boolean>(false);

  // Mandatory Legal Agreements State
  const [hasAgreedPrivacyTerms, setHasAgreedPrivacyTerms] = useState<boolean>(false);
  const [hasAgreedPersonalData, setHasAgreedPersonalData] = useState<boolean>(false);
  const [hasAgreedMarketing, setHasAgreedMarketing] = useState<boolean>(false);
  const [isLegalModalOpen, setIsLegalModalOpen] = useState<boolean>(false);
  const [legalModalTab, setLegalModalTab] = useState<DocumentType>("privacy");
  const [consentError, setConsentError] = useState<string | null>(null);

  const openLegalModal = (tab: DocumentType) => {
    setLegalModalTab(tab);
    setIsLegalModalOpen(true);
  };

  // Practice state
  const [showGift, setShowGift] = useState<boolean>(false);
  const [breathingPhase, setBreathingPhase] = useState<"inhale" | "holdIn" | "exhale" | "holdOut">("inhale");
  const [secondsLeft, setSecondsLeft] = useState<number>(4);
  const [isBreathingActive, setIsBreathingActive] = useState<boolean>(false);

  // Fetch active questionnaire and profile from backend
  useEffect(() => {
    const fetchActiveQ = async () => {
      try {
        const res = await fetch("/api/questionnaires/active");
        const data = await res.json();
        if (data) {
          setActiveQ(data);
        }
      } catch (err) {
        console.error("Error fetching active questionnaire:", err);
      } finally {
        setQLoading(false);
      }
    };

    const fetchProfile = async () => {
      try {
        const res = await fetch("/api/profile");
        const data = await res.json();
        if (data && data.name) {
          setProfile(data);
        }
      } catch (err) {
        console.error("Error fetching profile:", err);
      }
    };

    fetchActiveQ();
    fetchProfile();
  }, []);

  // Pre-fill form fields from Telegram user info
  useEffect(() => {
    if (telegramUser) {
      if (telegramUser.first_name) {
        const fullName = telegramUser.first_name + (telegramUser.last_name ? ` ${telegramUser.last_name}` : "");
        setName(fullName);
      } else {
        setName("");
      }
      if (telegramUser.username) {
        setContact(`@${telegramUser.username}`);
      } else {
        setContact("");
      }
    }
  }, [telegramUser]);

  // Expand Telegram WebApp on mount
  useEffect(() => {
    if (typeof window !== "undefined" && (window as any).Telegram?.WebApp) {
      try {
        (window as any).Telegram.WebApp.ready();
        (window as any).Telegram.WebApp.expand();
      } catch (e) {
        console.error("Failed to initialize Telegram WebApp SDK", e);
      }
    }
  }, []);

  // Interactive breathing practice guide
  useEffect(() => {
    let timer: any = null;
    if (isBreathingActive) {
      timer = setInterval(() => {
        setSecondsLeft((prev) => {
          if (prev <= 1) {
            setTimeout(() => {
              setBreathingPhase((currentPhase) => {
                switch (currentPhase) {
                  case "inhale": return "holdIn";
                  case "holdIn": return "exhale";
                  case "exhale": return "holdOut";
                  case "holdOut": return "inhale";
                  default: return "inhale";
                }
              });
            }, 0);
            return 4;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      clearInterval(timer);
    }
    return () => clearInterval(timer);
  }, [isBreathingActive]);

  const toggleSteady = (item: string) => {
    setSteadyHelp(prev => 
      prev.includes(item) ? prev.filter(x => x !== item) : [...prev, item]
    );
  };

  const toggleFormat = (item: string) => {
    setFormatPreference(prev => 
      prev.includes(item) ? prev.filter(x => x !== item) : [...prev, item]
    );
  };

  const getPersonalizedTitle = (title: string, userName: string) => {
    if (!userName || !userName.trim()) return title;
    const cleanName = formatRussianName(userName);

    if (title.includes("{name}")) return title.replace(/{name}/g, cleanName);
    if (title.includes("[Имя]")) return title.replace(/\[Имя\]/g, cleanName);
    if (title.includes("[имя]")) return title.replace(/\[имя\]/g, cleanName);

    const firstChar = title.charAt(0).toLowerCase();
    const rest = title.slice(1);
    return `${cleanName}, ${firstChar}${rest}`;
  };

  const computeNeuroCoachResult = () => {
    const getOptScore = (ansStr: string) => {
      if (!ansStr) return 2;
      if (ansStr.startsWith("A)")) return 1;
      if (ansStr.startsWith("B)")) return 2;
      if (ansStr.startsWith("C)")) return 3;
      if (ansStr.startsWith("D)")) return 4;
      return 2;
    };

    const q1Score = getOptScore(dynamicAnswers["q1"] || "");
    const q2Score = getOptScore(dynamicAnswers["q2"] || "");

    const q5Ans = dynamicAnswers["q5"] || "";
    let q5Score = 2;
    if (q5Ans.startsWith("A)")) q5Score = 4;
    else if (q5Ans.startsWith("B)")) q5Score = 3;
    else if (q5Ans.startsWith("C)")) q5Score = 2;
    else if (q5Ans.startsWith("D)")) q5Score = 1;

    const q6Ans = dynamicAnswers["q6"] || "";
    let q6Score = 2;
    if (q6Ans.startsWith("A)")) q6Score = 4;
    else if (q6Ans.startsWith("B)")) q6Score = 3;
    else if (q6Ans.startsWith("C)")) q6Score = 2;
    else if (q6Ans.startsWith("D)")) q6Score = 1;

    const q7Score = getOptScore(dynamicAnswers["q7"] || "");

    const indexCalm = q1Score + q2Score + q5Score + q6Score + q7Score;

    let resourceLevel = "";
    let resourceIntro = "";
    if (indexCalm >= 16) {
      resourceLevel = "Высокий ресурс";
      resourceIntro = "При этом ваш внутренний ресурс сейчас в хорошем состоянии — это отличная база для изменений.";
    } else if (indexCalm >= 11) {
      resourceLevel = "Средний ресурс, есть просадки";
      resourceIntro = "Ваш внутренний ресурс сейчас неровный — будут дни подъёма и дни спада, это нормально на данном этапе.";
    } else if (indexCalm >= 8) {
      resourceLevel = "Низкий ресурс, истощение";
      resourceIntro = "Обратите внимание: ваш внутренний ресурс сейчас снижен. Прежде чем менять бизнес-процессы, важно немного восстановиться.";
    } else {
      resourceLevel = "Критически низкий ресурс";
      resourceIntro = "Ваш внутренний ресурс сейчас на критически низком уровне. Рекомендуем начать не с бизнес-задач, а с восстановления состояния — иначе изменения в деле будут даваться слишком тяжело.";
    }

    let operations = 0;
    let strategy = 0;
    let clients = 0;
    let blocks = 0;

    const q8 = dynamicAnswers["q8"] || "";
    if (q8.startsWith("B)")) blocks += 1;
    else if (q8.startsWith("C)")) operations += 1;
    else if (q8.startsWith("D)")) strategy += 1;

    const q9 = dynamicAnswers["q9"] || "";
    if (q9.startsWith("A)")) operations += 2;
    else if (q9.startsWith("B)")) strategy += 2;
    else if (q9.startsWith("C)")) clients += 2;
    else if (q9.startsWith("D)")) blocks += 2;

    const q10 = dynamicAnswers["q10"] || "";
    if (q10.startsWith("A)")) strategy += 1;
    else if (q10.startsWith("B)")) operations += 1;
    else if (q10.startsWith("C)")) operations += 1;
    else if (q10.startsWith("D)")) strategy += 1;

    const q11 = dynamicAnswers["q11"] || "";
    if (q11.startsWith("A)")) operations += 2;
    else if (q11.startsWith("B)")) clients += 2;
    else if (q11.startsWith("C)")) strategy += 2;
    else if (q11.startsWith("D)")) blocks += 2;

    const q14 = dynamicAnswers["q14"] || "";
    let leadPriority = "";
    if (q14.startsWith("A)")) leadPriority = "HOT: связаться в течение часа";
    else if (q14.startsWith("B)")) leadPriority = "WARM: связаться в течение суток";
    else if (q14.startsWith("C)")) leadPriority = "COLD: добавить в рассылку и прогрев";
    else if (q14.startsWith("D)")) leadPriority = "NO ACTION: только отправить результат на почту";

    const scoresMap = { OPERATIONS: operations, STRATEGY: strategy, CLIENTS: clients, BLOCKS: blocks };
    const maxScore = Math.max(operations, strategy, clients, blocks);
    const maxCategories = Object.keys(scoresMap).filter(
      (key) => scoresMap[key as keyof typeof scoresMap] === maxScore
    );

    const categoryDetails = {
      OPERATIONS: {
        name: "Операционка",
        title: "Вы двигатель, который тащит всё на себе",
        text: "Похоже, сейчас вы держите на себе слишком много рутины: задачи, которые можно делегировать, но пока делаете сами. Именно поэтому энергии не хватает даже на стратегические шаги, вы буквально тушите пожары вместо того, чтобы строить дом.",
        recommendation: "Разбор точек делегирования и выстраивание системы, которая освободит 30-50% вашего времени."
      },
      STRATEGY: {
        name: "Стратегия",
        title: "У вас есть энергия, но нет карты",
        text: "Вы двигаетесь, пробуете, ищете, но часто чувствуете, что делаете это вслепую. Нет чёткого понимания, какой следующий шаг приведёт к результату, а какой просто отнимет время.",
        recommendation: "Стратегическая сессия для построения чёткого плана на 3-6 месяцев вперёд."
      },
      CLIENTS: {
        name: "Продажи и Клиенты",
        title: "Вы делаете дело, но оно пока не приносит того, что должно",
        text: "Сейчас основная боль — недостаток клиентов, продаж или стабильного дохода. Это состояние выматывает больше всего, потому что вы вкладываетесь, а отдачи не видно.",
        recommendation: "Разбор воронки и системы продаж, плюс определение, где именно теряются клиенты."
      },
      BLOCKS: {
        name: "Внутренние блоки",
        title: "Главное препятствие сейчас не снаружи, а внутри",
        text: "Похоже, что ресурсов и возможностей у вас достаточно, но что-то внутри тормозит: сомнения, страх ошибиться, синдром самозванца или просто нет уверенности в своём пути.",
        recommendation: "Работа с нейрокоучем на снятие внутренних блоков и восстановление уверенности в действиях."
      }
    };

    let segment = "";
    let title = "";
    let text = "";
    let recommendation = "";

    if (maxCategories.length > 1 || maxScore === 0) {
      segment = "COMBINED";
      title = "У вас переплетаются сразу несколько факторов";
      const combinedTexts = maxCategories.map(cat => categoryDetails[cat as keyof typeof categoryDetails]?.text).filter(Boolean);
      text = combinedTexts.length > 0
        ? `В первую очередь это комплекс ситуаций: ${combinedTexts.join(" ")}`
        : "У вас наблюдается сочетание нескольких факторов в операционке и стратегии.";
      recommendation = "Комплексная диагностика: вместо точечного решения нужен разбор с приоритизацией, что решать в первую очередь.";
    } else {
      segment = maxCategories[0];
      const details = categoryDetails[segment as keyof typeof categoryDetails];
      title = details.title;
      text = details.text;
      recommendation = details.recommendation;
    }

    // 1. Generate 80-year-old Psychologist Advice (First-person human wisdom)
    const formattedName = formatRussianName(name);
    const gender = detectGenderByName(name);
    const isFemale = gender === "female";

    const greeting = isFemale ? `Дорогая ${formattedName}!` : `Дорогой ${formattedName}!`;
    const q13Vision = dynamicAnswers["q13"] || "";

    let psychologistAdvice = `${greeting}\n\n` +
      `За свои 80 лет работы с людьми я поняла одну главную истину: человек не должен жить вопреки себе и превращать свой бизнес или работу в ежедневную каторгу.\n\n`;

    if (indexCalm <= 10) {
      psychologistAdvice += `Судя по твоим ответам, твоя внутренняя батарея сейчас находится в зоне критического истощения (${indexCalm}/20). Твоя нервная система привыкла постоянно находиться в режиме тревожной боевой готовности. Самое главное, что тебе нужно сделать прямо сейчас, это снизить планку требований к себе, сделать глубокий выдох и дать телу полноценный отдых, не испытывая за это вины.\n\n`;
    } else if (indexCalm <= 15) {
      psychologistAdvice += `Твой уровень спокойствия сейчас неровный (${indexCalm}/20), тревога и усталость накапливаются тихо, незаметно подтачивая твои силы. Тебе жизненно необходимо научиться сбрасывать фоновый стресс и давать себе паузу до того, как он перерастет в выгорание.\n\n`;
    } else {
      psychologistAdvice += `Твоё внутреннее состояние сейчас достаточно устойчиво (${indexCalm}/20), и это замечательный фундамент. Сейчас идеальный момент, чтобы без спешки и с ясным умом упорядочить свои дела.\n\n`;
    }

    if (segment === "OPERATIONS") {
      const vzvalil = isFemale ? "взвалила" : "взвалил";
      psychologistAdvice += `Ты ${vzvalil} на себя роль единственной опоры, которая тащит весь груз на себе. Поверь опыту: если не научиться передавать рутину и освобождать руки, силы неизбежно закончатся. Тебе прямо сейчас нужно перепоручить текучку системам и цифровым ассистентам.`;
    } else if (segment === "STRATEGY") {
      psychologistAdvice += `Ты тратишь колоссально много энергии на хаотичные движения без ясности. Тебе прямо сейчас не нужно делать ещё больше, тебе нужно остановиться, в тишине проложить понятную дорожную карту и двигаться строго по ней.`;
    } else if (segment === "CLIENTS") {
      psychologistAdvice += `Ты отдаёшь много тепла, но чувствуешь досаду от недостатка отдачи. Перестань сомневаться в своей ценности. Тебе просто нужно выстроить спокойную систему, которая прозрачно покажет твой продукт нужным людям.`;
    } else if (segment === "BLOCKS") {
      const neideal = isFemale ? "неидеальной" : "неидеальным";
      const gotov = isFemale ? "готова" : "готов";
      psychologistAdvice += `Твой главный барьер сейчас: не внешние обстоятельства, а внутренние сомнения и гиперответственность. Разреши себе быть ${neideal}, ошибаться и делать шаги с легкостью. Ты уже ${gotov}.`;
    } else {
      psychologistAdvice += `В твоей жизни переплелось сразу несколько узлов: и усталость от рутины, и поиски своего пути. Не пытайся развязать всё сразу. Выбери один самый простой шаг и дай себе выдохнуть.`;
    }

    if (q13Vision && q13Vision.trim().length > 2) {
      psychologistAdvice += `\n\nТвоя мечта: «${q13Vision.trim()}» абсолютно реальна. Начни двигаться к ней не через надрыв, а через бережность к себе. Помни: ты — главное сокровище в своей жизни.`;
    }

    // 2. Technical Digital Product Recommendation for KISELEVY_CREO team
    let digitalProductProposal = {
      productType: "🤖 Telegram AI-ассистент / Умный ИИ-секретарь",
      techDetails: "Разработка персонального Telegram-бота на базе Gemini API для приема заявок, авто-ответов клиентам и передачи данных в CRM.",
      expectedImpact: "Снимет до 80% рутинных чатов, освободит от 2 до 4 часов в день и снизит уровень выгорания."
    };

    const q9Ans = dynamicAnswers["q9"] || "";
    if (segment === "OPERATIONS" || q9Ans.startsWith("A)")) {
      digitalProductProposal = {
        productType: "🤖 Telegram AI-ассистент / Умный ИИ-секретарь",
        techDetails: "Создание персонального Telegram-бота с ИИ на базе Gemini 2.5 Flash для авто-ответов на частые вопросы, квалификации лидов и выдачи лид-магнитов 24/7.",
        expectedImpact: "Автоматизирует ежедневную рутину, освобождая 2-4 часа в день для отдыха и стратегии."
      };
    } else if (segment === "STRATEGY") {
      digitalProductProposal = {
        productType: "📊 Интерактивная квиз-воронка с ИИ-сегментацией",
        techDetails: "Разработка умного веб-квиза, который диагностирует потребности клиентов, сам подбирает тарифы и передает готовых горячих лидов в Telegram.",
        expectedImpact: "Даст 100% ясность в воронке, отсеет нецелевые запросы и повысит конверсию в продажу на 30-40%."
      };
    } else if (segment === "CLIENTS") {
      digitalProductProposal = {
        productType: "🌐 Упаковка Landing Page + Автоворонка привлечения",
        techDetails: "Создание высокого уровня продуктового лендинга с формой оплаты, записью и подключенным Telegram-ботом прогрева.",
        expectedImpact: "Сформирует системный поток заявок и поднимет воспринимаемую ценность продукта."
      };
    } else if (segment === "BLOCKS") {
      digitalProductProposal = {
        productType: "🌿 Персональный нейро-коуч бот сопровождения клиентов",
        techDetails: "Настройка ИИ-бота для ведения клиентов, отслеживания прогресса и проведения ежедневных малых практик.",
        expectedImpact: "Повысит удержание клиентов (LTV) и позволит масштабировать ваш проект без увеличения личной нагрузки."
      };
    }

    return {
      indexCalm,
      resourceLevel,
      resourceIntro,
      scores: { operations, strategy, clients, blocks },
      segment,
      title,
      text,
      recommendation,
      leadPriority,
      visionText: q13Vision,
      psychologistAdvice,
      digitalProductProposal
    };
  };

  const handleStartConversation = () => {
    if (!name.trim()) {
      setError("Пожалуйста, введите ваше имя, чтобы Опрус мог к вам обращаться.");
      return;
    }
    if (!hasAgreedPrivacyTerms || !hasAgreedPersonalData || !hasAgreedMarketing) {
      setConsentError("⚠️ Для начала опроса необходимо ознакомиться с документами и поставить все 3 обязательные галочки согласия.");
      return;
    }
    setConsentError(null);
    setError(null);
    setStep(2);
  };

  const handleNext = () => {
    setError(null);

    if (questionsList.length > 0 && step >= 2 && step <= questionsList.length + 1) {
      const q = questionsList[step - 2];
      if (q) {
        const ans = dynamicAnswers[q.id];
        if (q.type === "single" && !ans) {
          setError("Пожалуйста, выберите один из вариантов.");
          return;
        }
        if (q.type === "multiple" && (!ans || ans.length === 0)) {
          setError("Пожалуйста, выберите хотя бы один вариант.");
          return;
        }
      }
    }
    setStep(prev => prev + 1);
  };

  const handlePrev = () => {
    setError(null);
    setStep(prev => prev - 1);
  };

  const handleSubmit = async () => {
    if (!acceptedConsent) {
      setError("Пожалуйста, подтвердите согласие на получение рассылки и рекламных материалов.");
      return;
    }

    setLoading(true);
    setError(null);

    const neuroResult = computeNeuroCoachResult();

    try {
      const answersPayload = questionsList.map((q: any) => ({
        questionId: q.id,
        questionTitle: q.title,
        answer: dynamicAnswers[q.id] || ""
      }));

      const bodyData: any = {
        questionnaireId: activeQ?.id || "default",
        questionnaireTitle: activeQ?.title || "Опросник KISELEVY_CREO",
        answers: answersPayload,
        subscribedPractices,
        subscribed: subscribedPractices === "Да" || subscribedPractices === "Иногда",
        name: name.trim() || "Анонимно",
        contact: contact.trim(),
        indexCalm: neuroResult.indexCalm,
        resourceLevel: neuroResult.resourceLevel,
        segment: neuroResult.segment,
        scores: neuroResult.scores,
        leadPriority: neuroResult.leadPriority,
        visionText: neuroResult.visionText,
        psychologistAdvice: neuroResult.psychologistAdvice,
        digitalProductProposal: neuroResult.digitalProductProposal
      };

      if (telegramUser) {
        bodyData.telegramUser = telegramUser;
      }

      const response = await fetch("/api/responses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bodyData)
      });

      if (!response.ok) {
        throw new Error("Не удалось отправить анкету. Пожалуйста, попробуйте еще раз.");
      }

      const successStep = questionsList.length + 3;
      setStep(successStep);
      window.scrollTo({ top: 0, behavior: "smooth" });
      const innerScroll = document.getElementById("telegram-inner-scroll");
      if (innerScroll) {
        innerScroll.scrollTo({ top: 0, behavior: "smooth" });
      }
    } catch (err: any) {
      setError(err.message || "Ошибка подключения...");
    } finally {
      setLoading(false);
    }
  };

  // Human-readable labels for the sidebar
  const stepsTitles = [
    "Начало диалога",
    ...questionsList.map((q: any) => {
      if (q.id === "feeling") return "Диагностика состояния";
      if (q.id === "quietTime") return "Спокойствие";
      if (q.id === "heavyReaction") return "Тяжесть";
      if (q.id === "innerStatePriority") return "Приоритет состояния";
      if (q.id === "psychologyOpen") return "Открытый разговор";
      if (q.id === "transition") return "Мягкий переход";
      if (q.id === "businessNiche") return "Ниша бизнеса";
      if (q.id === "businessLack") return "Потребности";
      if (q.id === "businessBurnoutPart") return "Точка выгорания";
      if (q.id === "businessOpen") return "Развитие дела";
      return q.title.length > 20 ? q.title.substring(0, 18) + "..." : q.title;
    }),
    "Контакты",
    "Финал"
  ];

  const getPersonalizedProgram = () => {
    
    let focusTitle = "Баланс и бережное заземление";
    let focusSubtitle = "Гармонизация нервной системы и восстановление ресурса";
    let weeks = [
      {
        title: "Неделя 1: Мягкий старт и сонастройка",
        desc: "Учимся прислушиваться к телесным ощущениям без осуждения.",
        practices: [
          { day: "Пн, Ср, Пт", name: "Дыхание «Квадрат» (4-4-4-4) для центрирования", duration: "5 мин" },
          { day: "Вт, Чт, Сб", name: "Мягкие потягивания в постели после пробуждения", duration: "7 мин" }
        ]
      },
      {
        title: "Неделя 2: Снятие первичного напряжения",
        desc: "Освобождаем дыхание и убираем микрозажимы.",
        practices: [
          { day: "Каждый день", name: "Диафрагмальное дыхание лежа", duration: "8 мин" },
          { day: "Вт, Чт, Сб", name: "Микрорелиз шеи и расслабление трапеций", duration: "10 мин" }
        ]
      },
      {
        title: "Неделя 3: Глубокое заземление",
        desc: "Формируем чувство внутренней опоры и безопасности.",
        practices: [
          { day: "Пн, Ср, Пт", name: "Медитация при ходьбе (осознанные шаги)", duration: "10-15 мин" },
          { day: "Каждый вечер", name: "Практика благодарности перед сном", duration: "5 мин" }
        ]
      },
      {
        title: "Неделя 4: Закрепление ресурса",
        desc: "Интегрируем полученное спокойствие в повседневную жизнь.",
        practices: [
          { day: "Каждый день", name: "Свободная медитация тишины", duration: "10 мин" },
          { day: "Ср, Вс", name: "Вечерняя Йога-Нидра для полного расслабления ума", duration: "20 мин" }
        ]
      }
    ];

    let selectedFeeling = feeling;
    if (isCustom && activeQ?.questions) {
      const firstQ = activeQ.questions[0];
      if (firstQ && (firstQ.type === 'single' || firstQ.type === 'multiple')) {
        const ans = dynamicAnswers[firstQ.id];
        selectedFeeling = Array.isArray(ans) ? ans[0] : ans;
      }
    }

    const fLower = (selectedFeeling || "").toLowerCase();

    if (fLower.includes("напряжение") || fLower.includes("теле") || fLower.includes("спина") || fLower.includes("болит") || fLower.includes("зажат") || fLower.includes("плеч") || fLower.includes("шея")) {
      focusTitle = "Освобождение тела и снятие зажимов";
      focusSubtitle = "Курс на снятие мышечного напряжения, зажимов шеи, спины и лопаток";
      weeks = [
        {
          title: "Неделя 1: Диагностика и мягкий релиз",
          desc: "Бережное исследование зажимов и снятие поверхностного напряжения.",
          practices: [
            { day: "Пн, Ср, Пт", name: "Мягкий массаж шеи пальцами и покачивания головы", duration: "5 мин" },
            { day: "Вт, Чт, Сб", name: "Поза ребенка (Баласана) с поддержкой под лоб", duration: "8-10 min" }
          ]
        },
        {
          title: "Неделя 2: Освобождение плеч и грудного отдела",
          desc: "Раскрытие плечевого пояса для восстановления глубокого дыхания.",
          practices: [
            { day: "Каждый день", name: "Практика «Полное дыхание йога» для расширения ребер", duration: "7 мин" },
            { day: "Пн, Ср, Пт", name: "Мягкое вращение плечами со звуком облегчения на выдохе", duration: "10 мин" }
          ]
        },
        {
          title: "Неделя 3: Расслабление поясницы и крестца",
          desc: "Снимаем груз забот и физической усталости с нижней части спины.",
          practices: [
            { day: "Вт, Чт, Сб", name: "Динамическая кошка-корова в очень медленном темпе", duration: "10 мин" },
            { day: "Каждый вечер", name: "Практика «Ноги на стену» (Випарита Карани) для разгрузки спины", duration: "12 мин" }
          ]
        },
        {
          title: "Неделя 4: Интеграция легкости в теле",
          desc: "Закрепление ощущения свободы движения и глубокого отдыха.",
          practices: [
            { day: "Пн, Ср, Пт", name: "Сессия мягкой растяжки всего тела", duration: "15 мин" },
            { day: "Каждый вечер", name: "Медитация сканирования тела перед сном для расслабления мышц", duration: "15 мин" }
          ]
        }
      ];
    } else if (fLower.includes("тревога") || fLower.includes("мыслях") || fLower.includes("уснуть") || fLower.includes("беспоко") || fLower.includes("страх")) {
      focusTitle = "Успокоение ума и глубокий сон";
      focusSubtitle = "Программа снижения тревожности и нормализации ночного отдыха";
      weeks = [
        {
          title: "Неделя 1: Снижение шума мыслей",
          desc: "Замедление ментального ритма и переход из режима мыслей в ощущения.",
          practices: [
            { day: "Каждый день", name: "Дыхание «Анти-паника» (Квадратное дыхание)", duration: "5 мин" },
            { day: "Каждый вечер", name: "Медленное выписывание тревожных мыслей на бумагу (фрирайтинг)", duration: "5 мин" }
          ]
        },
        {
          title: "Неделя 2: Стабилизация нервной системы",
          desc: "Активация парасимпатики для глубокого внутреннего покоя.",
          practices: [
            { day: "Пн, Ср, Пт", name: "Дыхание 4-7-8 (удлиненный выдох для сна)", duration: "6 мин" },
            { day: "Каждый вечер", name: "Йога-Нидра — бережное аудио-путешествие", duration: "15 мин" }
          ]
        },
        {
          title: "Неделя 3: Создание вечернего ритуала",
          desc: "Настройка биологических ритмов на бережное засыпание.",
          practices: [
            { day: "Каждый день", name: "Медитация созерцания свечи перед сном", duration: "8 мин" },
            { day: "Вт, Чт, Сб", name: "Расслабление мышц лица, челюсти и глаз", duration: "10-12 мин" }
          ]
        },
        {
          title: "Неделя 4: Интеграция тишины",
          desc: "Полная интеграция тишины и глубокой расслабленности ума.",
          practices: [
            { day: "Пн, Ср, Пт", name: "Медитация осознанного присутствия (Mindfulness)", duration: "10-15 min" },
            { day: "Каждый вечер", name: "Краткая благодарность за прожитый день", duration: "5 мин" }
          ]
        }
      ];
    } else if (fLower.includes("бессилия") || fLower.includes("замирания") || fLower.includes("апатия") || fLower.includes("сил") || fLower.includes("устал")) {
      focusTitle = "Бережное восстановление ресурса";
      focusSubtitle = "Мягкая программа реанимации сил, восполнения энергии и заземления";
      weeks = [
        {
          title: "Неделя 1: Бережное заземление и опора",
          desc: "Возвращаем уму ощущение безопасности и физической опоры под ногами.",
          practices: [
            { day: "Пн, Ср, Пт", name: "Практика заземления «5-4-3-2-1» (осознание пространства)", duration: "5 мин" },
            { day: "Каждый день", name: "Мягкое согревающее дыхание животом", duration: "7 мин" }
          ]
        },
        {
          title: "Неделя 2: Мягкие пробуждающие микродвижения",
          desc: "Аккуратно выводим тело из режима замирания через бережное движение.",
          practices: [
            { day: "Вт, Чт, Сб", name: "Легкие вращения суставами рук и стоп лежа в постели", duration: "8 мин" },
            { day: "Каждый день", name: "Дыхание «Очищающий выдох» со звуком «Ха»", duration: "5-10 мин" }
          ]
        },
        {
          title: "Неделя 3: Наполнение теплом",
          desc: "Мягкое внимание на область сердца и восстановление эмоциональной емкости.",
          practices: [
            { day: "Пн, Ср, Пт", name: "Медитация любящей доброты (Метта) к себе", duration: "10 мин" },
            { day: "Каждый день", name: "Утреннее созерцание естественного дневного света", duration: "10 мин" }
          ]
        },
        {
          title: "Неделя 4: Закрепление тонуса",
          desc: "Сборка энергии и интеграция новых сил в повседневные дела.",
          practices: [
            { day: "Каждый день", name: "Энергетическая сонастройка и утренний фокус", duration: "10-15 мин" },
            { day: "Ср, Вс", name: "Дыхательная практика «Баланс полушарий» (Нади Шодхана)", duration: "12 мин" }
          ]
        }
      ];
    } else if (fLower.includes("пределе") || fLower.includes("выживани") || fLower.includes("выгора") || fLower.includes("срыв")) {
      focusTitle = "Реанимация нервной системы";
      focusSubtitle = "Интенсивная бережная разгрузка сверхнапряженной психики";
      weeks = [
        {
          title: "Неделя 1: Экстренное торможение ума",
          desc: "Перезагрузка нервных окончаний и мгновенное расслабление.",
          practices: [
            { day: "Каждый день", name: "Дыхание «Со вдохом облегчения» (физиологический вздох)", duration: "5-7 мин" },
            { day: "Каждый вечер", name: "Поза «Ноги на стену» с теплым пледом на животе", duration: "10 мин" }
          ]
        },
        {
          title: "Неделя 2: Границы безопасности",
          desc: "Возвращение ощущения контроля над своим микропространством.",
          practices: [
            { day: "Пн, Ср, Пт", name: "Упражнение «Кокон» (обнимание себя руками под лопатки)", duration: "8 мин" },
            { day: "Каждый день", name: "Удлиненный спокойный выдох через сомкнутые губы трубочкой", duration: "6 мин" }
          ]
        },
        {
          title: "Неделя 3: Физический сброс стресс-гормонов",
          desc: "Мягкое выведение адреналина и кортизола через естественные циклы тела.",
          practices: [
            { day: "Вт, Чт, Сб", name: "Стряхивание напряжения с кистей рук и стоп (shaking)", duration: "5 мин" },
            { day: "Каждый вечер", name: "Йога-нидра для восстановления сил, заменяющая 3 часа сна", duration: "20-25 мин" }
          ]
        },
        {
          title: "Неделя 4: Сборка целостности",
          desc: "Обретение устойчивого баланса и спокойной внутренней опоры.",
          practices: [
            { day: "Каждый день", name: "Мягкая сонастройка с ритмом дыхания", duration: "10 мин" },
            { day: "Пн, Чт", name: "Медитация тихой неспешной ходьбы в парке", duration: "20 мин" }
          ]
        }
      ];
    }

    return { focusTitle, focusSubtitle, weeks };
  };

  return (
    <div className="w-full max-w-5xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-12 gap-12" id="minimalist-layout">
      {/* Sidebar: Clean Minimalism Aesthetic */}
      <aside className="lg:col-span-3 flex flex-col justify-between border-r border-shanti-earth pr-8 py-2 hidden lg:flex">
        <div>
          <h3 className="font-sans text-[10px] uppercase tracking-[0.2em] text-shanti-green font-semibold mb-6">Этапы разговора</h3>
          <ul className="space-y-5">
            {stepsTitles.map((title, i) => {
              const num = i + 1;
              const isActive = step === num;
              const isPassed = step > num;
              return (
                <li key={i} className={`flex items-start gap-3 transition-opacity duration-300 ${isActive ? "opacity-100 font-semibold" : "opacity-40"}`}>
                  <span className={`font-mono text-[10px] pt-1 ${isActive ? "text-shanti-green" : "text-gray-400"}`}>
                    {num < 10 ? `0${num}` : num}
                  </span>
                  <span className="text-sm tracking-tight"><SmartText text={title} /></span>
                </li>
              );
            })}
          </ul>
        </div>
        
        <div className="bg-shanti-green/10 p-5 rounded-2xl border border-shanti-green/5 mt-8">
          <p className="text-xs leading-relaxed italic text-shanti-olive font-serif">
            «Будущее уже наступило — нужно лишь настроить технологии. Мы помогаем находить и создавать умные решения для твоего роста.»
          </p>
        </div>
      </aside>

      {/* Main Interaction Area */}
      <section className="lg:col-span-9 flex flex-col justify-center max-w-2xl min-h-[460px] relative">
        {/* Progress header on small screens */}
        {step < questionsList.length + 3 && (
          <div className="lg:hidden flex items-center justify-between font-sans text-xs uppercase tracking-widest text-shanti-green mb-6">
            <span>Шаг {step} из {questionsList.length + 2}</span>
            <div className="w-24 h-1 bg-shanti-earth relative rounded-full">
              <div 
                className="absolute left-0 top-0 h-full bg-shanti-green transition-all duration-300" 
                style={{ width: `${(step / (questionsList.length + 2)) * 100}%` }}
              />
            </div>
          </div>
        )}

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              className="space-y-6"
            >
              <div className="flex flex-col">
                <span className="text-xs uppercase tracking-[0.2em] font-sans text-shanti-green font-semibold">
                  Опросник KISELEVY_CREO
                </span>
                <h1 className="text-4xl leading-tight font-serif mt-2 text-shanti-dark flex items-center gap-2">
                  <Leaf className="w-8 h-8 text-shanti-green shrink-0 inline-block mr-1" />
                  <SmartText text={activeQ?.title || "Опросник KISELEVY_CREO"} />
                </h1>
              </div>

              {/* Oprus Personal Avatar & Greeting Dialogue Block */}
              <div className="flex flex-col sm:flex-row items-center gap-5 bg-white p-5 rounded-2xl border border-shanti-earth shadow-xs mb-4">
                <div className="relative shrink-0 w-24 h-24 rounded-full border-2 border-shanti-green/30 p-1 bg-shanti-sand overflow-hidden flex items-center justify-center">
                  <img
                    src={profile.avatarUrl}
                    alt={profile.name}
                    className="w-full h-full object-cover rounded-full"
                    referrerPolicy="no-referrer"
                  />
                  <span className="absolute bottom-1 right-1 w-3.5 h-3.5 bg-shanti-green rounded-full border-2 border-white animate-pulse" />
                </div>
                <div className="text-center sm:text-left space-y-1.5 flex-1">
                  <div className="flex items-center justify-center sm:justify-start gap-1.5">
                    <h4 className="font-serif text-base text-shanti-dark font-bold">{profile.name}</h4>
                    <span className="text-[9px] uppercase tracking-wider bg-shanti-green/10 text-shanti-green px-2 py-0.5 rounded-full font-sans font-semibold">{profile.role || "ИИ-диагност"}</span>
                  </div>
                  <div className="p-3.5 bg-[#FAF9F5] rounded-xl border border-shanti-earth/60 text-sm text-shanti-dark leading-relaxed font-sans shadow-2xs">
                    💬 «Привет! Давай познакомимся поближе 👋<br />
                    Я — <b>Опрус</b>. Как тебя зовут?»
                  </div>
                </div>
              </div>

              {/* Name Input Box */}
              <div className="space-y-2 bg-white/90 p-5 rounded-2xl border border-shanti-earth/80 shadow-xs">
                <label className="block text-xs font-semibold text-shanti-dark font-sans uppercase tracking-wider flex items-center gap-1.5">
                  <User className="w-4 h-4 text-shanti-green" />
                  Ваше имя:
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    if (error) setError(null);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleStartConversation();
                    }
                  }}
                  placeholder="Введите ваше имя (например: Алексей)"
                  className="w-full p-4 rounded-xl border border-shanti-earth bg-white text-sm text-shanti-dark focus:outline-none focus:ring-2 focus:ring-shanti-green/30 focus:border-shanti-green font-sans shadow-xs transition-all"
                />
                {name.trim() && (
                  <p className="text-xs text-shanti-green font-medium font-sans pt-1 flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Очень приятно, {name.trim()}!</span>
                  </p>
                )}
              </div>

              {/* Mandatory Legal Documents & Consents Block */}
              <div className="space-y-3 bg-white/90 p-5 rounded-2xl border border-shanti-earth/80 shadow-xs">
                <div className="flex items-center gap-2 border-b border-shanti-earth/60 pb-2.5">
                  <ShieldCheck className="w-4 h-4 text-shanti-green shrink-0" />
                  <span className="text-xs font-bold uppercase tracking-wider text-shanti-dark font-sans">
                    Официальные правила и согласие с документами
                  </span>
                </div>

                <p className="text-xs text-gray-600 leading-relaxed font-sans">
                  Перед началом опроса ознакомьтесь с документами и подтвердите согласие:
                </p>

                <div className="space-y-3 text-xs text-shanti-dark font-sans pt-1">
                  {/* Checkbox 1: Privacy Policy & Terms of Service */}
                  <label className="flex items-start gap-3 cursor-pointer select-none group">
                    <input
                      type="checkbox"
                      checked={hasAgreedPrivacyTerms}
                      onChange={(e) => {
                        setHasAgreedPrivacyTerms(e.target.checked);
                        if (consentError) setConsentError(null);
                      }}
                      className="mt-0.5 w-4 h-4 rounded border-shanti-earth text-shanti-green focus:ring-shanti-green/30 cursor-pointer accent-shanti-green shrink-0"
                    />
                    <span className="leading-relaxed">
                      Подтверждаю ознакомление и согласие с{" "}
                      <button
                        type="button"
                        onClick={(e) => { e.preventDefault(); e.stopPropagation(); openLegalModal("privacy"); }}
                        className="text-shanti-green font-bold underline hover:text-shanti-olive cursor-pointer"
                      >
                        Политикой конфиденциальности
                      </button>{" "}
                      и{" "}
                      <button
                        type="button"
                        onClick={(e) => { e.preventDefault(); e.stopPropagation(); openLegalModal("terms"); }}
                        className="text-shanti-green font-bold underline hover:text-shanti-olive cursor-pointer"
                      >
                        Пользовательским соглашением
                      </button>{" "}
                      ИП Киселева А.П. <span className="text-rose-500 font-bold">*</span>
                    </span>
                  </label>

                  {/* Checkbox 2: Personal Data Consent */}
                  <label className="flex items-start gap-3 cursor-pointer select-none group">
                    <input
                      type="checkbox"
                      checked={hasAgreedPersonalData}
                      onChange={(e) => {
                        setHasAgreedPersonalData(e.target.checked);
                        if (consentError) setConsentError(null);
                      }}
                      className="mt-0.5 w-4 h-4 rounded border-shanti-earth text-shanti-green focus:ring-shanti-green/30 cursor-pointer accent-shanti-green shrink-0"
                    />
                    <span className="leading-relaxed">
                      Даю{" "}
                      <button
                        type="button"
                        onClick={(e) => { e.preventDefault(); e.stopPropagation(); openLegalModal("personal_data"); }}
                        className="text-shanti-green font-bold underline hover:text-shanti-olive cursor-pointer"
                      >
                        Согласие на обработку персональных данных
                      </button>{" "}
                      (ФЗ № 152-ФЗ) <span className="text-rose-500 font-bold">*</span>
                    </span>
                  </label>

                  {/* Checkbox 3: Marketing & Notification Consent */}
                  <label className="flex items-start gap-3 cursor-pointer select-none group">
                    <input
                      type="checkbox"
                      checked={hasAgreedMarketing}
                      onChange={(e) => {
                        setHasAgreedMarketing(e.target.checked);
                        if (consentError) setConsentError(null);
                      }}
                      className="mt-0.5 w-4 h-4 rounded border-shanti-earth text-shanti-green focus:ring-shanti-green/30 cursor-pointer accent-shanti-green shrink-0"
                    />
                    <span className="leading-relaxed">
                      Даю{" "}
                      <button
                        type="button"
                        onClick={(e) => { e.preventDefault(); e.stopPropagation(); openLegalModal("marketing"); }}
                        className="text-shanti-green font-bold underline hover:text-shanti-olive cursor-pointer"
                      >
                        Согласие на получение рассылок и рекламных материалов
                      </button>{" "}
                      (ФЗ № 38-ФЗ) <span className="text-rose-500 font-bold">*</span>
                    </span>
                  </label>
                </div>

                {consentError && (
                  <div className="flex items-center gap-2 text-rose-600 text-xs bg-rose-50 p-3 rounded-xl border border-rose-200 mt-2 font-medium">
                    <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
                    <span>{consentError}</span>
                  </div>
                )}
              </div>

              {error && (
                <div className="flex items-center gap-2 text-rose-500 text-xs bg-rose-50 p-3 rounded-lg border border-rose-100">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div className="pt-2">
                <button
                  id="btn-start-conversation"
                  onClick={handleStartConversation}
                  className="w-full sm:w-auto px-10 py-4 bg-shanti-green text-white rounded-full font-sans text-xs uppercase tracking-widest hover:bg-shanti-olive transition-all flex items-center justify-center gap-2 cursor-pointer shadow-md hover:shadow-lg transform active:scale-95"
                >
                  <span>{name.trim() ? `Очень приятно! Поехали` : `Познакомиться`}</span>
                  <Play className="w-3.5 h-3.5 fill-white text-white" />
                </button>
              </div>
            </motion.div>
          )}

          {/* DYNAMIC QUESTIONS RENDERER FOR ALL QUESTIONNAIRES */}
          {questionsList.length > 0 && step >= 2 && step <= questionsList.length + 1 && (
            <motion.div
              key={`dynamic-step-${step}`}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              className="space-y-6"
            >
              {(() => {
                const q = questionsList[step - 2];
                if (!q) return null;
                const isTransition = q.type === "transition";
                return (
                  <>
                    {!isTransition && (
                      <div className="space-y-2">
                        {name.trim() && (
                          <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-shanti-green/10 text-shanti-green rounded-full text-xs font-semibold font-sans mb-1">
                            <Bot className="w-3.5 h-3.5" />
                            <span>Опрус обращается к вам, {name.trim()}</span>
                          </div>
                        )}
                        <h2 className="text-3xl leading-tight font-serif text-shanti-dark">
                          {getPersonalizedTitle(q.title, name)}
                        </h2>
                        {q.subtitle && (
                          <p className="font-sans text-xs tracking-wider text-shanti-green uppercase mt-2">
                            {q.subtitle}
                          </p>
                        )}
                      </div>
                    )}

                    {q.type === "transition" && (
                      <div className="bg-[#FAF9F5] border border-shanti-earth/60 p-8 rounded-2xl flex flex-col items-center text-center space-y-4">
                        <div className="w-16 h-16 rounded-full bg-shanti-green/10 flex items-center justify-center text-shanti-green animate-pulse mb-2">
                          <Sparkles className="w-8 h-8 text-shanti-green" />
                        </div>
                        <h2 className="text-2xl font-serif text-shanti-dark leading-snug">
                          <SmartText text={q.title} />
                        </h2>
                        {q.subtitle && (
                          <p className="text-xs text-gray-500 font-sans uppercase tracking-wider">
                            <SmartText text={q.subtitle} />
                          </p>
                        )}
                      </div>
                    )}

                    {q.type === "single" && (
                      <div className="space-y-3">
                        {q.options.map((opt: string, i: number) => (
                          <button
                            key={i}
                            onClick={() => {
                              setDynamicAnswers(prev => ({ ...prev, [q.id]: opt }));
                            }}
                            className={`w-full group flex items-center justify-between p-4 px-6 rounded-xl border text-left transition-all duration-300 cursor-pointer ${
                              dynamicAnswers[q.id] === opt 
                                ? "border-shanti-green bg-white shadow-sm font-medium" 
                                : "border-shanti-earth bg-[#FBFBFA]/60 hover:bg-white"
                            }`}
                          >
                            <span className="text-sm text-shanti-dark flex items-center gap-1.5"><SmartText text={opt} /></span>
                            <div className={`w-5 h-5 rounded-full border flex items-center justify-center transition-all ${
                              dynamicAnswers[q.id] === opt ? "border-shanti-green bg-shanti-green" : "border-shanti-earth"
                            }`}>
                              {dynamicAnswers[q.id] === opt && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
                            </div>
                          </button>
                        ))}
                        {q.allowCustom && dynamicAnswers[q.id] && String(dynamicAnswers[q.id]).includes("Другое") && (
                          <input
                            type="text"
                            value={dynamicAnswers[q.id + "_custom"] || ""}
                            onChange={(e) => {
                              setDynamicAnswers(prev => ({ ...prev, [q.id + "_custom"]: e.target.value }));
                            }}
                            placeholder="Расскажите подробнее..."
                            className="w-full mt-2 p-4 rounded-xl border border-shanti-earth bg-white text-sm text-[#3E3F35] focus:outline-none focus:ring-1 focus:ring-shanti-green focus:border-shanti-green"
                          />
                        )}
                      </div>
                    )}

                    {q.type === "multiple" && (
                      <div className="space-y-3">
                        {q.options.map((opt: string, i: number) => {
                          const selectedList = dynamicAnswers[q.id] || [];
                          const isSelected = selectedList.includes(opt);
                          return (
                            <button
                              key={i}
                              onClick={() => {
                                const newList = isSelected 
                                  ? selectedList.filter((x: string) => x !== opt)
                                  : [...selectedList, opt];
                                setDynamicAnswers(prev => ({ ...prev, [q.id]: newList }));
                              }}
                              className={`w-full group flex items-center justify-between p-4 px-6 rounded-xl border text-left transition-all duration-300 cursor-pointer ${
                                isSelected 
                                  ? "border-shanti-green bg-white shadow-sm font-medium" 
                                  : "border-shanti-earth bg-[#FBFBFA]/60 hover:bg-white"
                              }`}
                            >
                              <span className="text-sm text-shanti-dark flex items-center gap-1.5"><SmartText text={opt} /></span>
                              <div className={`w-5 h-5 rounded border flex items-center justify-center transition-all ${
                                isSelected ? "border-shanti-green bg-shanti-green" : "border-shanti-earth"
                              }`}>
                                {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-white" />}
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    )}

                    {q.type === "text" && (
                      <div className="space-y-4">
                        <textarea
                          value={dynamicAnswers[q.id] || ""}
                          onChange={(e) => {
                            setDynamicAnswers(prev => ({ ...prev, [q.id]: e.target.value }));
                          }}
                          placeholder={q.placeholder || "Напишите ваши мысли..."}
                          rows={5}
                          className="w-full p-4 rounded-xl border border-shanti-earth bg-white text-sm text-[#3E3F35] focus:outline-none focus:ring-1 focus:ring-shanti-green focus:border-shanti-green resize-none leading-relaxed"
                        />
                      </div>
                    )}

                    {error && (
                      <div className="flex items-center gap-2 text-rose-500 text-xs bg-rose-50 p-3 rounded-lg border border-rose-100">
                        <AlertCircle className="w-4 h-4 shrink-0" />
                        <span>{error}</span>
                      </div>
                    )}

                    <div className="mt-8 flex items-center gap-6 font-sans">
                      <button
                        onClick={handleNext}
                        className="px-10 py-4 bg-shanti-green text-white rounded-full font-sans text-xs uppercase tracking-widest hover:bg-shanti-olive transition-colors cursor-pointer"
                      >
                        Продолжить
                      </button>
                      <button
                        onClick={handlePrev}
                        className="text-shanti-green font-sans text-xs uppercase tracking-widest hover:underline decoration-1 underline-offset-8"
                      >
                        Назад
                      </button>
                    </div>
                  </>
                );
              })()}
            </motion.div>
          )}

          {/* Name & Contacts Step */}
          {step === questionsList.length + 2 && (
            <motion.div
              key="step7"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              className="space-y-6"
            >
              <div>
                <h2 className="text-3xl leading-tight font-serif text-shanti-dark">
                  Как тебя зовут?
                </h2>
                <p className="font-sans text-xs tracking-wider text-shanti-green uppercase mt-2">
                  Оставь контакты, чтобы мы отправили тебе наш анализ и подарок
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-[#8B8C7A] mb-1 font-sans uppercase">Твое имя</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Например: Иван"
                    className="w-full p-4 rounded-xl border border-shanti-earth bg-white text-sm text-shanti-dark focus:outline-none focus:ring-1 focus:ring-shanti-green"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-[#8B8C7A] mb-1 font-sans uppercase">Ник в Telegram или Телефон</label>
                  <input
                    type="text"
                    value={contact}
                    onChange={(e) => setContact(e.target.value)}
                    placeholder="Например: @ivan_creo или +7..."
                    className="w-full p-4 rounded-xl border border-shanti-earth bg-white text-sm text-shanti-dark focus:outline-none focus:ring-1 focus:ring-shanti-green"
                  />
                </div>

                <div className="pt-2 flex items-start gap-2.5 text-[11px] text-[#8B8C7A] leading-relaxed">
                  <input
                    type="checkbox"
                    id="consent-checkbox"
                    checked={acceptedConsent}
                    onChange={(e) => setAcceptedConsent(e.target.checked)}
                    className="mt-0.5 rounded border-shanti-earth text-shanti-green focus:ring-shanti-green accent-shanti-green cursor-pointer shrink-0"
                  />
                  <label htmlFor="consent-checkbox" className="cursor-pointer select-none">
                    Я подтверждаю свое{" "}
                    <button
                      type="button"
                      onClick={() => setIsConsentOpen(true)}
                      className="text-shanti-green underline font-semibold hover:text-shanti-olive cursor-pointer"
                    >
                      Согласие на получение рассылки и рекламных материалов
                    </button>{" "}
                    ИП Киселев А.П. (ФЗ № 38-ФЗ «О рекламе»).
                  </label>
                </div>
              </div>

              {error && (
                <div className="flex items-center gap-2 text-rose-500 text-xs bg-rose-50 p-3 rounded-lg border border-rose-100">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div className="mt-8 flex flex-col sm:flex-row gap-4 items-stretch sm:items-center">
                <button
                  disabled={loading}
                  onClick={handleSubmit}
                  className="px-10 py-4 bg-shanti-green text-white rounded-full font-sans text-xs uppercase tracking-widest hover:bg-shanti-olive transition-colors cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50 shadow-sm"
                >
                  {loading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>
                      <span>Отправить KISELEVY_CREO</span>
                      <Send className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
                <button
                  disabled={loading}
                  onClick={handlePrev}
                  className="text-shanti-green font-sans text-xs uppercase tracking-widest hover:underline decoration-1 underline-offset-8 text-center py-2 cursor-pointer"
                >
                  Назад
                </button>
              </div>
            </motion.div>
          )}

          {/* Final Screen (Congratulations & Gift & Neuro-Coach Results) */}
          {step === questionsList.length + 3 && (() => {
            const result = computeNeuroCoachResult();
            const userGenitive = toGenitiveCase(name);
            return (
              <motion.div
                key="step8"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-6 text-left py-2"
              >
                <div className="flex items-center gap-3 bg-gradient-to-r from-shanti-green/10 via-white to-white p-5 rounded-2xl border-2 border-shanti-green/40 shadow-xs">
                  <div className="relative shrink-0 w-14 h-14 rounded-full border-2 border-shanti-green p-0.5 bg-shanti-sand overflow-hidden flex items-center justify-center">
                    <img
                      src="/rimma_portrait.jpg"
                      alt="Опрус"
                      className="w-full h-full object-cover rounded-full"
                    />
                    <span className="absolute bottom-0 right-0 w-3.5 h-3.5 bg-shanti-green rounded-full border-2 border-white animate-pulse" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase tracking-widest bg-shanti-green text-white px-2.5 py-0.5 rounded-full font-bold font-sans inline-block mb-1">
                      🤖 ВЫВОД СИСТЕМЫ ИИ-ДИАГНОСТИКИ
                    </span>
                    <h2 className="text-xl sm:text-2xl font-serif text-shanti-dark font-bold leading-tight">
                      Заключение и план помощи для {userGenitive}
                    </h2>
                  </div>
                </div>

                {/* Resource & Calm Banner */}
                <div className="bg-[#FAF9F5] border border-shanti-earth rounded-2xl p-5 space-y-3 shadow-xs">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-shanti-earth/60 pb-3">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-shanti-green" />
                      <span className="text-xs font-semibold uppercase tracking-wider text-shanti-dark font-sans">
                        Индекс спокойствия: <b className="text-shanti-green text-sm">{result.indexCalm}/20</b>
                      </span>
                    </div>
                    <span className={`text-[11px] px-3 py-1 rounded-full font-semibold font-sans shadow-2xs ${
                      result.indexCalm >= 16 ? "bg-emerald-100 text-emerald-800 border border-emerald-200" :
                      result.indexCalm >= 11 ? "bg-amber-100 text-amber-800 border border-amber-200" :
                      "bg-rose-100 text-rose-800 border border-rose-200"
                    }`}>
                      {result.resourceLevel}
                    </span>
                  </div>
                  <p className="text-xs sm:text-sm text-gray-700 leading-relaxed font-sans">
                    {result.resourceIntro}
                  </p>
                </div>

                {/* Main Segment Result Card */}
                <div className="bg-white border-2 border-shanti-green/30 rounded-2xl p-6 space-y-4 shadow-sm relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-shanti-green/5 rounded-full blur-2xl -mr-10 -mt-10" />
                  <span className="text-[10px] uppercase tracking-widest bg-shanti-green/10 text-shanti-green px-3 py-1 rounded-full font-bold font-sans inline-block">
                    Ключевой профиль в бизнесе
                  </span>
                  <h3 className="text-xl font-serif text-shanti-dark font-bold leading-snug">
                    {result.title}
                  </h3>
                  <p className="text-sm text-gray-600 leading-relaxed font-sans">
                    {result.text}
                  </p>

                  <div className="pt-3 border-t border-shanti-earth/60 space-y-2">
                    <span className="text-xs font-semibold text-shanti-dark uppercase tracking-wider font-sans flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-shanti-green" />
                      Персональная рекомендация нейро-коуча:
                    </span>
                    <div className="text-xs sm:text-sm text-shanti-dark font-medium bg-[#FAF9F5] p-4 rounded-xl border border-shanti-earth/80 shadow-2xs">
                      {result.recommendation}
                    </div>
                  </div>
                </div>

                {/* Scores Breakdown */}
                <div className="bg-white border border-shanti-earth rounded-2xl p-5 space-y-3">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-shanti-dark font-sans">
                    Баланс бизнес-категорий
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
                    <div className="p-3 rounded-xl bg-[#FAF9F5] border border-shanti-earth/60">
                      <div className="text-gray-500 text-[10px] uppercase font-sans">Операционка</div>
                      <div className="text-base font-bold text-shanti-dark mt-0.5 font-serif">{result.scores.operations}/6</div>
                    </div>
                    <div className="p-3 rounded-xl bg-[#FAF9F5] border border-shanti-earth/60">
                      <div className="text-gray-500 text-[10px] uppercase font-sans">Стратегия</div>
                      <div className="text-base font-bold text-shanti-dark mt-0.5 font-serif">{result.scores.strategy}/6</div>
                    </div>
                    <div className="p-3 rounded-xl bg-[#FAF9F5] border border-shanti-earth/60">
                      <div className="text-gray-500 text-[10px] uppercase font-sans">Продажи</div>
                      <div className="text-base font-bold text-shanti-dark mt-0.5 font-serif">{result.scores.clients}/6</div>
                    </div>
                    <div className="p-3 rounded-xl bg-[#FAF9F5] border border-shanti-earth/60">
                      <div className="text-gray-500 text-[10px] uppercase font-sans">Блоки</div>
                      <div className="text-base font-bold text-shanti-dark mt-0.5 font-serif">{result.scores.blocks}/6</div>
                    </div>
                  </div>
                </div>

                {/* 1. 80-year-old Psychologist First-Person Personal Counsel */}
                <div className="bg-gradient-to-br from-[#FAF9F5] to-emerald-50/40 border-2 border-shanti-green/30 rounded-2xl p-6 space-y-3 shadow-xs">
                  <div className="flex items-center gap-2 border-b border-shanti-earth/60 pb-3">
                    <HeartHandshake className="w-5 h-5 text-shanti-green shrink-0" />
                    <span className="text-xs font-bold uppercase tracking-wider text-shanti-dark font-sans">
                      Личный совет наставника (80 лет жизненного и терапевтического опыта)
                    </span>
                  </div>
                  <div className="text-xs sm:text-sm text-gray-800 leading-relaxed font-serif whitespace-pre-line space-y-2">
                    {result.psychologistAdvice}
                  </div>
                </div>

                {/* 2. Technical Digital Product Recommendation for KISELEVY_CREO */}
                <div className="bg-white border-2 border-shanti-earth rounded-2xl p-6 space-y-3 shadow-xs">
                  <div className="flex items-center justify-between gap-2 border-b border-shanti-earth/60 pb-3">
                    <div className="flex items-center gap-2">
                      <Bot className="w-5 h-5 text-shanti-green shrink-0" />
                      <span className="text-xs font-bold uppercase tracking-wider text-shanti-dark font-sans">
                        Техническое решение от KISELEVY_CREO
                      </span>
                    </div>
                    <span className="text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider bg-shanti-green/10 text-shanti-green">
                      Цифровой продукт
                    </span>
                  </div>
                  <h4 className="text-base font-serif font-bold text-shanti-dark">
                    {result.digitalProductProposal.productType}
                  </h4>
                  <p className="text-xs sm:text-sm text-gray-600 leading-relaxed font-sans">
                    <b>Как реализуем технически:</b> {result.digitalProductProposal.techDetails}
                  </p>
                  <div className="bg-[#FAF9F5] p-3 rounded-xl border border-shanti-earth/80 text-xs text-shanti-dark font-sans">
                    ⚡ <b>Ожидаемый эффект:</b> {result.digitalProductProposal.expectedImpact}
                  </div>
                </div>

                {/* 3. Algorithmic Answers Breakdown (System Output per Question) */}
                <div className="bg-white border border-shanti-earth rounded-2xl p-5 space-y-4 shadow-xs">
                  <div className="flex items-center gap-2 border-b border-shanti-earth/60 pb-3">
                    <FileText className="w-4 h-4 text-shanti-green shrink-0" />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-shanti-dark font-sans">
                      Алгоритмический анализ ваших ответов
                    </h4>
                  </div>
                  <div className="space-y-3 divide-y divide-shanti-earth/40 text-xs">
                    {questionsList.map((q, idx) => {
                      const userAns = dynamicAnswers[q.id];
                      if (!userAns) return null;
                      const ansText = Array.isArray(userAns) ? userAns.join(", ") : String(userAns);
                      if (!ansText || ansText.trim() === "") return null;
                      return (
                        <div key={q.id || idx} className="pt-2.5 first:pt-0 space-y-1">
                          <div className="font-semibold text-shanti-dark font-sans flex items-center justify-between gap-2">
                            <span>{idx + 1}. {q.title}</span>
                            <span className="text-[9px] bg-shanti-sand px-2 py-0.5 rounded text-shanti-olive font-mono">Ваш ответ</span>
                          </div>
                          <p className="text-shanti-olive italic font-serif pl-2 border-l-2 border-shanti-green/40 leading-relaxed">
                            «{ansText}»
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {result.visionText && (
                  <div className="bg-[#FAF9F5] border border-shanti-earth p-4 rounded-xl space-y-1">
                    <span className="text-[10px] uppercase tracking-wider text-shanti-green font-bold font-sans">Ваше видение успеха:</span>
                    <p className="text-xs italic text-shanti-dark font-serif">«{result.visionText}»</p>
                  </div>
                )}

                {/* Gift Section */}
                <div className="bg-gradient-to-br from-amber-50 to-orange-50/50 border border-amber-200/80 rounded-2xl p-5 space-y-3 shadow-2xs">
                  <div className="flex items-center gap-2">
                    <Gift className="w-5 h-5 text-amber-700 shrink-0" />
                    <span className="text-xs font-bold uppercase tracking-wider text-amber-900 font-sans">
                      СУПЕР-БОНУС: 7 ДНЕЙ БЕСПЛАТНО
                    </span>
                  </div>
                  <p className="text-xs text-amber-900/80 leading-relaxed font-sans">
                    Вам открыт бесплатный доступ на 7 дней к нейро-коучу KISELEVY_CREO — ИИ-психологу и бизнес-консультанту в одном боте.
                  </p>
                </div>

                <div className="pt-2 flex flex-col gap-3">
                  <button
                    onClick={() => {
                      if (onSuccess) onSuccess();
                    }}
                    className="w-full py-4 px-6 bg-shanti-green text-white rounded-full font-sans text-xs uppercase tracking-widest hover:bg-shanti-olive transition-all flex items-center justify-center gap-2 cursor-pointer shadow-md text-center font-bold"
                  >
                    <span>Активировать бонус и перейти к 7 дням 🎁</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>

                  <div className="flex flex-col sm:flex-row gap-3">
                    <a
                      href="https://t.me/neuro_kouch_creo_bot?start=neuro_coach_7days"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 py-3 px-4 border border-shanti-green text-shanti-green hover:bg-shanti-green/10 rounded-full font-sans text-xs uppercase tracking-wider transition-all flex items-center justify-center gap-2 cursor-pointer text-center font-semibold"
                    >
                      <span>Перейти в Telegram-бота</span>
                      <Send className="w-3.5 h-3.5" />
                    </a>
                    <button
                      onClick={() => {
                        setStep(1);
                        setName("");
                        setContact("");
                        setDynamicAnswers({});
                      }}
                      className="py-3 px-4 border border-shanti-earth text-gray-500 hover:bg-shanti-earth/10 rounded-full text-xs font-sans uppercase tracking-wider transition-all cursor-pointer text-center"
                    >
                      Пройти заново
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })()}
        </AnimatePresence>
      </section>

      {/* Legal Footer */}
      <footer className="w-full text-center pt-8 pb-4 text-[11px] text-[#8B8C7A] space-y-1 font-sans border-t border-shanti-earth/30 mt-8">
        <p>© KISELEVY_CREO & ИП Киселев А.П. Все права защищены.</p>
        <p className="flex flex-wrap items-center justify-center gap-3 text-[10px]">
          <button
            type="button"
            onClick={() => openLegalModal("privacy")}
            className="text-shanti-green underline hover:text-shanti-olive cursor-pointer"
          >
            Политика конфиденциальности
          </button>
          <span>•</span>
          <button
            type="button"
            onClick={() => openLegalModal("terms")}
            className="text-shanti-green underline hover:text-shanti-olive cursor-pointer"
          >
            Пользовательское соглашение
          </button>
          <span>•</span>
          <button
            type="button"
            onClick={() => openLegalModal("personal_data")}
            className="text-shanti-green underline hover:text-shanti-olive cursor-pointer"
          >
            Согласие на ОПД
          </button>
          <span>•</span>
          <button
            type="button"
            onClick={() => openLegalModal("marketing")}
            className="text-shanti-green underline hover:text-shanti-olive cursor-pointer"
          >
            Согласие на рассылку
          </button>
        </p>
      </footer>

      {/* Consent Modal */}
      <ConsentModal
        isOpen={isConsentOpen}
        onClose={() => setIsConsentOpen(false)}
      />

      {/* Full Legal Documents Modal */}
      <LegalDocumentsModal
        isOpen={isLegalModalOpen}
        onClose={() => setIsLegalModalOpen(false)}
        initialTab={legalModalTab}
      />
    </div>
  );
}
