import React from "react";
import { motion, AnimatePresence } from "motion/react";
import { X, FileText, Download, Printer, ShieldCheck } from "lucide-react";

export interface Requisites {
  companyName: string;
  inn: string;
  ogrn: string;
  address?: string;
  email: string;
  website: string;
}

export const defaultRequisites: Requisites = {
  companyName: "Индивидуальный предприниматель Киселев Артур Пшимахович",
  inn: "231406735404",
  ogrn: "312231421500020",
  address: "352505, Краснодарский край, г. Лабинск, ул. Филатова, д. 45",
  email: "dj.mr.fobs@gmail.com",
  website: "https://t.me/kiselevy_creo"
};

interface ConsentModalProps {
  isOpen: boolean;
  onClose: () => void;
  customRequisites?: Partial<Requisites>;
}

export const ConsentModal: React.FC<ConsentModalProps> = ({
  isOpen,
  onClose,
  customRequisites
}) => {
  const req = { ...defaultRequisites, ...customRequisites };

  const handlePrint = () => {
    window.print();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-shanti-dark/60 backdrop-blur-xs overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl overflow-hidden border border-shanti-earth my-8 flex flex-col max-h-[90vh]"
          >
            {/* Header */}
            <div className="p-6 bg-shanti-light border-b border-shanti-earth flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-shanti-green/10 flex items-center justify-center text-shanti-green">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-serif font-bold text-shanti-dark text-base">
                    Официальный документ
                  </h3>
                  <p className="font-sans text-[11px] text-shanti-olive uppercase tracking-wider font-medium">
                    Согласие на получение рассылки
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handlePrint}
                  className="p-2 text-shanti-olive hover:text-shanti-dark hover:bg-shanti-earth/30 rounded-full transition-colors cursor-pointer"
                  title="Распечатать документ"
                >
                  <Printer className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={onClose}
                  className="p-2 text-shanti-olive hover:text-shanti-dark hover:bg-shanti-earth/30 rounded-full transition-colors cursor-pointer"
                  title="Закрыть"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Document Body */}
            <div className="p-6 sm:p-8 overflow-y-auto space-y-5 text-shanti-dark text-xs sm:text-sm leading-relaxed font-sans select-text">
              <div className="text-center space-y-1 pb-4 border-b border-shanti-earth/50">
                <h2 className="font-serif font-bold text-base sm:text-lg text-shanti-dark uppercase tracking-tight">
                  СОГЛАСИЕ
                </h2>
                <p className="font-serif italic text-shanti-olive text-xs">
                  на получение рассылки и рекламных материалов
                </p>
              </div>

              <p className="text-justify indent-4">
                Настоящим я, во исполнение требований Федерального закона от 13.03.2006 № 38-ФЗ «О рекламе», регистрируясь и/или вводя свои данные на сайте{" "}
                <span className="font-medium underline decoration-shanti-green/40">{req.website}</span>, его сервисах и/или его поддоменах (далее — «Сайт») добровольно, свободно, своей волей и в своем интересе даю свое согласие{" "}
                <span className="font-semibold">{req.companyName}</span> (ИНН: {req.inn}, ОГРНИП: {req.ogrn}) (далее — «Оператор») на получение рассылки материалов рекламного и/или информационного характера посредством SMS-сервисов и/или электронной почты, а также посредством WhatsApp или Telegram-рассылки от Оператора и подтверждаю, что в полной мере ознакомился с настоящим Согласием и Политикой обработки персональных данных Оператора, а также подтверждаю достоверность предоставленных мною данных.
              </p>

              <div className="space-y-2 bg-shanti-light/60 p-4 rounded-xl border border-shanti-earth/40">
                <p className="font-semibold text-shanti-dark">
                  Настоящее Согласие дано с целью оперативного получения следующей информации, но не ограничиваясь ей:
                </p>
                <ul className="list-disc list-inside space-y-1 text-shanti-dark/90 pl-1">
                  <li>новостей и информации о продуктах и услугах Оператора, партнеров Оператора;</li>
                  <li>информации о специальных предложениях и рекламных акциях, системах скидок, бонусов и различного рода мероприятиях и презентациях по продуктам и услугам Оператора, партнеров Оператора.</li>
                </ul>
              </div>

              <p className="text-justify">
                Настоящее Согласие действует бессрочно, либо до получения Оператором отзыва Согласия.
              </p>

              <p className="text-justify indent-4">
                Я подтверждаю, что владею информацией о том, что в любой момент в течение всего срока действия настоящего Согласия, я вправе отозвать свое согласие на получение рассылки материалов рекламного и/или информационного характера и отписаться от их получения, путем перехода по соответствующей ссылке, имеющейся в любом письме, полученном от Оператора, либо, направив письмо на адрес электронной почты Оператора с пометкой: <span className="font-medium italic">«Отзыв согласия на получение рассылки и рекламных материалов»</span>.
              </p>

              {/* Contacts & Requisites Block */}
              <div className="mt-6 p-4 sm:p-5 rounded-2xl bg-shanti-earth/20 border border-shanti-earth/60 space-y-2">
                <div className="flex items-center gap-2 font-serif font-bold text-shanti-dark text-xs uppercase tracking-wider text-shanti-green">
                  <ShieldCheck className="w-4 h-4 text-shanti-green" />
                  <span>Контакты и реквизиты Оператора:</span>
                </div>
                <div className="space-y-1 text-xs text-shanti-dark/90 font-mono leading-relaxed pt-1">
                  <p className="font-sans font-semibold text-shanti-dark">{req.companyName}</p>
                  {req.address && <p><span className="text-shanti-olive font-sans">Регион:</span> {req.address}</p>}
                  <p><span className="text-shanti-olive font-sans">ИНН:</span> {req.inn}</p>
                  <p><span className="text-shanti-olive font-sans">ОГРНИП:</span> {req.ogrn}</p>
                  <p><span className="text-shanti-olive font-sans">Электронная почта:</span> <a href={`mailto:${req.email}`} className="text-shanti-green underline">{req.email}</a></p>
                </div>
              </div>
            </div>

            {/* Footer button */}
            <div className="p-4 bg-shanti-light border-t border-shanti-earth flex items-center justify-between shrink-0">
              <span className="text-[11px] text-shanti-olive font-sans">
                Документ составлен в соответствии с ФЗ № 38-ФЗ «О рекламе»
              </span>
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-2.5 bg-shanti-green text-white text-xs font-bold rounded-full hover:bg-shanti-olive transition-colors cursor-pointer"
              >
                Понятно
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default ConsentModal;
