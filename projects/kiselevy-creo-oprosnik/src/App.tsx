import { useState, useEffect } from "react";
import { motion } from "motion/react";
import { 
  Heart, Users, Sparkles, Smartphone, Bot, User, Globe, 
  Battery, Wifi, Monitor, Check, RefreshCw, Leaf, X, Clock
} from "lucide-react";
import Questionnaire from "./components/Questionnaire";
import AdminDashboard from "./components/AdminDashboard";
import BonusScreen from "./components/BonusScreen";
import ConsentPage from "./components/ConsentPage";
import PersonalCabinet from "./components/PersonalCabinet";

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
}

export default function App() {
  const [currentPath, setCurrentPath] = useState<string>(() => typeof window !== "undefined" ? window.location.pathname : "/");
  const [viewMode, setViewMode] = useState<"client" | "cabinet" | "admin">("client");

  if (currentPath === "/consent") {
    return <ConsentPage />;
  }
  const isRealTelegram = typeof window !== "undefined" && !!(window as any).Telegram?.WebApp?.initData;
  const [telegramUser, setTelegramUser] = useState<TelegramUser | null>(() => {
    if (typeof window !== "undefined" && (window as any).Telegram?.WebApp?.initDataUnsafe?.user) {
      return (window as any).Telegram.WebApp.initDataUnsafe.user;
    }
    return null;
  });
  const [isSimulatorEnabled, setIsSimulatorEnabled] = useState(!isRealTelegram);
  const [showBonus, setShowBonus] = useState<boolean>(false);

  useEffect(() => {
    if (isRealTelegram) {
      try {
        (window as any).Telegram.WebApp.ready();
        (window as any).Telegram.WebApp.expand();
      } catch (e) {
        console.error("Error communicating with native Telegram API", e);
      }
    }
  }, [isRealTelegram]);

  return (
    <div className="min-h-screen flex flex-col justify-between relative bg-shanti-sand text-shanti-dark font-sans selection:bg-shanti-green/20 selection:text-shanti-olive">
      {/* Elegant Header */}
      <header className="relative z-10 w-full max-w-5xl mx-auto px-4 sm:px-6 py-6 border-b border-shanti-earth flex flex-col sm:flex-row justify-between items-center gap-4" id="app-header">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-shanti-green/10 flex items-center justify-center border border-shanti-green/20">
            <Heart className="w-4 h-4 text-shanti-green fill-shanti-green/5" />
          </div>
          <div>
            <span className="font-serif font-medium text-lg tracking-tight block text-shanti-dark leading-none">KISELEVY_CREO</span>
            <span className="font-sans text-[9px] uppercase tracking-[0.2em] font-semibold text-shanti-green">Опрус — цифровой диагност & ИИ-коуч</span>
          </div>
        </div>

        {/* View Switcher Controls */}
        <div className="flex flex-wrap items-center justify-center gap-1 bg-white/80 p-1 rounded-xl border border-shanti-earth shadow-sm" id="view-mode-selector">
          <button
            onClick={() => setViewMode("client")}
            className={`px-3 py-1.5 rounded-lg text-xs font-sans uppercase tracking-wider transition-all flex items-center gap-1.5 cursor-pointer ${
              viewMode === "client"
                ? "bg-shanti-green text-white shadow-sm"
                : "text-gray-500 hover:text-gray-800"
            }`}
          >
            <Leaf className="w-3.5 h-3.5" />
            <span>Опросник</span>
          </button>

          <button
            onClick={() => setViewMode("cabinet")}
            className={`px-3 py-1.5 rounded-lg text-xs font-sans uppercase tracking-wider transition-all flex items-center gap-1.5 cursor-pointer ${
              viewMode === "cabinet"
                ? "bg-shanti-green text-white shadow-sm"
                : "text-gray-500 hover:text-gray-800"
            }`}
          >
            <User className="w-3.5 h-3.5" />
            <span>Личный кабинет</span>
            <span className="bg-amber-100 text-amber-800 text-[9px] font-bold px-1.5 py-0.5 rounded-full font-mono">
              7 дней
            </span>
          </button>

          <button
            id="btn-switch-admin"
            onClick={() => setViewMode("admin")}
            className={`px-3 py-1.5 rounded-lg text-xs font-sans uppercase tracking-wider transition-all flex items-center gap-1.5 cursor-pointer ${
              viewMode === "admin"
                ? "bg-shanti-green text-white shadow-sm"
                : "text-gray-500 hover:text-gray-800"
            }`}
          >
            <Users className="w-3.5 h-3.5" />
            <span>Кабинет команды</span>
          </button>
        </div>
      </header>

      {/* Main Content Space */}
      <main className="flex-grow flex items-center relative z-10 w-full max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-10">
        {viewMode === "admin" ? (
          <div className="w-full">
            <AdminDashboard />
          </div>
        ) : viewMode === "cabinet" ? (
          <div className="w-full">
            <PersonalCabinet 
              telegramUser={telegramUser} 
              onOpenQuestionnaire={() => setViewMode("client")} 
            />
          </div>
        ) : (
          /* Client mode with optional high-fidelity simulator */
          <div className="w-full">
            {isSimulatorEnabled && !isRealTelegram ? (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center w-full">
                
                {/* Simulator Control Panel (Left column on large screens) */}
                <div className="col-span-12 lg:col-span-4 bg-white/60 backdrop-blur-md p-6 rounded-3xl border border-shanti-earth shadow-sm space-y-6">
                  <div className="space-y-1.5">
                    <span className="text-[10px] font-bold text-shanti-green uppercase tracking-wider block">Окружение TMA</span>
                    <h2 className="font-serif text-2xl text-shanti-dark italic font-light">Симулятор Telegram</h2>
                    <p className="text-xs text-gray-500 leading-relaxed">
                      Приложение полностью адаптировано под <strong>Telegram Mini App</strong>. Мы автоматически считываем профиль, подставляем контакты и ведем 7-дневный трекинг.
                    </p>
                  </div>

                  {/* Quick view switcher inside simulator panel */}
                  <div className="bg-white/80 p-3 rounded-2xl border border-shanti-earth space-y-2">
                    <span className="text-[9px] font-bold text-shanti-olive uppercase tracking-wider block">Режим экрана:</span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setViewMode("client")}
                        className={`flex-1 py-1.5 px-2 rounded-xl text-[10px] font-bold uppercase transition-all ${
                          viewMode === "client" ? "bg-shanti-green text-white" : "bg-shanti-sand text-gray-600"
                        }`}
                      >
                        Опросник
                      </button>
                      <button
                        onClick={() => setViewMode("cabinet")}
                        className={`flex-1 py-1.5 px-2 rounded-xl text-[10px] font-bold uppercase transition-all ${
                          viewMode === "cabinet" ? "bg-shanti-green text-white" : "bg-shanti-sand text-gray-600"
                        }`}
                      >
                        Л. Кабинет (7 дн)
                      </button>
                    </div>
                  </div>

                  {/* Текущий профиль */}
                  <div className="space-y-3 bg-white/80 p-4 rounded-2xl border border-shanti-earth shadow-inner">
                    <span className="text-[9px] font-bold text-shanti-olive uppercase tracking-wider block">Текущий профиль:</span>
                    {telegramUser ? (
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-shanti-green/10 border border-shanti-green/20 flex items-center justify-center font-serif text-shanti-olive font-bold">
                          {telegramUser.first_name[0] || "U"}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-xs font-serif font-bold text-shanti-dark truncate">
                            {telegramUser.first_name} {telegramUser.last_name || ""}
                          </p>
                          <p className="text-[10px] text-[#8B8C7A] font-mono truncate">
                            {telegramUser.username ? `@${telegramUser.username}` : `id: ${telegramUser.id}`}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-shanti-olive/10 border border-shanti-olive/20 flex items-center justify-center font-serif text-shanti-olive italic">
                          ?
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-xs font-serif font-bold text-shanti-dark truncate">
                            Анонимный гость
                          </p>
                          <p className="text-[10px] text-[#8B8C7A] font-mono truncate">
                            web-клиент (вне Telegram)
                          </p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Toggle Web Mode */}
                  <div className="border-t border-shanti-earth pt-4 flex flex-col gap-2">
                    <button
                      onClick={() => setIsSimulatorEnabled(false)}
                      className="w-full border border-shanti-earth hover:bg-white text-gray-600 text-xs py-2.5 px-4 rounded-xl flex items-center justify-center gap-1.5 transition-all cursor-pointer font-medium"
                    >
                      <Globe className="w-3.5 h-3.5" />
                      <span>Полноэкранный Web-вид</span>
                    </button>
                  </div>
                </div>

                {/* Smartphone Device Mockup Container */}
                <div className="col-span-12 lg:col-span-8 flex justify-center items-center py-2">
                  <div className="w-full max-w-[400px] h-[780px] bg-shanti-sand border-[10px] border-shanti-dark rounded-[44px] shadow-2xl relative overflow-hidden flex flex-col ring-4 ring-[#8B8C7A]/20">
                    
                    {/* Phone Top Speaker/Notch Overlay */}
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-6 bg-shanti-dark rounded-b-2xl z-50 flex items-center justify-center">
                      <div className="w-12 h-1 bg-gray-700 rounded-full mb-1" />
                    </div>

                    {/* Mock Status Bar */}
                    <div className="bg-[#F5F3EE] pt-6 pb-2 px-6 flex justify-between items-center text-[10px] font-sans font-bold text-shanti-dark/70 z-40 relative">
                      <span>09:41</span>
                      <div className="flex items-center gap-1.5">
                        <Wifi className="w-3 h-3" />
                        <span className="text-[8px] font-mono leading-none">LTE</span>
                        <Battery className="w-3.5 h-3.5" />
                      </div>
                    </div>

                    {/* Mock Telegram Header Area */}
                    <div className="bg-[#F5F3EE] pb-3 px-4 flex justify-between items-center border-b border-shanti-earth z-40 relative shadow-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-shanti-green/25 text-shanti-olive flex items-center justify-center font-bold text-xs">
                          К
                        </div>
                        <div>
                          <h4 className="text-xs font-serif font-bold leading-none text-shanti-dark flex items-center gap-1">
                            KISELEVY_CREO <Leaf className="w-3 h-3 text-shanti-green" />
                          </h4>
                          <span className="text-[9px] font-sans text-shanti-green uppercase tracking-wide leading-none">bot</span>
                        </div>
                      </div>
                      
                      {/* Telegram Mini App Action Buttons */}
                      <div className="flex items-center gap-1.5 bg-shanti-dark/5 px-2 py-1 rounded-full border border-shanti-earth">
                        <div className="flex gap-0.5">
                          <span className="w-1 h-1 bg-shanti-dark/70 rounded-full" />
                          <span className="w-1 h-1 bg-shanti-dark/70 rounded-full" />
                          <span className="w-1 h-1 bg-shanti-dark/70 rounded-full" />
                        </div>
                        <span className="w-px h-2.5 bg-shanti-dark/10 mx-0.5" />
                        <X className="w-2.5 h-2.5 text-shanti-dark/70" />
                      </div>
                    </div>

                    {/* Simulator Info Tag */}
                    <div className="bg-shanti-green/10 px-4 py-1 text-[9px] text-shanti-olive font-sans text-center flex items-center justify-between border-b border-shanti-green/10 z-30 relative">
                      <span className="flex items-center gap-1">
                        <Bot className="w-3 h-3" />
                        <strong>{telegramUser ? `${telegramUser.first_name}` : "Гость"}</strong>
                      </span>
                      <button 
                        onClick={() => setViewMode(viewMode === "client" ? "cabinet" : "client")}
                        className="text-shanti-green font-bold hover:underline cursor-pointer"
                      >
                        {viewMode === "client" ? "В личный кабинет →" : "← К опросник"}
                      </button>
                    </div>

                    {/* Scrollable WebApp Content Area */}
                    <div className="flex-grow overflow-y-auto bg-shanti-sand p-4 pb-12 relative" id="telegram-inner-scroll">
                      {viewMode === "cabinet" ? (
                        <PersonalCabinet 
                          telegramUser={telegramUser} 
                          onOpenQuestionnaire={() => setViewMode("client")} 
                        />
                      ) : showBonus ? (
                        <BonusScreen onReset={() => setShowBonus(false)} />
                      ) : (
                        <Questionnaire 
                          telegramUser={telegramUser} 
                          onSuccess={() => setShowBonus(true)} 
                        />
                      )}
                    </div>

                    {/* Phone Bottom Bar Overlay */}
                    <div className="absolute bottom-1.5 left-1/2 -translate-x-1/2 w-32 h-1 bg-shanti-dark rounded-full z-50 pointer-events-none" />
                  </div>
                </div>

              </div>
            ) : (
              /* Raw Full Screen Web/Telegram view */
              <div className="w-full space-y-6">
                {/* Mode active flag outside Telegram */}
                {!isRealTelegram && (
                  <div className="bg-[#8B8C7A]/10 border border-[#8B8C7A]/20 rounded-2xl p-4 flex flex-col sm:flex-row justify-between items-center gap-3 font-sans text-xs mb-4">
                    <p className="text-shanti-olive flex items-center gap-2 font-medium">
                      <Smartphone className="w-4 h-4" />
                      <span>Полноэкранный Web-вид активен.</span>
                    </p>
                    <button
                      onClick={() => setIsSimulatorEnabled(true)}
                      className="px-4 py-1.5 bg-[#8B8C7A] text-white rounded-lg font-bold uppercase tracking-wider text-[10px] hover:bg-[#5A5A40] cursor-pointer transition-colors"
                    >
                      Включить симулятор Telegram
                    </button>
                  </div>
                )}
                
                {/* Main Questionnaire or Personal Cabinet */}
                {viewMode === "cabinet" ? (
                  <PersonalCabinet 
                    telegramUser={telegramUser} 
                    onOpenQuestionnaire={() => setViewMode("client")} 
                  />
                ) : showBonus ? (
                  <BonusScreen onReset={() => setShowBonus(false)} />
                ) : (
                  <Questionnaire 
                    telegramUser={telegramUser} 
                    onSuccess={() => setShowBonus(true)} 
                  />
                )}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Aesthetic Footer */}
      <footer className="relative z-10 text-center py-6 border-t border-shanti-earth/10 w-full max-w-5xl mx-auto px-4 space-y-2" id="app-footer">
        <p className="font-sans text-xs text-shanti-olive font-semibold">© 2026 ИП Киселев А.П.</p>
        <p className="font-sans text-[10px] text-gray-400 leading-relaxed max-w-3xl mx-auto opacity-80">
          Сервис предоставляется на условиях Пользовательского соглашения. Используя сервис, вы принимаете условия обработки персональных данных. Не является публичной офертой. Данные ИП: ИНН 231406735404 | ОГРН 312231421500020 | Краснодарский край, г. Лабинск, ул. Филатова 45
        </p>
      </footer>
    </div>
  );
}
