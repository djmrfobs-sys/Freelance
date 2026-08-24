import React from "react";
import { FileText, Printer, ArrowLeft, ShieldCheck, Download } from "lucide-react";
import { defaultRequisites } from "./ConsentModal";

export const ConsentPage: React.FC = () => {
  const req = defaultRequisites;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-shanti-sand text-shanti-dark py-8 px-4 sm:px-6 font-sans">
      <div className="max-w-3xl mx-auto bg-white rounded-3xl shadow-xl border border-shanti-earth overflow-hidden">
        {/* Header */}
        <div className="p-6 bg-shanti-light border-b border-shanti-earth flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <a
              href="/"
              className="p-2 text-shanti-olive hover:text-shanti-dark hover:bg-shanti-earth/30 rounded-full transition-colors cursor-pointer"
              title="На главную"
            >
              <ArrowLeft className="w-5 h-5" />
            </a>
            <div className="w-10 h-10 rounded-full bg-shanti-green/10 flex items-center justify-center text-shanti-green">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-serif font-bold text-shanti-dark text-base sm:text-lg">
                Официальный документ
              </h1>
              <p className="font-sans text-[11px] text-shanti-olive uppercase tracking-wider font-semibold">
                ИП Киселев А.П. — ФЗ № 38-ФЗ «О рекламе»
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handlePrint}
            className="px-4 py-2 bg-shanti-light border border-shanti-earth text-shanti-dark text-xs font-semibold rounded-full hover:bg-shanti-earth/40 transition-colors flex items-center gap-2 cursor-pointer"
          >
            <Printer className="w-4 h-4 text-shanti-green" />
            <span>Распечатать / PDF</span>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 sm:p-10 space-y-6 text-shanti-dark text-sm leading-relaxed font-sans select-text">
          <div className="text-center space-y-1.5 pb-6 border-b border-shanti-earth/60">
            <h2 className="font-serif font-bold text-lg sm:text-xl text-shanti-dark uppercase tracking-tight">
              СОГЛАСИЕ
            </h2>
            <p className="font-serif italic text-shanti-olive text-sm">
              на получение рассылки и рекламных материалов
            </p>
          </div>

          <p className="text-justify indent-6">
            Настоящим я, во исполнение требований Федерального закона от 13.03.2006 № 38-ФЗ «О рекламе», регистрируясь и/или вводя свои данные на сайте{" "}
            <a href={req.website} target="_blank" rel="noreferrer" className="font-medium text-shanti-green underline">
              {req.website}
            </a>
            , его сервисах и/или его поддоменах (далее — «Сайт») добровольно, свободно, своей волей и в своем интересе даю свое согласие{" "}
            <span className="font-semibold">{req.companyName}</span> (ИНН: {req.inn}, ОГРНИП: {req.ogrn}) (далее — «Оператор») на получение рассылки материалов рекламного и/или информационного характера посредством SMS-сервисов и/или электронной почты, а также посредством WhatsApp или Telegram-рассылки от Оператора и подтверждаю, что в полной мере ознакомился с настоящим Согласием и Политикой обработки персональных данных Оператора, а также подтверждаю достоверность предоставленных мною данных.
          </p>

          <div className="space-y-3 bg-shanti-light/70 p-5 rounded-2xl border border-shanti-earth/50">
            <p className="font-semibold text-shanti-dark">
              Настоящее Согласие дано с целью оперативного получения следующей информации, но не ограничиваясь ей:
            </p>
            <ul className="list-disc list-inside space-y-1.5 text-shanti-dark/90 pl-2">
              <li>новостей и информации о продуктах и услугах Оператора, партнеров Оператора;</li>
              <li>информации о специальных предложениях и рекламных акциях, системах скидок, бонусов и различного рода мероприятиях и презентациях по продуктам и услугам Оператора, партнеров Оператора.</li>
            </ul>
          </div>

          <p className="text-justify">
            Настоящее Согласие действует бессрочно, либо до получения Оператором отзыва Согласия.
          </p>

          <p className="text-justify indent-6">
            Я подтверждаю, что владею информацией о том, что в любой момент в течение всего срока действия настоящего Согласия, я вправе отозвать свое согласие на получение рассылки материалов рекламного и/или информационного характера и отписаться от их получения, путем перехода по соответствующей ссылке, имеющейся в любом письме, полученном от Оператора, либо, направив письмо на адрес электронной почты Оператора с пометкой: <span className="font-medium italic">«Отзыв согласия на получение рассылки и рекламных материалов»</span>.
          </p>

          {/* Requisites Card */}
          <div className="mt-8 p-6 rounded-2xl bg-shanti-earth/20 border border-shanti-earth/80 space-y-3">
            <div className="flex items-center gap-2 font-serif font-bold text-shanti-dark text-sm uppercase tracking-wider text-shanti-green">
              <ShieldCheck className="w-5 h-5 text-shanti-green" />
              <span>Контакты и реквизиты Оператора:</span>
            </div>
            <div className="space-y-1.5 text-xs sm:text-sm text-shanti-dark/90 font-mono leading-relaxed pt-1">
              <p className="font-sans font-semibold text-shanti-dark text-base">{req.companyName}</p>
              {req.address && <p><span className="text-shanti-olive font-sans">Регион:</span> {req.address}</p>}
              <p><span className="text-shanti-olive font-sans">ИНН:</span> {req.inn}</p>
              <p><span className="text-shanti-olive font-sans">ОГРНИП:</span> {req.ogrn}</p>
              <p><span className="text-shanti-olive font-sans">Электронная почта:</span> <a href={`mailto:${req.email}`} className="text-shanti-green underline">{req.email}</a></p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 bg-shanti-light border-t border-shanti-earth text-center text-xs text-shanti-olive font-sans space-y-2">
          <p>© ИП Киселев А.П. (KISELEVY_CREO). Согласие на получение рассылки и рекламных материалов.</p>
          <a
            href="/"
            className="inline-block px-6 py-2 bg-shanti-green text-white font-bold rounded-full hover:bg-shanti-olive transition-colors"
          >
            Вернуться в сервис Опрус
          </a>
        </div>
      </div>
    </div>
  );
};

export default ConsentPage;
