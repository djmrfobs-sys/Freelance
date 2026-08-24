import { useState } from "react";
import { motion } from "motion/react";
import { Star, Sparkles, Send, FileText } from "lucide-react";
import ConsentModal from "./ConsentModal";

interface BonusScreenProps {
  onReset: () => void;
}

export default function BonusScreen({ onReset }: BonusScreenProps) {
  const [isConsentOpen, setIsConsentOpen] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="w-full max-w-xl mx-auto my-4 p-8 rounded-[32px] border border-shanti-earth shadow-xl bg-gradient-to-b from-[#8B8C7A]/20 via-[#F9F8F6] to-[#F9F8F6] relative overflow-hidden text-center"
      id="bonus-screen-container"
    >
      {/* Decorative subtle background sparkles */}
      <div className="absolute top-6 left-6 text-shanti-green/30 animate-pulse">
        <Sparkles className="w-5 h-5" />
      </div>
      <div className="absolute bottom-8 right-8 text-shanti-green/20">
        <Sparkles className="w-8 h-8" />
      </div>

      {/* Large beautiful star icon */}
      <div className="mx-auto w-20 h-20 rounded-full bg-white/80 border border-shanti-earth flex items-center justify-center shadow-md mb-6 animate-bounce" style={{ animationDuration: "3s" }}>
        <Star className="w-10 h-10 text-shanti-green fill-shanti-green/20" />
      </div>

      {/* Header and Titles */}
      <div className="space-y-3 mb-8">
        <h2 className="text-3xl font-serif font-bold text-shanti-dark tracking-tight flex items-center justify-center gap-2">
          <Star className="w-6 h-6 text-shanti-green fill-shanti-green" /> Поздравляем!
        </h2>
        <p className="text-shanti-olive font-sans text-xs uppercase tracking-widest font-semibold">
          Вы прошли диагностику и получили бонус
        </p>
      </div>

      {/* Premium Bonus Offer Card */}
      <div className="bg-white/90 backdrop-blur-sm border border-shanti-earth/80 rounded-2xl p-6 mb-8 shadow-sm space-y-4">
        <span className="text-[10px] uppercase tracking-widest bg-[#8B8C7A]/10 text-shanti-olive px-3 py-1 rounded-full font-bold inline-flex items-center gap-1.5 w-fit">
          <Star className="w-3 h-3 fill-shanti-green text-shanti-green" /> СУПЕР-БОНУС АКТИВЕН
        </span>
        
        <h3 className="text-xl font-serif font-bold text-shanti-dark leading-tight">
          7 дней бесплатного Нейро-коуча KISELEVY CREO
        </h3>
        
        <p className="text-xs text-gray-500 leading-relaxed max-w-md mx-auto">
          Ваш персональный ИИ-психолог и сертифицированный бизнес-консультант в одном боте. Готов разобрать вашу диагностику, снять ментальные блоки и составить пошаговый план развития вашего дела.
        </p>
      </div>

      {/* Big Green Action Button */}
      <div className="space-y-4">
        <a
          href="https://t.me/neuro_kouch_creo_bot?start=neuro_coach_7days"
          target="_blank"
          rel="noopener noreferrer"
          className="w-full py-4.5 px-8 bg-shanti-green text-white rounded-full font-sans text-xs uppercase tracking-widest hover:bg-shanti-olive active:scale-95 transition-all flex items-center justify-center gap-2.5 cursor-pointer shadow-lg font-bold text-center"
          id="btn-activate-neuro-coach"
        >
          <Star className="w-3.5 h-3.5 fill-white text-white" />
          <span>Активировать Нейро-коуча</span>
          <Send className="w-3.5 h-3.5" />
        </a>

        {/* Small text disclaimer */}
        <div className="text-[10px] text-[#8B8C7A] font-sans max-w-sm mx-auto leading-relaxed space-y-1">
          <p className="font-semibold text-gray-500">Через 7 дней: 599 ₽/мес. Отменить можно в любой момент.</p>
          <p className="text-[9px] text-gray-400">ИП Киселев А.П. | ИНН 231406735404 | ОГРНИП 312231421500020</p>
          <p className="text-[9px] text-gray-400">
            <button
              type="button"
              onClick={() => setIsConsentOpen(true)}
              className="text-shanti-green underline hover:text-shanti-olive cursor-pointer inline-flex items-center gap-1"
            >
              <FileText className="w-3 h-3" />
              <span>Согласие на получение рассылки и рекламных материалов</span>
            </button>
          </p>
        </div>
      </div>

      {/* Restart Button */}
      <div className="border-t border-shanti-earth/40 mt-8 pt-6">
        <button
          onClick={onReset}
          className="text-[11px] text-[#8B8C7A] hover:text-shanti-dark font-sans uppercase tracking-widest font-semibold transition-colors cursor-pointer"
        >
          Пройти диагностику заново
        </button>
      </div>

      {/* Consent Modal */}
      <ConsentModal
        isOpen={isConsentOpen}
        onClose={() => setIsConsentOpen(false)}
      />
    </motion.div>
  );
}
