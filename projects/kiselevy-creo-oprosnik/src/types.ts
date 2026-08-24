export interface PollResponse {
  id: string;
  timestamp: string;
  feeling: string;
  feelingCustom?: string;
  steadyHelp: string[];
  steadyHelpCustom?: string;
  formatPreference: string[];
  openPain: string;
  subscribedPractices: string; // "Да" | "Нет" | "Иногда"
  subscribed: boolean;
  name?: string;
  contact?: string;
  stressLevel?: number; // Calculated stress scale 1-10
  questionnaireId?: string;
  questionnaireTitle?: string;
  answers?: Array<{ questionId: string; questionTitle: string; answer: string | string[] }>;
}

export interface AIAnalysisResult {
  emotionMap: string[];
  bodyTensionMap: string[];
  copywritingKeywords: string[];
  recommendedProgram: {
    title: string;
    description: string;
    steps: {
      day: string;
      title: string;
      practice: string;
      duration: string;
    }[];
  };
}

export const feelings = [
  { text: "Напряжение в теле (зажаты плечи, болит спина)", color: "hover:bg-[#F9F8F6]" },
  { text: "Постоянная тревога в мыслях, сложно уснуть", color: "hover:bg-[#F9F8F6]" },
  { text: "Чувство бессилия и замирания", color: "hover:bg-[#F9F8F6]" },
  { text: "Стараюсь держаться, но на пределе", color: "hover:bg-[#F9F8F6]" },
  { text: "Другое", color: "hover:bg-[#F9F8F6]" }
];

export const steadyOptions = [
  "Покой",
  "Расслабление тела",
  "Поддержка",
  "Хороший сон",
  "Другое"
];

export const formatOptions = [
  "Антистресс дыхание",
  "Йога",
  "Расслабление шеи",
  "Медитация перед сном",
  "Не знаю"
];

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initDataUnsafe?: {
          user?: {
            id: number;
            first_name?: string;
            last_name?: string;
            username?: string;
            language_code?: string;
          };
        };
        ready: () => void;
        expand: () => void;
        close: () => void;
        openTelegramLink: (url: string) => void;
        openLink: (url: string) => void;
        MainButton: {
          text: string;
          show: () => void;
          hide: () => void;
          onClick: (fn: () => void) => void;
        };
      };
    };
  }
}

